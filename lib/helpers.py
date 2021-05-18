import csv
import logging
from pathlib import Path

def peek_into_file(fname: Path) -> csv.Dialect:
    '''
    Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions.

    :param fname: a Path object for the filename
    :return: a csv.Dialect
    '''

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