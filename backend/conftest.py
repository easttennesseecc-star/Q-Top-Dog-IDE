# Ensure parent directory is on sys.path so `backend` package imports resolve
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, relationship
from backend.main import app
from backend.database.database_service import get_db
from backend.models import Base
# Import all models to ensure they are registered with the Base
from backend.models import subscription, workflow 
import asyncio

# Define minimal required models for testing (to satisfy FKs)
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    # Minimal relationship to satisfy Subscription.back_populates="user"
    subscription = relationship("Subscription", back_populates="user", uselist=False)

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables for all models that use the central Base
Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    Dependency override for tests.
    Creates a new session for each test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """
    Pytest fixture to create a new database session for each test, and rollback transactions.
    This is for tests that do NOT need to commit data for background tasks.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    """
    A fixture that provides a TestClient with an isolated DB session using rollbacks.
    """
    def override_get_db_for_client():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db_for_client
    yield TestClient(app)
    # remove the override to avoid side-effects
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def test_client_with_db():
    """
    Provides a TestClient that uses a separate, committed transaction.
    This is essential for E2E tests where a background task in the app
    needs to see data that was set up by the test.
    It cleans the database completely after each test.
    """
    # Yield the client that is already configured with the override_get_db
    yield TestClient(app)

    # After the test is done, clean up the database to ensure isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """
    Redefine the event_loop fixture to be session-scoped.
    This allows background tasks to run and be awaited properly in tests.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
