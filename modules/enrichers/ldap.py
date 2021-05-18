
from modules.enrichers.ldap_lib import CEDQuery


class LDAPEnricher:
    """LDAP Enricher can query LDAP and offers multiple functions such as email-> dg"""

    def __init__(self):
        self.ced = CEDQuery()

    def email_to_DG(self, email: str) -> str:
        """Return the DG of an email. Note that there might be multiple DGs, we just return the first one here."""
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['dg'] and \
                    results[0]['attributes']['dg'][0]:
                return results[0]['attributes']['dg'][0]
            else:
                return "Unknown"
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def email_to_user_id(self, email: str) -> str:
        """Return the userID of an email. """
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and  results[0]['attributes']['ecMoniker'] and \
                    results[0]['attributes']['ecMoniker'][0]:
                return results[0]['attributes']['ecMoniker'][0]
            else:
                return None
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def email_to_status(self, email: str) -> str:
        """Return the active status."""
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['recordStatus'] and \
                    results[0]['attributes']['recordStatus'][0]:
                return results[0]['attributes']['recordStatus'][0]
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def exists(self, email: str) -> bool:
        """Check if a user exists."""
        if "A" == self.email_to_status(email).upper():
            return True
        else:
            return False
