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
        te = VIPenricher(path)      # will pass because there we catch the exception
        self.assertRaises(Exception, te.load_vips, path)


class TestIsExternalEmail(unittest.TestCase):
    def test_is_internal(self):
        email = "foobar.example@ext.ec.europa.eu"
        te = ExternalEnricher()
        assert te.is_internal_email(email)
        domain = "ec.europa.eu"
        assert te.is_internal_email(domain)

    def test_is_external(self):
        email = "aaron@example.com"
        te = ExternalEnricher()
        assert te.is_external_email(email)

