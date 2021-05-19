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
        pass

    def parse(self, df: pd.DataFrame) -> List[InternalDataFormat]:
        """parse a pandas DF and return the data in the Internal Data Format."""


        # First, map empty columns to None so that it fits nicely into the IDF
        df.replace({"-": None}, inplace = True)
        df.replace({"nan": None}, inplace = True)
        df.replace({np.nan: None}, inplace = True)
        df.replace({'breach_date': {'Unknown': None}}, inplace = True)
        print(df.describe())

        # validate via pydantic
        items = []
        for row in df.reset_index().to_dict(orient = 'records'):
            logging.error("row=%s" % row)
            try:
                indf_item = parse_obj_as(SpyCloudInputEntry, row)  # here the validation magic happens
                idf_dict = indf_item.dict()  # conversion magic happens between input format and internal data format
                idf_dict['domain'] = indf_item.email_domain        # map specific fields
            except ValidationError as ex:
                idf_dict['needs_human_intervention'] = True
                idf_dict['notify'] = False
                idf_dict['error_msg'] = ex.json()
                idf_dict['original_line'] = str(row)
                logging.error("could not parse CSV file. Original line: %r.\nReason: %s" % (repr(row), str(ex)))
            else:
                idf_dict['needs_human_intervention'] = False
                idf_dict['notify'] = True
                idf_dict['error_msg'] = None
            finally:
                idf = InternalDataFormat(**idf_dict)  # another step of validation happens here
                items.append(idf)
        return items
