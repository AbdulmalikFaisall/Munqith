"""Invalidate snapshot endpoint for Sprint 8."""
from fastapi import APIRouter, Path, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import require_role
from app.domain.enums import UserRole
from app.application.use_cases.invalidate_snapshot import InvalidateSnapshotUseCase
from app.domain.exceptions import InvalidateDraftSnapshotError

router = APIRouter()


class InvalidateRequest(BaseModel):
    """Invalidate snapshot request model."""
    reason: str


@router.post("/snapshots/{snapshot_id}/invalidate")
async def invalidate_snapshot(
    snapshot_id: UUID = Path(..., description="Snapshot UUID"),
    request: InvalidateRequest = None,
    user=Depends(require_role(UserRole.ADMIN)),
    session: Session = Depends(get_db)
):
    """
    Invalidate a finalized snapshot.
    
    Only ADMIN users can invalidate snapshots.
    Requires a non-empty reason for invalidation.
    
    Args:
        snapshot_id: UUID of snapshot to invalidate (path parameter)
        request: InvalidateRequest with reason
        user: Current user (must be ADMIN, from role dependency)
        session: Database session (injected)
        
    Returns:
        JSONResponse with invalidation result:
        {
            "snapshot_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "INVALIDATED",
            "invalidation_reason": "Incorrect financial data",
            "invalidated_at": "2026-03-01T12:00:00"
        }
        
    Raises:
        HTTPException 403: If user is not ADMIN
        HTTPException 400: If reason is empty
        HTTPException 404: If snapshot not found or is DRAFT
    """
    # Validate reason
    if not request or not request.reason or not request.reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalidation reason cannot be empty"
        )
    
    try:
        # Execute invalidation
        use_case = InvalidateSnapshotUseCase(session)
        result = use_case.execute(snapshot_id, request.reason)
        
        return JSONResponse(
            status_code=200,
            content=result
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )
    
    except InvalidateDraftSnapshotError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
