
def test_assistant_readiness_endpoint(test_client):
    r = test_client.get("/assistant/readiness")
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") in {"ok", "degraded"}
    # Core keys
    assert "inbox" in j and "plan_store" in j and "llm_pool" in j and "comms" in j and "flags" in j
    # Autopilot retired
    assert j.get("deprecated", {}).get("autopilot") == "retired"
    # Flags structure
    flags = j.get("flags", {})
    assert isinstance(flags.get("spool_pump_enabled"), bool)
    assert isinstance(flags.get("email_disabled"), bool)
    # Comms structure
    comms = j.get("comms", {})
    assert "email" in comms and "sms" in comms and "push" in comms
    assert isinstance(comms["email"].get("enabled"), bool)
    assert isinstance(comms["sms"].get("available"), bool)
    assert isinstance(comms["push"].get("available"), bool)
