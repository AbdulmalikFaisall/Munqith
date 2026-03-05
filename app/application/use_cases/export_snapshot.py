"""
Export snapshot use case for Sprint 10.

Loads snapshot and related data for export (JSON/PDF).
Returns structured data reflecting DB values exactly - no recomputation.
Application layer - coordinates repositories for read-only access.
"""
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional, Dict, List, Any

from app.domain.entities.snapshot import Snapshot
from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.exceptions import SnapshotNotFoundOrNotFinalized
from app.domain.enums import SnapshotStatus


class ExportSnapshotUseCase:
    """
    Export snapshot use case.
    
    Responsibilities:
    - Load finalized snapshot from repository
    - Fetch all related data (signals, rule results, contributing signals)
    - Return structured export format
    - Never recompute or modify data
    
    Architecture:
    - Application layer (this class): Orchestration and data structuring
    - Domain layer: No changes
    - Infrastructure: Persistence layer (read-only)
    
    Key Rule: Reports must reflect stored DB values exactly.
    No signal recomputation, no rule re-evaluation.
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
        self.session = session
    
    def execute(self, snapshot_id: UUID) -> Dict[str, Any]:
        """
        Export finalized snapshot as structured data.
        
        Pipeline:
        1. Load snapshot from repository
        2. Verify snapshot is FINALIZED
        3. Fetch company metadata
        4. Fetch signals (if stored)
        5. Fetch rule results (if stored)
        6. Fetch contributing signals (if stored)
        7. Return structured export dict
        
        Args:
            snapshot_id: UUID of snapshot to export
            
        Returns:
            Structured dict with:
            - snapshot_date
            - stage
            - financials (cash_balance, revenue, costs, burn, runway)
            - signals (list of signal objects)
            - rules (list of rule result objects)
            - contributing_signals (list of signal names/ids that influenced stage)
            
        Raises:
            FileNotFoundError: If snapshot doesn't exist
            SnapshotNotFoundOrNotFinalized: If snapshot is not FINALIZED
            
        Data Integrity:
            All values are from database - no recomputation.
            If signals/rules not yet implemented, returns empty lists.
        """
        # ===================== Step 1: Load Snapshot =====================
        snapshot = self.repository.get_by_id(snapshot_id)
        if not snapshot:
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found")
        
        # ===================== Step 2: Verify Finalized =====================
        if snapshot.status != SnapshotStatus.FINALIZED:
            raise SnapshotNotFoundOrNotFinalized(
                company_id=str(snapshot.company_id),
                snapshot_date=str(snapshot.snapshot_date)
            )
        
        # ===================== Step 3: Fetch Company Metadata =====================
        # For now, use company_id (company repository not yet used in exports)
        # Can be enhanced in future sprints
        company_id = str(snapshot.company_id)
        
        # ===================== Step 4-6: Fetch Related Data =====================
        # These will be populated when signal/rule persistence is implemented
        # For now, return empty lists - structure is ready for future sprints
        signals = []
        rule_results = []
        contributing_signals = []
        
        # ===================== Step 7: Structure Export =====================
        export_data = {
            "snapshot_id": str(snapshot.id),
            "company_id": company_id,
            "snapshot_date": snapshot.snapshot_date.isoformat(),
            "stage": snapshot.stage.value if snapshot.stage else None,
            "status": snapshot.status.value,
            "finalized_at": snapshot.finalized_at.isoformat() if snapshot.finalized_at else None,
            "financials": {
                "cash_balance": float(snapshot.cash_balance) if snapshot.cash_balance else None,
                "monthly_revenue": float(snapshot.monthly_revenue) if snapshot.monthly_revenue else None,
                "operating_costs": float(snapshot.operating_costs) if snapshot.operating_costs else None,
                "monthly_burn": float(snapshot.monthly_burn) if snapshot.monthly_burn else None,
                "runway_months": float(snapshot.runway_months) if snapshot.runway_months else None,
            },
            "signals": signals,
            "rules": rule_results,
            "contributing_signals": contributing_signals,
        }
        
        return export_data
