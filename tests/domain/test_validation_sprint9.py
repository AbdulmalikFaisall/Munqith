"""
Unit tests for Sprint 9 validation features.

These tests verify:
- Financial sanity validation
- Duplicate snapshot detection
- Snapshot state validation
"""
import pytest
from uuid import uuid4
from datetime import date
from decimal import Decimal

from app.domain.entities import Snapshot
from app.domain.validators import FinancialValidator
from app.domain.exceptions import (
    FinancialSanityError,
    DuplicateSnapshotError,
    SnapshotValidationError,
)


class TestFinancialValidator:
    """Test FinancialValidator for sanity checks."""
    
    def test_valid_snapshot_passes(self):
        """Valid financial data passes validation."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("50000"),
            monthly_revenue=Decimal("10000"),
            operating_costs=Decimal("8000")
        )
        
        # Should not raise
        FinancialValidator.validate_snapshot_inputs(snapshot)
    
    def test_negative_cash_balance_rejected(self):
        """Negative cash balance is rejected."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("-5000")
        )
        
        with pytest.raises(FinancialSanityError) as exc_info:
            FinancialValidator.validate_snapshot_inputs(snapshot)
        
        assert "cash_balance" in str(exc_info.value)
        assert "cannot be negative" in str(exc_info.value)
    
    def test_negative_monthly_revenue_rejected(self):
        """Negative monthly revenue is rejected."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            monthly_revenue=Decimal("-1000")
        )
        
        with pytest.raises(FinancialSanityError) as exc_info:
            FinancialValidator.validate_snapshot_inputs(snapshot)
        
        assert "monthly_revenue" in str(exc_info.value)
    
    def test_negative_operating_costs_rejected(self):
        """Negative operating costs is rejected."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            operating_costs=Decimal("-2000")
        )
        
        with pytest.raises(FinancialSanityError) as exc_info:
            FinancialValidator.validate_snapshot_inputs(snapshot)
        
        assert "operating_costs" in str(exc_info.value)
    
    def test_extreme_cash_balance_rejected(self):
        """Extremely large cash balance is rejected."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("1e13")  # Exceeds MAX_CASH_BALANCE of 1e12
        )
        
        with pytest.raises(FinancialSanityError) as exc_info:
            FinancialValidator.validate_snapshot_inputs(snapshot)
        
        assert "exceeds realistic threshold" in str(exc_info.value)
    
    def test_zero_values_allowed(self):
        """Zero values are allowed (company might have no revenue yet)."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("0"),
            monthly_revenue=Decimal("0"),
            operating_costs=Decimal("0")
        )
        
        # Should not raise
        FinancialValidator.validate_snapshot_inputs(snapshot)
    
    def test_none_values_allowed(self):
        """None values are allowed (optional fields)."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=None,
            monthly_revenue=None,
            operating_costs=None
        )
        
        # Should not raise
        FinancialValidator.validate_snapshot_inputs(snapshot)
    
    def test_profitable_company_allowed(self):
        """Profitable companies (revenue > costs) are allowed."""
        snapshot = Snapshot(
            id=uuid4(),
            company_id=uuid4(),
            snapshot_date=date.today(),
            cash_balance=Decimal("100000"),
            monthly_revenue=Decimal("50000"),
            operating_costs=Decimal("30000")  # Profitable: burn is negative
        )
        
        # Should not raise
        FinancialValidator.validate_snapshot_inputs(snapshot)


class TestDuplicateSnapshotError:
    """Test DuplicateSnapshotError exception."""
    
    def test_error_message_format(self):
        """DuplicateSnapshotError has clear message."""
        company_id = str(uuid4())
        snapshot_date = "2026-03-01"
        
        error = DuplicateSnapshotError(company_id, snapshot_date)
        
        assert "already exists" in str(error)
        assert company_id in str(error)
        assert snapshot_date in str(error)


class TestSnapshotValidationError:
    """Test SnapshotValidationError exception."""
    
    def test_error_message_format(self):
        """SnapshotValidationError has clear message."""
        snapshot_id = str(uuid4())
        violation = "stage must be None"
        
        error = SnapshotValidationError(snapshot_id, violation)
        
        assert "validation failed" in str(error)
        assert snapshot_id in str(error)
        assert violation in str(error)
