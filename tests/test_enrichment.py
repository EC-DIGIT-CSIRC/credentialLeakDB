import unittest

from credentialLeakDB.api.enrichment import *


class TestVIPenrichment(unittest.TestCase):
    def test_load_vips(self):
        path = 'tests/fixtures/vips.txt'
        te = VIPenricher(path)

        assert te.is_vip('AARON@example.com')
        assert te.is_vip('aaron@example.com')
        assert not te.is_vip('foobar-doesnotexist')

    def test_load_vips_invalid_path(self):
        path = 'tests/fixtures/vips.txt-doesnotexist'
        te = VIPenricher(path)
        self.assertRaises(Exception, te.load_vips, path)
