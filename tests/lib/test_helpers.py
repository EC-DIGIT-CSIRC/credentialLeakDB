from lib.helpers import anonymize_password

def test_anonymize_password():
    pass1 = "12345678"
    expected = "1*****78"
    assert anonymize_password(pass1) == expected

    pass2 = "123"
    expected = "123"
    assert anonymize_password(pass2) == expected

    pass3 = "12"
    expected = "12"
    assert anonymize_password(pass3) == expected

    pass4 = ""
    expected = ""
    assert anonymize_password(pass4) == expected

    pass5 = None
    expected = None
    assert anonymize_password(pass5) == expected
