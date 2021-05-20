import unittest

from lib.baseenricher.enricher import BaseEnricher
from models.idf import InternalDataFormat


class TestBaseEnricher(unittest.TestCase):
    def test_enrich(self):
        idf = InternalDataFormat(email="foo@example.com", password = "12345", notify = True)
        te = BaseEnricher()
        result = te.enrich(idf)
        assert result == idf