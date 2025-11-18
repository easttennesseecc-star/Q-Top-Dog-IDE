from fastapi.testclient import TestClient
import pytest
pytestmark = pytest.mark.skip(reason="Auto task creation via inbox deprecated; feature will migrate to spool if needed.")


def test_auto_task_creation_from_inbox(test_client: TestClient):
    client = test_client
    u = "auto-user"

    # Add actionable and non-actionable messages
    r1 = client.post("/assistant-inbox/add", json={"user_id": u, "source": "sms", "text": "add login form"})
    assert r1.status_code == 200 and r1.json().get("status") == "ok"

    r2 = client.post("/assistant-inbox/add", json={"user_id": u, "source": "email", "text": "Note: backlog triage next week"})
    assert r2.status_code == 200 and r2.json().get("status") == "ok"

    # List tasks; only actionable should appear
    rt = client.get("/tasks/list", params={"user_id": u, "include_completed": True})
    assert rt.status_code == 200
    tasks = rt.json().get("tasks", [])
    titles = [t.get("title") for t in tasks]
    assert any("add login form" in (t or "") for t in titles)
    assert not any("backlog triage next week" in (t or "") for t in titles)

    # Check metadata linkage
    actionable = next(t for t in tasks if "add login form" in t.get("title", ""))
    assert actionable.get("metadata", {}).get("inbox_id")
