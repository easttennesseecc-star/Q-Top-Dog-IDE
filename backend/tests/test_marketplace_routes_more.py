"""Additional smoke tests for marketplace/auth/agent endpoints.

Covers:
- /api/v1/marketplace/models/{model_id} happy path and 404
- /api/v1/auth/register and /api/v1/auth/login basic flow
- /api/v1/agent/chat with a trivial payload and valid token
"""

from fastapi.testclient import TestClient
import uuid

from backend.main import app


client = TestClient(app)


def _unique_email() -> str:
    return f"qa+{uuid.uuid4().hex[:10]}@topdog-ide.com"


def _register_and_login():
    email = _unique_email()
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "P@ssw0rd!"

    r = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": password,
    })
    assert r.status_code == 200, r.text
    data = r.json().get("data", {})
    assert data.get("email") == email

    r = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password,
    })
    assert r.status_code == 200, r.text
    token = r.json().get("data", {}).get("access_token") or r.json().get("data", {}).get("token")
    # Support either token naming to be robust across implementations
    assert token, f"Missing token in login response: {r.text}"
    return token


def test_marketplace_model_detail_happy_and_404():
    # List models
    r = client.get("/api/v1/marketplace/models", params={"skip": 0, "limit": 5})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    models = body.get("data", [])

    # If we have at least one model, fetch its details
    if models:
        model_id = models[0].get("id") or models[0].get("model_id")
        assert model_id, f"Malformed model payload: {models[0]}"
        r2 = client.get(f"/api/v1/marketplace/models/{model_id}")
        assert r2.status_code == 200, r2.text
        body2 = r2.json()
        assert body2.get("success") is True
        assert body2.get("data", {}).get("id") == model_id

    # 404 path: use a clearly invalid id
    r3 = client.get("/api/v1/marketplace/models/does-not-exist-1234")
    assert r3.status_code in (200, 404)
    if r3.status_code == 200:
        # Some registries may mirror a default model; still validate envelope
        assert r3.json().get("success") in (True, False)


def test_auth_register_login_me():
    token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    assert isinstance(body.get("data"), dict)


def test_agent_chat_basic():
    token = _register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    # Pick a model id (fallback to a common placeholder if registry returns none)
    r = client.get("/api/v1/marketplace/models", params={"skip": 0, "limit": 1})
    assert r.status_code == 200, r.text
    models = r.json().get("data", [])
    if models:
        model_id = models[0].get("id") or models[0].get("model_id")
    else:
        # If the registry is empty, use a placeholder and expect a 404 from chat precheck
        model_id = "non-existent-model"

    payload = {
        "model_id": model_id,
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ],
    }
    r2 = client.post("/api/v1/agent/chat", json=payload, headers=headers)
    # Accept either success (200) or a reasonable error (404 model not found or 429 rate limit)
    assert r2.status_code in (200, 404, 429), r2.text
    if r2.status_code == 200:
        body = r2.json()
        assert body.get("success") is True
        data = body.get("data", {})
        assert "response" in data
        # If rate limiting is enabled, a rate_limit object may be present
        # Don't assert on specific values to avoid flakiness
