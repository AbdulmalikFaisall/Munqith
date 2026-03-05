"""Export endpoints for Sprint 10."""
from fastapi import APIRouter, Path, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from uuid import UUID
from sqlalchemy.orm import Session
import io

from app.infrastructure.db.session import get_db
from app.api.dependencies.auth import require_role
from app.domain.enums import UserRole
from app.application.services.report_service import ReportService
from app.domain.exceptions import SnapshotNotFoundOrNotFinalized
from app.infrastructure.reporting.pdf_generator import PDFGenerationError

router = APIRouter()


@router.get("/snapshots/{snapshot_id}/export/json")
async def export_snapshot_json(
    snapshot_id: UUID = Path(..., description="Snapshot UUID"),
    user=Depends(require_role(UserRole.ANALYST)),
    session: Session = Depends(get_db)
):
    """
    Export snapshot as JSON.
    
    Returns structured JSON with all snapshot data:
    - Financial attributes
    - Derived metrics
    - Signals
    - Rule results
    - Contributing signals
    
    Only ANALYST and ADMIN users can export.
    Only FINALIZED snapshots can be exported.
    
    Args:
        snapshot_id: UUID of snapshot to export
        user: Current user (must be ANALYST or ADMIN)
        session: Database session (injected)
        
    Returns:
        JSONResponse with snapshot data
        
    Raises:
        HTTPException 403: If user is not ANALYST or ADMIN
        HTTPException 404: If snapshot not found or not finalized
    """
    try:
        service = ReportService(session)
        export_data = service.export_snapshot_data(snapshot_id)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=export_data
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )
    
    except SnapshotNotFoundOrNotFinalized as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting snapshot"
        )


@router.get("/snapshots/{snapshot_id}/export/pdf")
async def export_snapshot_pdf(
    snapshot_id: UUID = Path(..., description="Snapshot UUID"),
    user=Depends(require_role(UserRole.ANALYST)),
    session: Session = Depends(get_db)
):
    """
    Export snapshot as PDF investor report.
    
    Generates formatted PDF with:
    - Snapshot metadata
    - Financial summary
    - Stage classification
    - Key signals
    - Contributing signals explanation
    
    Only ANALYST and ADMIN users can export.
    Only FINALIZED snapshots can be exported.
    
    Args:
        snapshot_id: UUID of snapshot to export
        user: Current user (must be ANALYST or ADMIN)
        session: Database session (injected)
        
    Returns:
        PDF file download (Content-Type: application/pdf)
        
    Raises:
        HTTPException 403: If user is not ANALYST or ADMIN
        HTTPException 404: If snapshot not found or not finalized
        HTTPException 500: If PDF generation fails
    """
    try:
        service = ReportService(session)
        pdf_bytes = service.generate_pdf_bytes(snapshot_id)
        
        # Return PDF as file download
        pdf_buffer = io.BytesIO(pdf_bytes)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            status_code=status.HTTP_200_OK,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=snapshot_{snapshot_id}.pdf"}
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )
    
    except SnapshotNotFoundOrNotFinalized as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except PDFGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating PDF report"
        )
