import uuid as uuid_lib
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, TEXT, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..session import Base


class SignalDefinition(Base):
    __tablename__ = "signal_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    signal_type = Column(String(50), nullable=False)
    description = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<SignalDefinition(id={self.id}, name={self.name}, type={self.signal_type})>"


class SnapshotSignal(Base):
    __tablename__ = "snapshot_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("snapshots.id"), nullable=False)
    signal_definition_id = Column(UUID(as_uuid=True), ForeignKey("signal_definitions.id"), nullable=False)
    signal_value = Column(Numeric(18, 4), nullable=False)
    computed_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<SnapshotSignal(snapshot_id={self.snapshot_id}, signal_id={self.signal_definition_id})>"
