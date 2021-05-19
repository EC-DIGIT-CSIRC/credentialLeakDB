"""Database output module. Stores an IDF item to the DB."""
import logging
import psycopg2
import psycopg2.extras

from lib.baseoutput.output import BaseOutput
from lib.db.db import _get_db
from models.outdf import LeakData


class PostgresqlOutput(BaseOutput):
    dbconn = None

    def __init__(self):
        super().__init__()
        self.dbconn = _get_db()

    def process(self, data: LeakData) -> bool:
        """Store the output format data into Postgresql.

        :returns True on success
        :raises psycopg2.Error exception
        """

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
        if data:
            try:
                with self.dbconn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cur:
                    print(cur.mogrify(sql, (
                        data.leak_id, data.email, data.password, data.password_plain, data.password, data.hash_algo,
                        data.ticket_id, data.email_verified, data.password_verified_ok, data.ip, data.domain,
                        data.browser, data.malware_name, data.infected_machine, data.dg)))
                    cur.execute(sql, (
                        data.leak_id, data.email, data.password, data.password_plain, data.password, data.hash_algo,
                        data.ticket_id, data.email_verified, data.password_verified_ok, data.ip, data.domain,
                        data.browser, data.malware_name, data.infected_machine, data.dg))
                    leak_data_id = int(cur.fetchone()['id'])
                    print("leak_data_id: %s" % leak_data_id)
            except psycopg2.Error as ex:
                logging.error("%s(): error: %s" % (self.process.__name__, ex.pgerror))
                raise ex
            return True


