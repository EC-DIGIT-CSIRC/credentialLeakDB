"""
SpyCloud Parser

Accepts a pandas DF, parses and validates it against the *IN*put format and returns it in the *internal* IDF format

"""

import logging
# from typing import List

from pydantic import parse_obj_as, ValidationError
import pandas as pd
import numpy as np
from typing import List

from lib.baseparser.parser import BaseParser
from models.indf import SpyCloudInputEntry
from models.idf import InternalDataFormat


class SpyCloudParser(BaseParser):
    def __init__(self):
        """init"""
        super().__init__()

    def parse(self, df: pd.DataFrame) -> List[InternalDataFormat]:
        """parse a pandas DF and return the data in the Internal Data Format."""

        # First, map empty columns to None so that it fits nicely into the IDF
        df.replace({"-": None}, inplace = True)
        df.replace({"nan": None}, inplace = True)
        df.replace({np.nan: None}, inplace = True)
        df.replace({'breach_date': {'Unknown': None}}, inplace = True)

        # some initial checks on the df

        # validate via pydantic
        items = []
        for row in df.reset_index().to_dict(orient = 'records'):
            logging.debug("row=%s" % row)
            idf_dict = dict(email = None, password = None, notify = False, domain = None, error_msg = "incomplete data",
                            needs_human_intervention = True)
            idf_dict['original_line'] = str(row)
            try:
                input_data_item = parse_obj_as(SpyCloudInputEntry, row)  # here the validation magic happens
                idf_dict = input_data_item.dict()  # conversion magic happens between input format and internal df
                idf_dict['domain'] = input_data_item.email_domain        # map specific fields
            except Exception as ex:
                idf_dict['needs_human_intervention'] = True
                idf_dict['notify'] = False
                idf_dict['error_msg'] = str(ex)
                logging.error("could not parse CSV row. Original line: %r.\nReason: %s" % (repr(row), str(ex)))
                logging.debug("idf_dict = %s" % idf_dict)
            else:
                logging.error("everything successfully converted")
                idf_dict['needs_human_intervention'] = False
                idf_dict['notify'] = True
                idf_dict['error_msg'] = None
            finally:
                try:
                    idf = InternalDataFormat(**idf_dict)  # another step of validation happens here
                    logging.debug("idf = %r" % idf)
                except Exception as ex2:
                    logging.error("Exception in finally. idf_dict = %r" % idf_dict)
                    raise ex2
                else:
                    items.append(idf)

        return items
