"""
Enrichment code

Author: Aaron Kaplan
License: see LICENSE

"""

import sys
import os
from pathlib import Path
from typing import List

class VIPenricher():
    """Can determine if an Email Adress is a VIP. Super trivial code."""

    vips = []

    def __init__(self, vipfile='VIPs.txt'):
        try:
            self.load_vips(os.getenv('VIPLIST', default=vipfile))
        except Exception as ex:
            print("Could not load VIP list. Using an empty list and continuing. Exception: %s" % str(ex), file=sys.stderr)

    def load_vips(self, path: Path()) -> List[str]:
        with open(path, 'r') as f:
            self.vips =  [l.strip().upper() for l in f.readlines()]
            return self.vips

    def is_vip(self, email: str) -> bool:
        return email.upper() in self.vips

    def __str__(self):
        return ",".join(self.vips)

    def __repr__(self):
        return ",".join(self.vips)
