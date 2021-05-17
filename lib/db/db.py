"""Very very lightweight DB abstraction"""

import os
import psycopg2
import psycopg2.extras

from fastapi import HTTPException
import logging


#################################
# DB functions

db_conn = None
DSN = "host=%s dbname=%s user=%s password=%s" % (os.getenv('DBHOST', 'localhost'),
                                                 os.getenv('DBNAME', 'credentialleakdb'),
                                                 os.getenv('DBUSER', 'credentialleakdb'),
                                                 os.getenv('DBPASSWORD'))


def _get_db():
    """
    Open a new database connection if there is none yet for the
    current application context.

    :returns: the DB handle."""
    global db_conn

    if not db_conn:
        db_conn = _connect_db(DSN)
    return db_conn


def _close_db():
    """Closes the database again at the end of the request."""
    global db_conn

    logging.info('shutting down....')
    if db_conn:
        db_conn.close()
        db_conn = None
    return db_conn


def _connect_db(dsn: str):
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

