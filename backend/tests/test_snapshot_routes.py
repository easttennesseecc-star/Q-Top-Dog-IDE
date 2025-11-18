from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


def test_snapshot_labels_catalog(test_client: TestClient, monkeypatch):
    monkeypatch.setenv("ENABLE_SNAPSHOT_API", "true")
    monkeypatch.setenv("REQUIRE_SNAPSHOT_AUTH", "false")
    r = test_client.get("/snapshots/labels")
    assert r.status_code == 200
    data = r.json()
    assert "labels" in data
    assert set(["init", "pre-advance", "post-advance"]).issubset(set(data["labels"]))


def test_checkpoint_create_list_and_rollback_flow(test_client: TestClient, tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ENABLE_SNAPSHOT_API", "true")
    monkeypatch.setenv("REQUIRE_SNAPSHOT_AUTH", "false")
    workflow_id = "wf-test-123"

    # Ensure the snapshots dir is clean for this workflow
    base_dir = Path("backend/snapshots") / workflow_id
    if base_dir.exists():
        for f in base_dir.glob("*.json"):
            try:
                f.unlink()
            except Exception:
                pass
    else:
        base_dir.mkdir(parents=True, exist_ok=True)

    # Initially, list snapshots should be empty
    r0 = test_client.get(f"/snapshots/{workflow_id}")
    assert r0.status_code == 200
    assert r0.json().get("count") == 0

    # Monkeypatch OrchestrationService to avoid DB setup
    with patch("backend.services.orchestration_service.OrchestrationService.get_workflow_status", new=AsyncMock()) as mock_status:
        mock_status.return_value = {
            "workflow_id": workflow_id,
            "current_state": "discovery",
            "status": "in_progress",
            "timestamp": "2025-11-02T00:00:00Z",
        }

        # Create a checkpoint with a label
        r1 = test_client.post(f"/snapshots/{workflow_id}/checkpoint", json={"label": "pre-release"})
        assert r1.status_code == 200
        snap_meta = r1.json()
        assert snap_meta.get("label").startswith("checkpoint")

    # List checkpoints (paginated)
    r2 = test_client.get(f"/snapshots/{workflow_id}/checkpoints?limit=10&offset=0")
    assert r2.status_code == 200
    listed = r2.json()
    assert listed.get("count") == 1
    item = listed["checkpoints"][0]
    assert item["label_base"] == "checkpoint"
    assert item["label_detail"] == "pre-release"

    # Filter only checkpoint label_base through generic list endpoint
    r3 = test_client.get(f"/snapshots/{workflow_id}?label_base=checkpoint")
    assert r3.status_code == 200
    assert r3.json().get("count") >= 1

    # Monkeypatch rollback to avoid DB dependency
    with patch("backend.services.orchestration_service.OrchestrationService.rollback_workflow", new=AsyncMock()) as mock_rb:
        mock_rb.return_value = {
            "workflow_id": workflow_id,
            "rollback_successful": True,
            "new_state": "implementation",
            "reason": "Rollback to checkpoint: test",
        }
        r4 = test_client.post(
            f"/snapshots/{workflow_id}/rollback-to-checkpoint",
            json={"label": "pre-release"},
        )
        assert r4.status_code == 200
        rb = r4.json()
        assert rb.get("rolled_back") is True
        assert rb.get("result", {}).get("rollback_successful") is True
