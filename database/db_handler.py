"""database/db_handler.py
Dynamic database initialization and session management.

Reads DATABASE_URL at runtime to support in-memory testing."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
from sqlalchemy.pool import StaticPool  # for in-memory SQLite pooling

# Cache engines by URL to persist in-memory DB schema across calls
_engine_cache: dict[str, any] = {}

def get_engine() -> any:
    """Create or retrieve a SQLAlchemy Engine based on DATABASE_URL."""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data.db")
    if db_url in _engine_cache:
        return _engine_cache[db_url]
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    # Use StaticPool for in-memory DB to maintain same connection
    if db_url.startswith("sqlite") and ":memory:" in db_url:
        engine = create_engine(db_url, connect_args=connect_args, poolclass=StaticPool)
    else:
        engine = create_engine(db_url, connect_args=connect_args)
    _engine_cache[db_url] = engine
    return engine

def init_db() -> None:
    """Create all tables in the database."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """Return a new SQLAlchemy Session for database operations."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

__all__ = ["init_db", "get_session"]
