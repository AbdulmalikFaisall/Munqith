"""Historical snapshot reader for analytics context.

Reads finalized snapshots only - filtered at DB layer.
Pure infrastructure - no domain logic.
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.infrastructure.db.models.snapshot import Snapshot as SnapshotModel


class SnapshotReader:
    """
    Reader for finalized historical snapshots.
    
    Responsibilities:
    - Load finalized snapshots from database
    - Filter out DRAFT and INVALIDATED snapshots
    - Return snapshots ordered chronologically
    
    Key principle:
    - Read-only access
    - Finalized-only (immutable snapshots)
    - Never modifies snapshot table
    """
    
    def __init__(self, session: Session):
        """
        Initialize reader with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
    
    def get_company_history(self, company_id: UUID) -> List[SnapshotModel]:
        """
        Get full finalized snapshot history for a company.
        
        Returns only FINALIZED snapshots, ordered chronologically (ascending).
        Excludes DRAFT and INVALIDATED snapshots.
        
        Args:
            company_id: Company UUID
            
        Returns:
            List of SnapshotModel objects ordered by snapshot_date (ascending)
        """
        snapshots = (
            self.session.query(SnapshotModel)
            .filter(
                and_(
                    SnapshotModel.company_id == company_id,
                    SnapshotModel.status == "FINALIZED",
                )
            )
            .order_by(SnapshotModel.snapshot_date.asc())
            .all()
        )
        return snapshots
    
    def get_snapshot_by_id(self, snapshot_id: UUID) -> SnapshotModel:
        """
        Get a specific snapshot by ID (must be finalized).
        
        Args:
            snapshot_id: Snapshot UUID
            
        Returns:
            SnapshotModel if found and finalized, None otherwise
        """
        snapshot = (
            self.session.query(SnapshotModel)
            .filter(
                and_(
                    SnapshotModel.id == snapshot_id,
                    SnapshotModel.status == "FINALIZED",
                )
            )
            .first()
        )
        return snapshot
