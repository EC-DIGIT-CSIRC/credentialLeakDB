import unittest

import pandas as pd

from lib.baseparser.parser import BaseParser

class TestBaseParser(unittest.TestCase):
    def test_parse(self):
        tp = BaseParser()
        df = pd.DataFrame()
        tp.parse(df)
        assert True     # not very useful right now but the structure for the test case is here
