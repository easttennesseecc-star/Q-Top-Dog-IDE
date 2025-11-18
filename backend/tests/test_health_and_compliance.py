
def test_health_ok(test_client):
    r = test_client.get("/health")
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


def test_compliance_blocks_medical_without_tier(test_client):
    # Expect 401 when medical profile provided without tier
    r = test_client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={"X-Workspace-Profile": "medical"},
    )
    assert r.status_code == 401, r.text

def test_compliance_allows_medical_with_enterprise_tier(test_client):
    # Provide enterprise tier to satisfy all medical requirements; should return 200
    r = test_client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={"X-Workspace-Profile": "medical", "X-User-Tier": "enterprise_standard"},
    )
    assert r.status_code == 200, r.text

def test_compliance_bypass_header(test_client):
    # Explicit bypass header should allow even without tier
    r = test_client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={"X-Workspace-Profile": "medical", "X-Compliance-Bypass": "true"},
    )
    assert r.status_code == 200, r.text


def test_compliance_allows_medical_with_enterprise_standard(test_client):
    r = test_client.post(
        "/med/trials/simulate",
        json=_trial_body(),
        headers={
            "X-Workspace-Profile": "medical",
            "X-User-Tier": "enterprise_standard",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json().get("status") == "ok"


def test_health_excluded_from_compliance(test_client):
    r = test_client.get("/health", headers={"X-Workspace-Profile": "medical"})
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
