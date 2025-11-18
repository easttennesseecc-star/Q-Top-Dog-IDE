"""
Database session management for the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Use an in-memory SQLite database for simplicity, but configurable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./topdog_ide.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency to provide a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
