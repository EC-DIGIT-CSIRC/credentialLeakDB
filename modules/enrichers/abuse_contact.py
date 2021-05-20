"""AbuseContactLookup: look up the right abuse contact based on a user's email address."""

import collections
import re
from typing import List


class AbuseContactLookup:
    """A simple abuse contact lookup class."""

    def lookup(self, email: str) -> List[str]:
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
            re.compile(r"example\.ec\.europa\.eu", re.X): ["ec-digit-csirc@ec.europa.eu"],       # example
            re.compile(r".*\.ec\.europa\.eu", re.X): "DIRECT",
            re.compile(r".*", re.X): "DIRECT"          # the default catch-all rule. Don't delete!
        })

        domain = email.split('@')[-1]
        for k, v in mapping_table.items():
            if re.match(k, domain):
                if v == "DIRECT":
                    return [email]
                else:
                    return v
        return [""]
