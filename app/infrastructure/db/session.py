from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

Base = declarative_base()

def get_database_url() -> str:
    """Retrieve database URL from environment or use default."""
    import os
    return os.getenv("DATABASE_URL", "postgresql://munqith:munqith@localhost:5432/munqith")

engine = create_engine(
    get_database_url(),
    poolclass=NullPool,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
