"""
API tests for Q-IDE backend (FastAPI)
"""

from fastapi.testclient import TestClient

def test_health(test_client: TestClient):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data

def test_llm_pool(test_client: TestClient):
    resp = test_client.get("/api/llm_pool")
    assert resp.status_code == 200
    data = resp.json()
    # The LLM pool endpoint returns a report dict with 'available' and 'excluded'
    assert isinstance(data, dict)
    assert "available" in data
    assert isinstance(data["available"], list)

def test_agent_orchestrate(test_client: TestClient):
    payload = {"task_type": "test", "input_data": {"foo": "bar"}}
    resp = test_client.post("/agent/orchestrate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["used_model"]
    assert data["result"]
