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

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
import uvicorn
from models import Leak, LeakData, Answer, AnswerMeta
from pydantic import EmailStr

# from ..importer import parser, parser_spycloud

app = FastAPI()  # root_path='/api/v1')

#################################
# DB functions

db_conn = None
DSN = "host=%s dbname=%s user=%s" % (os.getenv('DBHOST', 'localhost'), os.getenv('DBNAME'), os.getenv('DBUSER'))


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
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get('/user_and_password/{email}/{password}')
async def get_user_by_email_and_password(email: EmailStr, password: str) -> Answer:
    sql = """SELECT * from leak_data where email=%s and password=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email, password))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get('/exists/by_email/{email}')
async def check_user_by_email(email: EmailStr) -> Answer:
    sql = """SELECT count(*) from leak_data where email=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (email,))
        return Answer(data=cur.fetchone())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get('/exists/by_password/{password}')
async def check_user_by_password(password: str) -> Answer:
    # can do better... use the hashid library?
    sql = """SELECT count(*) from leak_data where password=%s or password_plain=%s or password_hashed=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (password, password, password))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get('/exists/by_domain/{domain}')
async def check_user_by_domain(domain: str) -> Answer:
    sql = """SELECT count(*) from leak_data where domain=%s"""
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (domain,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


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


@app.get("/leak/{id}", tags=["Leak"])
@app.get("/leak/by_id/{id}", tags=["Leak"])
async def get_leak_by_id(_id: int) -> Answer:
    """Fetch a leak by its ID"""
    sql = "SELECT * from leak WHERE id = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (_id,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get("/leak/by_summary/{summary}", tags=["Leak"])
async def get_leak_by_summary(summary: str) -> Answer:
    """Fetch a leak by summary"""
    sql = "SELECT * from leak WHERE summary = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (summary,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get("/leak/by_reporter/{reporter}", tags=["Leak"])
async def get_leak_by_reporter(reporter: str) -> Answer:
    """Fetch a leak by its reporter"""
    sql = "SELECT * from leak WHERE reporter_name = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (reporter,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.get("/leak/by_source/{source_name}", tags=["Leak"])
async def get_leak_by_source(source_name: str) -> Answer:
    """Fetch a leak by its source (i.e. WHO collected the leak data (spycloud, HaveIBeenPwned, etc.)"""
    sql = "SELECT * from leak WHERE source_name = %s"
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (source_name,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


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
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name, leak.source_name, leak.breach_ts,
                          leak.source_publish_ts,))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


@app.put("/leak/", tags=["Leak"])
async def update_leak(leak: Leak) -> Answer:
    """
    UPDATE an existing leak.
    """
    sql = """UPDATE leak SET 
                summary = %s, ticket_id = %s, reporter_name = %s, source_name = %s, 
                breach_ts = %s, source_publish_ts = %s, ingestion_ts = %s
             WHERE id = %s
             ON CONFLICT DO NOTHING 
             RETURNING id
        """
    db = get_db()
    if not leak.id:
        return {"error": "id %s not given. Please specify a leak.id you want to UPDATE", "data": []}
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name,
                          leak.source_name, leak.breach_ts, leak.source_publish_ts, leak.id))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


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
    db = get_db()
    print(row)
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


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
    db = get_db()
    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (row.leak_id, row.email, row.password, row.password_plain, row.password_hashed, row.hash_algo,
                          row.ticket_id, row.email_verified, row.password_verified_ok, row.ip, row.domain, row.browser,
                          row.malware_name, row.infected_machine, row.dg, row.id))
        return Answer(data=cur.fetchall())
    except Exception as ex:
        return Answer(error=str(ex), data={})


# async def import_csv(leak: Leak = Form(...), file: UploadFile = File(...)):
@app.post("/import/csv", tags=["Leak"])
async def import_csv(leak: Leak = Form(...), file: UploadFile = File(...)) -> Answer:
    """Import a CSV file into the DB. The parameters are given for the leak table entry."""
    t0 = time.time()

    print(leak)
    sql = '''
    INSERT INTO leak (summary, ticket_id, reporter_name, source_name, breach_ts, source_publish_ts, ingestion_ts)
    VALUES (%s, %s, %s, %s, %s, %s, now()) 
    ON CONFLICT  DO NOTHING RETURNING id
    '''
    leak_id = -1
    db = get_db()
    file_on_disk = await store_file(file.filename, file.file)
    await check_file(file_on_disk)  # XXX FIXME. Additional checks on the dumped file still missing

    try:
        cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (leak.summary, leak.ticket_id, leak.reporter_name,
                          leak.source_name,
                          leak.breach_ts, leak.source_publish_ts))
        leak_id = cur.fetchall()[0]
    except Exception as ex:
        return Answer(error=str(ex), data={})

    # p = parser.BaseParser()
    # try:
    #     # p = parser_spycloud.Parser()      # XXX FIXME need to be flexible when chosing which parser to use
    #     df = p.parse_file(Path(file_on_disk))
    # except Exception as ex:
    #     return Answer(error=str(ex), data={})

    # insert file into DB XXX FIXME

    # dedup

    t1 = time.time()
    # return results
    return Answer(error="XXX not implemented right now, fixing something at the moment", data=[])
    # return {"meta": {"duration": (t1 - t0)}, "data": df.to_dict(orient="records")}  # orient='table', index=False)

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
            return Answer(error=str(ex), data={})
    """


@app.post("/deduplicate/csv/")
async def dedup_csv(file: UploadFile = File(...)) -> Answer:
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
    return Answer(meta=AnswerMeta(duration=t1 - t0), data=df.to_dict(orient="records"))  # orient='table', index=False)


if __name__ == "__main__":
    db_conn = connect_db(DSN)
    uvicorn.run(app, debug=True, port=os.getenv('PORT', default=8888))
