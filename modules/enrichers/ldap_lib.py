import sys
import os
import logging
from ldap3 import Server, Connection, ALL

import json

from typing import List


class CEDQuery:
    """ CEDQuery class. Encapsulates the LDAP connect and queries to CED.
    Author: L. Aaron Kaplan <leon-aaron.kaplan@ext.ec.europa.eu>
    """

    is_connected = False
    conn = None

    def __init__(self):
        """ init() function. Automatically connects to LDAP (calls the connect_ldap() function). """
        if not self.is_connected:
            self.server = os.getenv('CED_SERVER', default = 'localhost')
            self.port=int(os.getenv('CED_PORT', default = 389))
            self.user=os.getenv('CED_USER')
            self.password=os.getenv('CED_PASSWORD')
            self.base_dn=os.getenv('CED_BASEDN')
            try:
                self.connect_ldap(self.server, self.port, self.user, self.password)
                self.is_connected = True
            except Exception as ex:
                logging.error("could ot connect to LDAP. Reason: %s" % str(ex))
                self.is_connected = False

    def connect_ldap(self, server="ldap.example.com", port=389, user=None, password=None):
        """ Connects to the CED LDAP server. Returns None on failure. """
        try:
            self.s = Server(server, port=port, get_info=ALL)
            self.conn = Connection(self.s, user=user, password=password)
            logging.info("connect_ldap(): self.conn = %s" %(self.conn,))
            logging.info("connect_ldap(): conn.bind() = %s" %(self.conn.bind(),))
        except Exception as ex:
            logging.error("error connecting to CED. Reason: %s" %(str(ex)))
            return None

    def search_by_mail(self, email: str) -> List[dict]:
        attributes = ['cn', 'dg', 'uid', 'ecMoniker', 'employeeType', 'recordStatus', 'sn', 'givenName', 'mail']
        if not self.is_connected:
            logging.error("Could not seearch via email. Not connected to LDAP.")
            return None
        try:
            self.conn.search(self.base_dn, "(mail=%s)" %(email,), attributes=attributes)
        except Exception as ex:
            logging.error("could not search LDAP. error: %s" %str(ex))
        logging.info("search_by_mail(): %s" %(self.conn.entries,))
        results = [] 
        for entry in self.conn.entries:
            results.append(  json.loads(entry.entry_to_json()))
        return results          # yeah, a list comprehension would be more pythonic


if __name__ == "__main__":
    ced = CEDQuery()
    email = sys.argv[1]
    print(ced.search_by_mail(email))
