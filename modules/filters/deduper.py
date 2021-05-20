"""Deduper - this package offers different deduplicaton functions."""

import logging
from typing import Union

import psycopg2
import psycopg2.extras

from lib.db.db import _get_db

from models.idf import InternalDataFormat


class Deduper:
    """The DB based deduper."""

    bloomf_loaded = False

    def __init__(self):
        pass

    def load_bf(self):
        # XXX IMPROVEMENT: we might want to use bloomfilters here
        self.bloomf_loaded = True

    def dedup(self, idf: InternalDataFormat) -> Union[None, InternalDataFormat]:
        """Deduplicate an IDF element based on the existence in the DB.
        FIXME: this is O(n^2) with n entries in the DB unless indexed properly. Think about indices or a bloom filter

        :param idf - internal data format element
        :returns: None if it already exists, otherwise the idf
        :raises Exception on DB problem

        """
        if not self.bloomf_loaded:
            self.load_bf()
            self.bloomf_loaded = True
        # at the moment, we'll use postgresql

        conn = _get_db()
        sql = "SELECT count(*) from leak_data WHERE email=%s and password=%s"

        try:
            cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
            cur.execute(sql, (idf.email, idf.password))
            rows = cur.fetchall()
            count = int(rows[0]['count'])
            if count >= 1:
                # row already exists, return None
                return None
            else:
                return idf
        except Exception as ex:
            logging.error("Deduper: could not select data from the DB. Reason: %s" % (str(ex)))
            raise ex
