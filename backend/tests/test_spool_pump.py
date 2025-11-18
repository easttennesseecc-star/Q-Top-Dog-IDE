import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def spool_tmpdir(tmp_path: Path):
    root = tmp_path / "spool"
    os.environ["ASSISTANT_SPOOL_DIR"] = str(root.resolve())
    (root / "incoming").mkdir(parents=True, exist_ok=True)
    (root / "done").mkdir(parents=True, exist_ok=True)
    yield root


def test_manual_pump_once_empty(spool_tmpdir: Path, test_client: TestClient):
    r = test_client.post("/spool/pump-once")
    assert r.status_code == 200
    assert r.json().get("status") == "empty"


def test_manual_pump_once_after_enqueue(spool_tmpdir: Path, test_client: TestClient):
    # Enqueue
    r1 = test_client.post("/spool/ingest/api", json={"user_id": "u1", "text": "create login form"})
    assert r1.status_code == 200
    # Pump once
    r2 = test_client.post("/spool/pump-once", params={"user_id": "u1"})
    assert r2.status_code == 200, r2.text
    j = r2.json()
    assert j.get("status") == "ok"
    orch = j.get("orchestrate", {})
    # Expect orchestrator echo structure
    assert orch.get("status") == "ok" or orch.get("message")
    assert "login form" in (j.get("message", {}).get("text") or "")


def test_manual_pump_once_drains_message(spool_tmpdir: Path, test_client: TestClient):
    test_client.post("/spool/ingest/sms", json={"user_id": "u2", "text": "refactor utils"})
    # First pump returns ok
    first = test_client.post("/spool/pump-once", params={"user_id": "u2"})
    assert first.status_code == 200
    assert first.json().get("status") == "ok"
    # Second pump should be empty
    second = test_client.post("/spool/pump-once", params={"user_id": "u2"})
    assert second.status_code == 200
    assert second.json().get("status") == "empty"
