import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_email_inbound_creates_task_for_freeform():
    from backend.services.tasks_service import get_tasks_service
    svc = get_tasks_service()
    before = len(svc.list_tasks("user-xyz"))
    payload = {
        "from": "alice@example.com",
        "user_id": "user-xyz",
        "subject": "Feature request",
        "text": "Please add a profile page"
    }
    resp = client.post("/email/inbound", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("action") == "task_added"
    after = len(svc.list_tasks("user-xyz"))
    assert after == before + 1


def test_email_inbound_saves_note_when_note_prefix():
    from backend.services.user_notes_service import get_notes_service, NoteType
    notes_svc = get_notes_service()
    # Count notes before
    before = len(notes_svc.list_notes("user-xyz", note_type=NoteType.CLARIFICATION))
    payload = {
        "from": "bob@example.com",
        "user_id": "user-xyz",
        "subject": "FYI",
        "text": "NOTE: The client prefers blue accents."
    }
    resp = client.post("/email/inbound", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("action") == "note_saved"
    after = len(notes_svc.list_notes("user-xyz", note_type=NoteType.CLARIFICATION))
    assert after == before + 1
