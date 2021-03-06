import logging
import os
from typing import Union

from modules.enrichers.ldap_lib import CEDQuery


class LDAPEnricher:
    """LDAP Enricher can query LDAP and offers multiple functions such as email-> dg"""

    simulate_ldap: bool = False

    def __init__(self):
        self.simulate_ldap = bool(os.getenv('SIMULATE_LDAP', default = False))
        self.ced = CEDQuery()

    def email_to_dg(self, email: str) -> str:
        """Return the DG of an email. Note that there might be multiple DGs, we just return the first one here."""

        if self.simulate_ldap:
            return "Not connected to LDAP"
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['dg'] and \
                    results[0]['attributes']['dg'][0]:
                return results[0]['attributes']['dg'][0]
            else:
                return "Unknown"
        except Exception as ex:
            logging.error("could not query LDAP/CED. Reason: %s" % str(ex))
            raise ex

    def email_to_user_id(self, email: str) -> Union[str, None]:
        """Return the userID of an email. """

        if self.simulate_ldap:
            return "Not connected to LDAP"
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['ecMoniker'] and \
                    results[0]['attributes']['ecMoniker'][0]:
                return results[0]['attributes']['ecMoniker'][0]
            else:
                return None
        except Exception as ex:
            logging.error("could not query LDAP/CED. Reason: %s" % str(ex))
            raise ex

    def email_to_status(self, email: str) -> str:
        """Return the active status."""

        if self.simulate_ldap:
            return "Not connected to LDAP"

        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['recordStatus'] and \
                    results[0]['attributes']['recordStatus'][0]:
                return results[0]['attributes']['recordStatus'][0]
        except Exception as ex:
            logging.error("could not query LDAP/CED. Reason: %s" % str(ex))
            raise ex

    def exists(self, email: str) -> bool:
        """Check if a user exists."""

        if self.simulate_ldap:
            return False

        status = self.email_to_status(email)
        if status and status.upper() == "A":
            return True
        else:
            return False
