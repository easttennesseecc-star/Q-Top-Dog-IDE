import os
import sqlite3
from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.ai_auth_service import auth_service
from backend.database.tier_schema import MembershipTierSchema


DB_PATH = MembershipTierSchema.get_db_path()


def _db():
    return sqlite3.connect(DB_PATH)


def seed_tiers_and_sub(user_id: str, tier_id: str = "test_pro", daily_limit: int = 5):
    MembershipTierSchema.setup_all_tables()
    con = _db()
    cur = con.cursor()
    # Upsert membership tier
    cur.execute(
        """
        INSERT INTO membership_tiers (tier_id, name, price, daily_call_limit, daily_llm_requests)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(tier_id) DO UPDATE SET
            daily_call_limit=excluded.daily_call_limit,
            daily_llm_requests=excluded.daily_llm_requests
        """,
        (tier_id, tier_id.upper(), 0, daily_limit, daily_limit),
    )
    # Upsert subscription for user
    cur.execute(
        """
        INSERT INTO user_subscriptions (user_id, tier_id, is_active)
        VALUES (?, ?, 1)
        ON CONFLICT(user_id) DO UPDATE SET tier_id=excluded.tier_id, is_active=1
        """,
        (user_id, tier_id),
    )
    con.commit()
    con.close()


def set_usage(user_id: str, used: int):
    con = _db()
    cur = con.cursor()
    today = date.today().isoformat()
    cur.execute(
        """
        INSERT INTO daily_usage_tracking (user_id, usage_date, api_calls_used)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, usage_date) DO UPDATE SET api_calls_used=excluded.api_calls_used
        """,
        (user_id, today, used),
    )
    con.commit()
    con.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_token():
    # Register and login a new user
    email = "tier@test.com"
    auth_service.register_user(email, "tiertester", "password123")
    ok, _, token = auth_service.login_user(email, "password123")
    assert ok and token
    return token.token


def test_tier_limits_ok(client, user_token):
    # Seed tier with limit 20 and no usage => no warning
    ok, user_id = auth_service.verify_token(user_token)
    assert ok
    seed_tiers_and_sub(user_id, daily_limit=20)
    set_usage(user_id, 0)

    r = client.get("/api/tier/limits", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 200
    payload = r.json()
    assert payload["success"] is True
    assert payload["data"]["limit"] == 20
    assert payload["data"]["remaining"] == 20
    assert payload["data"]["soft_warning"] is False


def test_tier_limits_soft_warning(client, user_token, monkeypatch):
    # Soft warning when remaining < pct (default 10%)
    ok, user_id = auth_service.verify_token(user_token)
    assert ok
    seed_tiers_and_sub(user_id, daily_limit=20)
    set_usage(user_id, 19)  # remaining=1 => 5% => warning

    r = client.get("/api/tier/limits", headers={"Authorization": f"Bearer {user_token}"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["remaining"] == 1
    assert data["soft_warning"] is True


def test_chat_rate_limit_429(client, user_token):
    ok, user_id = auth_service.verify_token(user_token)
    assert ok
    # daily limit 1, set used=1 to force exceed
    seed_tiers_and_sub(user_id, daily_limit=1)
    set_usage(user_id, 1)

    body = {"model_id": "gpt4-turbo", "messages": [{"role": "user", "content": "hi"}]}
    r = client.post("/api/v1/agent/chat", headers={"Authorization": f"Bearer {user_token}"}, json=body)
    assert r.status_code == 429
    j = r.json()
    assert j["success"] is False
    assert j["error"]
    assert j["remaining"] == 0


def test_recs_rate_limit_429(client, user_token):
    ok, user_id = auth_service.verify_token(user_token)
    assert ok
    # daily limit 1, set used=1 to force exceed
    seed_tiers_and_sub(user_id, daily_limit=1)
    set_usage(user_id, 1)

    r = client.post(
        "/api/v1/marketplace/recommendations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"query": "Generate Python function", "budget": "medium"},
    )
    assert r.status_code == 429
    j = r.json()
    assert j["success"] is False
    assert j["error"]
    assert j["remaining"] == 0
