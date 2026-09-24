"""Database engine and session dependency."""

from collections.abc import Generator
from functools import lru_cache

from sqlmodel import Session, create_engine

from app.core.config import settings


@lru_cache
def get_engine():
    """Return a cached SQLAlchemy engine, built once per process."""
    return create_engine(settings.database_url)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(get_engine()) as session:
        yield session
