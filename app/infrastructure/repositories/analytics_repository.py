"""Analytics repository for persistence of insights.

Handles analytics insight persistence without modifying core domain tables.
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.db.models.analytics_insight import AnalyticsInsight as AnalyticsInsightModel


class AnalyticsRepository:
    """
    Repository for analytics insight persistence.
    
    Responsibilities:
    - Persist analytics insights (append-only)
    - Never modify core snapshot data
    - Handle analytics-specific queries
    
    Key principle:
    - This repository is isolated from core domain repositories
    - Outputs only, never reads/modifies snapshot.stage or rule results
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
    
    def save_insight(
        self,
        company_id: UUID,
        snapshot_id: UUID,
        insight_type: str,
        insight_value: str,
        details: str = None,
    ) -> AnalyticsInsightModel:
        """
        Save a single analytics insight (append-only).
        
        Args:
            company_id: Company UUID
            snapshot_id: Snapshot UUID
            insight_type: Category of insight (e.g., RISK_ARCHETYPE, TRAJECTORY_ALERT)
            insight_value: The insight value (e.g., RUNWAY_COLLAPSE)
            details: Optional JSON/text details
            
        Returns:
            Persisted AnalyticsInsight model
        """
        insight = AnalyticsInsightModel(
            company_id=company_id,
            snapshot_id=snapshot_id,
            insight_type=insight_type,
            insight_value=insight_value,
            details=details,
        )
        self.session.add(insight)
        self.session.flush()  # Flush to get ID before commit
        return insight
    
    def save_insights(
        self,
        company_id: UUID,
        snapshot_id: UUID,
        insights: List[dict],
    ) -> List[AnalyticsInsightModel]:
        """
        Save multiple insights in batch.
        
        Args:
            company_id: Company UUID
            snapshot_id: Snapshot UUID
            insights: List of dicts with keys:
                - insight_type: str
                - insight_value: str
                - details: str (optional)
            
        Returns:
            List of persisted AnalyticsInsight models
        """
        saved_insights = []
        for insight_data in insights:
            insight = self.save_insight(
                company_id=company_id,
                snapshot_id=snapshot_id,
                insight_type=insight_data["insight_type"],
                insight_value=insight_data["insight_value"],
                details=insight_data.get("details"),
            )
            saved_insights.append(insight)
        
        self.session.flush()
        return saved_insights
    
    def get_insights_for_snapshot(
        self, snapshot_id: UUID
    ) -> List[AnalyticsInsightModel]:
        """
        Get all insights for a specific snapshot.
        
        Args:
            snapshot_id: Snapshot UUID
            
        Returns:
            List of AnalyticsInsight models
        """
        return (
            self.session.query(AnalyticsInsightModel)
            .filter(AnalyticsInsightModel.snapshot_id == snapshot_id)
            .order_by(AnalyticsInsightModel.created_at)
            .all()
        )
    
    def get_insights_for_company(self, company_id: UUID) -> List[AnalyticsInsightModel]:
        """
        Get all insights for a specific company.
        
        Args:
            company_id: Company UUID
            
        Returns:
            List of AnalyticsInsight models ordered by snapshot and creation time
        """
        return (
            self.session.query(AnalyticsInsightModel)
            .filter(AnalyticsInsightModel.company_id == company_id)
            .order_by(
                AnalyticsInsightModel.snapshot_id,
                AnalyticsInsightModel.created_at,
            )
            .all()
        )
    
    def get_insights_by_type(
        self, company_id: UUID, insight_type: str
    ) -> List[AnalyticsInsightModel]:
        """
        Get insights of a specific type for a company.
        
        Args:
            company_id: Company UUID
            insight_type: Insight type (e.g., RISK_ARCHETYPE)
            
        Returns:
            List of AnalyticsInsight models
        """
        return (
            self.session.query(AnalyticsInsightModel)
            .filter(
                AnalyticsInsightModel.company_id == company_id,
                AnalyticsInsightModel.insight_type == insight_type,
            )
            .order_by(AnalyticsInsightModel.created_at)
            .all()
        )
