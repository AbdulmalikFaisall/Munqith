import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, TEXT, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from ..session import Base


class RuleDefinition(Base):
    __tablename__ = "rule_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(TEXT, nullable=True)
    rule_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<RuleDefinition(id={self.id}, name={self.name})>"


class SnapshotRuleResult(Base):
    __tablename__ = "snapshot_rule_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=False)
    rule_definition_id = Column(UUID(as_uuid=True), ForeignKey("rule_definitions.id"), nullable=False)
    rule_satisfied = Column(Boolean, nullable=False)
    evaluated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<SnapshotRuleResult(snapshot_id={self.snapshot_id}, rule_id={self.rule_definition_id})>"
