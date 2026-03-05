"""Analytics insight model for appending analytics results.

Stores offline AI/analytics insights without affecting core decision system.
Append-only table - never edited once created.
"""
import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    TEXT,
    TIMESTAMP,
    text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from ..session import Base


class AnalyticsInsight(Base):
    """
    Analytics insight table - stores offline analysis results.
    
    Characteristics:
    - Append-only (no updates)
    - Foreign keys reference core snapshots (read-only)
    - Separate from snapshot.stage and rule results
    - No circular references from domain into analytics
    
    Fields align with Sprint 11 spec:
    - insight_type: Category of insight (e.g., RISK_ARCHETYPE, TRAJECTORY_ALERT)
    - insight_value: The actual insight (e.g., RUNWAY_COLLAPSE, COST_SPIKE)
    - details: JSON/TEXT for additional context
    """

    __tablename__ = "analytics_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    snapshot_id = Column(
        UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=False
    )

    # Insight classification
    insight_type = Column(String(100), nullable=False)  # e.g., RISK_ARCHETYPE, TRAJECTORY_ALERT
    insight_value = Column(String(255), nullable=False)  # e.g., RUNWAY_COLLAPSE, BURN_SPIKE

    # Optional details (JSON-like content)
    details = Column(TEXT, nullable=True)

    # Audit trail
    created_at = Column(
        TIMESTAMP(timezone=False), nullable=False, server_default=text("now()")
    )

    # Indexes for efficient querying
    __table_args__ = (
        Index("ix_analytics_company_snapshot", "company_id", "snapshot_id"),
        Index("ix_analytics_snapshot_id", "snapshot_id"),
        Index("ix_analytics_company_id", "company_id"),
        Index("ix_analytics_insight_type", "insight_type"),
        Index("ix_analytics_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<AnalyticsInsight(id={self.id}, company_id={self.company_id}, snapshot_id={self.snapshot_id}, type={self.insight_type}, value={self.insight_value})>"
