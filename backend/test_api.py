"""
API tests for Q-IDE backend (FastAPI)
"""

from fastapi.testclient import TestClient
from main import app

def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_llm_pool():
    client = TestClient(app)
    resp = client.get("/llm_pool")
    assert resp.status_code == 200
    data = resp.json()
    # The LLM pool endpoint returns a report dict with 'available' and 'excluded'
    assert isinstance(data, dict)
    assert "available" in data
    assert isinstance(data["available"], list)

def test_agent_orchestrate():
    client = TestClient(app)
    payload = {"task_type": "test", "input_data": {"foo": "bar"}}
    resp = client.post("/agent/orchestrate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["used_model"]
    assert data["result"]
