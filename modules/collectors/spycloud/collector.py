"""
Spycloud collector

This code implements a SpyCloud collector (inherits from BaseCollector)

Upon running a SpyCloud parser on a CSV, the result will be a
"""
from pathlib import Path
import logging
import pandas as pd

from lib.basecollector.collector import BaseCollector
from lib.helpers import peek_into_file

NaN_values = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A',
              'NA', 'NULL', 'NaN', 'n/a', 'null', '-']


class SpyCloudCollector(BaseCollector):
    def __init__(self):
        pass

    def collect(self, input_file: Path, **kwargs) -> (str, pd.DataFrame):
        try:
            dialect = peek_into_file(input_file)
            df = pd.read_csv(input_file, dialect=dialect, na_values=NaN_values,
                             keep_default_na=False, error_bad_lines=False, warn_bad_lines=True)
            # XXX FIXME: need to collect the list of (pandas-) unparseable rows and present to user.
            # For now we simply fail on the whole file. Good enough for the moment.
        except pd.errors.ParserError as ex:
            logging.error("could not parse CSV file. Reason: %r" % (str(ex),))
            return str(ex), pd.DataFrame()
        return "OK", df
