from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.application.use_cases.finalize_snapshot import FinalizeDraftOnlyError
from app.infrastructure.db.session import get_db
from app.main import app


class _EnumLike:
    def __init__(self, value: str):
        self.value = value


class _FakeSnapshot:
    def __init__(self, status: str = "DRAFT"):
        self.id = uuid4()
        self.company_id = uuid4()
        self.snapshot_date = date(2026, 3, 1)
        self.status = _EnumLike(status)
        self.cash_balance = Decimal("100000")
        self.monthly_revenue = Decimal("20000")
        self.operating_costs = Decimal("18000")
        self.monthly_burn = Decimal("-2000")
        self.runway_months = None
        self.stage = _EnumLike("SEED") if status == "FINALIZED" else None
        self.created_at = datetime(2026, 3, 1, 12, 0, 0)
        self.finalized_at = datetime(2026, 3, 1, 12, 5, 0) if status == "FINALIZED" else None
        self.invalidated_at = None
        self.invalidation_reason = None


def _override_dependencies() -> TestClient:
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    app.dependency_overrides[get_current_user] = lambda: {
        "id": str(uuid4()),
        "email": "qa@example.com",
        "role": "ANALYST",
        "is_active": True,
    }
    return TestClient(app)


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_get_snapshot_detail_returns_payload(monkeypatch):
    import app.api.v1.endpoints.snapshots as snapshots_module

    class _Repo:
        def __init__(self, _session):
            pass

        def get_by_id(self, _snapshot_id):
            return _FakeSnapshot(status="FINALIZED")

    monkeypatch.setattr(snapshots_module, "SnapshotRepository", _Repo)
    client = _override_dependencies()

    response = client.get(f"/api/v1/snapshots/{uuid4()}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FINALIZED"
    assert body["stage"] == "SEED"
    assert body["company_id"]

    _clear_overrides()


def test_get_snapshot_detail_returns_404(monkeypatch):
    import app.api.v1.endpoints.snapshots as snapshots_module

    class _Repo:
        def __init__(self, _session):
            pass

        def get_by_id(self, _snapshot_id):
            return None

    monkeypatch.setattr(snapshots_module, "SnapshotRepository", _Repo)
    client = _override_dependencies()

    response = client.get(f"/api/v1/snapshots/{uuid4()}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

    _clear_overrides()


def test_finalize_snapshot_success(monkeypatch):
    import app.api.v1.endpoints.snapshots as snapshots_module

    class _UseCase:
        def __init__(self, _session):
            pass

        def execute(self, _snapshot_id):
            return _FakeSnapshot(status="FINALIZED")

    monkeypatch.setattr(snapshots_module, "FinalizeSnapshotUseCase", _UseCase)
    client = _override_dependencies()

    response = client.post(f"/api/v1/snapshots/{uuid4()}/finalize")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FINALIZED"
    assert body["finalized_at"] is not None

    _clear_overrides()


def test_finalize_snapshot_conflict(monkeypatch):
    import app.api.v1.endpoints.snapshots as snapshots_module

    class _UseCase:
        def __init__(self, _session):
            pass

        def execute(self, _snapshot_id):
            raise FinalizeDraftOnlyError(str(_snapshot_id), "FINALIZED")

    monkeypatch.setattr(snapshots_module, "FinalizeSnapshotUseCase", _UseCase)
    client = _override_dependencies()

    response = client.post(f"/api/v1/snapshots/{uuid4()}/finalize")

    assert response.status_code == 409
    assert "only draft" in response.json()["detail"].lower()

    _clear_overrides()
