import urllib.parse
import json

from fastapi.testclient import TestClient

from credentialLeakDB.api.main import *

VALID_AUTH = {'x-api-key': 'random-test-api-key'}
INVALID_AUTH = {'x-api-key': 'random-test-api-XXX'}

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_get_db():
    assert True


def test_close_db():
    assert True


def test_connect_db():
    assert True


def test_fetch_valid_api_keys():
    assert True


def test_is_valid_api_key():
    assert is_valid_api_key(VALID_AUTH['x-api-key'])


def test_is_INvalid_api_key():
    assert not is_valid_api_key(INVALID_AUTH['x-api-key'])


def test_validate_api_key():
    assert True


def test_root_auth():
    response = client.get("/", headers = VALID_AUTH)
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_root_INVALID_auth():
    response = client.get("/", headers = INVALID_AUTH)
    assert response.status_code == 403


def test_get_user_by_email():
    email = urllib.parse.quote("aaron@example.com")
    response = client.get("/user/%s" % email, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1


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
    response = client.post("/leak/", json=test_data, headers = VALID_AUTH)
    assert response.status_code == 201
    data = response.json()
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['id'] >= 1



def test_update_leak():
    test_data = {
        "ticket_id": "CSIRC-202",
        "summary": "an UPDATE-able test leak, please ignore",
        "reporter_name": "aaron",
        "source_name": "spycloud",
        "breach_ts": "2021-01-01T00:00:00.000Z",
        "source_publish_ts": "2021-01-02T00:00:00.000Z",
    }
    response = client.post("/leak/", json=test_data, headers = VALID_AUTH)
    assert response.status_code == 201
    data = response.json()
    assert "meta" in response.text and \
           "data" in response.text and \
           data['meta']['count'] >= 1 and \
           data['data'][0]['id'] >= 1
    id = data['data'][0]['id']

    # now UPDATE it
    test_data['summary'] = "We UPDATED the test leak now!"
    test_data['id'] = id
    response = client.put('/leak/', json=test_data, headers=VALID_AUTH)
    assert response.status_code == 200

    # fetch the results and see if it's really updated
    response = client.get('/leak/%s' %(id,), headers=VALID_AUTH)
    assert response.status_code == 200
    assert response.json()['data'][0]['summary'] == "We UPDATED the test leak now!"

