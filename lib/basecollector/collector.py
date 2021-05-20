"""
BaseCollector

This implements the abstract collector interface
"""
import pandas as pd
import logging


class BaseCollector:
    """
    BaseCollector: purely abstract class which defines the interface:
      collect(input_source)

    Please note that this does *not* yet return a data frame in the internal data format (IDF).
    So all that a BaseCollector shall return is a tuple ("OK"/some_error string and a pandas DF (which may be empty
    in case of error).

    Example:
        ("OK", pd.DataFrame(... my data...) )           --> all ok, the data is in the DF.
    or
        ("Could not parse CSV file: file does not exist", pd.DataFrame())   --> error message and empty DF.

    The role of the Collector is to
     1. fetch the data
     2. check if the data is complete
     3. put it into an internal format (in our case a pandas DF) which may be processed by a parser
     4. return it as pandas DF to the next processing step in the chain
     5. return errors in case it encountered errors in validation.
    """

    def __init__(self):
        pass

    def collect(self, input_file: str, **kwargs) -> (str, pd.DataFrame):
        """
        Collect the data from input_file and return a pandas DF.

        :rtype: tuple return code ("OK" in case of success) and pandas DataFrame with the data
        """
        try:
            with open(input_file, "r") as f:
                df = pd.read_csv(f, **kwargs)
                return "OK", df
        except Exception as ex:
            logging.exception("could not parse CSV file. Reason: %r" % (str(ex),))
            return str(ex), pd.DataFrame()
