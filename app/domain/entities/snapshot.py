"""
Snapshot domain entity with lifecycle state machine.

Represents a time-bound financial snapshot for a company.
Enforces immutability and state transitions.
Pure business logic - no DB calls, no HTTP, no frameworks.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from app.domain.enums import Stage, SnapshotStatus
from app.domain.exceptions import (
    InvalidSnapshotTransition,
    ImmutableSnapshotError,
    InvalidateDraftSnapshotError,
    FinalizeDraftOnlyError,
)


class Snapshot:
    """
    Snapshot entity - represents a time-bound financial snapshot.
    
    Core responsibility: Enforce lifecycle transitions and immutability.
    
    Lifecycle:
        DRAFT → FINALIZED → INVALIDATED
    
    Rules:
    - Only DRAFT snapshots can be modified
    - FINALIZED snapshots are immutable
    - Only FINALIZED snapshots can be invalidated
    - Each transition is triggered by explicit methods
    """
    
    def __init__(
        self,
        id: UUID,
        company_id: UUID,
        snapshot_date: date,
        status: SnapshotStatus = SnapshotStatus.DRAFT,
        cash_balance: Optional[Decimal] = None,
        monthly_revenue: Optional[Decimal] = None,
        operating_costs: Optional[Decimal] = None,
        monthly_burn: Optional[Decimal] = None,
        runway_months: Optional[Decimal] = None,
        stage: Optional[Stage] = None,
        invalidation_reason: Optional[str] = None,
        finalized_at: Optional[datetime] = None,
        invalidated_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
    ):
        """
        Initialize a Snapshot entity.
        
        Args:
            id: Unique identifier (UUID)
            company_id: Parent company ID (UUID)
            snapshot_date: Date this snapshot represents
            status: Current lifecycle status (default: DRAFT)
            cash_balance: Cash available (SAR)
            monthly_revenue: Monthly revenue (SAR)
            operating_costs: Monthly operating costs (SAR)
            monthly_burn: Monthly cash burn (SAR)
            runway_months: Months of runway
            stage: Derived stage
            invalidation_reason: Why snapshot was invalidated
            finalized_at: When snapshot was finalized
            invalidated_at: When snapshot was invalidated
            created_at: When snapshot was created
            
        Raises:
            ValueError: If required fields are invalid
        """
        if not isinstance(snapshot_date, date):
            raise ValueError("snapshot_date must be a date object")
        
        self.id = id
        self.company_id = company_id
        self.snapshot_date = snapshot_date
        self._status = status or SnapshotStatus.DRAFT
        
        # Financial attributes
        self.cash_balance = cash_balance
        self.monthly_revenue = monthly_revenue
        self.operating_costs = operating_costs
        
        # Derived metrics
        self.monthly_burn = monthly_burn
        self.runway_months = runway_months
        
        # Stage and lifecycle
        self.stage = stage
        self.invalidation_reason = invalidation_reason
        
        # Timestamps
        self.finalized_at = finalized_at
        self.invalidated_at = invalidated_at
        self.created_at = created_at or datetime.utcnow()
    
    # ==================== Properties ====================
    
    @property
    def status(self) -> SnapshotStatus:
        """Current lifecycle status."""
        return self._status
    
    @property
    def is_draft(self) -> bool:
        """True if in DRAFT status."""
        return self._status == SnapshotStatus.DRAFT
    
    @property
    def is_finalized(self) -> bool:
        """True if in FINALIZED status."""
        return self._status == SnapshotStatus.FINALIZED
    
    @property
    def is_invalidated(self) -> bool:
        """True if in INVALIDATED status."""
        return self._status == SnapshotStatus.INVALIDATED
    
    # ==================== Lifecycle Methods ====================
    
    def finalize(self) -> None:
        """
        Transition snapshot from DRAFT to FINALIZED.
        
        Requirements:
        - Only allowed when status is DRAFT
        - Sets finalized_at timestamp
        - After finalization, snapshot is immutable
        
        Raises:
            FinalizeDraftOnlyError: If not in DRAFT status
        """
        if self._status != SnapshotStatus.DRAFT:
            raise FinalizeDraftOnlyError(str(self.id), self._status.value)
        
        self._status = SnapshotStatus.FINALIZED
        self.finalized_at = datetime.utcnow()
    
    def invalidate(self, reason: str) -> None:
        """
        Transition snapshot from FINALIZED to INVALIDATED.
        
        Requirements:
        - Only allowed when status is FINALIZED
        - Requires invalidation reason
        - Sets invalidated_at timestamp
        - Reason is stored for audit trail
        
        Args:
            reason: Why snapshot is being invalidated (required)
            
        Raises:
            InvalidateDraftSnapshotError: If not in FINALIZED status
            ValueError: If reason is empty
        """
        if self._status != SnapshotStatus.FINALIZED:
            raise InvalidateDraftSnapshotError(str(self.id), self._status.value)
        
        if not reason or not isinstance(reason, str) or len(reason.strip()) == 0:
            raise ValueError("Invalidation reason must be a non-empty string")
        
        self._status = SnapshotStatus.INVALIDATED
        self.invalidation_reason = reason.strip()
        self.invalidated_at = datetime.utcnow()
    
    # ==================== Modification Methods ====================
    
    def update_financials(
        self,
        cash_balance: Optional[Decimal] = None,
        monthly_revenue: Optional[Decimal] = None,
        operating_costs: Optional[Decimal] = None,
        monthly_burn: Optional[Decimal] = None,
        runway_months: Optional[Decimal] = None,
    ) -> None:
        """
        Update financial attributes.
        
        Requirements:
        - Only allowed when status is DRAFT
        - Cannot update after finalization (immutability)
        
        Args:
            cash_balance: Cash available (SAR)
            monthly_revenue: Monthly revenue (SAR)
            operating_costs: Monthly operating costs (SAR)
            monthly_burn: Monthly burn (SAR)
            runway_months: Months of runway
            
        Raises:
            ImmutableSnapshotError: If snapshot is finalized or invalidated
        """
        if not self.is_draft:
            raise ImmutableSnapshotError(
                str(self.id),
                "update financial attributes"
            )
        
        if cash_balance is not None:
            self.cash_balance = cash_balance
        if monthly_revenue is not None:
            self.monthly_revenue = monthly_revenue
        if operating_costs is not None:
            self.operating_costs = operating_costs
        if monthly_burn is not None:
            self.monthly_burn = monthly_burn
        if runway_months is not None:
            self.runway_months = runway_months
    
    def set_stage(self, stage: Optional[Stage]) -> None:
        """
        Set the derived stage.
        
        Requirements:
        - Only allowed when status is DRAFT
        - Cannot change after finalization
        
        Args:
            stage: Derived company stage
            
        Raises:
            ImmutableSnapshotError: If snapshot is finalized or invalidated
        """
        if not self.is_draft:
            raise ImmutableSnapshotError(str(self.id), "set stage")
        
        self.stage = stage
    
    # ==================== Derived Metrics Calculation ====================
    
    def compute_derived_metrics(self) -> None:
        """
        Compute derived financial metrics from raw financial attributes.
        
        Calculations:
        - monthly_burn = operating_costs - monthly_revenue
        - runway_months = cash_balance / monthly_burn (if burn > 0)
        - If burn <= 0: runway_months = None (profitable or break-even)
        
        Requirements:
        - Deterministic (same input always produces same output)
        - No DB calls
        - No external state
        - Can be called at any time (DRAFT or FINALIZED)
        
        Rules:
        - Operating costs and monthly revenue must be set
        - Calculations use Decimal arithmetic for precision
        - Division by zero is prevented (burn <= 0 returns None)
        
        Side Effects:
        - Updates self.monthly_burn
        - Updates self.runway_months
        """
        # Only compute if both required inputs are present
        if self.operating_costs is None or self.monthly_revenue is None:
            return
        
        # Calculate monthly burn: operating_costs - monthly_revenue
        self.monthly_burn = self.operating_costs - self.monthly_revenue
        
        # Calculate runway only if cash_balance is set
        if self.cash_balance is None:
            self.runway_months = None
            return
        
        # Calculate runway months
        # If burn is <= 0, company is profitable or break-even → no runway concern
        if self.monthly_burn <= 0:
            self.runway_months = None
        else:
            # runway_months = cash_balance / monthly_burn
            self.runway_months = self.cash_balance / self.monthly_burn
    
    # ==================== Utilities ====================
    
    def __repr__(self) -> str:
        return (
            f"Snapshot(id={self.id}, company_id={self.company_id}, "
            f"date={self.snapshot_date}, status={self.status.value})"
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Snapshot):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
