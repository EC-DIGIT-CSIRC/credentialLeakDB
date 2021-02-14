#!/usr/bin/env python3


import sys
import logging
from pathlib import Path
import csv
import time
from tqdm import tqdm

import pandas as pd
import psycopg2

debug=True
conn = None
cur = None


def peek_into_file(_f: Path()) -> csv.Dialect:
    """Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions."""
    with _f.open(mode='r') as f:
        sniffer = csv.Sniffer()
        logging.debug("has header: %s" % sniffer.has_header(f.read(1024)))
        f.seek(0)
        dialect = sniffer.sniff(f.read(1024))
        logging.debug("delim: '%s'" % dialect.delimiter)
        logging.debug("quotechar: '%s'" % dialect.quotechar)
        logging.debug("doublequote: %s" % dialect.doublequote)
        logging.debug("escapechar: '%s'" % dialect.escapechar)
        logging.debug("lineterminator: %r" % dialect.lineterminator)
        logging.debug("quoting: %s" % dialect.quoting)
        logging.debug("skipinitialspace: %s" % dialect.skipinitialspace)
        return dialect


def parse(folder: Path(), pattern='*.txt') -> pd.DataFrame:
    """Recursively search a given folder for <pattern> and parse all files there.
    Return a pandas dataframe with the parsed data.

    Iterator.
    """
    total_errs = 0
    errcnt = 0
    i = 0
    for fname in tqdm(Path(folder).rglob(pattern)):
        i+=1
        errcnt = 0
        leak_name = str(fname).split('/')[1]

        dialect = peek_into_file(Path(fname))
        try:
            df = pd.read_csv(fname, dialect=dialect, error_bad_lines=False, warn_bad_lines=True, usecols=range(2), engine='c')
            if debug:
                print(df.head(), file=sys.stderr)
                print(df.describe(), file=sys.stderr)
            yield df

        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file" %(fname, str(ex)))
            errcnt += 1
        print("parsed {} with {} errors".format(fname, errcnt))
        total_errs += errcnt
    print("Summary: in total we parse {} files with {} errors".format(i, errcnt))


def prepare_db_structures(breach_title, reporter, collection=None, breach_ts=None, source_publish_ts=None, leaked_website=None, jira_ticket_id=None):
    """Fill up all relevant tables (leak, reporter, when the breach happened,
    etc. etc.) up first before we insert the actual leak data (individual rows).

    This whole thing is super ugly and could use some ORM love. Feel free to improve it please.
    """

    if not breach_title:
        logging.error("can't insert into DB when no breach title given")
        return
    if not reporter:
        logging.error("can't insert into DB when no reporter given")
        return

    # first try to insert the collection, if we have one
    if collection:
        try:
            sql = 'INSERT into collection (name) values (%s) ON CONFLICT (name) DO UPDATE SET name = %s RETURNING id'
            cur.execute(sql, (collection, collection))
            collection_id = cur.fetchone()[0]
        except Exception as ex:
            print("could not insert/fetch collection, reason: {}. SQL={}".format(str(ex), cur.mogrify(sql, (collection, collection))))
    else:
        collection_id = None

    # next the reporter
    try:
        sql = 'INSERT into leak_reporter (name) values (%s) RETURNING id'
        cur.execute(sql, (reporter, ))
        reporter_id = cur.fetchone()[0]
    except Exception as ex:
        print("could not insert/fetch reporter, reason: {}. SQL={}".format(str(ex), cur.mogrify(sql, (reporter,))))

    # the actual leak
    leak_id = None
    sql = 'INSERT INTO leak (breach_title, leak_reporter_id, ingestion_ts) values (%s, %s, now()) ON CONFLICT DO NOTHING RETURNING id'
    try:
        cur.execute(sql, (breach_title, reporter_id, ))
        leak_id = cur.fetchone()[0]
    except Exception as ex:
        print("could not insert to DB, reason: {}".format(str(ex)))

    # and if we have a collection, do the n-to-m intersection tbl
    if leak_id and collection and collection_id:
        try:
            sql = 'INSERT into leak2collection (collection_id, leak_id) values (%s, %s)'
            cur.execute(sql, (collection_id, leak_id))
        except Exception as ex:
            print("could not insert/fetch into leak2collection, reason: {}. SQL={}".format(str(ex), cur.mogrify(sql, (collection_id, leak_id,))))

    conn.commit()
    cur.close()


if __name__ == "__main__":
    errcnt = 0

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    conn = psycopg2.connect("dbname=credentialleakdb user=credentialleakdb")
    cur = conn.cursor()

    prepare_db_structures(breach_title='COMB', reporter='Anonymous', collection='COMB')

    t0 = time.time()
    for df in parse('test_leaks', '*.txt'):
        print(df)
    t1 = time.time()
    logging.info("processed everything in %f [sec]" % (t1 - t0))
