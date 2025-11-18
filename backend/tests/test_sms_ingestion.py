import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

@pytest.mark.parametrize("message", [
    "TODO: fix login bug",
    "add dark mode toggle",  # freeform should become a task now
])
def test_sms_webhook_ingests_tasks(message):
    from backend.services.tasks_service import get_tasks_service
    svc = get_tasks_service()
    # Count tasks before
    before = len(svc.list_tasks("+15555550123"))
    resp = client.post("/phone/sms/webhook", data={"From": "+15555550123", "Body": message})
    assert resp.status_code == 200
    # After webhook, task count should increase by 1
    after = len(svc.list_tasks("+15555550123"))
    assert after == before + 1, f"Expected one new task for message '{message}'"
    latest = svc.list_tasks("+15555550123")[0]
    # Normalize to dict in case Task instance is returned
    if hasattr(latest, "to_dict"):
        latest_dict = latest.to_dict()
    else:
        latest_dict = latest
    title_lower = latest_dict.get("title", "").lower()
    content_focus = message.split(":",1)[-1].strip()
    first_token = content_focus.split()[0][:10].lower() if content_focus else ""
    assert first_token in title_lower or message[:15].lower() in title_lower

