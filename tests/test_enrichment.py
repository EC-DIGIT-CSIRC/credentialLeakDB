import unittest
from pathlib import Path

# from modules.enrichers.ldap import LDAPEnricher
from modules.enrichers.external_email import ExternalEmailEnricher
from modules.enrichers.abuse_contact import AbuseContactLookup
from modules.enrichers.vip import VIPEnricher


class TestVIPenrichment(unittest.TestCase):
    def test_load_vips(self):
        path = 'tests/fixtures/vips.txt'
        te = VIPEnricher(Path(path))

        assert te.is_vip('AARON@example.com')
        assert te.is_vip('aaron@example.com')
        assert not te.is_vip('foobar-doesnotexist')

    def test_load_vips_invalid_path(self):
        path = 'tests/fixtures/vips.txt-doesnotexist'
        te = VIPEnricher(Path(path))  # will pass because there we catch the exception
        self.assertRaises(Exception, te.load_vips, path)


class TestIsExternalEmail(unittest.TestCase):
    def test_is_internal(self):
        email = "foobar.example@ext.ec.europa.eu"
        te = ExternalEmailEnricher()
        assert te.is_internal_email(email)
        domain = "ec.europa.eu"
        assert te.is_internal_email(domain)

    def test_is_external(self):
        email = "aaron@example.com"
        te = ExternalEmailEnricher()
        assert te.is_external_email(email)


class TestAbuseContactLookup(unittest.TestCase):
    def test_lookup(self):
        email = "aaron@example.com"
        te = AbuseContactLookup()
        assert email == te.lookup(email)[0]
        email = "aaron@example.ec.europa.eu"
        assert "ec-digit-csirc@ec.europa.eu" == te.lookup(email)[0]
