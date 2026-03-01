"""Compare endpoint for Sprint 6.

GET /companies/{company_id}/snapshots/compare?from=YYYY-MM-DD&to=YYYY-MM-DD

Compares two finalized snapshots and computes deltas.
API layer - thin routing and validation only (no business logic).
"""
from fastapi import APIRouter, Path, Query, Depends
from fastapi.responses import JSONResponse
from uuid import UUID
from datetime import date

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import get_current_user
from app.application.use_cases.compare_snapshots import CompareSnapshotsUseCase
from app.domain.exceptions import SnapshotNotFoundOrNotFinalized

router = APIRouter()


@router.get("/companies/{company_id}/snapshots/compare")
async def compare_snapshots(
    company_id: UUID = Path(..., description="Company UUID"),
    from_date: date = Query(..., description="From date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="To date (YYYY-MM-DD)"),
    user: dict = Depends(get_current_user),
    session=Depends(get_db)
):
    """
    Compare two finalized snapshots for a company.
    
    Computes deltas for revenue, burn, and runway.
    Detects stage transitions between snapshots.
    
    Both snapshots must be FINALIZED:
    - DRAFT snapshots will return error
    - INVALIDATED snapshots will return error
    - If no finalized snapshot exists on either date, returns error
    
    Args:
        company_id: UUID of company (path parameter)
        from_date: Earlier snapshot date (YYYY-MM-DD query parameter)
        to_date: Later snapshot date (YYYY-MM-DD query parameter)
        session: Database session (injected)
        
    Returns:
        JSONResponse with comparison:
        {
            "from_date": "2026-01-15",
            "to_date": "2026-03-15",
            "from_stage": "PRE_SEED",
            "to_stage": "SEED",
            "stage_changed": true,
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
    try:
        # No business logic here - only routing and response formatting
        use_case = CompareSnapshotsUseCase(session)
        comparison = use_case.execute(company_id, from_date, to_date)
        
        return JSONResponse(
            status_code=200,
            content=comparison
        )
    
    except SnapshotNotFoundOrNotFinalized as e:
        return JSONResponse(
            status_code=404,
            content={
                "error": str(e)
            }
        )
