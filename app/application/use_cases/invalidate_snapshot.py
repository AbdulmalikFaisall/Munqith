"""Invalidate snapshot use case for Sprint 8.

Invalidates a finalized snapshot with reason.
Application layer - coordinates repository and domain logic.
"""
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.exceptions import ImmutableSnapshotError, InvalidateDraftSnapshotError


class InvalidateSnapshotUseCase:
    """
    Invalidate snapshot use case.
    
    Responsibilities:
    - Load snapshot from repository
    - Validate it's in FINALIZED status
    - Invalidate with reason
    - Persist changes atomically
    
    Constraints:
    - Only FINALIZED snapshots can be invalidated
    - DRAFT snapshots cannot be invalidated
    - Reason must be provided and non-empty
    - Atomic transaction (all-or-nothing)
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
    
    def execute(self, snapshot_id: UUID, reason: str) -> dict:
        """
        Execute snapshot invalidation.
        
        Args:
            snapshot_id: UUID of snapshot to invalidate
            reason: Reason for invalidation (required, non-empty)
            
        Returns:
            Dictionary with invalidation result:
            {
                "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "INVALIDATED",
                "invalidation_reason": "Incorrect financial data",
                "invalidated_at": "2026-03-01T12:00:00"
            }
            
        Raises:
            ValueError: If reason is empty
            InvalidateDraftSnapshotError: If snapshot is DRAFT
            FileNotFoundError: If snapshot not found
            Exception: On database errors (transaction rolls back)
        """
        # Validate reason
        if not reason or not reason.strip():
            raise ValueError("Invalidation reason cannot be empty")
        
        # Load snapshot
        snapshot = self.repository.get_by_id(snapshot_id)
        if not snapshot:
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found")
        
        # Validate snapshot is finalized
        if not snapshot.is_finalized:
            raise InvalidateDraftSnapshotError(str(snapshot.id), snapshot.status.value)
        
        # Invalidate snapshot
        snapshot.invalidate(reason)
        
        # Persist changes
        self.repository.save(
            snapshot=snapshot,
            signals=[],
            rule_results=[],
            contributing_signals=[]
        )
        
        return {
            "snapshot_id": str(snapshot.id),
            "status": snapshot.status.value,
            "invalidation_reason": snapshot.invalidation_reason,
            "invalidated_at": snapshot.invalidated_at.isoformat() if snapshot.invalidated_at else None
        }
