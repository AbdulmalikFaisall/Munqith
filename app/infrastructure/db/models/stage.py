import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, TEXT, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from ..session import Base


class StageDefinition(Base):
    __tablename__ = "stage_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(TEXT, nullable=True)
    order = Column(String(10), nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<StageDefinition(id={self.id}, name={self.name})>"


class SnapshotContributingSignal(Base):
    __tablename__ = "snapshot_contributing_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=False)
    snapshot_signal_id = Column(UUID(as_uuid=True), ForeignKey("snapshot_signals.id"), nullable=False)
    contribution_reason = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<SnapshotContributingSignal(snapshot_id={self.snapshot_id})>"
