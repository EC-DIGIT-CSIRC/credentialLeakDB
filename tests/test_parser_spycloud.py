import json
import unittest
import pandas as pd
from pathlib import Path
from modules.parsers.spycloud import SpyCloudParser
from modules.collectors.spycloud.collector import SpyCloudCollector


class SpyCloudParserTest(unittest.TestCase):
    def test_parse(self):
        df = pd.DataFrame()
        path = 'tests/fixtures/data_anonymized_spycloud.csv'
        tc = SpyCloudCollector()
        statuscode, df = tc.collect(Path(path))
        assert statuscode == "OK"
        tp = SpyCloudParser()
        idf = tp.parse(df)
        assert idf
        # print([ i for i in idf ])
        for i in idf:
            if "error_msg" in i.dict() and i.error_msg:
                print("error_msg: %s" % i.error_msg)
                print("orig_line: %s" %i.original_line)