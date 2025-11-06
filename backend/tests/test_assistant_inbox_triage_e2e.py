from starlette.testclient import TestClient
from backend.main import app


client = TestClient(app)


def test_triage_executes_plan_from_imperative():
    # Add an imperative message that should normalize to PLAN and execute
    r = client.post(
        "/assistant-inbox/add",
        json={"user_id": "e2e-user", "source": "api", "text": "add a healthcheck endpoint"},
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"

    r2 = client.post("/assistant-inbox/triage", json={"user_id": "e2e-user", "limit": 10})
    assert r2.status_code == 200
    t = r2.json()
    assert t.get("status") == "ok"
    assert t.get("processed", 0) >= 1
    assert t.get("acted", 0) >= 1
    executed = [x for x in (t.get("results") or []) if x.get("action") == "executed"]
    assert executed, f"Expected at least one executed action, got: {t}"
    # Optional: ensure normalization inserted PLAN prefix
    assert any((x.get("norm") or "").startswith("PLAN:") for x in executed)


def test_triage_marks_notes_when_not_actionable():
    r = client.post(
        "/assistant-inbox/add",
        json={"user_id": "e2e-user", "source": "api", "text": "Note: just info for later"},
    )
    assert r.status_code == 200

    r2 = client.post("/assistant-inbox/triage", json={"user_id": "e2e-user", "limit": 10})
    assert r2.status_code == 200
    t = r2.json()
    assert t.get("status") == "ok"
    # Either acted or noted, but ensure at least one noted
    noted = [x for x in (t.get("results") or []) if x.get("action") == "noted"]
    assert noted or t.get("notes", 0) >= 1
