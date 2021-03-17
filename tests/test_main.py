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


def test_root_invalid_auth():
    response = client.get("/", headers = INVALID_AUTH)
    assert response.status_code == 403


def test_get_user_by_email():
    email = urllib.parse.quote("aaron@example.com")
    response = client.get("/user/%s" % email, headers = VALID_AUTH)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] >= 1

def test_get_nonexistent_user_by_email():
    email = urllib.parse.quote("aaron@doesnotexist.com")
    response = client.get("/user/%s" % email, headers = VALID_AUTH)
    assert response.status_code != 200
    data = response.json()
    assert "meta" in response.text and "data" in response.text and data['meta']['count'] == 0
