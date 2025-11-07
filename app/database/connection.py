from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
from app.core.config import settings

# Use the same database URL from settings
DATABASE_URL = settings.database_url

# Create SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get a SQLModel session for FastAPI."""
    with Session(engine) as session:
        yield session

# For Alembic compatibility
Base = SQLModel