from backend.services.formal_verification import FormalVerificationService


def test_modus_ponens_proves_goal():
    svc = FormalVerificationService()
    trace = {
        "assumptions": ["A", "A->B"],
        "goals": ["B"],
        "steps": [
            {"rule": "assume", "out": "A"},
            {"rule": "assume", "out": "A->B"},
            {"rule": "modus_ponens", "in": ["A", "A->B"], "out": "B"},
        ],
    }
    res = svc.verify(trace)
    assert res.ok
    assert "b" in res.proved
    assert res.missing_goals == []


def test_transitivity_builds_implication():
    svc = FormalVerificationService()
    trace = {
        "assumptions": ["A->B", "B->C"],
        "goals": ["A->C"],
        "steps": [
            {"rule": "assume", "out": "A->B"},
            {"rule": "assume", "out": "B->C"},
            {"rule": "transitivity", "in": ["A->B", "B->C"], "out": "A->C"},
        ],
    }
    res = svc.verify(trace)
    assert res.ok
    assert "a->c" in res.proved
