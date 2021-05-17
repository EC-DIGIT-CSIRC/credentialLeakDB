"""ExternalEmailEnricher"""

class ExternalEmailEnricher:
    """Can determine if an Email Adress is an (organisation-) external email address. Also super trivial code."""

    @staticmethod
    def is_internal_email(email: str) -> bool:
        email = email.lower()
        if email and email.endswith('europa.eu') or email.endswith('jrc.it'):
            return True
        else:
            return False

    @staticmethod
    def is_external_email(email: str) -> bool:
        return not ExternalEmailEnricher.is_internal_email(email)

