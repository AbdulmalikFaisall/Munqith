"""Trends endpoint for Sprint 7.

GET /companies/{company_id}/trends

Retrieves time-series financial trends and indicators.
API layer - thin routing and validation only (no business logic).
"""
from fastapi import APIRouter, Path, Depends
from fastapi.responses import JSONResponse
from uuid import UUID

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.application.use_cases.company_trends import CompanyTrendsUseCase

router = APIRouter()


@router.get("/companies/{company_id}/trends")
async def get_trends(
    company_id: UUID = Path(..., description="Company UUID"),
    user: dict = Depends(get_current_user),
    session=Depends(get_db)
):
    """
    Get time-series trends for a company.
    
    Retrieves all finalized snapshots and computes:
    - Time-series data (revenue, burn, runway)
    - Revenue growth percentages
    - Trend indicators (UP/DOWN/FLAT)
    
    Only FINALIZED snapshots are included.
    INVALIDATED snapshots are automatically excluded.
    
    Args:
        company_id: UUID of company (path parameter)
        session: Database session (injected)
        
    Returns:
        JSONResponse with trends:
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
                ...
            ],
            "indicators": {
                "revenue_trend": "UP",
                "burn_trend": "DOWN",
                "runway_trend": "UP"
            },
            "snapshot_count": 2
        }
        
        Returns empty time_series if no finalized snapshots exist.
    """
    # No business logic here - only routing and response formatting
    use_case = CompanyTrendsUseCase(session)
    trends = use_case.execute(company_id)
    
    return JSONResponse(
        status_code=200,
        content=trends
    )
