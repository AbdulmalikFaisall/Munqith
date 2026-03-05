"""
Reporting service for Sprint 10.

High-level service for generating investor reports.
Coordinates export use case with PDF generation.
Application layer - business logic for report generation.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.application.use_cases.export_snapshot import ExportSnapshotUseCase


class ReportService:
    """
    Report generation service.
    
    Responsibilities:
    - Coordinate snapshot export
    - Format data for presentation
    - Delegate PDF generation to infrastructure layer
    
    Key Rule: Service handles application logic only.
    PDF generation is delegated to infrastructure.
    """
    
    def __init__(self, session: Session):
        """
        Initialize service with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.export_use_case = ExportSnapshotUseCase(session)
    
    def export_snapshot_data(self, snapshot_id: UUID) -> Dict[str, Any]:
        """
        Export snapshot data in application format.
        
        Args:
            snapshot_id: UUID of snapshot to export
            
        Returns:
            Structured dict with all snapshot data
            
        Raises:
            FileNotFoundError: If snapshot doesn't exist
            SnapshotNotFoundOrNotFinalized: If snapshot is not finalized
        """
        return self.export_use_case.execute(snapshot_id)
    
    def generate_pdf_bytes(self, snapshot_id: UUID) -> bytes:
        """
        Generate PDF investor report as bytes.
        
        Coordinates export and PDF generation.
        
        Args:
            snapshot_id: UUID of snapshot to report on
            
        Returns:
            Raw PDF file bytes
            
        Raises:
            FileNotFoundError: If snapshot doesn't exist
            SnapshotNotFoundOrNotFinalized: If snapshot is not finalized
            PDFGenerationError: If PDF generation fails
        """
        from app.infrastructure.reporting.pdf_generator import PDFGenerator
        
        # Step 1: Export snapshot data
        export_data = self.export_snapshot_data(snapshot_id)
        
        # Step 2: Generate PDF from exported data
        pdf_bytes = PDFGenerator.generate_report(export_data)
        
        return pdf_bytes
