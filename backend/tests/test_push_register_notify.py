from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_push_register_and_notify():
    # Register a dummy token
    r = client.post("/push/register", json={"user_id": "test-user", "token": "dummy-token", "platform": "web"})
    assert r.status_code == 200
    # Send a test notification (stubbed)
    r2 = client.post("/push/notify", json={"user_id": "test-user", "title": "Hello", "body": "World"})
    assert r2.status_code == 200
    assert r2.json().get("sent", 0) >= 1
