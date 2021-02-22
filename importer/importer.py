#!/usr/bin/env python
"""Import data from test_data/* to the DB.

Author: L. Aaron Kaplan <Leon-Aaron.Kaplan@ext.ec.europa.eu>
License: see LICENSE

"""

import logging
import time
import argparse
from pathlib import Path
from tqdm import tqdm

import parser, parser_spycloud


def parse_recursively(folder: Path, pattern='*.csv'):
    """Recursively search a given folder for <pattern> and parse all files there. Calls the DB insert."""
    i = 0
    for fname in tqdm(folder.rglob(pattern)):
        i += 1
        logging.debug("looking at %s", fname)
        leak_path = str(fname).split('/')[1].upper()
        if 'SPYCLOUD' in leak_path:
            p = parser_spycloud.SpycloudParser()
        # elif 'CIT0DAY' in leak_path:
        #     p = parser_spycloud.SpycloudParser()
        else:
            p = parser.BaseParser()
        df = p.parse_file(fname)
        df = p.normalize_data(df)
        # this code below is leak-parser specific, please adapt
        logging.info("INSERTING %s into DB..", fname)
        #      db.insert_leak(df)
    logging.info("Summary: in total we parse %s files", i)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--debug', action="store_true", help="enable debug output")
    ap.add_argument('-p', '--regexp_pattern', help="The glob pattern for searching for files. Default=*.csv",
                    default="*.csv")
    ap.add_argument('dir', help="The directory to scan for leaks")
    args = ap.parse_args()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    logging.info("params = %r", args)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    t0 = time.time()
    parse_recursively(Path(args.dir), args.regexp_pattern)
    t1 = time.time()
    logging.info("processed everything in %f [sec]", (t1 - t0))
