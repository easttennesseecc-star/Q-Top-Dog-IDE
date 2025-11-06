import re
from fastapi.testclient import TestClient


def get_app():
    from backend.main import app
    return app


def test_modify_email_form_invalid_token():
    client = TestClient(get_app())
    r = client.get("/api/assistant/modify-email", params={"token": "invalid-token"})
    assert r.status_code == 400
    assert "Invalid or expired" in r.text


def test_modify_email_submit_and_approve():
    # Register a modify token to simulate clicking 'Request Changes'
    from backend.services.email_token_service import register_token
    token = register_token({
        "kind": "ui_draft_modify",
        "project_id": "test-user",
        "description": "Test draft",
    }, expires_seconds=3600)

    client = TestClient(get_app())

    # Load the modify form
    r = client.get("/api/assistant/modify-email", params={"token": token})
    assert r.status_code == 200
    assert "Request Changes" in r.text

    # Extract hidden short-lived token from the form
    m = re.search(r"name='token' value='([^']+)'", r.text)
    assert m, "short-lived token not found in form"
    short_token = m.group(1)

    # Submit changes
    r2 = client.post("/api/assistant/modify-email", data={
        "token": short_token,
        "changes": "Make primary button blue; add onboarding checklist",
    })
    assert r2.status_code == 200
    assert "Approve Revised Plan" in r2.text

    # Extract approval link and token
    m2 = re.search(r"href='([^']+/api/assistant/approve-email\?token=([^']+))'", r2.text)
    assert m2, "approve link not found"
    approve_url = m2.group(1)
    approve_token = m2.group(2)

    # Approve the revised plan
    r3 = client.get("/api/assistant/approve-email", params={"token": approve_token})
    assert r3.status_code == 200
    assert ("Revised plan approved" in r3.text) or ("Approved. Your build plan is executing now." in r3.text)
