#!/usr/bin/env python
"""
Manual test runner for Sprint 2 domain tests (without pytest).

Provides basic test execution and reporting.
"""

import sys
sys.path.insert(0, '.')

from uuid import uuid4
from datetime import date, datetime
from decimal import Decimal

from app.domain.entities import Company, Snapshot
from app.domain.enums import Stage, SnapshotStatus
from app.domain.exceptions import (
    ImmutableSnapshotError,
    FinalizeDraftOnlyError,
    InvalidateDraftSnapshotError,
)

print("=" * 70)
print("SPRINT 2 - DOMAIN TESTS (Manual Runner)")
print("=" * 70)

passed = 0
failed = 0

def test(name, test_func):
    global passed, failed
    try:
        test_func()
        print(f"✓ {name}")
        passed += 1
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        failed += 1
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        failed += 1

# === COMPANY TESTS ===
print("\n[Company Tests]")

def test_company_creation():
    company = Company(id=uuid4(), name="TechCo")
    assert company.name == "TechCo"

def test_company_name_stripped():
    company = Company(id=uuid4(), name="  TechCo  ")
    assert company.name == "TechCo"

def test_company_empty_name_fails():
    try:
        Company(id=uuid4(), name="")
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass

def test_company_with_sector():
    company = Company(id=uuid4(), name="TechCo", sector="Technology")
    assert company.sector == "Technology"

def test_company_equality():
    cid = uuid4()
    c1 = Company(id=cid, name="Company1")
    c2 = Company(id=cid, name="Company2")
    assert c1 == c2

test("Company creation", test_company_creation)
test("Company name stripped", test_company_name_stripped)
test("Company empty name validation", test_company_empty_name_fails)
test("Company with sector", test_company_with_sector)
test("Company equality by ID", test_company_equality)

# === SNAPSHOT TESTS ===
print("\n[Snapshot Tests]")

def test_snapshot_creation():
    snapshot = Snapshot(id=uuid4(), company_id=uuid4(), snapshot_date=date.today())
    assert snapshot.is_draft
    assert snapshot.status == SnapshotStatus.DRAFT

def test_snapshot_with_financials():
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        cash_balance=Decimal("100000"),
        monthly_revenue=Decimal("50000"),
    )
    assert snapshot.cash_balance == Decimal("100000")
    assert snapshot.monthly_revenue == Decimal("50000")

def test_snapshot_finalize():
    snapshot = Snapshot(id=uuid4(), company_id=uuid4(), snapshot_date=date.today())
    snapshot.finalize()
    assert snapshot.is_finalized

def test_snapshot_cannot_finalize_twice():
    snapshot = Snapshot(id=uuid4(), company_id=uuid4(), snapshot_date=date.today())
    snapshot.finalize()
    try:
        snapshot.finalize()
        raise AssertionError("Should raise FinalizeDraftOnlyError")
    except FinalizeDraftOnlyError:
        pass

def test_snapshot_cannot_update_finalized():
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        status=SnapshotStatus.FINALIZED,
    )
    try:
        snapshot.update_financials(cash_balance=Decimal("100000"))
        raise AssertionError("Should raise ImmutableSnapshotError")
    except ImmutableSnapshotError:
        pass

def test_snapshot_invalidate():
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        status=SnapshotStatus.FINALIZED,
    )
    snapshot.invalidate("Data error")
    assert snapshot.is_invalidated
    assert snapshot.invalidation_reason == "Data error"

def test_snapshot_cannot_invalidate_draft():
    snapshot = Snapshot(id=uuid4(), company_id=uuid4(), snapshot_date=date.today())
    try:
        snapshot.invalidate("Data error")
        raise AssertionError("Should raise InvalidateDraftSnapshotError")
    except InvalidateDraftSnapshotError:
        pass

def test_snapshot_set_stage():
    snapshot = Snapshot(id=uuid4(), company_id=uuid4(), snapshot_date=date.today())
    snapshot.set_stage(Stage.SEED)
    assert snapshot.stage == Stage.SEED

def test_snapshot_cannot_set_stage_finalized():
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
        status=SnapshotStatus.FINALIZED,
    )
    try:
        snapshot.set_stage(Stage.SEED)
        raise AssertionError("Should raise ImmutableSnapshotError")
    except ImmutableSnapshotError:
        pass

def test_snapshot_full_lifecycle():
    snapshot = Snapshot(
        id=uuid4(),
        company_id=uuid4(),
        snapshot_date=date.today(),
    )
    
    # DRAFT
    assert snapshot.is_draft
    snapshot.update_financials(cash_balance=Decimal("100000"))
    snapshot.set_stage(Stage.SEED)
    
    # FINALIZED
    snapshot.finalize()
    assert snapshot.is_finalized
    
    # INVALIDATED
    snapshot.invalidate("Outdated")
    assert snapshot.is_invalidated

test("Snapshot creation", test_snapshot_creation)
test("Snapshot with financials", test_snapshot_with_financials)
test("Snapshot finalize", test_snapshot_finalize)
test("Snapshot cannot finalize twice", test_snapshot_cannot_finalize_twice)
test("Snapshot cannot update finalized", test_snapshot_cannot_update_finalized)
test("Snapshot invalidate", test_snapshot_invalidate)
test("Snapshot cannot invalidate draft", test_snapshot_cannot_invalidate_draft)
test("Snapshot set stage", test_snapshot_set_stage)
test("Snapshot cannot set stage finalized", test_snapshot_cannot_set_stage_finalized)
test("Snapshot full lifecycle", test_snapshot_full_lifecycle)

# === ENUMS TESTS ===
print("\n[Enum Tests]")

def test_stage_enum():
    assert Stage.IDEA.value == "IDEA"
    assert Stage.PRE_SEED.value == "PRE_SEED"
    assert Stage.SEED.value == "SEED"
    assert Stage.SERIES_A.value == "SERIES_A"
    assert Stage.GROWTH.value == "GROWTH"

def test_snapshot_status_enum():
    assert SnapshotStatus.DRAFT.value == "DRAFT"
    assert SnapshotStatus.FINALIZED.value == "FINALIZED"
    assert SnapshotStatus.INVALIDATED.value == "INVALIDATED"

def test_enum_string_conversion():
    assert str(Stage.SEED) == "SEED"
    assert str(SnapshotStatus.DRAFT) == "DRAFT"

test("Stage enum values", test_stage_enum)
test("SnapshotStatus enum values", test_snapshot_status_enum)
test("Enum string conversion", test_enum_string_conversion)

# === SUMMARY ===
print("\n" + "=" * 70)
print(f"TEST RESULTS: {passed} passed, {failed} failed")
if failed == 0:
    print("✓ ALL TESTS PASSED")
else:
    print(f"✗ {failed} TEST(S) FAILED")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
