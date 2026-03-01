"""Snapshot creation endpoint for Sprint 9."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import require_role
from app.domain.enums import UserRole
from app.application.use_cases.create_snapshot import CreateSnapshotUseCase
from app.domain.exceptions import (
    DuplicateSnapshotError,
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
            content={
                "id": str(snapshot.id),
                "company_id": str(snapshot.company_id),
                "snapshot_date": str(snapshot.snapshot_date),
                "status": snapshot.status.value,
                "cash_balance": float(snapshot.cash_balance) if snapshot.cash_balance else None,
                "monthly_revenue": float(snapshot.monthly_revenue) if snapshot.monthly_revenue else None,
                "operating_costs": float(snapshot.operating_costs) if snapshot.operating_costs else None,
                "stage": snapshot.stage.value if snapshot.stage else None,
                "created_at": str(snapshot.created_at) if snapshot.created_at else None,
            }
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
