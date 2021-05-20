import unittest

import pandas as pd

from lib.basecollector.collector import *


class TestBaseCollector(unittest.TestCase):
    def test_collect(self):
        valid_csv_file = 'tests/fixtures/data.csv'
        invalid_csv_file = 'tests/fixtures/dataDOESNTEXIST.csv'

        tc = BaseCollector()
        df: pd.DataFrame
        status, df = tc.collect(valid_csv_file)
        assert status == "OK"
        assert not df.empty
        assert df.shape[0] > 1

        status, df = tc.collect(invalid_csv_file)
        assert status != "OK"
        assert df.empty
