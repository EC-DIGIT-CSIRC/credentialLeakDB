import unittest

from modules.enrichers.external_email import ExternalEmailEnricher

class TestExternalEmailEnricher(unittest.TestCase):
    def test_is_external(self):
        external_email = "foobar@example.com"
        tee = ExternalEmailEnricher()
        assert tee.is_external_email(external_email)

        internal_email = "foobar.example@ec.europa.eu"
        assert tee.is_internal_email(internal_email)
