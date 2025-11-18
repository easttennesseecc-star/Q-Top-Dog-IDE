import pytest
from starlette.testclient import TestClient
from sqlalchemy import inspect

def test_database_initialization(test_client: TestClient):
    """
    Tests if the database tables are created during application startup.
    """
    # The test_client fixture starts the app, which should trigger the lifespan
    # event and initialize the database.
    
    db_manager = test_client.app.workflow_db_manager
    engine = db_manager.engine
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert "build_workflows" in tables
    assert "workflow_events" in tables
    assert "workflow_handoffs" in tables
