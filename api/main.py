"""
FastAPI based API on the credentialLeakDB

Author: Aaron Kaplan
License: see LICENSE

"""

# system / base packages
import os
from tempfile import SpooledTemporaryFile
import time
import shutil
import logging
from pathlib import Path

# database, ASGI, etc.
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
import uvicorn
from pydantic import EmailStr
import pandas as pd

# packages from this code repo
from api.models import Leak, LeakData, Answer, AnswerMeta
from importer.parser import BaseParser


app = FastAPI()  # root_path='/api/v1')

#################################
# DB functions

db_conn = None
DSN = "host=%s dbname=%s user=%s" % (os.getenv('DBHOST', 'localhost'), os.getenv('DBNAME'), os.getenv('DBUSER'))

VER = "0.4"


#############
# DB specific functions
@app.on_event('startup')
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.  """
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
    """Connects to the specific database."""
    try:
        conn = psycopg2.connect(dsn)
        conn.set_session(autocommit=True)
    except Exception as ex:
        raise HTTPException(status_code=500, detail="could not connect to the DB. Reason: %s" % (str(ex)))
    logging.info("connection to DB established")
    return conn


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/")
async def root():
    return {"message": "Hello World"}  # , "root_path": request.scope.get("root_path")}


@app.get('/user/{email}')
async def get_user_by_email(email: EmailStr) -> Answer:
    sql = """SELECT * from leak_data where email=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/user_and_password/{email}/{password}')
async def get_user_by_email_and_password(email: EmailStr, password: str) -> Answer:
    sql = """SELECT * from leak_data where email=%s and password=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email, password))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_email/{email}')
async def check_user_by_email(email: EmailStr) -> Answer:
    sql = """SELECT count(*) from leak_data where email=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        rows = cur.fetchone()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_password/{password}')
async def check_user_by_password(password: str) -> Answer:
    # can do better... use the hashid library?
    sql = """SELECT count(*) from leak_data where password=%s or password_plain=%s or password_hashed=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (password, password, password))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get('/exists/by_domain/{domain}')
async def check_user_by_domain(domain: str) -> Answer:
    sql = """SELECT count(*) from leak_data where domain=%s"""
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (domain,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


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
    path = "{}/{}".format(upload_path, orig_filename)  # prefix, orig_filename, sha256, pid, suffix)
    logging.info("storing %s ... to %s" % (orig_filename, path))
    file.seek(0)
    with open(path, "w+b") as outfile:
        shutil.copyfileobj(file._file, outfile)
    return path


async def check_file(_filename: str) -> bool:
    return True  # XXX FIXME Implement


@app.get("/leak/all", tags=["Leak"])
async def get_all_leaks() -> Answer:
    """Fetch all leaks."""
    t0 = time.time()
    sql = "SELECT * from leak"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak_data/{leak_id}", tags=["Leak Data"])
async def get_leak_data_by_leak(leak_id: int) -> Answer:
    """Fetch all leak data entries of a given leak_id."""
    t0 = time.time()
    sql = "SELECT * from leak_data where leak_id=%s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak_id,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/{_id}", tags=["Leak"], description='Get the leak info by its ID.')
@app.get("/leak/by_id/{_id}", tags=["Leak"], description='Alias endpoint for /leak/{id}.')
async def get_leak_by_id(_id: int) -> Answer:
    """Fetch a leak by its ID"""
    t0 = time.time()
    sql = "SELECT * from leak WHERE id = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (_id,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_ticket_id/{ticket_id}", tags=["Leak"])
async def get_leak_by_ticket_id(ticket_id: str) -> Answer:
    """Fetch a leak by its ticket system id"""
    t0 = time.time()
    sql = "SELECT * from leak WHERE ticket_id = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (ticket_id,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_summary/{summary}", tags=["Leak"])
async def get_leak_by_summary(summary: str) -> Answer:
    """Fetch a leak by summary"""
    sql = "SELECT * from leak WHERE summary = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (summary,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_reporter/{reporter}", tags=["Leak"])
async def get_leak_by_reporter(reporter: str) -> Answer:
    """Fetch a leak by its reporter"""
    sql = "SELECT * from leak WHERE reporter_name = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (reporter,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak/by_source/{source_name}", tags=["Leak"])
async def get_leak_by_source(source_name: str) -> Answer:
    """Fetch a leak by its source (i.e. WHO collected the leak data (spycloud, HaveIBeenPwned, etc.)"""
    sql = "SELECT * from leak WHERE source_name = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (source_name,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.post("/leak/", tags=["Leak"])
async def new_leak(leak: Leak) -> Answer:
    """
    INSERT a new leak into the leak table in the database.
    """
    sql = """INSERT into leak
             (summary, ticket_id, reporter_name, source_name, breach_ts, source_publish_ts, ingestion_ts)
             VALUES (%s, %s, %s, %s, %s, %s, now())
             ON CONFLICT DO NOTHING
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name, leak.source_name, leak.breach_ts,
                          leak.source_publish_ts,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.put("/leak/", tags=["Leak"])
async def update_leak(leak: Leak) -> Answer:
    """
    UPDATE an existing leak.
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
        return {"error": "id %s not given. Please specify a leak.id you want to UPDATE", "data": []}
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name,
                          leak.source_name, leak.breach_ts, leak.source_publish_ts, leak.id))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.get("/leak_data/by_ticket_id/{ticket_id}", tags=["Leak Data"])
async def get_leak_data_by_ticket_id(ticket_id: str) -> Answer:
    """Fetch a leak row (leak_data table) by its ticket system id"""
    sql = "SELECT * from leak_data WHERE ticket_id = %s"
    t0 = time.time()
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (ticket_id,))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.post("/leak_data/", tags=["Leak Data"])
async def new_leak_data(row: LeakData) -> Answer:
    """
    INSERT a new leak_data row into the leak_data table.
    """
    sql = """INSERT into leak_data
             (leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id,
             email_verified, password_verified_ok, ip, domain, browser, malware_name, infected_machine, dg)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
             ON CONFLICT DO NOTHING
             RETURNING id
        """
    t0 = time.time()
    db = get_db()
    print(row)
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.put("/leak_data/", tags=["Leak Data"])
async def update_leak_data(row: LeakData) -> Answer:
    """
    UPDATE leak_data row in the leak_data table.
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
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg, row.id))
        rows = cur.fetchall()
        t1 = time.time()
        d = t1 - t0
        return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
    except Exception as ex:
        return Answer(error=str(ex), data=[])


@app.post("/import/csv/{leak_id}", tags=["Leak"])
async def import_csv(leak_id: int, _file: UploadFile = File(...)) -> Answer:
    """
    Import a CSV file into the DB. You **need** to specify a ?leak_id=<int> parameter so that the CSV file may be
    linked to a leak_id. Failure to provide a leak_id will result in the file not being imported into the DB.
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
            return Answer(error="Leak ID %s not found" % leak_id, data=[])
    except Exception as ex:
        return Answer(error=str(ex), data=[])

    # okay, we found the leak, let's insert the CSV
    print('leak_id = %s' % leak_id)

    file_on_disk = await store_file(_file.filename, _file.file)
    await check_file(file_on_disk)  # XXX FIXME. Additional checks on the dumped file still missing

    print('still alive 1')
    p = BaseParser()
    df = pd.DataFrame()
    print('still alive 2')
    try:
        # p = parser_spycloud.Parser()      # XXX FIXME need to be flexible when chosing which parser to use
        print('still alive 2a')
        print('still alive 2a: file on disk = %s' % file_on_disk)
        df = p.parse_file(Path(file_on_disk), leak_id=leak_id)
        print('still alive 3')
    except Exception as ex:
        return Answer(error=str(ex), data=[])

    df = p.normalize_data(df, leak_id=leak_id)
    print(df.describe())

    """ 
    Now, after normalization, the df is in the format:
      leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id, email_verified, 
         password_verified_ok, ip, domain, browser , malware_name, infected_machine, dg
    Example:
    
    """

    for r in data_pandas.reset_index().to_dict('rows'):
        sql = """
        INSERT into leak_data(
          leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id, email_verified, 
          password_verified_ok, ip, domain, browser , malware_name, infected_machine, dg
          )
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) ON CONFLICT DO NOTHING RETURNING *
        """
        try:
            cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, (r['leak_id'], r['email'], r['password'], r['password_plain'], r['password_hashed'],
                r['hash_algo'], r['ticket_id'], r['email_verified'], r['password_verified_ok'], r['ip'],
                r['domain'], r['browser'], r['malware_name'], r['infected_machine'], r['dg']))
            rows = cur.fetchall()
            t1 = time.time()
            d = t1 - t0
            return Answer(meta=AnswerMeta(version=VER, duration=d, count=len(rows)), data=rows)
        except Exception as ex:
            return Answer(error=str(ex), data=[])

    # XXX FIXME implement dedup

    """
    sql2 = '''
    INSERT INTO leak_data (leak_id, email, password, password_plain, password_hashed, hash_algo, email_verified,
       password_verified_ok, ip, domain, browser, malware_name, infected_machine, dg)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING RETURNING id
    '''
    p = parser_spycloud.SpycloudParser()
    df = p.parse_file(file)
    for i, row in df.iterrows():
        try:
            cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql2, (leak_id, row['email'], row['password'], ...))
            leak_id = cur.fetchall()[0]
        except Exception as ex:
            return Answer(error=str(ex), data=[])
    """


@app.post("/deduplicate/csv/")
async def dedup_csv(file: UploadFile = File(...)) -> Answer:
    """ XXX FIXME. need to implement deduping. XXX"""

    t0 = time.time()

    # The UploadFile object, is a
    # https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile) . So first write it to disk:
    file_on_disk = await store_file(file.filename, file.file)
    await check_file(file_on_disk)  # XXX FIXME. Additional checks on the dumped file still missing

    p = BaseParser()
    # p = parser_spycloud.Parser()      # XXX FIXME need to be flexible when chosing which parser to use
    df = p.parse_file(Path(file_on_disk, leak_id = leak_id))
    df = pd.DataFrame()

    # insert file into DB XXX FIXME

    # dedup

    t1 = time.time()
    # return results
    return Answer(meta=AnswerMeta(duration=t1 - t0, version=VER, count=len(df)), data=df.to_dict(orient="records"))


if __name__ == "__main__":
    db_conn = connect_db(DSN)
    uvicorn.run(app, debug=True, port=os.getenv('PORT', default=8080))
