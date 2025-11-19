"""
Database session management for the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Use an in-memory SQLite database for simplicity, but configurable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./topdog_ide.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

__all__ = ["SessionLocal", "get_db", "engine"]

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session as a generator.

    Returns a SQLAlchemy Session wrapped in a generator so FastAPI can handle
    lifecycle (dependency injection with cleanup after response).
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
