"""
FastAPI based API on the credentialLeakDB

Author: Aaron Kaplan
License: see LICENSE

"""

# system / base packages
import logging
import os
import shutil
import time
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import List

# database, ASGI, etc.
import pandas as pd
import psycopg2
import psycopg2.extras
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Security, Response
from fastapi.security.api_key import APIKeyHeader, APIKey, Request
from pydantic import EmailStr

# packages from this code repo
from api.models import Leak, LeakData, Answer, AnswerMeta
from importer.parser import BaseParser
from api.config import config

###############################################################################
# API key stuff
API_KEYLEN = 32
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

#################################
# DB functions

db_conn = None
DSN = "host=%s dbname=%s user=%s password=%s" % (os.getenv('DBHOST', 'localhost'),
                                                 os.getenv('DBNAME', 'credentialleakdb'),
                                                 os.getenv('DBUSER', 'credentialleakdb'),
                                                 os.getenv('DBPASSWORD'))

VER = "0.5"

app = FastAPI(title="CredentialLeakDB", version=VER, )  # root_path='/api/v1')


# ##############################################################################
# DB specific functions
@app.on_event('startup')
def get_db():
    """
    Open a new database connection if there is none yet for the
    current application context.

    :returns: the DB handle."""
    global db_conn

    if not db_conn:
        db_conn = connect_db(DSN)
    return db_conn


@app.on_event('shutdown')
def close_db():
    """Closes the database again at the end of the request."""
    global db_conn

    logging.info('shutting down....')
    if db_conn:
        db_conn.close()
        db_conn = None


def connect_db(dsn: str):
    """Connects to the specific database.

    :param dsn: the database connection string.
    :returns: the DB connection handle
    """
    try:
        conn = psycopg2.connect(dsn)
        conn.set_session(autocommit=True)
    except Exception as ex:
        raise HTTPException(status_code=500, detail="could not connect to the DB. Reason: %s" % (str(ex)))
    logging.info("connection to DB established")
    return conn


# ##############################################################################
# security / authentication
def fetch_valid_api_keys() -> List[str]:
    """Fetch the list of valid API keys from a DB or a config file.

    :returns: List of strings - the API keys
    """

    return config['api_keys']


def is_valid_api_key(key: str) -> bool:
    """
    Validate a given key if it is in the list of allowed API keys *or* if the source IP where the
    request is coming from in in a list of valid IP addresses.

    :param key: the API key
    :returns: boolean: YES/NO
    """

    valid_api_keys = fetch_valid_api_keys()

    # allowed_ips = ['127.0.0.1',
    #                '192.168.1.1',     # my own IP, in this example an RFC1918
    #               ]
    # if key in valid_api_keys or (request.client.host in allowed_ips):
    if key in valid_api_keys:
        return True
    return False


def validate_api_key_header(apikeyheader: str = Security(api_key_header)):
    """
    Validate if a given API key is present in the HTTP apikeyheader.

    :param apikeyheader: the required HTTP Header
    :returns: the apikey apikeyheader again, if it is valid. Otherwise, raise an HTTPException and return 403.
    """
    if not apikeyheader:
        raise HTTPException(status_code=403,
                            detail="""need API key. Please get in contact with the admins of this
                            site in order get your API key.""")
    if is_valid_api_key(apikeyheader):
        return apikeyheader
    else:
        raise HTTPException(
            status_code=403,  # HTTP FORBIDDEN
            detail="""Could not validate the provided credentials. Please get in contact with the admins of this
            site in order get your API key."""
        )


# ##############################################################################
# File uploading
async def store_file(orig_filename: str, _file: SpooledTemporaryFile,
                     upload_path=os.getenv('UPLOAD_PATH', default='/tmp')) -> str:
    """
    Stores a SpooledTemporaryFile to a permanent location and returns the path to it

    :param orig_filename:  the filename according to multipart
    :param _file: the SpooledTemporary File
    :param upload_path: where the uploaded file should be stored permanently
    :returns: full path to the stored file
    """
    # Unfortunately we need to really shutil.copyfileobj() the file object to disk, even though we already have a
    # SpooledTemporaryFile object... this is needed for SpooledTemporaryFiles . Sucks. See here:
    #   https://stackoverflow.com/questions/94153/how-do-i-persist-to-disk-a-temporary-file-using-python
    #
    # filepath syntax:  <UPLOAD_PATH>/<original filename>
    #   example: /tmp/Spycloud.csv
    path = "{}/{}".format(upload_path, orig_filename)  # prefix, orig_filename, sha256, pid, suffix)
    logging.info("storing %s ... to %s" % (orig_filename, path))
    _file.seek(0)
    with open(path, "w+b") as outfile:
        shutil.copyfileobj(_file._file, outfile)
    return path


async def check_file(filename: str) -> bool:
    return True  # XXX FIXME Implement


# ====================================================
# API endpoints

@app.get("/ping",
         name="Ping test",
         summary="Run a ping test, to check if the service is running",
         tags=["Tests"])
async def ping():
    """A simple ping / liveliness test endpoint. No API Key required."""
    return {"message": "pong"}


@app.get("/", tags=["Tests"])
async def root(api_key: APIKey = Depends(validate_api_key_header)):
    """A simple hello world endpoint. This one requires an API key."""
    return {"message": "Hello World"}  # , "root_path": request.scope.get("root_path")}


# ##############################################################################
# General API endpoints


@app.get('/user/{email}',
         tags=["General queries"],
         status_code=200,
         response_model=Answer)
async def get_user_by_email(email: EmailStr,
                            response: Response,
                            api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """
    Get the all credential leaks in the DB of a given user specified by his email address.

    # Parameters
      * email: string. The email address of the user (case insensitive).

    # Returns
      * A JSON Answer object with rows being an array of answers, or [] in case there was no data in the DB
    """
    sql = """SELECT * from leak_data where upper(email)=upper(%s)"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/user_and_password/{email}/{password}',
         tags=["General queries"],
         status_code=200,
         response_model=Answer)
async def get_user_by_email_and_password(email: EmailStr,
                                         password: str,
                                         response: Response,
                                         api_key: APIKey = Depends(validate_api_key_header)
                                         ) -> Answer:
    """
    Get the all credential leaks in the DB of a given user given by the combination email + password.
    Note that both email and password must match (where email is case insensitive, the password *is case sensitive*).

    # Parameters
      * email: string. The email address of the user (**case insensitive**, since email is usually case insensitive).
      * password: string. The (hashed or plaintext) password (**note: this is case sensitive**)

    # Returns
      * A JSON Answer object with rows being an array of answers, or [] in case there was no data in the DB

    # Example
    ``foo@example.com`` and ``12345`` -->

    ``{ "meta": { ... }, "data": [ { "id": 14, "leak_id": 1, "email": "aaron@example.com", "password": "12345", ...,  ],
        "error": null }``

    """
    sql = """SELECT * from leak_data where upper(email)=upper(%s) and password=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email, password))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_email/{email}',
         tags=["General queries"],
         status_code=200,
         response_model=Answer)
async def check_user_by_email(email: EmailStr,
                              response: Response,
                              api_key: APIKey = Depends(validate_api_key_header)
                              ) -> Answer:
    """
    Check if a certain email address was present in any leak.

    # Parameters
    * email: string. The email address of the user (**case insensitive**, since email is usually case insensitive).

    # Returns
    * A JSON Answer object with rows being an array of answers, or [] in case there was no data in the DB

    # Example
    ``foo@example.com`` -->
    ``{ "meta": { "version": "0.5", "duration": 0.002, "count": 1 }, "data": [ { "count": 1 } ], "error": null }``
    """
    sql = """SELECT count(*) from leak_data where upper(email)=upper(%s)"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_password/{password}',
         tags=["General queries"],
         status_code=200,
         response_model=Answer)
async def check_user_by_password(password: str,
                                 response: Response,
                                 api_key: APIKey = Depends(validate_api_key_header)
                                 ) -> Answer:
    """
    Check if a user exists with the given password (either plaintext or hashed) in the DB. If so, return the user.

    # Parameters
    * password: string. The password to be searched.

    # Returns
    * A JSON Answer object with rows being an array of answers, or [] in case there was no data in the DB

    # Example
    ``12345`` -->
    ``{ "meta": { ... }, "data": [ { "id": 14, "leak_id": 1, "email": "aaron@example.com", "password": "12345",
        ...,  ], "error": null }``
    """
    # can do better... use the hashid library?

    sql = """SELECT count(*) from leak_data where password=%s or password_plain=%s or password_hashed=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (password, password, password))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_domain/{domain}',
         tags=["General queries"],
         status_code=200,
         response_model=Answer)
async def check_by_domain(domain: str,
                          response: Response,
                          api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """
    Check if a given domain appears in some leak.

    # Parameters
      * domain : string. The domain to search for (case insensitive).

    # Returns:
    A JSON Answer object with the count of occurrences in the data: field.
    """

    sql = """SELECT count(*) from leak_data where upper(domain)=upper(%s)"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (domain,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


# ##############################################################################
# Reference data (reporter, source, etc) starts here
@app.get('/reporter',
         tags=["Reference data"],
         status_code=200,
         response_model=Answer)
async def get_reporters(response: Response,
                        api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """
    Get the all reporter_name entries (sorted, unique).

    # Parameters

    # Returns
      * A JSON Answer object with data containing an array of answers, or [] in case there was no data in the DB
    """
    sql = """SELECT distinct(reporter_name) from leak ORDER by reporter_name asc"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/source_name',
         tags=["Reference data"],
         status_code=200,
         response_model=Answer)
async def get_sources(response: Response,
                      api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """
    Get the all names of sources of leaks (sorted, unique) - i.e. "SpyCloud", "HaveIBeenPwned", etc..

    # Parameters

    # Returns
      * A JSON Answer object with data containing an array of answers, or [] in case there was no data in the DB
    """
    sql = """SELECT distinct(source_name) from leak ORDER by source_name asc"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


# ##############################################################################
# Leak table starts here

@app.get("/leak/all",
         tags=["Leak"],
         status_code=200,
         response_model=Answer)
async def get_all_leaks(response: Response,
                        api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """Fetch all leaks.

    # Parameters

    # Returns
     * A JSON Answer object with all leak (i.e. meta-data of leaks) data from the `leak` table.
    """

    t0 = time.time()
    sql = "SELECT * from leak"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/{_id}", tags=["Leak"],
         description='Get the leak info by its ID.',
         status_code=200,
         response_model=Answer)
async def get_leak_by_id(_id: int,
                         response: Response,
                         api_key: APIKey = Depends(validate_api_key_header)
                         ) -> Answer:
    """Fetch a leak by its ID"""
    t0 = time.time()
    sql = "SELECT * from leak WHERE id = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (_id,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_ticket_id/{ticket_id}",
         tags = ["Leak"],
         status_code=200,
         response_model = Answer)
async def get_leak_by_ticket_id(ticket_id: str,
                                response: Response,
                                api_key: APIKey = Depends(validate_api_key_header)
                                ) -> Answer:
    """Fetch a leak by its ticket system id"""
    t0 = time.time()
    sql = "SELECT * from leak WHERE ticket_id = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (ticket_id,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_summary/{summary}",
         tags=["Leak"],
         status_code=200,
         response_model=Answer)
async def get_leak_by_summary(summary: str,
                              response: Response,
                              api_key: APIKey = Depends(validate_api_key_header)
                              ) -> Answer:
    """Fetch a leak by summary"""
    sql = "SELECT * from leak WHERE summary = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (summary,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_reporter/{reporter}",
         tags=["Leak"],
         status_code=200,
         response_model=Answer)
async def get_leak_by_reporter(reporter: str,
                               response: Response,
                               api_key: APIKey = Depends(validate_api_key_header)
                               ) -> Answer:
    """Fetch a leak by its reporteri. """
    sql = "SELECT * from leak WHERE reporter_name = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (reporter,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_source/{source_name}",
         tags=["Leak"],
         status_code=200,
         response_model=Answer)
async def get_leak_by_source(source_name: str,
                             response: Response,
                             api_key: APIKey = Depends(validate_api_key_header)
                             ) -> Answer:
    """Fetch all leaks by their source (i.e. *who* collected the leak data (spycloud, HaveIBeenPwned, etc.).

    # Parameters
      * source_name: string. The name of the source (case insensitive).

    # Returns
      * a JSON Answer object with all leaks for that given source_name.
    """

    sql = "SELECT * from leak WHERE upper(source_name) = upper(%s)"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (source_name,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.post("/leak/",
          tags=["Leak"],
          description="INSERT a new leak into the DB",
          status_code=201,
          response_model=Answer)
async def new_leak(leak: Leak,
                   response: Response,
                   api_key: APIKey = Depends(validate_api_key_header)
                   ) -> Answer:
    """
    INSERT a new leak into the leak table in the database.

    # Parameters
      * leak:  a Leak object. Note that all fields must be set, except for leak.id
    # Returns
      * a JSON Answer object with the leak_id in the data: field

    """
    sql = """INSERT into leak
             (summary, ticket_id, reporter_name, source_name, breach_ts, source_publish_ts, ingestion_ts)
             VALUES (%s, %s, %s, %s, %s, %s, now())
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name, leak.source_name, leak.breach_ts,
                          leak.source_publish_ts,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 400 in case the INSERT failed.
            response.status_code = 400
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.put("/leak/",
         tags=["Leak"],
         status_code=200,
         response_model=Answer)
async def update_leak(leak: Leak,
                      response: Response,
                      api_key: APIKey = Depends(validate_api_key_header)
                      ) -> Answer:
    """
    UPDATE an existing leak.

    # Parameters
      * leak: a Leak object. Note that all fields must be set in the Leak object.
    # Returns
      * a JSON Answer object with the ID of the updated leak.
    """
    sql = """UPDATE leak SET
                summary = %s, ticket_id = %s, reporter_name = %s, source_name = %s,
                breach_ts = %s, source_publish_ts = %s
             WHERE id = %s
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    if not leak.id:
        return Answer(error="id %s not given. Please specify a leak.id you want to UPDATE", data=[])
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name,
                          leak.source_name, leak.breach_ts, leak.source_publish_ts, leak.id))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 400 in case the INSERT failed.
            response.status_code = 400
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


# ############################################################################################################
# Leak Data starts here

@app.get("/leak_data/{leak_data_id}",
         tags=["Leak Data"],
         status_code=200,
         response_model=Answer)
async def get_leak_data_by_id(leak_data_id: int,
                              response: Response,
                              api_key: APIKey = Depends(validate_api_key_header)) -> Answer:
    """
    Fetch all leak data entries of a given id.

    # Parameters
        * leak_data_id: integer, the DB internal leak_data_id.

    # Returns
     * A JSON Answer object with the corresponding leak data (i.e. actual usernames, passwords) from the `leak_data`
       table which are contained within the specified leak (leak_data_id).
    """
    t0 = time.time()
    sql = "SELECT * from leak_data where id=%s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak_data_id,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak_data/by_ticket_id/{ticket_id}",
         tags=["Leak Data"],
         status_code=200,
         response_model=Answer)
async def get_leak_data_by_ticket_id(ticket_id: str,
                                     response: Response,
                                     api_key: APIKey = Depends(validate_api_key_header)
                                     ) -> Answer:
    """Fetch a leak row (leak_data table) by its ticket system id

    # Parameters
      * ticket_id: string. The ticket system ID which references the leak_data row
    # Returns
      * a JSON Answer object with the leak data row or in data.
    """
    sql = "SELECT * from leak_data WHERE ticket_id = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (ticket_id,))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 404 in case no data was found
            response.status_code = 404
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.post("/leak_data/",
          tags=["Leak Data"],
          status_code=201,
          response_model=Answer)
async def new_leak_data(row: LeakData,
                        response: Response,
                        api_key: APIKey = Depends(validate_api_key_header)
                        ) -> Answer:
    """
    INSERT a new leak_data row into the leak_data table.

    # Parameters
      * row: a leakData object. If that data already exists, it will not be inserted again.
    # Returns
      * a JSON Answer object containing the ID of the inserted leak_data row.
    """
    sql = """INSERT into leak_data
             (leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id,
             email_verified, password_verified_ok, ip, domain, browser, malware_name, infected_machine, dg)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
             ON CONFLICT ON CONSTRAINT constr_unique_leak_data_leak_id_email_password_domain DO UPDATE SET email=%s
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    print(row)
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg, row.email))
        rows = cur.fetchall()
        if len(rows) == 0:      # return 400 in case the INSERT failed.
            response.status_code = 400
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.put("/leak_data/",
         tags=["Leak Data"],
         status_code=200,
         response_model=Answer)
async def update_leak_data(row: LeakData,
                           request: Request,
                           response: Response,
                           api_key: APIKey = Depends(validate_api_key_header)
                           ) -> Answer:
    """
    UPDATE leak_data row in the leak_data table.

    # Parameters
      * row : a leakData object with all the relevant information. Please note that you **have to** supply all fields,
        even if you do not plan to update them. In other words: you might have to GET / the leak_data object first.
    # Returns
      * a JSON Answer object containing the ID of the inserted leak_data row.
    """
    sql = """UPDATE leak_data SET
                leak_id = %s,
                email = %s,
                password = %s,
                password_plain = %s,
                password_hashed = %s,
                hash_algo = %s,
                ticket_id = %s,
                email_verified = %s,
                password_verified_ok = %s,
                ip = %s,
                domain = %s,
                browser = %s,
                malware_name = %s,
                infected_machine = %s,
                dg = %s
             WHERE id = %s
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        print("HTTP request: '%r'" % request )
        print("SQL command:")
        # print(cur.mogrify(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
        #                    row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
        #                    row.malware_name, row.infected_machine, row.dg, row.id)))
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg, row.id))
        db.commit()
        rows = cur.fetchall()
        if len(rows) == 0:      # return 400 in case the INSERT failed.
            response.status_code = 400
        t1 = time.time()
        d = round(t1 - t0, 3)
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


# ############################################################################################################
# CSV file importing
@app.post("/import/csv/{leak_id}",
          tags=["CSV import"],
          status_code=200,
          response_model=Answer)
async def import_csv(leak_id: int,
                     response: Response,
                     _file: UploadFile = File(...),
                     api_key: APIKey = Depends(validate_api_key_header)
                     ) -> Answer:
    """
    Import a CSV file into the DB. You **need** to specify a ?leak_id=<int> parameter so that the CSV file may be
    linked to a leak_id. Failure to provide a leak_id will result in the file not being imported into the DB.

    # Parameters
      * leak_id : int. As a GET parameter. This allows the DB to link the leak data (CSV file) to the leak_id entry in
        in the leak table.
      * _file: a file which must be uploaded via HTML forms/multipart.

    # Returns
      * a JSON Answer object where the data: field is the **deduplicated** CSV file (i.e. lines which were already
        imported as part of that leak (same username, same password, same domain) will not be returned.
        In other words, data: [] contains the rows from the CSV file which did not yet exist in the DB.
    """

    t0 = time.time()

    if not leak_id:
        return Answer(error="Please specify a leak_id GET-style parameter in the URL", data=[])

    # first check if the leak_id exists
    sql = """SELECT count(*) from leak where id = %s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak_id,))
        rows = cur.fetchone()
        nr_results = int(rows['count'])
        if nr_results != 1:
            response.status_code = 404
            return Answer(error="Leak ID %s not found" % leak_id, data=[])
    except Exception as ex:
        return Answer(error=str(ex), data=[])

    # okay, we found the leak, let's insert the CSV
    file_on_disk = await store_file(_file.filename, _file.file)
    await check_file(file_on_disk)  # XXX FIXME. Additional checks on the dumped file still missing

    p = BaseParser()
    df = pd.DataFrame()
    try:
        df = p.parse_file(Path(file_on_disk), leak_id=leak_id)
    except Exception as ex:
        return Answer(error=str(ex), data=[])

    df = p.normalize_data(df, leak_id=leak_id)
    """
    Now, after normalization, the df is in the format:
      leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id, email_verified,
         password_verified_ok, ip, domain, browser , malware_name, infected_machine, dg
         
    Example
    -------
    [5 rows x 15 columns]
       leak_id                email  ... infected_machine     dg
    0        1    aaron@example.com  ...     local_laptop  DIGIT
    1        1    sarah@example.com  ...    sarahs_laptop  DIGIT
    2        1  rousben@example.com  ...      WORKSTATION  DIGIT
    3        1    david@example.com  ...      Macbook Pro  DIGIT
    4        1    lauri@example.com  ...  Raspberry PI 3+  DIGIT
    5        1  natasha@example.com  ...  Raspberry PI 3+  DIGIT

    """

    i = 0
    inserted_ids = []
    for r in df.reset_index().to_dict(orient='rows'):
        sql = """
        INSERT into leak_data(
          leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id, email_verified, 
          password_verified_ok, ip, domain, browser , malware_name, infected_machine, dg
          )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) 
        ON CONFLICT ON CONSTRAINT constr_unique_leak_data_leak_id_email_password_domain 
        DO UPDATE SET  count_seen = leak_data.count_seen + 1 
        RETURNING id
        """
        try:
            cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, (r['leak_id'], r['email'], r['password'], r['password_plain'], r['password_hashed'],
                              r['hash_algo'], r['ticket_id'], r['email_verified'], r['password_verified_ok'], r['ip'],
                              r['domain'], r['browser'], r['malware_name'], r['infected_machine'], r['dg']))
            leak_data_id = int(cur.fetchone()['id'])
            inserted_ids.append(leak_data_id)
            i += 1
        except Exception as ex:
            return Answer(error=str(ex), data=[])
    t1 = time.time()
    d = round(t1 - t0, 3)
    num_deduped = len(inserted_ids)
    logging.info("inserted %d rows, %d duplicates, %d new rows" % (i, i - num_deduped))

    # now get the data of all the IDs / dedup
    try:
        sql = """SELECT * from leak_data where id in %s"""
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (tuple(inserted_ids),))
        data = cur.fetchall()
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(inserted_ids)), data=data)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


if __name__ == "__main__":
    db_conn = connect_db(DSN)
    uvicorn.run(app, debug=True, port=os.getenv('PORT', default=8080))
