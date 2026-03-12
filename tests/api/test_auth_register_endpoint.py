from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.infrastructure.db.session import get_db
from app.main import app


class _FakeRepo:
    def __init__(self, _session):
        self._existing = None

    def get_by_email(self, _email: str):
        return self._existing

    def create_user(self, email: str, hashed_password: str, role: str = "ANALYST"):
        return {
            "id": str(uuid4()),
            "email": email,
            "hashed_password": hashed_password,
            "role": role,
            "is_active": True,
        }


def _setup_client() -> TestClient:
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    return TestClient(app)


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_register_success_returns_token(monkeypatch):
    import app.api.v1.endpoints.auth as auth_module

    class _Repo(_FakeRepo):
        pass

    monkeypatch.setattr(auth_module, "UserRepository", _Repo)
    client = _setup_client()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new.user@example.com", "password": "StrongPass1!"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 10

    _clear_overrides()


def test_register_conflict_when_email_exists(monkeypatch):
    import app.api.v1.endpoints.auth as auth_module

    class _Repo(_FakeRepo):
        def get_by_email(self, email: str):
            return {
                "id": str(uuid4()),
                "email": email,
                "hashed_password": "hashed",
                "role": "ANALYST",
                "is_active": True,
            }

    monkeypatch.setattr(auth_module, "UserRepository", _Repo)
    client = _setup_client()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "StrongPass1!"},
    )

    assert response.status_code == 409
    assert "already" in response.json()["detail"].lower()

    _clear_overrides()


def test_register_rejects_short_password(monkeypatch):
    import app.api.v1.endpoints.auth as auth_module

    class _Repo(_FakeRepo):
        pass

    monkeypatch.setattr(auth_module, "UserRepository", _Repo)
    client = _setup_client()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "12345"},
    )

    assert response.status_code == 422
    assert "at least 8" in response.json()["detail"].lower()

    _clear_overrides()
