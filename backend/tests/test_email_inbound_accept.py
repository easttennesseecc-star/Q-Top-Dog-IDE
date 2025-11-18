import json
from starlette.testclient import TestClient
from backend.main import app
from backend.services.email_token_service import register_token

def test_email_inbound_accept_ui_draft(test_client):
    token = register_token({
        "kind": "ui_draft_approval",
        "project_id": "test-user",
        "description": "Test draft",
    }, expires_seconds=3600)
    payload = {
        "from": "user@example.com",
        "subject": "Re: UI Draft",
        "text": f"ACCEPT {token}"
    }
    resp = test_client.post("/email/inbound", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("action") == "approved"
