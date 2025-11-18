"""Smoke tests for marketplace FastAPI routes.

These tests verify that the marketplace router is mounted and basic
endpoints respond as expected (shape only, not full semantics).
"""

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_marketplace_models_lists_ok():
    resp = client.get("/api/v1/marketplace/models", params={"skip": 0, "limit": 1})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, dict)
    # We expect standard response envelope
    assert body.get("success") is True
    assert "data" in body
    assert "pagination" in body


def test_marketplace_stats_ok():
    resp = client.get("/api/v1/marketplace/stats")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("success") is True
    assert isinstance(body.get("data"), dict)
