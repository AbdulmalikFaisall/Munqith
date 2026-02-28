"""Finalize snapshot use case for Sprint 5.

Orchestrates the full snapshot finalization pipeline in an atomic transaction.
Application layer - coordinates domain engines and repositories.
"""
from uuid import UUID
from sqlalchemy.orm import Session

from app.domain.entities.snapshot import Snapshot
from app.domain.engines import (
    SignalEngine,
    RuleEngine,
    StageEvaluator,
    ExplainabilityResolver,
)
from app.infrastructure.repositories.snapshot_repository import SnapshotRepository
from app.domain.exceptions import FinalizeDraftOnlyError


class FinalizeSnapshotUseCase:
    """
    Finalize snapshot use case.
    
    Responsibilities:
    - Orchestrate full snapshot finalization pipeline
    - Ensure atomic transaction (all-or-nothing)
    - Coordinate domain engines and repositories
    - Never contain business logic (only orchestration)
    
    Pipeline Execution Order (Critical):
    1. Load snapshot from repository
    2. Compute derived metrics
    3. Generate signals
    4. Evaluate rules
    5. Determine stage
    6. Resolve contributing signals
    7. Assign stage to snapshot
    8. Finalize snapshot (status transition)
    9. Persist all changes in one transaction
    
    Architecture:
    - Application layer (this class): Orchestrates only
    - Domain engines: Pure computation, no DB
    - Repository: Persistence with transaction management
    
    Performance Constraint:
    - Full finalization must complete under 500ms
    - No external API calls
    - No blocking I/O except database
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.repository = SnapshotRepository(session)
        self.session = session
    
    def execute(self, snapshot_id: UUID) -> Snapshot:
        """
        Execute snapshot finalization.
        
        Full Pipeline:
        1. Load snapshot from repository
        2. Validate snapshot is in DRAFT status
        3. Compute derived metrics (monthly_burn, runway_months)
        4. Generate signals from snapshot data
        5. Evaluate deterministic rules
        6. Determine company stage
        7. Resolve contributing signals
        8. Assign stage to snapshot
        9. Finalize snapshot (DRAFT → FINALIZED)
        10. Persist snapshot, signals, rule results, and contributing signals
        
        All steps 1-10 occur in a single database transaction.
        If any step fails, entire transaction rolls back.
        
        Args:
            snapshot_id: UUID of snapshot to finalize
            
        Returns:
            Finalized Snapshot entity with:
            - status = FINALIZED
            - stage = derived stage
            - monthly_burn = computed
            - runway_months = computed
            - finalized_at = timestamp
            
        Raises:
            ValueError: If snapshot_id is invalid
            FileNotFoundError: If snapshot doesn't exist
            FinalizeDraftOnlyError: If snapshot is not in DRAFT status
            Exception: On database errors (transaction rolls back)
            
        Execution Time:
        - Target: < 500ms
        - Actual: Depends on database performance and snapshot size
        """
        # ===================== Step 1: Load Snapshot =====================
        snapshot = self.repository.get_by_id(snapshot_id)
        if not snapshot:
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found")
        
        # ===================== Step 2: Validate State =====================
        if not snapshot.is_draft:
            raise FinalizeDraftOnlyError(str(snapshot.id), snapshot.status.value)
        
        # ===================== Step 3: Compute Derived Metrics =====================
        # Pure calculation: operating_costs - revenue = monthly_burn
        # Pure calculation: cash_balance / monthly_burn = runway_months
        snapshot.compute_derived_metrics()
        
        # ===================== Step 4: Generate Signals =====================
        # Pure computation from snapshot financial attributes
        # Produces: MonthlyBurn, RunwayMonths, RunwayRisk signals
        signals = SignalEngine.compute(snapshot)
        
        # ===================== Step 5: Evaluate Rules =====================
        # Pure computation from signals
        # Produces: RunwayRiskRule result, ProfitabilityRule result
        rule_results = RuleEngine.evaluate(signals)
        
        # ===================== Step 6: Determine Stage =====================
        # Pure determination from rule results
        # Returns: Stage enum (IDEA, PRE_SEED, SEED, SERIES_A, GROWTH)
        stage = StageEvaluator.determine(rule_results)
        
        # ===================== Step 7: Resolve Contributing Signals =====================
        # Determine which signals influenced the stage decision
        # Returns: List of Signal entities that contributed
        contributing_signals = ExplainabilityResolver.resolve(signals, rule_results)
        
        # ===================== Step 8: Assign Stage to Snapshot =====================
        # Set derived stage on snapshot entity
        snapshot.set_stage(stage)
        
        # ===================== Step 9: Finalize Snapshot =====================
        # Transition status from DRAFT to FINALIZED
        # Sets finalized_at timestamp
        snapshot.finalize()
        
        # ===================== Step 10: Persist Everything Atomically =====================
        # Single transaction: all-or-nothing persistence
        # If any part fails, entire operation rolls back
        self.repository.save(
            snapshot=snapshot,
            signals=signals,
            rule_results=rule_results,
            contributing_signals=contributing_signals,
        )
        
        # ===================== Return Finalized Snapshot =====================
        return snapshot
