"""Timeline endpoint for Sprint 6.

GET /companies/{company_id}/timeline

Retrieves finalized snapshots in chronological order with stage transitions.
API layer - thin routing and validation only (no business logic).
"""
from fastapi import APIRouter, Path, Depends
from fastapi.responses import JSONResponse
from uuid import UUID

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.application.use_cases.company_timeline import CompanyTimelineUseCase

router = APIRouter()


@router.get("/companies/{company_id}/timeline")
async def get_timeline(
    company_id: UUID = Path(..., description="Company UUID"),
    user: dict = Depends(get_current_user),
    session=Depends(get_db)
):
    """
    Get timeline of finalized snapshots for a company.
    
    Timeline includes all FINALIZED snapshots ordered chronologically.
    INVALIDATED snapshots are automatically excluded.
    
    Args:
        company_id: UUID of company (path parameter)
        session: Database session (injected)
        
    Returns:
        JSONResponse with timeline items:
        {
            "timeline": [
                {
                    "snapshot_date": "2026-01-15",
                    "stage": "IDEA",
                    "monthly_revenue": 20000.00,
                    "monthly_burn": 40000.00,
                    "runway_months": 5.00,
                    "stage_transition_from_previous": null
                },
                ...
            ]
        }
        
        Returns empty list if no finalized snapshots exist.
    """
    # No business logic here - only routing and response formatting
    use_case = CompanyTimelineUseCase(session)
    timeline_items = use_case.execute(company_id)
    
    return JSONResponse(
        status_code=200,
        content={
            "timeline": timeline_items
        }
    )
