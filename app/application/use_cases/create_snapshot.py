"""
Create snapshot use case for Sprint 9.

Orchestrates snapshot creation with validation and uniqueness enforcement.
Application layer - coordinates validation and persistence.
"""
from uuid import UUID, uuid4
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Optional

from app.domain.entities.snapshot import Snapshot
from app.domain.validators import FinancialValidator
from app.domain.exceptions import (
    DuplicateSnapshotError,
    FinancialSanityError,
    SnapshotValidationError,
)
from app.infrastructure.repositories.snapshot_repository import SnapshotRepository


class CreateSnapshotUseCase:
    """
    Create snapshot use case.
    
    Responsibilities:
    - Validate financial inputs
    - Enforce snapshot date uniqueness per company
    - Create snapshot entity in DRAFT status
    - Persist snapshot to database
    
    Architecture:
    - Application layer (this class): Orchestration and uniqueness checking
    - Domain layer: Business validation (FinancialValidator)
    - Infrastructure: Persistence and uniqueness constraint
    
    Validation Flow:
    1. Check repository for existing snapshot with same (company_id, snapshot_date)
    2. Create Snapshot entity in DRAFT status
    3. Validate financial inputs (via FinancialValidator)
    4. Persist to database
    
    Raises:
    - DuplicateSnapshotError: If snapshot already exists for this date
    - FinancialSanityError: If financial inputs fail validation
    - SnapshotValidationError: If snapshot state is invalid
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
        self.session = session
    
    def execute(
        self,
        company_id: UUID,
        snapshot_date: date,
        cash_balance: Optional[Decimal] = None,
        monthly_revenue: Optional[Decimal] = None,
        operating_costs: Optional[Decimal] = None,
    ) -> Snapshot:
        """
        Execute snapshot creation.
        
        Pipeline:
        1. Check for existing snapshot with same (company_id, snapshot_date)
        2. Create domain Snapshot entity
        3. Validate financial inputs
        4. Validate snapshot initial state
        5. Persist to database
        
        Args:
            company_id: UUID of company owning the snapshot
            snapshot_date: Date this snapshot represents
            cash_balance: Cash balance in SAR (optional, must be >= 0)
            monthly_revenue: Monthly revenue in SAR (optional, must be >= 0)
            operating_costs: Monthly operating costs in SAR (optional, must be >= 0)
            
        Returns:
            Created Snapshot entity in DRAFT status with:
            - status = DRAFT
            - stage = None (derived during finalization)
            - finalized_at = None
            - invalidated_at = None
            
        Raises:
            DuplicateSnapshotError: If snapshot already exists for (company_id, snapshot_date)
            FinancialSanityError: If financial inputs fail validation
            SnapshotValidationError: If snapshot initialization fails
            Exception: On database errors
        """
        # ===================== Step 1: Check Uniqueness =====================
        existing = self.repository.get_any_by_company_and_date(company_id, snapshot_date)
        if existing is not None:
            raise DuplicateSnapshotError(
                company_id=str(company_id),
                snapshot_date=str(snapshot_date)
            )
        
        # ===================== Step 2: Create Snapshot Entity =====================
        snapshot = Snapshot(
            id=uuid4(),
            company_id=company_id,
            snapshot_date=snapshot_date,
            cash_balance=cash_balance,
            monthly_revenue=monthly_revenue,
            operating_costs=operating_costs,
        )
        
        # ===================== Step 3: Validate Financial Inputs =====================
        FinancialValidator.validate_snapshot_inputs(snapshot)
        
        # ===================== Step 4: Validate Snapshot Initial State =====================
        self._validate_initial_state(snapshot)
        
        # ===================== Step 5: Persist to Database =====================
        self.repository.save(
            snapshot=snapshot,
            signals=[],
            rule_results=[],
            contributing_signals=[]
        )
        
        return snapshot
    
    @staticmethod
    def _validate_initial_state(snapshot: Snapshot) -> None:
        """
        Validate snapshot is in correct initial state.
        
        Rules:
        - status must be DRAFT
        - stage must be None
        - finalized_at must be None
        - invalidated_at must be None
        - invalidation_reason must be None
        
        Args:
            snapshot: Snapshot to validate
            
        Raises:
            SnapshotValidationError: If validation fails
        """
        # Import here to avoid circular imports
        from app.domain.enums import SnapshotStatus
        
        # Check status is DRAFT
        if snapshot.status != SnapshotStatus.DRAFT:
            raise SnapshotValidationError(
                snapshot_id=str(snapshot.id),
                violation=f"New snapshots must be in DRAFT status, not {snapshot.status.value}"
            )
        
        # Check stage is None
        if snapshot.stage is not None:
            raise SnapshotValidationError(
                snapshot_id=str(snapshot.id),
                violation="New snapshots must not have a stage assigned (stage must be None)"
            )
        
        # Check finalized_at is None
        if snapshot.finalized_at is not None:
            raise SnapshotValidationError(
                snapshot_id=str(snapshot.id),
                violation="New snapshots must not be marked as finalized (finalized_at must be None)"
            )
        
        # Check invalidated_at is None
        if snapshot.invalidated_at is not None:
            raise SnapshotValidationError(
                snapshot_id=str(snapshot.id),
                violation="New snapshots must not be marked as invalidated (invalidated_at must be None)"
            )
        
        # Check invalidation_reason is None
        if snapshot.invalidation_reason is not None:
            raise SnapshotValidationError(
                snapshot_id=str(snapshot.id),
                violation="New snapshots must not have an invalidation reason (invalidation_reason must be None)"
            )
