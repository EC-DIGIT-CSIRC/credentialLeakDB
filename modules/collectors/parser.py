#!/usr/bin/env python3
"""importer.parser """


import logging
from pathlib import Path
import csv
import time

import pandas as pd

debug = True


# noinspection PyTypeChecker
def peek_into_file(fname: Path) -> csv.Dialect:
    """
    Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions.

    :param fname: a Path object for the filename
    :return: a csv.Dialect
    """

    with fname.open(mode='r') as f:
        sniffer = csv.Sniffer()
        logging.debug("has apikeyheader: %s", sniffer.has_header(f.readline()))
        f.seek(0)
        dialect = sniffer.sniff(f.readline(50))
        logging.debug("delim: '%s'", dialect.delimiter)
        logging.debug("quotechar: '%s'", dialect.quotechar)
        logging.debug("doublequote: %s", dialect.doublequote)
        logging.debug("escapechar: '%s'", dialect.escapechar)
        logging.debug("lineterminator: %r", dialect.lineterminator)
        logging.debug("quoting: %s", dialect.quoting)
        logging.debug("skipinitialspace: %s", dialect.skipinitialspace)
        return dialect


class BaseParser:
    """The abstract Parser class."""
    def __init__(self):
        pass

    def parse_file(self, fname: Path, leak_id: int = None, csv_dialect=None) -> pd.DataFrame:
        """Parse file (non-recursive) and returns a DataFrame with the contents.
        Overwrite this method in YOUR Parser subclass.

        # Parameters
          * fname: a Path object with the filename of the CSV file which should be parsed.
          * leak_id: the leak_id in the DB which is associated with that CSV dump file.
        # Returns
            a DataFrame
            number of errors while parsing
        """
        logging.info("Parsing file %s..." % fname)
        try:
            if csv_dialect:
                dialect = csv_dialect
            else:
                dialect = peek_into_file(fname)     # try to guess
            df = pd.read_csv(fname, dialect=dialect, error_bad_lines=False, warn_bad_lines=True)  # , usecols=range(2))
            logging.debug(df.head())
            logging.debug(df.info())
            logging.debug("Parsing file 2...")
            df.insert(0, 'leak_id', leak_id)
            logging.debug(df.head())
            logging.debug("parsed %s", fname)
            return df

        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file." % (fname, str(ex)))
            raise ex        # pass it on

    def normalize_data(self, df: pd.DataFrame, leak_id: int = None) -> pd.DataFrame:
        """
        Normalize the given data / data frame

        :param df: a pandas df with the leak_data
        :param leak_id: foreign key to the leak table
        :return: a pandas df
        """
        # replace NaN with None
        return df.where(pd.notnull(df), None)


if __name__ == "__main__":

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    p = BaseParser()
    t0 = time.time()
    # p.parse_recursively('test_leaks', '*.txt')
    t1 = time.time()
    logging.info("processed everything in %f [sec]", (t1 - t0))
