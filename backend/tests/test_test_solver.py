"""
Tests for the LLM Test-Solving System.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from backend.main import app
from backend.services.test_solver_service import TestSolvingStatus

@pytest.fixture
def test_client():
    """Provides a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

def test_start_session(test_client: TestClient):
    """
    Tests the successful start of a new test-solving session.
    """
    test_id = "test_example_hanging_test"
    response = test_client.post("/api/test-solver/start", json={"test_id": test_id})
    
    assert response.status_code == 200
    data = response.json()
    assert data["test_id"] == test_id
    assert data["status"] == TestSolvingStatus.OBSERVING
    assert "id" in data
    assert len(data["logs"]) > 0

def test_get_session(test_client: TestClient):
    """
    Tests retrieving an existing test-solving session.
    """
    # First, create a session
    test_id = "test_another_hanging_test"
    start_response = test_client.post("/api/test-solver/start", json={"test_id": test_id})
    assert start_response.status_code == 200
    session_id = start_response.json()["id"]

    # Now, retrieve it
    get_response = test_client.get(f"/api/test-solver/sessions/{session_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == session_id
    assert data["test_id"] == test_id

def test_get_nonexistent_session(test_client: TestClient):
    """
    Tests that retrieving a nonexistent session returns a 404 error.
    """
    nonexistent_id = "this-id-does-not-exist"
    response = test_client.get(f"/api/test-solver/sessions/{nonexistent_id}")
    assert response.status_code == 404

@patch("backend.services.test_solver_service.TestSolverService.run_llm_task", new_callable=AsyncMock)
def test_session_full_run(mock_run_llm_task: AsyncMock, test_client: TestClient):
    """
    Tests the full run of a session, mocking the LLM calls.
    """
    # Mock the responses from the LLM
    mock_run_llm_task.side_effect = [
        "Code analysis result",
        "System diagnostics result",
        "Hypothesis: The database is slow. Intervention Plan: 1. Restart the database.",
    ]

    test_id = "test_full_run_scenario"
    start_response = test_client.post("/api/test-solver/start", json={"test_id": test_id})
    assert start_response.status_code == 200
    session_id = start_response.json()["id"]

    # The session runs in the background, so we need to poll for its status
    import time
    timeout = 10  # seconds
    start_time = time.time()
    final_status = None
    while time.time() - start_time < timeout:
        get_response = test_client.get(f"/api/test-solver/sessions/{session_id}")
        if get_response.status_code == 200:
            status = get_response.json()["status"]
            if status in [TestSolvingStatus.SOLVED, TestSolvingStatus.FAILED]:
                final_status = status
                break
        time.sleep(0.5)

    assert final_status == TestSolvingStatus.SOLVED
    
    # Verify that the LLM tasks were called
    assert mock_run_llm_task.call_count == 3
