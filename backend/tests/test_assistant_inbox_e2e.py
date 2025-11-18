from fastapi.testclient import TestClient
import pytest
pytestmark = pytest.mark.skip(reason="Assistant inbox deprecated in favor of spool ingestion.")

# Note: Triage endpoints have been removed. These tests validate inbox add/list only.


def _get_messages(test_client: TestClient, user_id: str, limit: int = 50, include_consumed: bool = False) -> list[dict]:
    r = test_client.get(
        "/assistant-inbox/list",
        params={"user_id": user_id, "limit": limit, "include_consumed": str(include_consumed).lower()},
    )
    assert r.status_code == 200, f"List failed: {r.status_code} {r.text}"
    return r.json().get("messages", [])


def test_inbox_add_and_list_without_triage(test_client: TestClient):
    # Use the standard test client (lifespan-enabled, loops disabled by tests conftest)
    

    # Add an imperative message (we're not triaging in this test)
    r = test_client.post(
        "/assistant-inbox/add",
        json={"user_id": "e2e-user", "source": "api", "text": "add a healthcheck endpoint"},
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"

    # List messages and assert the message is present
    msgs = _get_messages(test_client, user_id="e2e-user", limit=10)
    assert any("healthcheck endpoint" in (m.get("text") or "").lower() for m in msgs)


def test_inbox_add_note_without_triage(test_client: TestClient):
    r = test_client.post(
        "/assistant-inbox/add",
        json={"user_id": "e2e-user", "source": "api", "text": "Note: just info for later"},
    )
    assert r.status_code == 200

    # List messages and ensure the note-like message is in the inbox
    msgs = _get_messages(test_client, user_id="e2e-user", limit=10)
    assert any("just info for later" in (m.get("text") or "").lower() for m in msgs)
