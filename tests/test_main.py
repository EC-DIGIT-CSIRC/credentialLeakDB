from lib.helpers import getlogger

import urllib.parse
import uuid
import unittest

from fastapi.testclient import TestClient

from lib.db.db import _connect_db as connect_db

from api.main import *

VALID_AUTH = {'x-api-key': 'random-test-api-key'}
INVALID_AUTH = {'x-api-key': 'random-test-api-XXX'}

logger = getlogger(__name__)
client = TestClient(app)  # ,  base_url='http://localhost:8080/')


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


class DBTestCases(unittest.TestCase):
    def test_get_db(self):
        assert get_db() is not None

    def test_close_db(self):
        get_db()  # initialize connection
        self.assertIsNone(close_db())
        get_db()  # re-initialize connection

    def test_connect_invalid_db(self):
        self.assertRaises(Exception, connect_db, 'SOME INVALID DSN')


def test_fetch_valid_api_keys():
    assert True


class APIKeyTests(unittest.TestCase):
    """Test API key functions"""

    def test_validate_api_key_header(self):
        self.assertRaises(Exception, validate_api_key_header, "")

    def test_is_valid_api_key(self):
        assert is_valid_api_key(VALID_AUTH['x-api-key'])

    def test_is_INVALID_api_key(self):
        assert not is_valid_api_key(INVALID_AUTH['x-api-key'])

    def test_validate_api_key(self):
        assert True


def test_root_auth():
    response = client.get("/", headers = VALID_AUTH)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


# noinspection PyPep8Naming
def test_root_INVALID_auth():
    response = client.get("/", headers = INVALID_AUTH)
    assert response.status_code == 403


def test_get_user_by_email():
    email = urllib.parse.quote("aaron@example.com")
    response = client.get("/user/%s" % email, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


# noinspection PyPep8Naming
def test_get_nonexistent_user_by_INVALID_email():
    email = urllib.parse.quote("aaron@doesnotexist.com")
    response = client.get("/user/%s" % email, headers = VALID_AUTH)
    assert response.status_code != 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] == 0


def test_get_user_by_email_and_password():
    email = urllib.parse.quote("aaron@example.com")
    passwd = "12345"
    response = client.get("/user_and_password/%s/%s" % (email, passwd), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


# noinspection PyPep8Naming
def test_get_nonexistent_user_by_email_and_INVALID_password():
    email = urllib.parse.quote("aaron@example.com")
    passwd = "12345XXXXXXXXXX"
    response = client.get("/user_and_password/%s/%s" % (email, passwd), headers = VALID_AUTH)
    assert response.status_code == 404
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] == 0


def test_check_user_by_email():
    email = urllib.parse.quote("aaron@example.com")
    response = client.get("/exists/by_email/%s" % email, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


# noinspection PyPep8Naming
def test_check_nonexistent_user_by_INVALID_email():
    email = urllib.parse.quote("aaron@doesnotexist.com")
    response = client.get("/exists/by_email/%s" % email, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert "meta" in response.text and "data" in response.text and data['data'][0]['count'] == 0


def test_check_user_by_password():
    password = "12345"
    response = client.get("/exists/by_password/%s" % password, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


# noinspection PyPep8Naming
def test_check_nonexistent_user_by_INVALID_password():
    password = 'DOESNOTEXIST@59w47YTISJGw496UASGJSATARSASJKGJSAKGASRG'
    response = client.get("/exists/by_password/%s" % password, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['data'][0]['count'] == 0


def test_check_user_by_domain():
    domain = "example.com"
    response = client.get("/exists/by_domain/%s" % domain, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


# noinspection PyPep8Naming
def test_check_nonexistent_user_by_INVALID_domain():
    domain = "example.com-foobar-2esugksti2uwasgjskhsjhsa.net"
    response = client.get("/exists/by_domain/%s" % domain, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['data'][0]['count'] == 0


def test_get_reporters():
    response = client.get("/reporter/", headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['reporter_name'] == 'aaron'


def test_get_sources():
    response = client.get("/source_name/", headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    answerset = set(i['source_name'] for i in data['data'])
    print(answerset)
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           "HaveIBeenPwned" in answerset


def test_new_leak():
    test_data = {
        "ticket_id": "CSIRC-202",
        "summary": "a test leak, please ignore",
        "reporter_name": "aaron",
        "source_name": "spycloud",
        "breach_ts": "2021-03-24T16:08:33.405Z",
        "source_publish_ts": "2021-03-24T16:08:33.405Z"
    }
    response = client.post("/leak/", json = test_data, headers = VALID_AUTH)
    assert response.status_code == 201
    data = response.json()
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['id'] >= 1
    return int(data['data'][0]['id'])


def test_update_leak():
    test_data = {
        "ticket_id": "CSIRC-202",
        "summary": "an UPDATE-able test leak, please ignore",
        "reporter_name": "aaron",
        "source_name": "spycloud",
        "breach_ts": "2021-01-01T00:00:00.000Z",
        "source_publish_ts": "2021-01-02T00:00:00.000Z",
    }
    response = client.post("/leak/", json = test_data, headers = VALID_AUTH)
    assert response.status_code == 201
    data = response.json()
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['id'] >= 1
    _id = data['data'][0]['id']

    # now UPDATE it
    test_data['summary'] = "We UPDATED the test leak now!"
    test_data['id'] = _id
    response = client.put('/leak/', json = test_data, headers = VALID_AUTH)
    assert response.status_code == 200

    # fetch the results and see if it's really updated
    response = client.get('/leak/%s' % (_id,), headers = VALID_AUTH)
    assert response.status_code == 200
    assert response.json()['data'][0]['summary'] == "We UPDATED the test leak now!"

    # now try to fetch an invalid ID
    response = client.get('/leak/%s' % (_id + 10000,), headers = VALID_AUTH)
    assert response.status_code == 404


# noinspection PyPep8Naming
def test_update_INVALID_leak():
    test_data = {
        "id": -1,
        "ticket_id": "CSIRC-202",
        "summary": "trying to update a leak which does NOT EXIST",
        "reporter_name": "aaron",
        "source_name": "spycloud",
        "breach_ts": "2021-01-01T00:00:00.000Z",
        "source_publish_ts": "2021-01-02T00:00:00.000Z",
    }
    response = client.put('/leak/', json = test_data, headers = VALID_AUTH)
    assert response.status_code == 400
    assert response.json()['data'] == []


# By summary
def test_get_leak_by_summary():
    summary = "COMB"
    response = client.get('/leak/by_summary/%s' % (summary,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert data['data'][0]['summary'] == summary
    assert data['data'][0]['reporter_name'] == 'aaron'


# noinspection PyPep8Naming
def test_get_leak_by_INVALID_summary():
    summary = "COMB-XXX-DOESNETEXIST"
    response = client.get('/leak/by_summary/%s' % (summary,), headers = VALID_AUTH)
    assert response.status_code == 404
    data = response.json()
    assert data['meta']['count'] == 0


# By ticket_id
def test_get_leak_by_ticket_id():
    ticket_id = "CSIRC-102"  # we know that exists based on the db.sql import
    response = client.get('/leak/by_ticket_id/%s' % (ticket_id,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert data['data'][0]['summary'] == "COMB"


# noinspection PyPep8Naming
def test_get_leak_by_INVALID_ticket_id():
    ticket_id = "COMB-XXX-DOESNETEXIST"
    response = client.get('/leak/by_ticket_id/%s' % (ticket_id,), headers = VALID_AUTH)
    assert response.status_code == 404
    data = response.json()
    assert data['meta']['count'] == 0


def test_get_all_leaks():
    response = client.get('/leak/all', headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] > 0


def test_get_leak_by_reporter():
    response = client.get('leak/by_reporter/%s' % ("aaron",), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] > 0


def test_get_leak_by_source():
    response = client.get('leak/by_source/%s' % ("spycloud",), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] > 0


# #################################################################################
# leak_data

def test_get_leak_data_by_leak():
    leak_id = 1  # we know this exists by the db.sql INSERT
    response = client.get('/leak_data/%s' % (leak_id,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert data['data'][0]['email'] == 'aaron@example.com'


# noinspection PyPep8Naming
def test_get_leak_data_by_INVALID_leak():
    leak_id = -1  # we know this does not exist
    response = client.get('/leak_data/%s' % (leak_id,), headers = VALID_AUTH)
    assert response.status_code == 404
    data = response.json()
    assert data['meta']['count'] == 0
    assert data['data'] == []


def test_get_leak_data_by_ticket_id():
    ticket_id = 'CISRC-199'  # we know this exists by the db.sql INSERT
    response = client.get('/leak_data/by_ticket_id/%s' % (ticket_id,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert data['data'][0]['email'] == 'aaron@example.com'
    assert data['data'][1]['email'] == 'sarah@example.com'


def insert_leak_data(d: dict) -> int:
    """ generic test function for INSERTing a leak_data row given by d.

    @:param d: a row as dict
    @:returns ID: ID of the newly inserted row
    @:rtype: int
    """
    response = client.post("/leak_data/", json = d, headers = VALID_AUTH)
    print(response)
    print(response.text)
    assert response.status_code == 201
    data = response.json()
    print(data)
    assert "meta" in data and \
           "data" in data and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['id'] >= 1
    return data['data'][0]['id']


def test_new_leak_data():
    """ INSERT a new leak_data row."""
    test_data = {
        "leak_id": 1,
        "email": "aaron2@example.com",
        "password": "000000",
        "password_plain": "000000",
        "password_hashed": "d232105eb59a344df4b54db1c24009b1",
        "hash_algo": "md5",
        "ticket_id": "CSIRC-102",
        "email_verified": False,
        "password_verified_ok": False,
        "ip": "5.6.7.8",
        "domain": "example.com",
        "browser": "Chrome",
        "malware_name": "n/a",
        "infected_machine": "n/a",
        "dg": "DIGIT",
        "needs_human_intervention": False,
        "notify": False
    }
    _id = insert_leak_data(test_data)
    assert _id >= 0
    return _id


def test_update_leak_data():
    random_str = uuid.uuid4()
    test_data = {
        "leak_id": 1,
        "email": "aaron%s@example.com" % (random_str,),
        "password": "000000",
        "password_plain": "000000",
        "password_hashed": "d232105eb59a344df4b54db1c24009b1",
        "hash_algo": "md5",
        "ticket_id": "CSIRC-102",
        "email_verified": False,
        "password_verified_ok": False,
        "ip": "5.6.7.8",
        "domain": "example.com",
        "browser": "Chrome",
        "malware_name": "n/a",
        "infected_machine": "n/a",
        "dg": "DIGIT",
        "needs_human_intervention": False,
        "notify": False
    }
    # create my own leak_data row
    _id = insert_leak_data(test_data)

    # now UPDATE it
    random_str2 = uuid.uuid4()
    email2 = "aaron-%s@example.com" % random_str2

    test_data['id'] = _id
    test_data.update({"email": email2})
    response = client.put('/leak_data/', json = test_data, headers = VALID_AUTH)
    assert response.status_code == 200
    print("after UPDATE: response = %r" % response.json())

    # fetch the results and see if it's really updated
    response = client.get('/leak_data/%s' % (_id,), headers = VALID_AUTH)
    assert response.status_code == 200
    print("data: %r" % response.json()['data'])
    assert response.json()['data'][0]['email'] == email2


def test_import_csv_with_leak_id():
    _id = test_new_leak()
    fixtures_file = "./tests/fixtures/data.csv"
    f = open(fixtures_file, "rb")
    response = client.post('/import/csv/by_leak/%s' % (_id,), files = {"_file": f}, headers = VALID_AUTH)
    logger.info("response = %r" % response.text)
    assert 200 <= response.status_code < 300
    assert response.json()['meta']['count'] >= 0


def test_check_file():
    assert True  # trivial check, not implemented yet actually in main.py


def test_enrich_email_to_vip():
    email_vip = "aaron@example.com"
    response = client.get('/enrich/email_to_vip/%s' % (email_vip,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert data['data'][0]['is_vip']


# noinspection PyPep8Naming
def test_enrich_email_to_vip_INVALID():
    email_vip = "aaron-invalid-does-not-exist@example.com"
    response = client.get('/enrich/email_to_vip/%s' % (email_vip,), headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert data['meta']['count'] >= 1
    assert not data['data'][0]['is_vip']


class TestImportCSVSpycloud(unittest.TestCase):
    def test_import_csv_spycloud_invalid_ticket_id(self):
        fixtures_file = "./tests/fixtures/data_anonymized_spycloud.csv"
        f = open(fixtures_file, "rb")
        response = client.post('/import/csv/spycloud/?summary=test2', files = {"_file": f}, headers = VALID_AUTH)
        assert response.status_code >= 400

    def test_import_csv_spycloud(self):
        fixtures_file = "./tests/fixtures/data_anonymized_spycloud.csv"
        f = open(fixtures_file, "rb")
        response = client.post('/import/csv/spycloud/%s?summary=test2' % ("ticket99",), files = {"_file": f},
                               headers = VALID_AUTH)
        assert 200 <= response.status_code < 300
        assert response.json()['meta']['count'] >= 0


class TestEnricherEmailToDG(unittest.TestCase):
    response = None

    def test_enrich_dg_by_email(self):
        email = "aaron@example.com"
        if not os.getenv('CED_SERVER'):
            with self.assertRaises(Exception):
                client.get('/enrich/email_to_dg/%s' % (email,), headers = VALID_AUTH)
        else:
            response = client.get('/enrich/email_to_dg/%s' % (email,), headers = VALID_AUTH)
            assert response.status_code == 200
            data = response.json()
            assert data['meta']['count'] >= 1
            assert data['data'][0]['dg']
