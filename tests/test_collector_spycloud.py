import unittest

from pathlib import Path

from modules.collectors.spycloud.collector import SpyCloudCollector


class SpyCloudCollectorTest(unittest.TestCase):
    def test_collect(self):
        path = Path('tests/fixtures/data_anonymized_spycloud.csv')
        tc = SpyCloudCollector()
        statuscode, data = tc.collect(path)
        assert statuscode == "OK"
        assert data.iloc[0]['breach_title'] == 'Freedom Fox Combo List'
        assert data.iloc[0]['email'] == 'peter@example.com'
