"""Simple DB wrapper class

Author: Aaron Kaplan
LICENSE: see LICENSE file
"""

import psycopg2
import logging

class DB:
    def __init__(self):
        self.conn = None
        self.cur = None
        pass

    def connect(dsn: str):
        try:
            self.conn = psycopg2.connect(dsn)
            self.cur = conn.cursor()
        except Exception as ex:
            logging.error("could not connect to the DB. Reason: %s", str(ex))
            raise(ex)
        return self


    def insert_leak(self, summary: str, reporter_name: str, source_name: str, breach_ts=None, source_publish_ts=None,
                    ticket_id=None, infected_machine=None, dg=None):
        """INSERTs the most leak table data.
           :rtype: integer (ID of the leak)
        """
        leak_id = None
        if not summary:
            logging.error("Can't INSERT without a summary! Skipping.")
        else:
            sql = '''INSERT into leak (
                    breach_ts,
                    source_publish_ts,
                    ingestion_ts,
                    summary,
                    ticket_id,
                    reporter_name,
                    source_name,
                    infected_machine,
                    dg)
                  VALUES ( %s, %s, now(), %s, %s, %s, %s , %s, %s)
                  ON CONFLICT DO UPDATE RETURNING id'''
            try:
                params = (breach_ts, source_publish_ts, summary, ticket_id, reporter_name, source_name,
                          infected_machine, dg)
                self.cur.execute(sql, params)
                leak_id = cur.fetchone()[0]
            except Exception as ex:
                logging.error("could not insert/fetch leak, reason: %s. SQL=%s", str(ex), cur.mogrify(sql, params))
        return leak_id

    def upsert_leak_data(self):
        pass