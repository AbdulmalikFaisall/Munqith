import uuid as uuid_lib
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Date, Numeric, ForeignKey, TEXT, CheckConstraint, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..session import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    
    # Financial attributes
    cash_balance = Column(Numeric(18, 2), nullable=True)
    monthly_revenue = Column(Numeric(18, 2), nullable=True)
    operating_costs = Column(Numeric(18, 2), nullable=True)
    
    # Derived metrics
    monthly_burn = Column(Numeric(18, 2), nullable=True)
    runway_months = Column(Numeric(10, 2), nullable=True)
    
    # Stage and status
    stage = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, server_default="DRAFT")
    
    # Lifecycle tracking
    invalidation_reason = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))
    finalized_at = Column(TIMESTAMP(timezone=False), nullable=True)
    invalidated_at = Column(TIMESTAMP(timezone=False), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('DRAFT', 'FINALIZED', 'INVALIDATED')", name="ck_snapshot_status"),
        CheckConstraint("cash_balance >= 0", name="ck_cash_balance_non_negative"),
        CheckConstraint("monthly_revenue >= 0", name="ck_monthly_revenue_non_negative"),
        CheckConstraint("operating_costs >= 0", name="ck_operating_costs_non_negative"),
    )

    def __repr__(self):
        return f"<Snapshot(id={self.id}, company_id={self.company_id}, date={self.snapshot_date})>"
