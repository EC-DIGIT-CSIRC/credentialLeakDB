#!/usr/bin/env python3
"""importer.parser """


import logging
from pathlib import Path
import csv
import time

import pandas as pd

debug = True


def peek_into_file(fname: Path) -> csv.Dialect:
    """Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions."""
    with fname.open(mode='r') as f:
        sniffer = csv.Sniffer()
        logging.debug("has header: %s", sniffer.has_header(f.readline()))
        f.seek(0)
        dialect = sniffer.sniff(f.readline(50))
        logging.debug("delim: '%s'", dialect.delimiter)
        logging.debug("quotechar: '%s'", dialect.quotechar)
        logging.debug("doublequote: %s", dialect.doublequote)
        logging.debug("escapechar: '%s'", dialect.escapechar)
        logging.debug("lineterminator: %r", dialect.lineterminator)
        logging.debug("quoting: %s", dialect.quoting)
        logging.debug("skipinitialspace: %s", dialect.skipinitialspace)
        return dialect


class BaseParser:
    """The abstract Parser class."""
    def __init__(self):
        pass

    def parse_file(self, fname: Path, csv_dialect=None) -> pd.DataFrame:
        """Parse file (non-recursive) and return either None (in case of errors) or a DataFrame with the contents.
        Overwrite this method in YOUR Parser subclass.

        Returns:
            a DataFrame
            number of errors while parsing
            :rtype: tuple
        """
        logging.debug("Parsing file %s...", fname)
        try:
            if csv_dialect:
                dialect = csv_dialect
            else:
                dialect = peek_into_file(fname)     # try to guess
            df = pd.read_csv(fname, dialect=dialect, error_bad_lines=False, warn_bad_lines=True, usecols=range(2))
            logging.debug(df.head())
            logging.debug(df.describe())
            logging.debug("parsed %s", fname)
            return df

        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file." %(fname, str(ex)))
            return None

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


'''
def prepare_db_structures(breach_title, reporter, collection=None, breach_ts=None, source_publish_ts=None,
                          leaked_website=None, jira_ticket_id=None, infected_machine=None, dg=None):
    """ XXX FIXME !! THIS IS BROKEN """
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
        sql = 'INSERT into collection (name) values (%s) ON CONFLICT (name) DO UPDATE SET name = %s RETURNING id'
        try:
            cur.execute(sql, (collection, collection))
            collection_id = cur.fetchone()[0]
        except Exception as ex:
            logging.error("could not insert/fetch collection, reason: %s. SQL=%s", str(ex), cur.mogrify(sql, (collection, collection)))
    else:
        collection_id = None

    # next the reporter
    sql = 'INSERT into leak_reporter (name) values (%s) RETURNING id'
    try:
        cur.execute(sql, (reporter, ))
        reporter_id = cur.fetchone()[0]
    except Exception as ex:
        logging.error("could not insert/fetch reporter, reason: %s. SQL=%s", str(ex), cur.mogrify(sql, (reporter,)))

    # the actual leak
    leak_id = None
    sql = 'INSERT INTO leak (breach_title, leak_reporter_id, ingestion_ts) values (%s, %s, now()) ON CONFLICT DO NOTHING RETURNING id'
    try:
        cur.execute(sql, (breach_title, reporter_id, ))
        leak_id = cur.fetchone()[0]
    except Exception as ex:
        logging.error("could not insert to DB, reason: %s", str(ex))

    # and if we have a collection, do the n-to-m intersection tbl
    if leak_id and collection and collection_id:
        sql = 'INSERT into leak2collection (collection_id, leak_id) values (%s, %s)'
        try:
            cur.execute(sql, (collection_id, leak_id))
        except Exception as ex:
            logging.error("could not insert/fetch into leak2collection, reason: %s. SQL=%s", str(ex), cur.mogrify(sql, (collection_id, leak_id,)))

    conn.commit()
    cur.close()
'''

if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    p = BaseParser()
    t0 = time.time()
    p.parse_recursively('test_leaks', '*.txt')
    t1 = time.time()
    logging.info("processed everything in %f [sec]", (t1 - t0))
