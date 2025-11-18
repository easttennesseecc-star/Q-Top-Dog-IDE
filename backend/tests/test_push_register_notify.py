
def test_push_register_and_notify(test_client):
    # Register a dummy token
    r = test_client.post("/push/register", json={"user_id": "test-user", "token": "dummy-token", "platform": "web"})
    assert r.status_code == 200
    # Send a test notification (stubbed)
    r2 = test_client.post("/push/notify", json={"user_id": "test-user", "title": "Hello", "body": "World"})
    assert r2.status_code == 200
    assert r2.json().get("sent", 0) >= 1
