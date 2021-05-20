from models.idf import InternalDataFormat

from modules.filters.deduper import Deduper


def test_load_bf():
    dd = Deduper()
    assert not dd.bloomf_loaded
    dd.load_bf()
    assert dd.bloomf_loaded


def test_dedup():
    dd = Deduper()
    idf = InternalDataFormat(email="aaron@example.com", password="12345",
                             notify=False, needs_human_intervention=False)
    idf2 = dd.dedup(idf)
    assert not idf2
    idf = InternalDataFormat(email="aaron999735@example.com", password="12345XXX",
                             notify=False, needs_human_intervention=False)
    idf2 = dd.dedup(idf)
    assert idf2
