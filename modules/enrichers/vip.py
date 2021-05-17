"""VIP Enricher. Can determine if an email addr. is a VIP and needs to be treated specially."""

import os
import logging
from pathlib import Path

from typing import List


class VIPEnricher:
    """Can determine if an Email Address is a VIP. Super trivial code."""

    vips = []

    def __init__(self, vipfile: Path = Path('VIPs.txt')):
        try:
            self.load_vips(os.getenv('VIPLIST', default = vipfile))
        except Exception as ex:
            logging.error("Could not load VIP list. Using an empty list and continuing. Exception: %s" % str(ex))

    def load_vips(self, path: Path) -> List[str]:
        """Load the external reference data set of the known VIPs."""
        with open(path, 'r') as f:
            self.vips = [x.strip().upper() for x in f.readlines()]
            return self.vips

    def is_vip(self, email: str) -> bool:
        """Check if an email address is a VIP."""
        return email.upper() in self.vips

    def __str__(self):
        return ",".join(self.vips)

    def __repr__(self):
        return ",".join(self.vips)
