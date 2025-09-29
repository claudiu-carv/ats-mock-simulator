from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ats_mock_api.db")
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


# Dependency for FastAPI
def get_db_session():
    """Dependency to get database session in FastAPI routes."""
    return next(get_session())