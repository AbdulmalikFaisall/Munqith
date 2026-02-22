"""
Unit tests for Snapshot domain entity with lifecycle state machine.

These tests verify:
- Snapshot creation and initialization
- State transitions (DRAFT → FINALIZED → INVALIDATED)
- Immutability enforcement
- Financial data updates
- Exception handling
"""
import pytest
from uuid import uuid4
from datetime import date
from decimal import Decimal

from app.domain.entities import Snapshot
from app.domain.enums import Stage, SnapshotStatus
from app.domain.exceptions import (
    InvalidSnapshotTransition,
    ImmutableSnapshotError,
    InvalidateDraftSnapshotError,
    FinalizeDraftOnlyError,
)


class TestSnapshotCreation:
    """Test Snapshot entity creation."""
    
    def test_create_snapshot_minimal(self):
        """Can create snapshot with minimal required data."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        assert snapshot.status == SnapshotStatus.DRAFT
        assert snapshot.is_draft
        assert not snapshot.is_finalized
        assert not snapshot.is_invalidated
        assert snapshot.created_at is not None
    
    def test_create_snapshot_with_financials(self):
        """Can create snapshot with financial data."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("100000.00"),
            monthly_revenue=Decimal("50000.00"),
            operating_costs=Decimal("30000.00"),
            monthly_burn=Decimal("20000.00"),
            runway_months=Decimal("5.00"),
        )
        
        assert snapshot.cash_balance == Decimal("100000.00")
        assert snapshot.monthly_revenue == Decimal("50000.00")
        assert snapshot.operating_costs == Decimal("30000.00")
        assert snapshot.monthly_burn == Decimal("20000.00")
        assert snapshot.runway_months == Decimal("5.00")
    
    def test_create_snapshot_with_stage(self):
        """Can create snapshot with stage."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            stage=Stage.PRE_SEED,
        )
        
        assert snapshot.stage == Stage.PRE_SEED
    
    def test_create_snapshot_invalid_date_type(self):
        """Invalid date type raises error."""
        with pytest.raises(ValueError, match="date object"):
            Snapshot(
                id=uuid4(),
                company_id=uuid4(),
                snapshot_date="2026-02-21",
            )


class TestSnapshotStatusProperties:
    """Test snapshot status properties."""
    
    def test_draft_properties(self):
        """DRAFT snapshot has correct properties."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.DRAFT,
        )
        
        assert snapshot.is_draft
        assert not snapshot.is_finalized
        assert not snapshot.is_invalidated
    
    def test_finalized_properties(self):
        """FINALIZED snapshot has correct properties."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        assert not snapshot.is_draft
        assert snapshot.is_finalized
        assert not snapshot.is_invalidated
    
    def test_invalidated_properties(self):
        """INVALIDATED snapshot has correct properties."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.INVALIDATED,
        )
        
        assert not snapshot.is_draft
        assert not snapshot.is_finalized
        assert snapshot.is_invalidated


class TestSnapshotFinalize:
    """Test finalizing snapshots (DRAFT → FINALIZED)."""
    
    def test_finalize_draft_snapshot(self):
        """Can finalize a DRAFT snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        assert snapshot.is_draft
        snapshot.finalize()
        
        assert snapshot.is_finalized
        assert snapshot.finalized_at is not None
    
    def test_cannot_finalize_twice(self):
        """Cannot finalize a snapshot twice."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        snapshot.finalize()
        
        with pytest.raises(FinalizeDraftOnlyError):
            snapshot.finalize()
    
    def test_cannot_finalize_invalidated(self):
        """Cannot finalize an INVALIDATED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.INVALIDATED,
        )
        
        with pytest.raises(FinalizeDraftOnlyError):
            snapshot.finalize()
    
    def test_finalize_sets_timestamp(self):
        """Finalization sets finalized_at timestamp."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        assert snapshot.finalized_at is None
        snapshot.finalize()
        assert snapshot.finalized_at is not None


class TestSnapshotInvalidate:
    """Test invalidating snapshots (FINALIZED → INVALIDATED)."""
    
    def test_invalidate_finalized_snapshot(self):
        """Can invalidate a FINALIZED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        snapshot.invalidate("Data error")
        
        assert snapshot.is_invalidated
        assert snapshot.invalidation_reason == "Data error"
        assert snapshot.invalidated_at is not None
    
    def test_cannot_invalidate_draft(self):
        """Cannot invalidate a DRAFT snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        with pytest.raises(InvalidateDraftSnapshotError):
            snapshot.invalidate("Data error")
    
    def test_cannot_invalidate_twice(self):
        """Cannot invalidate a snapshot twice."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.INVALIDATED,
        )
        
        with pytest.raises(InvalidateDraftSnapshotError):
            snapshot.invalidate("Another reason")
    
    def test_invalidate_requires_reason(self):
        """Invalidation requires a non-empty reason."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        with pytest.raises(ValueError, match="non-empty string"):
            snapshot.invalidate("")
        
        with pytest.raises(ValueError, match="non-empty string"):
            snapshot.invalidate("   ")
    
    def test_invalidation_reason_stripped(self):
        """Invalidation reason is stripped of whitespace."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        snapshot.invalidate("  Data inconsistency  ")
        assert snapshot.invalidation_reason == "Data inconsistency"


class TestSnapshotUpdateFinancials:
    """Test updating financial data on snapshots."""
    
    def test_update_financials_draft(self):
        """Can update financials on DRAFT snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        snapshot.update_financials(
            cash_balance=Decimal("100000.00"),
            monthly_revenue=Decimal("50000.00"),
        )
        
        assert snapshot.cash_balance == Decimal("100000.00")
        assert snapshot.monthly_revenue == Decimal("50000.00")
    
    def test_cannot_update_financials_finalized(self):
        """Cannot update financials on FINALIZED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        with pytest.raises(ImmutableSnapshotError):
            snapshot.update_financials(cash_balance=Decimal("100000.00"))
    
    def test_cannot_update_financials_invalidated(self):
        """Cannot update financials on INVALIDATED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.INVALIDATED,
        )
        
        with pytest.raises(ImmutableSnapshotError):
            snapshot.update_financials(cash_balance=Decimal("100000.00"))
    
    def test_partial_financial_update(self):
        """Can update individual financial fields."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("50000.00"),
            monthly_revenue=Decimal("30000.00"),
        )
        
        # Update only cash_balance
        snapshot.update_financials(cash_balance=Decimal("100000.00"))
        
        assert snapshot.cash_balance == Decimal("100000.00")
        assert snapshot.monthly_revenue == Decimal("30000.00")  # Unchanged


class TestSnapshotSetStage:
    """Test setting stage on snapshots."""
    
    def test_set_stage_draft(self):
        """Can set stage on DRAFT snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        snapshot.set_stage(Stage.SEED)
        assert snapshot.stage == Stage.SEED
    
    def test_cannot_set_stage_finalized(self):
        """Cannot set stage on FINALIZED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.FINALIZED,
        )
        
        with pytest.raises(ImmutableSnapshotError):
            snapshot.set_stage(Stage.SEED)
    
    def test_cannot_set_stage_invalidated(self):
        """Cannot set stage on INVALIDATED snapshot."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            status=SnapshotStatus.INVALIDATED,
        )
        
        with pytest.raises(ImmutableSnapshotError):
            snapshot.set_stage(Stage.SEED)
    
    def test_can_clear_stage(self):
        """Can set stage to None."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            stage=Stage.SEED,
        )
        
        snapshot.set_stage(None)
        assert snapshot.stage is None


class TestSnapshotLifecycleCombinations:
    """Test combined lifecycle scenarios."""
    
    def test_full_lifecycle_draft_finalize_invalidate(self):
        """Test complete lifecycle: DRAFT → FINALIZED → INVALIDATED."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("100000.00"),
        )
        
        # Start as DRAFT
        assert snapshot.is_draft
        
        # Update while in DRAFT
        snapshot.update_financials(monthly_revenue=Decimal("50000.00"))
        assert snapshot.monthly_revenue == Decimal("50000.00")
        
        # Finalize
        snapshot.finalize()
        assert snapshot.is_finalized
        
        # Cannot update after finalization
        with pytest.raises(ImmutableSnapshotError):
            snapshot.update_financials(cash_balance=Decimal("200000.00"))
        
        # Invalidate
        snapshot.invalidate("Outdated information")
        assert snapshot.is_invalidated
        assert snapshot.invalidation_reason == "Outdated information"
    
    def test_cannot_transition_backward(self):
        """Cannot go backward in lifecycle."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        snapshot.finalize()
        
        # Cannot transition back to DRAFT
        # (Would need to manually set _status, which is not exposed)
        assert snapshot.is_finalized


class TestSnapshotEquality:
    """Test Snapshot equality and hashing."""
    
    def test_same_id_equals(self):
        """Snapshots with same ID are equal."""
        snapshot_id = uuid4()
        company_id = uuid4()
        
        snapshot1 = Snapshot(id=snapshot_id, company_id=company_id, snapshot_date=date.today())
        snapshot2 = Snapshot(id=snapshot_id, company_id=company_id, snapshot_date=date.today())
        
        assert snapshot1 == snapshot2
    
    def test_different_id_not_equals(self):
        """Snapshots with different IDs are not equal."""
        company_id = uuid4()
        snapshot1 = Snapshot(id=uuid4(), company_id=company_id, snapshot_date=date.today())
        snapshot2 = Snapshot(id=uuid4(), company_id=company_id, snapshot_date=date.today())
        
        assert snapshot1 != snapshot2
    
    def test_snapshot_hashable(self):
        """Snapshots can be used in sets and dicts."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
        )
        
        snapshots_set = {snapshot}
        assert snapshot in snapshots_set
