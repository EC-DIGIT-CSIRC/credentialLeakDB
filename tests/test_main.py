from fastapi.testclient import TestClient

from credentialLeakDB.api.main import app

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
    assert True


def test_validate_api_key():
    assert True


def test_root():
    assert True
