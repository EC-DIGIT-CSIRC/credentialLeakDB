from fastapi.testclient import TestClient

from credentialLeakDB.api.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
