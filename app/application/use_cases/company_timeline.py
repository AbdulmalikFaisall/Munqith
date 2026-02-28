"""Company timeline use case for Sprint 6.

Retrieves chronological history of finalized snapshots.
Application layer - coordinates repository and returns timeline items.
"""
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from app.infrastructure.repositories.snapshot_repository import SnapshotRepository


class CompanyTimelineUseCase:
    """
    Company timeline use case.
    
    Responsibilities:
    - Load all finalized snapshots for company
    - Order chronologically (earliest first)
    - Detect stage transitions between consecutive snapshots
    - Return timeline item list
    
    Constraints:
    - Only FINALIZED snapshots included
    - DRAFT and INVALIDATED snapshots excluded
    - Timeline ordered by snapshot_date ASC
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
    
    def execute(self, company_id: UUID) -> List[dict]:
        """
        Execute company timeline retrieval.
        
        Loads all finalized snapshots ordered chronologically.
        Computes stage transitions between consecutive snapshots.
        
        Args:
            company_id: UUID of company
            
        Returns:
            List of timeline items (chronologically ordered, earliest first):
            [
                {
                    "snapshot_date": "2026-01-15",
                    "stage": "IDEA",
                    "monthly_revenue": 20000.00,
                    "monthly_burn": 40000.00,
                    "runway_months": 5.00,
                    "stage_transition_from_previous": None  # First item
                },
                {
                    "snapshot_date": "2026-02-15",
                    "stage": "PRE_SEED",
                    "monthly_revenue": 30000.00,
                    "monthly_burn": 35000.00,
                    "runway_months": 8.57,
                    "stage_transition_from_previous": "IDEA -> PRE_SEED"  # Changed from previous
                },
                ...
            ]
            
            Returns empty list if company has no finalized snapshots.
        """
        # Load all finalized snapshots
        snapshots = self.repository.get_finalized_by_company(company_id)
        
        # Build timeline items
        timeline_items = []
        previous_stage = None
        
        for snapshot in snapshots:
            # Detect stage transition
            current_stage = snapshot.stage.value if snapshot.stage else None
            stage_transition = None
            
            if previous_stage is not None:
                if previous_stage != current_stage:
                    stage_transition = f"{previous_stage} -> {current_stage}"
            
            # Build timeline item
            timeline_item = {
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "stage": current_stage,
                "monthly_revenue": float(snapshot.monthly_revenue) if snapshot.monthly_revenue else None,
                "monthly_burn": float(snapshot.monthly_burn) if snapshot.monthly_burn else None,
                "runway_months": float(snapshot.runway_months) if snapshot.runway_months else None,
                "stage_transition_from_previous": stage_transition,
            }
            
            timeline_items.append(timeline_item)
            previous_stage = current_stage
        
        return timeline_items
