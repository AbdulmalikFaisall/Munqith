"""Company read endpoints for frontend intelligence views."""
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.dependencies.auth import get_current_user
from app.domain.enums.snapshot_status import SnapshotStatus
from app.infrastructure.db.models.company import Company
from app.infrastructure.db.models.snapshot import Snapshot
from app.infrastructure.db.session import get_db

router = APIRouter()


def _trend_label(first_value, last_value) -> str | None:
    if first_value is None or last_value is None:
        return None
    if last_value > first_value:
        return "UP"
    if last_value < first_value:
        return "DOWN"
    return "FLAT"


def _snapshot_payload(model: Snapshot) -> dict:
    return {
        "id": str(model.id),
        "company_id": str(model.company_id),
        "snapshot_date": model.snapshot_date.isoformat(),
        "status": model.status,
        "cash_balance": float(model.cash_balance) if model.cash_balance is not None else None,
        "monthly_revenue": float(model.monthly_revenue) if model.monthly_revenue is not None else None,
        "operating_costs": float(model.operating_costs) if model.operating_costs is not None else None,
        "monthly_burn": float(model.monthly_burn) if model.monthly_burn is not None else None,
        "runway_months": float(model.runway_months) if model.runway_months is not None else None,
        "stage": model.stage,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "finalized_at": model.finalized_at.isoformat() if model.finalized_at else None,
        "invalidated_at": model.invalidated_at.isoformat() if model.invalidated_at else None,
        "invalidation_reason": model.invalidation_reason,
    }


@router.get("/companies")
async def list_companies(
    search: str | None = Query(default=None, description="Optional case-insensitive company name search"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    """List companies with basic latest-intelligence summary."""
    query = session.query(Company)
    if search:
        query = query.filter(Company.name.ilike(f"%{search.strip()}%"))

    companies = query.order_by(Company.created_at.desc()).all()
    response = []

    for company in companies:
        finalized_snapshots = (
            session.query(Snapshot)
            .filter(
                Snapshot.company_id == company.id,
                Snapshot.status == SnapshotStatus.FINALIZED.value,
            )
            .order_by(Snapshot.snapshot_date.asc())
            .all()
        )

        latest = finalized_snapshots[-1] if finalized_snapshots else None
        first = finalized_snapshots[0] if finalized_snapshots else None

        response.append(
            {
                "id": str(company.id),
                "name": company.name,
                "sector": company.sector,
                "created_at": company.created_at.isoformat() if company.created_at else None,
                "latest_snapshot_id": str(latest.id) if latest else None,
                "latest_snapshot_date": latest.snapshot_date.isoformat() if latest else None,
                "latest_stage": latest.stage if latest else None,
                "snapshot_count": len(finalized_snapshots),
                "revenue_trend": _trend_label(
                    first.monthly_revenue if first else None,
                    latest.monthly_revenue if latest else None,
                ),
                "burn_trend": _trend_label(
                    first.monthly_burn if first else None,
                    latest.monthly_burn if latest else None,
                ),
                "runway_trend": _trend_label(
                    first.runway_months if first else None,
                    latest.runway_months if latest else None,
                ),
            }
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@router.get("/companies/{company_id}")
async def get_company_detail(
    company_id: UUID = Path(..., description="Company UUID"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    """Return company metadata and aggregate snapshot counts by lifecycle status."""
    company = session.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Company {company_id} not found")

    counts = (
        session.query(Snapshot.status, func.count(Snapshot.id))
        .filter(Snapshot.company_id == company.id)
        .group_by(Snapshot.status)
        .all()
    )
    counts_map = {status: count for status, count in counts}

    latest_any = (
        session.query(Snapshot)
        .filter(Snapshot.company_id == company.id)
        .order_by(Snapshot.snapshot_date.desc())
        .first()
    )

    payload = {
        "id": str(company.id),
        "name": company.name,
        "sector": company.sector,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
        "snapshot_counts": {
            "draft": int(counts_map.get(SnapshotStatus.DRAFT.value, 0)),
            "finalized": int(counts_map.get(SnapshotStatus.FINALIZED.value, 0)),
            "invalidated": int(counts_map.get(SnapshotStatus.INVALIDATED.value, 0)),
        },
        "latest_snapshot_id": str(latest_any.id) if latest_any else None,
        "latest_snapshot_date": latest_any.snapshot_date.isoformat() if latest_any else None,
        "latest_snapshot_status": latest_any.status if latest_any else None,
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=payload)


@router.get("/companies/{company_id}/snapshots")
async def list_company_snapshots(
    company_id: UUID = Path(..., description="Company UUID"),
    include_invalidated: bool = Query(default=False),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    """List snapshots for a company in chronological order."""
    company_exists = session.query(Company.id).filter(Company.id == company_id).first()
    if not company_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Company {company_id} not found")

    query = session.query(Snapshot).filter(Snapshot.company_id == company_id)
    if not include_invalidated:
        query = query.filter(Snapshot.status != SnapshotStatus.INVALIDATED.value)

    snapshots = query.order_by(Snapshot.snapshot_date.asc()).all()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "company_id": str(company_id),
            "snapshots": [_snapshot_payload(item) for item in snapshots],
        },
    )
