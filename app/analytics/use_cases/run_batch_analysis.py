"""Batch analysis use case for offline insights generation.

Orchestrates reading historical snapshots and generating analytics insights.
Application layer - coordinates reader, engines, and repository.
"""
from uuid import UUID
from sqlalchemy.orm import Session

from app.analytics.reader.snapshot_reader import SnapshotReader
from app.analytics.engines.trajectory_detector import TrajectoryDetector
from app.analytics.engines.archetype_labeler import ArchetypeLabeler
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository


class RunBatchAnalysisUseCase:
    """
    Run offline batch analytics for a company.
    
    Responsibilities:
    - Orchestrate full analytics pipeline
    - Load finalized snapshot history
    - Run detectors and labelers
    - Persist results to analytics tables
    
    Pipeline Execution:
    1. Load finalized snapshot history (chronological)
    2. Run trajectory detector on full history
    3. Run archetype labeler on full history
    4. Persist all insights to analytics_insights table
    
    Key principles:
    - Never modifies snapshot table
    - Append-only writes to analytics_insights
    - Deterministic: same history → same insights
    - Pure orchestration - no business logic
    """
    
    def __init__(self, session: Session):
        """
        Initialize use case with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
        self.snapshot_reader = SnapshotReader(session)
        self.trajectory_detector = TrajectoryDetector()
        self.archetype_labeler = ArchetypeLabeler()
        self.analytics_repository = AnalyticsRepository(session)
    
    def execute(self, company_id: UUID) -> dict:
        """
        Execute full batch analysis for a company.
        
        Args:
            company_id: Company UUID
            
        Returns:
            Summary dict with keys:
                - company_id: UUID
                - snapshots_analyzed: int
                - insights_created: int
                - trajectory_alerts: int
                - archetype_labels: int
        
        Raises:
            ValueError: If company_id is invalid
        """
        # Step 1: Load finalized snapshot history
        snapshots = self.snapshot_reader.get_company_history(company_id)
        
        # If no finalized snapshots, return early
        if not snapshots:
            return {
                "company_id": company_id,
                "snapshots_analyzed": 0,
                "insights_created": 0,
                "trajectory_alerts": 0,
                "archetype_labels": 0,
            }
        
        # Step 2: Run trajectory detection on full history
        trajectory_alerts = self.trajectory_detector.detect(snapshots)
        
        # Step 3: Run archetype labeling on full history
        archetype_labels = self.archetype_labeler.label(snapshots)
        
        # Step 4: Persist all insights
        # For trajectory alerts - use latest snapshot
        latest_snapshot = snapshots[-1]
        insights_created = 0
        
        for alert in trajectory_alerts:
            self.analytics_repository.save_insight(
                company_id=company_id,
                snapshot_id=latest_snapshot.id,
                insight_type=alert["alert_type"],
                insight_value=alert["alert_value"],
                details=alert.get("details"),
            )
            insights_created += 1
        
        # For archetype labels - assign to latest snapshot
        for label in archetype_labels:
            self.analytics_repository.save_insight(
                company_id=company_id,
                snapshot_id=latest_snapshot.id,
                insight_type=label["label_type"],
                insight_value=label["label_value"],
                details=label.get("details"),
            )
            insights_created += 1
        
        # Commit all changes
        self.session.commit()
        
        return {
            "company_id": company_id,
            "snapshots_analyzed": len(snapshots),
            "insights_created": insights_created,
            "trajectory_alerts": len(trajectory_alerts),
            "archetype_labels": len(archetype_labels),
        }
