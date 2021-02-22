"""
FastAPI based API on the credentialLeakDB

Author: Aaron Kaplan
License: see LICENSE

"""
import os
from tempfile import SpooledTemporaryFile
import time
import shutil
from pathlib import Path

import psycopg2
import psycopg2.extras
import logging

from fastapi import FastAPI, Request, HTTPException, File, UploadFile
import uvicorn
# import models
from pydantic import EmailStr

from importer import parser, parser_spycloud


app = FastAPI()         # root_path='/api/v1')

#################################
# DB functions

db_conn = None
DSN = "dbname=credentialdb dbuser=aaron"


#############
# DB specific functions
@app.on_event('startup')
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.  """
    global db_conn

    if not db_conn:
        db_conn = connect_db("dbname=credentialleakdb user=aaron")
    return db_conn


@app.on_event('shutdown')
def close_db(db_conn):
    """Closes the database again at the end of the request."""

    logging.info('shutting down....')
    if db_conn:
        db_conn.close()
        db_conn = None


def connect_db(dsn: str):
    """Connects to the specific database."""
    try:
        conn = psycopg2.connect(dsn)
    except Exception as ex:
        raise HTTPException(status_code=500, detail="could not connect to the DB. Reason: %s" % (str(ex)))
    logging.info("connection to DB established")
    return conn


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}       # , "root_path": request.scope.get("root_path")}


@app.get('/user/{email}')
async def get_user_by_email(email: EmailStr):
    sql = """SELECT * from leak_data where email=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        return {"data": cur.fetchall()}
    except Exception as ex:
        return {"error": str(ex), "data": []}

@app.get('/user_and_password/{email}/{password}')
async def get_user_by_email(email: EmailStr, password: str):
    sql = """SELECT * from leak_data where email=%s and password=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email, password))
        return {"data": cur.fetchall()}
    except Exception as ex:
        return {"error": str(ex), "data": []}


@app.get('/exists/by_email/{email}')
async def check_user_by_email(email: EmailStr):
    sql = """SELECT count(*) from leak_data where email=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        return {"data": cur.fetchone()}
    except Exception as ex:
        return {"error": str(ex), "data": []}


@app.get('/exists/by_password/{password}')
async def check_user_by_password(password: str):
    # can do better... use the hashid library?
    sql = """SELECT count(*) from leak_data where password=%s or password_plain=%s or password_hashed=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (password, password, password))
        return {"data": cur.fetchall()}
    except Exception as ex:
        return {"error": str(ex), "data": []}


@app.get('/exists/by_domain/{domain}')
async def check_user_by_domain(domain: str):
    sql = """SELECT count(*) from leak_data where domain=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (domain,))
        return {"data": cur.fetchall()}
    except Exception as ex:
        return {"error": str(ex), "data": []}


#####################################
# File uploading
async def store_file(orig_filename: str, file: SpooledTemporaryFile,
                     upload_path=os.getenv('UPLOAD_PATH', default='/tmp')) -> str:
    """
    Stores a SpooledTemporaryFile to a permanent location and returns the path to it
    @param orig_filename:  the filename according to multipart
    @param file: the SpooledTemporary File
    @param upload_path: where the uploaded file should be stored permanently
    @return: full path to the stored file
    """
    # Unfortunately we need to really shutil.copyfileobj() the file object to disk, even though we already have a
    # SpooledTemporaryFile object... this is needed for SpooledTemporaryFiles . Sucks. See here:
    #   https://stackoverflow.com/questions/94153/how-do-i-persist-to-disk-a-temporary-file-using-python
    #
    # filepath syntax:  <UPLOAD_PATH>/<original filename>
    #   example: /tmp/Spycloud.csv
    path = "{}/{}".format(upload_path, orig_filename)     # prefix, orig_filename, sha256, pid, suffix)
    logging.info("storing %s ... to %s" % (orig_filename, path))
    file.seek(0)
    with open(path, "w+b") as outfile:
        shutil.copyfileobj(file._file, outfile)
    return path


async def check_file(filename: str) -> bool:
    return True     # XXX FIXME Implement


@app.post("/deduplicate/csv/")
async def dedup_csv(file: UploadFile = File(...)):
    """ XXX FIXME. need to implement deduping. XXX"""

    t0 = time.time()

    # The UploadFile object, is a
    # https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile) . So first write it to disk:
    file_on_disk = await store_file(file.filename, file.file)
    await check_file(file_on_disk)  # XXX FIXME. Additional checks on the dumped file still missing

    p = parser.BaseParser()
    # p = parser_spycloud.Parser()      # XXX FIXME need to be flexible when chosing which parser to use
    df = p.parse_file(Path(file_on_disk))

    # insert file into DB XXX FIXME

    # dedup

    t1 = time.time()
    # return results
    return {"meta": {"duration": (t1 - t0)}, "data": df.to_dict(orient="records")}         # orient='table', index=False)


if __name__ == "__main__":

    db_conn = connect_db(DSN)
    uvicorn.run(app, debug=True, port=os.getenv('PORT', default=8888))
