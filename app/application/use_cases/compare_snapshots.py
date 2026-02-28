"""Compare snapshots use case for Sprint 6.

Compares two finalized snapshots and computes deltas.
Application layer - coordinates repository and returns comparison DTO.
"""
from uuid import UUID
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.exceptions import SnapshotNotFoundOrNotFinalized


class CompareSnapshotsUseCase:
    """
    Compare two finalized snapshots use case.
    
    Responsibilities:
    - Load two finalized snapshots by date
    - Compute deltas for metrics
    - Detect stage transitions
    - Return comparison DTO
    
    Constraints:
    - Only FINALIZED snapshots can be compared
    - DRAFT and INVALIDATED snapshots are rejected
    - Dates must exist as finalized snapshots
    - No comparison logic in API layer
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
    
    def execute(
        self,
        company_id: UUID,
        from_date: date,
        to_date: date
    ) -> dict:
        """
        Execute snapshot comparison.
        
        Loads finalized snapshots at two dates and computes deltas.
        
        Args:
            company_id: UUID of company
            from_date: Earlier snapshot date
            to_date: Later snapshot date
            
        Returns:
            Dictionary with comparison data:
            {
                "from_date": "2026-01-15",
                "to_date": "2026-03-15",
                "from_stage": "PRE_SEED",
                "to_stage": "SEED",
                "stage_changed": True,
                "from_metrics": {
                    "monthly_revenue": 50000.00,
                    "monthly_burn": 30000.00,
                    "runway_months": 10.00
                },
                "to_metrics": {
                    "monthly_revenue": 75000.00,
                    "monthly_burn": 25000.00,
                    "runway_months": 16.00
                },
                "deltas": {
                    "delta_revenue": 25000.00,
                    "delta_burn": -5000.00,
                    "delta_runway": 6.00
                }
            }
            
        Raises:
            SnapshotNotFoundOrNotFinalized: If either snapshot not found or not finalized
        """
        # Load from_snapshot
        from_snapshot = self.repository.get_finalized_by_company_and_date(
            company_id,
            from_date
        )
        if not from_snapshot:
            raise SnapshotNotFoundOrNotFinalized(
                str(company_id),
                from_date.isoformat()
            )
        
        # Load to_snapshot
        to_snapshot = self.repository.get_finalized_by_company_and_date(
            company_id,
            to_date
        )
        if not to_snapshot:
            raise SnapshotNotFoundOrNotFinalized(
                str(company_id),
                to_date.isoformat()
            )
        
        # Compute stage transition
        from_stage = from_snapshot.stage.value if from_snapshot.stage else None
        to_stage = to_snapshot.stage.value if to_snapshot.stage else None
        stage_changed = from_stage != to_stage
        
        # Compute deltas
        delta_revenue = self._safe_delta(
            from_snapshot.monthly_revenue,
            to_snapshot.monthly_revenue
        )
        delta_burn = self._safe_delta(
            from_snapshot.monthly_burn,
            to_snapshot.monthly_burn
        )
        delta_runway = self._safe_delta(
            from_snapshot.runway_months,
            to_snapshot.runway_months
        )
        
        # Build response
        return {
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
            "from_stage": from_stage,
            "to_stage": to_stage,
            "stage_changed": stage_changed,
            "from_metrics": {
                "monthly_revenue": float(from_snapshot.monthly_revenue) if from_snapshot.monthly_revenue else None,
                "monthly_burn": float(from_snapshot.monthly_burn) if from_snapshot.monthly_burn else None,
                "runway_months": float(from_snapshot.runway_months) if from_snapshot.runway_months else None,
            },
            "to_metrics": {
                "monthly_revenue": float(to_snapshot.monthly_revenue) if to_snapshot.monthly_revenue else None,
                "monthly_burn": float(to_snapshot.monthly_burn) if to_snapshot.monthly_burn else None,
                "runway_months": float(to_snapshot.runway_months) if to_snapshot.runway_months else None,
            },
            "deltas": {
                "delta_revenue": float(delta_revenue) if delta_revenue is not None else None,
                "delta_burn": float(delta_burn) if delta_burn is not None else None,
                "delta_runway": float(delta_runway) if delta_runway is not None else None,
            }
        }
    
    @staticmethod
    def _safe_delta(from_value, to_value) -> Optional[object]:
        """
        Safely compute delta, handling None values.
        
        If either value is None, returns None.
        Otherwise returns to_value - from_value.
        
        Args:
            from_value: Earlier value
            to_value: Later value
            
        Returns:
            Delta or None if either value is None
        """
        if from_value is None or to_value is None:
            return None
        return to_value - from_value
