"""User database model for authentication and RBAC."""
import uuid as uuid_lib
from datetime import datetime
from sqlalchemy import Column, String, Boolean, TIMESTAMP, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from ..session import Base


class User(Base):
    """
    User model for authentication and RBAC.
    
    Stores:
    - User credentials (email, hashed password)
    - Role (ANALYST or ADMIN)
    - Active status
    - Timestamps
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_lib.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, server_default="ANALYST")
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text("now()"))

    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('ANALYST', 'ADMIN')", name="ck_user_role"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
