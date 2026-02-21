import uuid as uuid_lib
from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
from ..session import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"
