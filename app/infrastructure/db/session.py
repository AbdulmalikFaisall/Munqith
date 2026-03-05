from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """
    Retrieve database URL from environment or use default.
    
    WARNING: In production, DATABASE_URL MUST be explicitly set.
    Default localhost URL is for development only.
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        env = os.getenv("ENV", "development")
        if env == "production":
            logger.error(
                "CRITICAL: DATABASE_URL not set in production environment. "
                "Set DATABASE_URL environment variable before deploying."
            )
            raise ValueError(
                "DATABASE_URL environment variable is required in production"
            )
        # Development: use default localhost
        logger.warning(
            "DATABASE_URL not set. Using development default (localhost). "
            "Set DATABASE_URL environment variable for custom database."
        )
        database_url = "postgresql://munqith:munqith@localhost:5432/munqith"
    
    return database_url

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
