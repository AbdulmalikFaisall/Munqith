"""Snapshot repository for persistence layer.

Handles snapshot entity persistence with transaction management.
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from decimal import Decimal

from app.infrastructure.db.models.snapshot import Snapshot as SnapshotModel
from app.domain.entities.snapshot import Snapshot
from app.domain.entities.signal import Signal
from app.domain.entities.rule_result import RuleResult
from app.domain.enums import SnapshotStatus


class SnapshotRepository:
    """
    Repository for snapshot persistence.
    
    Responsibilities:
    - Load snapshots from database
    - Save snapshots to database
    - Marshal between domain entities and ORM models
    - Manage transaction boundaries
    
    Note: For Sprint 5, we persist snapshot state.
    Signal and rule result persistence will be implemented in future sprints.
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
    
    def get_by_id(self, snapshot_id: UUID) -> Optional[Snapshot]:
        """
        Load snapshot from database by ID.
        
        Args:
            snapshot_id: UUID of snapshot to load
            
        Returns:
            Domain Snapshot entity or None if not found
        """
        model = self.session.query(SnapshotModel).filter(
            SnapshotModel.id == str(snapshot_id)
        ).first()
        
        if not model:
            return None
        
        # Convert ORM model to domain entity
        return self._model_to_domain(model)
    
    def get_finalized_by_company(self, company_id: UUID) -> List[Snapshot]:
        """
        Load all finalized snapshots for a company, ordered by snapshot_date ASC.
        
        Only returns FINALIZED snapshots.
        Automatically excludes DRAFT and INVALIDATED snapshots.
        
        Args:
            company_id: UUID of company
            
        Returns:
            List of finalized Snapshot entities, ordered chronologically (earliest first)
        """
        models = self.session.query(SnapshotModel).filter(
            SnapshotModel.company_id == str(company_id),
            SnapshotModel.status == SnapshotStatus.FINALIZED.value
        ).order_by(SnapshotModel.snapshot_date.asc()).all()
        
        return [self._model_to_domain(model) for model in models]
    
    def get_finalized_by_company_and_date(
        self,
        company_id: UUID,
        snapshot_date: date
    ) -> Optional[Snapshot]:
        """
        Load finalized snapshot for a company on a specific date.
        
        Only returns FINALIZED snapshots.
        Automatically excludes DRAFT and INVALIDATED snapshots.
        
        Args:
            company_id: UUID of company
            snapshot_date: Date of snapshot to load
            
        Returns:
            Domain Snapshot entity or None if not found or not finalized
        """
        model = self.session.query(SnapshotModel).filter(
            SnapshotModel.company_id == str(company_id),
            SnapshotModel.snapshot_date == snapshot_date,
            SnapshotModel.status == SnapshotStatus.FINALIZED.value
        ).first()
        
        if not model:
            return None
        
        return self._model_to_domain(model)
    
    def get_any_by_company_and_date(
        self,
        company_id: UUID,
        snapshot_date: date
    ) -> Optional[Snapshot]:
        """
        Load any snapshot (DRAFT, FINALIZED, or INVALIDATED) for a company on a specific date.
        
        Used for uniqueness enforcement during creation (check if ANY snapshot exists).
        
        Args:
            company_id: UUID of company
            snapshot_date: Date of snapshot to load
            
        Returns:
            Domain Snapshot entity or None if not found
        """
        model = self.session.query(SnapshotModel).filter(
            SnapshotModel.company_id == str(company_id),
            SnapshotModel.snapshot_date == snapshot_date
        ).first()
        
        if not model:
            return None
        
        return self._model_to_domain(model)
    
    def save(
        self,
        snapshot: Snapshot,
        signals: list,
        rule_results: list,
        contributing_signals: list,
    ) -> None:
        """
        Save snapshot in a transaction.
        
        Persists:
        - Snapshot entity with all fields
        - Derived metrics
        - Stage
        - Finalization state
        
        All persisted in one transaction - if any part fails, entire operation rolls back.
        
        Args:
            snapshot: Domain Snapshot entity to persist
            signals: List of Signal entities (for future use)
            rule_results: List of RuleResult entities (for future use)
            contributing_signals: List of contributing Signal entities (for future use)
            
        Raises:
            Exception: On database error (transaction will be rolled back)
        """
        try:
            # Convert domain snapshot to ORM model
            snapshot_model = self._domain_to_model(snapshot)
            
            # Merge or add to session - this handles inserts and updates
            self.session.merge(snapshot_model)
            
            # Commit transaction - atomic operation
            self.session.commit()
        
        except Exception:
            # Rollback on any failure
            self.session.rollback()
            raise
    
    def _domain_to_model(self, domain: Snapshot) -> SnapshotModel:
        """
        Convert domain Snapshot to ORM SnapshotModel.
        
        Args:
            domain: Domain Snapshot entity
            
        Returns:
            ORM SnapshotModel for database persistence
        """
        return SnapshotModel(
            id=str(domain.id),
            company_id=str(domain.company_id),
            snapshot_date=domain.snapshot_date,
            status=domain.status.value,
            cash_balance=Decimal(str(domain.cash_balance)) if domain.cash_balance else None,
            monthly_revenue=Decimal(str(domain.monthly_revenue)) if domain.monthly_revenue else None,
            operating_costs=Decimal(str(domain.operating_costs)) if domain.operating_costs else None,
            monthly_burn=Decimal(str(domain.monthly_burn)) if domain.monthly_burn else None,
            runway_months=Decimal(str(domain.runway_months)) if domain.runway_months else None,
            stage=domain.stage.value if domain.stage else None,
            finalized_at=domain.finalized_at,
            invalidated_at=domain.invalidated_at,
            invalidation_reason=domain.invalidation_reason,
            created_at=domain.created_at,
        )
    
    def _model_to_domain(self, model: SnapshotModel) -> Snapshot:
        """
        Convert ORM SnapshotModel to domain Snapshot.
        
        Args:
            model: ORM SnapshotModel from database
            
        Returns:
            Domain Snapshot entity
        """
        from app.domain.enums import SnapshotStatus, Stage
        
        return Snapshot(
            id=UUID(model.id),
            company_id=UUID(model.company_id),
            snapshot_date=model.snapshot_date,
            status=SnapshotStatus(model.status),
            cash_balance=model.cash_balance,
            monthly_revenue=model.monthly_revenue,
            operating_costs=model.operating_costs,
            monthly_burn=model.monthly_burn,
            runway_months=model.runway_months,
            stage=Stage(model.stage) if model.stage else None,
            finalized_at=model.finalized_at,
            invalidated_at=model.invalidated_at,
            invalidation_reason=model.invalidation_reason,
            created_at=model.created_at,
        )

