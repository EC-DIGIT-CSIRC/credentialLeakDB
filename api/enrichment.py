"""
Enrichment code

Author: Aaron Kaplan
License: see LICENSE

"""

import sys
import os
from pathlib import Path
from typing import List

class VIP_enricher():
    """Can determine if an Email Adress is a VIP. Super trivial code."""

    vips = []

    def __init__(self, vipfile='VIPs.txt'):
        try:
            self.load_vips(os.getenv('VIPLIST', default=vipfile))
        except Exception as ex:
            print("Could not load VIP list. Using an empty list and continuing.", file=sys.stderr)

    def load_vips(self, path: Path()) -> List[str]:
        with open(path, 'r') as f:
            self.vips = f.readlines()
            self.vips = [s.rstrip() for s in self.vips]
            self.vips = list(map(str.upper, self.vips))
            print(self.vips)
            return self.vips

    def is_vip(self, email: str) -> bool:
        return email.upper() in self.vips

    def __str__(self):
        return ",".join(self.vips)

    def __repr__(self):
        return ",".join(self.vips)
