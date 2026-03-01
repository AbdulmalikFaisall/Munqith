"""Company trends use case for Sprint 7.

Retrieves time-series financial trends for a company.
Application layer - orchestrates repository and trend engine.
"""
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.engines.trend_engine import TrendEngine


class CompanyTrendsUseCase:
    """
    Company trends use case.
    
    Responsibilities:
    - Load finalized snapshots for company
    - Ensure chronological order
    - Pass to trend engine
    - Return trend analysis
    
    Constraints:
    - Only FINALIZED snapshots included
    - DRAFT and INVALIDATED excluded
    - Works with 1+ snapshots
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
    
    def execute(self, company_id: UUID) -> dict:
        """
        Execute company trend analysis.
        
        Loads all finalized snapshots and builds time-series with indicators.
        
        Args:
            company_id: UUID of company
            
        Returns:
            Dictionary with trend analysis:
            {
                "company_id": "550e8400-e29b-41d4-a716-446655440000",
                "time_series": [
                    {
                        "date": "2026-01-15",
                        "runway_months": 5.00,
                        "monthly_burn": 40000.00,
                        "monthly_revenue": 10000.00,
                        "revenue_growth_percent": null
                    },
                    {
                        "date": "2026-02-15",
                        "runway_months": 6.00,
                        "monthly_burn": 35000.00,
                        "monthly_revenue": 15000.00,
                        "revenue_growth_percent": 50.00
                    },
                    ...
                ],
                "indicators": {
                    "revenue_trend": "UP",
                    "burn_trend": "DOWN",
                    "runway_trend": "UP"
                },
                "snapshot_count": 2
            }
            
            Returns empty time_series if company has no finalized snapshots.
        """
        # Load finalized snapshots (already ordered chronologically)
        snapshots = self.repository.get_finalized_by_company(company_id)
        
        # Build time-series and indicators
        trend_data = TrendEngine.build_time_series(snapshots)
        
        # Add company_id to response
        return {
            "company_id": str(company_id),
            "time_series": trend_data["time_series"],
            "indicators": trend_data["indicators"],
            "snapshot_count": trend_data["snapshot_count"]
        }
