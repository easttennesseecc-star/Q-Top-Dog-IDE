from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def _trial_body():
    return {
        "title": "T",
        "population_size": 10,
        "duration_days": 7,
        "arms": [
            {"name": "c", "size": 5, "effect_mean": 0, "effect_std": 1},
            {"name": "t", "size": 5, "effect_mean": 0.5, "effect_std": 1},
        ],
    }


def test_compliance_blocks_medical_without_tier():
    r = client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={"X-Workspace-Profile": "medical"},
    )
    assert r.status_code == 401, r.text


def test_compliance_allows_medical_with_enterprise_standard():
    r = client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={
            "X-Workspace-Profile": "medical",
            "X-User-Tier": "enterprise_standard",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "ok"


def test_health_excluded_from_compliance():
    r = client.get("/health", headers={"X-Workspace-Profile": "medical"})
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
