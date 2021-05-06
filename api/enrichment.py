"""
Enrichment code

Author: Aaron Kaplan
License: see LICENSE

"""
import collections
import sys
import os
import re
from pathlib import Path
from typing import List

from modules.enrichers.ced import CEDQuery


class VIPenricher:
    """Can determine if an Email Adress is a VIP. Super trivial code."""

    vips = []

    def __init__(self, vipfile='VIPs.txt'):
        try:
            self.load_vips(os.getenv('VIPLIST', default=vipfile))
        except Exception as ex:
            print("Could not load VIP list. Using an empty list and continuing. Exception: %s" % str(ex), file=sys.stderr)

    def load_vips(self, path: Path()) -> List[str]:
        with open(path, 'r') as f:
            self.vips = [x.strip().upper() for x in f.readlines()]
            return self.vips

    def is_vip(self, email: str) -> bool:
        return email.upper() in self.vips

    def __str__(self):
        return ",".join(self.vips)

    def __repr__(self):
        return ",".join(self.vips)


class ExternalEnricher:
    """Can determine if an Email Adress is an (organisation-) external email address. Also super trivial code."""

    @staticmethod
    def is_internal_email(email: str) -> bool:
        email = email.lower()
        if email and email.endswith('europa.eu') or email.endswith('jrc.it'):
            return True
        else:
            return False

    @staticmethod
    def is_external_email(email: str) -> bool:
        return not ExternalEnricher.is_internal_email(email)


class LDAPEnricher:
    """LDAP Enricher can query LDAP and offers multiple functions such as email-> dg"""

    def __init__(self):
        self.ced = CEDQuery()

    def email2DG(self, email: str) -> List[str]:
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['dg'][0]:
                return results[0]['attributes']['dg'][0]
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def email2userId(self, email: str) -> str:
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['ecMoniker'][0]:
                return results[0]['attributes']['ecMoniker'][0]
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def email2status(self, email: str) -> str:
        try:
            results = self.ced.search_by_mail(email)
            if results and results[0]['attributes'] and results[0]['attributes']['recordStatus'][0]:
                return results[0]['attributes']['recordStatus'][0]
        except Exception as ex:
            print("could not query LDAP/CED. Reason: %s" % str(ex))
            return None

    def exists(self, email: str) -> bool:
        if "A" == self.email2status(email).upper():
            return True
        else:
            return False


class AbuseContactLookup:
    """A simple abuse contact lookup class."""

    def lookup(self, email: str) -> str:
        """Look up the right abuse contact for credential leaks based on the email address.
        Example:
            lookup("example@jrc.it")   --> "reports@jrc.it"

        :argument email: the email address
        :rtype string: string
        :returns email: the email address for the abuse contact
        """

        """The following mapping table is of the form:
           regular expression   --> email address or "DIRECT".   If DIRECT is returned, send directly to the email addr. 
           The matching should proceed top down
        """

        mapping_table = collections.OrderedDict({
            re.compile(r"example\.ec\.europa\.eu", re.X): "ec-digit-csirc@ec.europa.eu",       # example
            re.compile(r".*\.ec\.europa\.eu", re.X): "DIRECT",
            re.compile(r".*", re.X): "DIRECT"          # the default catch-all rule. Don't delete!
        })

        domain = email.split('@')[-1]
        print("%s domain part of %s" %(domain, email))
        for k,v in mapping_table.items():
            if re.match(k, domain):
                if v == "DIRECT":
                    return email
                else:
                    return v
        return None



