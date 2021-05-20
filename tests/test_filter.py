from models.idf import InternalDataFormat

from modules.filters.filter import Filter


def test_filter():
    fi = Filter()
    idf = InternalDataFormat(email = "aaron@example.com", password = "12345", notify = False,
                             needs_human_intervention = False)
    idf2 = fi.filter(idf)
    assert idf2 == idf
