import os
import subprocess
from datetime import date, timedelta
from uuid import uuid4

import psycopg2
import pytest
import requests

from app.application.services.auth_service import AuthService


if os.getenv("RUN_STACK_SMOKE") != "1":
    pytest.skip("Set RUN_STACK_SMOKE=1 to run docker/local stack smoke tests.", allow_module_level=True)


BACKEND_BASE = os.getenv("SMOKE_BACKEND_BASE_URL", "http://localhost:8000")
FRONTEND_BASE = os.getenv("SMOKE_FRONTEND_BASE_URL", "http://localhost:3000")
DATABASE_URL = os.getenv("SMOKE_DATABASE_URL", "postgresql://munqith:munqith@localhost:5432/munqith")
ANALYST_EMAIL = os.getenv("SMOKE_ANALYST_EMAIL", "smoke_analyst@munqith.local")
ADMIN_EMAIL = os.getenv("SMOKE_ADMIN_EMAIL", "smoke_admin@munqith.local")
PASSWORD = os.getenv("SMOKE_PASSWORD", "Passw0rd!")


def _wait_service(url: str) -> None:
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException as exc:
        pytest.skip(f"Service unavailable at {url}: {exc}")

    if response.status_code >= 500:
        pytest.skip(f"Service unhealthy at {url}: HTTP {response.status_code}")


def _seed_required_data() -> str:
    company_id = str(uuid4())
    company_name = f"Smoke Company {company_id[:8]}"
    analyst_hash = AuthService.hash_password(PASSWORD)
    admin_hash = AuthService.hash_password(PASSWORD)

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO companies (id, name, sector)
                    VALUES (%s, %s, %s)
                    """,
                    (company_id, company_name, "SaaS"),
                )

                analyst_id = str(uuid4())
                admin_id = str(uuid4())

                cur.execute(
                    """
                    INSERT INTO users (id, email, hashed_password, role, is_active)
                    VALUES (%s, %s, %s, 'ANALYST', true)
                    ON CONFLICT (email)
                    DO UPDATE SET
                        hashed_password = EXCLUDED.hashed_password,
                        role = 'ANALYST',
                        is_active = true
                    """,
                    (analyst_id, ANALYST_EMAIL, analyst_hash),
                )

                cur.execute(
                    """
                    INSERT INTO users (id, email, hashed_password, role, is_active)
                    VALUES (%s, %s, %s, 'ADMIN', true)
                    ON CONFLICT (email)
                    DO UPDATE SET
                        hashed_password = EXCLUDED.hashed_password,
                        role = 'ADMIN',
                        is_active = true
                    """,
                    (admin_id, ADMIN_EMAIL, admin_hash),
                )
    except psycopg2.OperationalError:
        env = os.environ.copy()
        env.update(
            {
                "SMOKE_COMPANY_ID": company_id,
                "SMOKE_COMPANY_NAME": company_name,
                "SMOKE_ANALYST_EMAIL": ANALYST_EMAIL,
                "SMOKE_ADMIN_EMAIL": ADMIN_EMAIL,
                "SMOKE_ANALYST_HASH": analyst_hash,
                "SMOKE_ADMIN_HASH": admin_hash,
            }
        )

        seed_script = '''
import os
from app.infrastructure.db.models.company import Company
from app.infrastructure.db.models.user import User
from app.infrastructure.db.session import SessionLocal
from sqlalchemy import select, text

session = SessionLocal()
try:
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'ANALYST',
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT ck_user_role CHECK (role IN ('ANALYST', 'ADMIN'))
        )
    """))

    company = Company(id=os.environ['SMOKE_COMPANY_ID'], name=os.environ['SMOKE_COMPANY_NAME'], sector='SaaS')
    session.add(company)

    analyst = session.execute(select(User).where(User.email == os.environ['SMOKE_ANALYST_EMAIL'])).scalar_one_or_none()
    if analyst is None:
        analyst = User(email=os.environ['SMOKE_ANALYST_EMAIL'], hashed_password=os.environ['SMOKE_ANALYST_HASH'], role='ANALYST', is_active=True)
        session.add(analyst)
    else:
        analyst.hashed_password = os.environ['SMOKE_ANALYST_HASH']
        analyst.role = 'ANALYST'
        analyst.is_active = True

    admin = session.execute(select(User).where(User.email == os.environ['SMOKE_ADMIN_EMAIL'])).scalar_one_or_none()
    if admin is None:
        admin = User(email=os.environ['SMOKE_ADMIN_EMAIL'], hashed_password=os.environ['SMOKE_ADMIN_HASH'], role='ADMIN', is_active=True)
        session.add(admin)
    else:
        admin.hashed_password = os.environ['SMOKE_ADMIN_HASH']
        admin.role = 'ADMIN'
        admin.is_active = True

    session.commit()
finally:
    session.close()
'''

        result = subprocess.run(
            [
                "docker",
                "compose",
                "exec",
                "-T",
                "-e",
                "SMOKE_COMPANY_ID",
                "-e",
                "SMOKE_COMPANY_NAME",
                "-e",
                "SMOKE_ANALYST_EMAIL",
                "-e",
                "SMOKE_ADMIN_EMAIL",
                "-e",
                "SMOKE_ANALYST_HASH",
                "-e",
                "SMOKE_ADMIN_HASH",
                "api",
                "python",
                "-c",
                seed_script,
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip(f"Unable to seed smoke data via docker compose exec: {result.stderr.strip()}")

    return company_id


def _login_backend(email: str) -> str:
    response = requests.post(
        f"{BACKEND_BASE}/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
        timeout=10,
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _login_frontend_session(email: str) -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{FRONTEND_BASE}/api/auth/login",
        json={"email": email, "password": PASSWORD},
        timeout=10,
    )
    assert response.status_code == 200, response.text
    assert "munqith_access_token" in session.cookies
    return session


def test_phase9_10_11_12_stack_smoke():
    _wait_service(f"{BACKEND_BASE}/health")
    _wait_service(FRONTEND_BASE)

    company_id = _seed_required_data()
    analyst_backend_token = _login_backend(ANALYST_EMAIL)

    analyst_session = _login_frontend_session(ANALYST_EMAIL)

    date_1 = date.today() - timedelta(days=2)
    date_2 = date.today() - timedelta(days=1)

    create_1 = analyst_session.post(
        f"{FRONTEND_BASE}/api/snapshots",
        json={
            "company_id": company_id,
            "snapshot_date": date_1.isoformat(),
            "cash_balance": 100000,
            "monthly_revenue": 20000,
            "operating_costs": 25000,
        },
        timeout=10,
    )
    assert create_1.status_code == 201, create_1.text
    snapshot_1 = create_1.json()["id"]

    finalize_1 = analyst_session.post(f"{FRONTEND_BASE}/api/snapshots/{snapshot_1}/finalize", timeout=10)
    assert finalize_1.status_code == 200, finalize_1.text
    assert finalize_1.json()["status"] == "FINALIZED"

    create_2 = analyst_session.post(
        f"{FRONTEND_BASE}/api/snapshots",
        json={
            "company_id": company_id,
            "snapshot_date": date_2.isoformat(),
            "cash_balance": 120000,
            "monthly_revenue": 30000,
            "operating_costs": 26000,
        },
        timeout=10,
    )
    assert create_2.status_code == 201, create_2.text
    snapshot_2 = create_2.json()["id"]

    finalize_2 = analyst_session.post(f"{FRONTEND_BASE}/api/snapshots/{snapshot_2}/finalize", timeout=10)
    assert finalize_2.status_code == 200, finalize_2.text
    assert finalize_2.json()["status"] == "FINALIZED"

    compare = analyst_session.get(
        f"{FRONTEND_BASE}/api/companies/{company_id}/compare",
        params={"fromDate": date_1.isoformat(), "toDate": date_2.isoformat()},
        timeout=10,
    )
    assert compare.status_code == 200, compare.text
    compare_payload = compare.json()
    assert compare_payload["from_date"] == date_1.isoformat()
    assert compare_payload["to_date"] == date_2.isoformat()

    backend_headers = {"Authorization": f"Bearer {analyst_backend_token}"}

    companies = requests.get(f"{BACKEND_BASE}/api/v1/companies", headers=backend_headers, timeout=10)
    assert companies.status_code == 200, companies.text
    assert any(item["id"] == company_id for item in companies.json())

    company_detail = requests.get(
        f"{BACKEND_BASE}/api/v1/companies/{company_id}",
        headers=backend_headers,
        timeout=10,
    )
    assert company_detail.status_code == 200, company_detail.text

    snapshots_list = requests.get(
        f"{BACKEND_BASE}/api/v1/companies/{company_id}/snapshots",
        headers=backend_headers,
        timeout=10,
    )
    assert snapshots_list.status_code == 200, snapshots_list.text
    assert len(snapshots_list.json()["snapshots"]) >= 2

    snapshot_detail = requests.get(
        f"{BACKEND_BASE}/api/v1/snapshots/{snapshot_1}",
        headers=backend_headers,
        timeout=10,
    )
    assert snapshot_detail.status_code == 200, snapshot_detail.text
    assert snapshot_detail.json()["id"] == snapshot_1

    admin_session = _login_frontend_session(ADMIN_EMAIL)
    invalidate = admin_session.post(
        f"{FRONTEND_BASE}/api/snapshots/{snapshot_2}/invalidate",
        json={"reason": "Smoke invalidation check"},
        timeout=10,
    )
    assert invalidate.status_code == 200, invalidate.text
    assert invalidate.json()["status"] == "INVALIDATED"
