import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

os.environ["ENABLE_SNAPSHOT_API"] = "true"
os.environ["REQUIRE_SNAPSHOT_AUTH"] = "false"

from backend.main import app
client = TestClient(app)

workflow_id = "wf-test-123"
# Clean dir
base_dir = Path("backend/snapshots") / workflow_id
if base_dir.exists():
    for f in base_dir.glob("*.json"):
        try:
            f.unlink()
        except Exception:
            pass
else:
    base_dir.mkdir(parents=True, exist_ok=True)

print("list 0:", client.get(f"/snapshots/{workflow_id}").status_code, client.get(f"/snapshots/{workflow_id}").text)

with patch("backend.services.orchestration_service.OrchestrationService.get_workflow_status", new=AsyncMock()) as mock_status:
    mock_status.return_value = {
        "workflow_id": workflow_id,
        "current_state": "discovery",
        "status": "in_progress",
        "timestamp": "2025-11-02T00:00:00Z",
    }
    r1 = client.post(f"/snapshots/{workflow_id}/checkpoint", json={"label": "pre-release"})
    print("checkpoint:", r1.status_code, r1.text)

print("checkpoints:", client.get(f"/snapshots/{workflow_id}/checkpoints?limit=10&offset=0").status_code, client.get(f"/snapshots/{workflow_id}/checkpoints?limit=10&offset=0").text)

with patch("backend.services.orchestration_service.OrchestrationService.rollback_workflow", new=AsyncMock()) as mock_rb:
    mock_rb.return_value = {
        "workflow_id": workflow_id,
        "rollback_successful": True,
        "new_state": "implementation",
        "reason": "Rollback to checkpoint: test",
    }
    r4 = client.post(f"/snapshots/{workflow_id}/rollback-to-checkpoint", json={"label": "pre-release"})
    print("rollback:", r4.status_code, r4.text)
