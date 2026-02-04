from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome" in r.json().get("message", "")


def test_list_users():
    r = client.get("/api/v1/users")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert data and "email" in data[0]
