#!/usr/bin/env python3


import sys
import logging
from pathlib import Path
import csv
import time
from tqdm import tqdm

import pandas as pd


debug=True


def peek_into_file(_f: Path()) -> csv.Dialect:
    """Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions."""
    with _f.open(mode='r') as f:
        sniffer = csv.Sniffer()
        logging.debug("has header: %s" % sniffer.has_header(f.read(1024)))
        f.seek(0)
        dialect = sniffer.sniff(f.read(1024))
        logging.debug("delim: '%s'" % dialect.delimiter)
        logging.debug("quotechar: '%s'" % dialect.quotechar)
        logging.debug("doublequote: %s" % dialect.doublequote)
        logging.debug("escapechar: '%s'" % dialect.escapechar)
        logging.debug("lineterminator: %r" % dialect.lineterminator)
        logging.debug("quoting: %s" % dialect.quoting)
        logging.debug("skipinitialspace: %s" % dialect.skipinitialspace)
        return dialect


def parse(folder: Path(), pattern='*.txt') -> pd.DataFrame:
    """Recursively search a given folder for <pattern> and parse all files there.
    Return a pandas dataframe with the parsed data.

    Iterator.
    """
    total_errs = 0
    errcnt = 0
    i = 0
    for fname in tqdm(Path(folder).rglob(pattern)):
        i+=1
        errcnt = 0
        dialect = peek_into_file(Path(fname))
        try:
            df = pd.read_csv(fname, dialect=dialect, error_bad_lines=False, warn_bad_lines=True, usecols=range(2), engine='c')
            yield df
            if debug:
                print(df.head(), file=sys.stderr)
                print(df.describe(), file=sys.stderr)
        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file" %(fname, str(ex)))
            errcnt += 1
        print("parsed {} with {} errors".format(fname, errcnt))
        total_errs += errcnt
    print("Summary: in total we parse {} files with {} errors".format(i, errcnt))


if __name__ == "__main__":
    errcnt = 0

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    t0 = time.time()
    for df in parse('test_leaks', '*.txt'):
        print(df)
    t1 = time.time()
    logging.info("processed everything in %f [sec]" % (t1 - t0))
