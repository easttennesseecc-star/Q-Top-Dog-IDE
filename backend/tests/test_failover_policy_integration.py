from importlib import reload


def test_choose_endpoint_default_off(monkeypatch):
    # Ensure the feature flag is off
    monkeypatch.delenv("FEATURE_FAILOVER_POLICY", raising=False)
    from backend.services import orchestration_service as osvc
    reload(osvc)
    svc = osvc.OrchestrationService(db=None)
    ep = svc.choose_endpoint({"task": "test"})
    assert isinstance(ep, str)
    assert ep == "primary-llm"


def test_choose_endpoint_flag_on(monkeypatch):
    monkeypatch.setenv("FEATURE_FAILOVER_POLICY", "1")
    from backend.services import orchestration_service as osvc
    reload(osvc)
    svc = osvc.OrchestrationService(db=None)
    ep = svc.choose_endpoint({"task": "test"})
    assert ep in {"primary-llm", "secondary-llm"}
    # ensure policy object exists
    assert getattr(svc, "failover_policy", None) is not None
