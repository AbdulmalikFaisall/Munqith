"""Snapshot endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import get_current_user, require_role
from app.domain.enums import UserRole
from app.application.use_cases.create_snapshot import CreateSnapshotUseCase
from app.application.use_cases.finalize_snapshot import FinalizeSnapshotUseCase
from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.exceptions import (
    DuplicateSnapshotError,
    FinalizeDraftOnlyError,
    FinancialSanityError,
    SnapshotValidationError,
)

router = APIRouter()


class CreateSnapshotRequest(BaseModel):
    """Create snapshot request model - validated by Pydantic (format validation)."""
    company_id: UUID = Field(..., description="Company UUID")
    snapshot_date: date = Field(..., description="Date of snapshot (YYYY-MM-DD)")
    cash_balance: Optional[Decimal] = Field(None, ge=0, description="Cash balance in SAR (must be >= 0)")
    monthly_revenue: Optional[Decimal] = Field(None, ge=0, description="Monthly revenue in SAR (must be >= 0)")
    operating_costs: Optional[Decimal] = Field(None, ge=0, description="Monthly operating costs in SAR (must be >= 0)")


class SnapshotResponse(BaseModel):
    """Snapshot response model."""
    id: UUID
    company_id: UUID
    snapshot_date: date
    status: str
    cash_balance: Optional[Decimal]
    monthly_revenue: Optional[Decimal]
    operating_costs: Optional[Decimal]
    stage: Optional[str]
    created_at: Optional[str]


def _snapshot_to_payload(snapshot) -> dict:
    return {
        "id": str(snapshot.id),
        "company_id": str(snapshot.company_id),
        "snapshot_date": str(snapshot.snapshot_date),
        "status": snapshot.status.value,
        "cash_balance": float(snapshot.cash_balance) if snapshot.cash_balance else None,
        "monthly_revenue": float(snapshot.monthly_revenue) if snapshot.monthly_revenue else None,
        "operating_costs": float(snapshot.operating_costs) if snapshot.operating_costs else None,
        "monthly_burn": float(snapshot.monthly_burn) if snapshot.monthly_burn else None,
        "runway_months": float(snapshot.runway_months) if snapshot.runway_months else None,
        "stage": snapshot.stage.value if snapshot.stage else None,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        "finalized_at": snapshot.finalized_at.isoformat() if snapshot.finalized_at else None,
        "invalidated_at": snapshot.invalidated_at.isoformat() if snapshot.invalidated_at else None,
        "invalidation_reason": snapshot.invalidation_reason,
    }


@router.post("/snapshots", response_model=SnapshotResponse)
async def create_snapshot(
    request: CreateSnapshotRequest,
    user=Depends(require_role(UserRole.ANALYST)),
    session: Session = Depends(get_db)
):
    """
    Create a new snapshot for a company.
    
    Only ANALYST and ADMIN users can create snapshots.
    
    Validation layers:
    1. API layer (Pydantic): Format validation, non-negative numbers
    2. Domain layer: Financial sanity checks, business logic
    3. Infrastructure layer: Uniqueness constraint
    
    Financial inputs are optional but if provided must be non-negative.
    
    Args:
        request: CreateSnapshotRequest with company_id, snapshot_date, and financial data
        user: Current user (must be ANALYST or ADMIN, from role dependency)
        session: Database session (injected)
        
    Returns:
        JSONResponse with created snapshot:
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "company_id": "660e8400-e29b-41d4-a716-446655440000",
            "snapshot_date": "2026-03-01",
            "status": "DRAFT",
            "cash_balance": "50000.00",
            "monthly_revenue": "10000.00",
            "operating_costs": "8000.00",
            "stage": null,
            "created_at": "2026-03-01T12:00:00"
        }
        
    Raises:
        HTTPException 403: If user is not ANALYST or ADMIN
        HTTPException 400: If financial inputs are negative (caught by Pydantic)
        HTTPException 409: If snapshot already exists for this (company_id, snapshot_date)
        HTTPException 422: If financial data fails domain validation (sanity checks)
    """
    try:
        # Execute use case
        use_case = CreateSnapshotUseCase(session)
        snapshot = use_case.execute(
            company_id=request.company_id,
            snapshot_date=request.snapshot_date,
            cash_balance=request.cash_balance,
            monthly_revenue=request.monthly_revenue,
            operating_costs=request.operating_costs,
        )
        
        # Return created snapshot
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=_snapshot_to_payload(snapshot)
        )
    
    except DuplicateSnapshotError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    
    except FinancialSanityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    except SnapshotValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during snapshot creation"
        )


@router.get("/snapshots/{snapshot_id}")
async def get_snapshot_detail(
    snapshot_id: UUID = Path(..., description="Snapshot UUID"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    """Return snapshot details for any lifecycle status."""
    repository = SnapshotRepository(session)
    snapshot = repository.get_by_id(snapshot_id)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=_snapshot_to_payload(snapshot))


@router.post("/snapshots/{snapshot_id}/finalize", response_model=SnapshotResponse)
async def finalize_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot UUID"),
    user=Depends(require_role(UserRole.ANALYST)),
    session: Session = Depends(get_db)
):
    """Finalize a DRAFT snapshot and compute derived intelligence."""
    try:
        use_case = FinalizeSnapshotUseCase(session)
        snapshot = use_case.execute(snapshot_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=_snapshot_to_payload(snapshot))

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )

    except FinalizeDraftOnlyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    except FinancialSanityError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during snapshot finalization"
        )
