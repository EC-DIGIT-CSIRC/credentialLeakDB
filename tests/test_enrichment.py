import unittest

from credentialLeakDB.api.enrichment import *


class TestVIP_Enrichment(unittest.TestCase):
    def test_load_vips(self):
        path = 'tests/fixtures/vips.txt'
        te = VIP_enricher(path)

        assert te.is_vip('AARON@example.com')
        assert te.is_vip('aaron@example.com')
        assert not te.is_vip('foobar-doesnotexist')