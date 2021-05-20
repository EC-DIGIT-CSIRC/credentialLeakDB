#!/usr/bin/env python3
"""importer.parser """


from lib.helpers import getlogger
from pathlib import Path
import csv
import time

import pandas as pd

debug = True

logger = getlogger(__name__)


# noinspection PyTypeChecker
def peek_into_file(fname: Path) -> csv.Dialect:
    """
    Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions.

    :param fname: a Path object for the filename
    :return: a csv.Dialect
    """

    with fname.open(mode='r') as f:
        sniffer = csv.Sniffer()
        logger.debug("has apikeyheader: %s", sniffer.has_header(f.readline()))
        f.seek(0)
        dialect = sniffer.sniff(f.readline(50))
        logger.debug("delim: '%s'", dialect.delimiter)
        logger.debug("quotechar: '%s'", dialect.quotechar)
        logger.debug("doublequote: %s", dialect.doublequote)
        logger.debug("escapechar: '%s'", dialect.escapechar)
        logger.debug("lineterminator: %r", dialect.lineterminator)
        logger.debug("quoting: %s", dialect.quoting)
        logger.debug("skipinitialspace: %s", dialect.skipinitialspace)
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
        logger.info("Parsing file %s..." % fname)
        try:
            if csv_dialect:
                dialect = csv_dialect
            else:
                dialect = peek_into_file(fname)     # try to guess
            df = pd.read_csv(fname, dialect=dialect, error_bad_lines=False, warn_bad_lines=True)  # , usecols=range(2))
            logger.debug(df.head())
            logger.debug(df.info())
            logger.debug("Parsing file 2...")
            df.insert(0, 'leak_id', leak_id)
            logger.debug(df.head())
            logger.debug("parsed %s", fname)
            return df

        except Exception as ex:
            logger.error("could not pandas.read_csv(%s). Reason: %s. Skipping file." % (fname, str(ex)))
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


    p = BaseParser()
    t0 = time.time()
    # p.parse_recursively('test_leaks', '*.txt')
    t1 = time.time()
    logger.info("processed everything in %f [sec]", (t1 - t0))
