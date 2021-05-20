import csv
import logging
from pathlib import Path

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FORMAT = '%(asctime)s - [%(name)s:%(module)s:%(funcName)s] - %(levelname)s - %(message)s'

def getlogger(name: str, log_level=logging.INFO) -> logging.Logger:
    """This is how we do logging. How to use it:

    Add the following code snippet to every module
    ```
    logger = getlogger(__name__)
    logger.info("foobar")
    ```

    :param name - name of the logger
    :param log_level - default log level

    :returns logging.Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # create console handler
    ch = logging.StreamHandler()

    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('Setting up logger: DONE')

    return logger


def peek_into_file(fname: Path) -> csv.Dialect:
    """
    Peek into a file in order to determine the dialect for pandas.read_csv() / csv functions.

    :param fname: a Path object for the filename
    :return: a csv.Dialect
    """

    with fname.open(mode = 'r') as f:
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
        # noinspection PyTypeChecker
        return dialect


def anonymize_password(password: str) -> str:
    """
    "*"-out the characters of a password. Must be 4 chars in length at least.

    :param password: str
    :returns anonymized password (str):

    """
    anon_password = password
    if password and len(password) >= 4:
        prefix = password[:1]
        suffix = password[-2:]
        anon_password = prefix + "*" * (len(password) - 3) + suffix
    return anon_password
