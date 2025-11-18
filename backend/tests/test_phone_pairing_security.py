from fastapi.testclient import TestClient
from backend.main import app


def test_accept_invite_requires_correct_otp(monkeypatch):
    client = TestClient(app)

    # Send an SMS invite (in MOCK mode, always succeeds)
    payload = {
        "phone_number": "+15555550123",
        "user_id": "test-user",
        "user_name": "Tester",
    }
    r = client.post("/phone/pairing/send-sms", json=payload)
    assert r.status_code == 200, r.text
    invite = r.json()

    # Attempt to accept with wrong OTP
    bad = {
        "invite_code": invite["invite_code"],
        "device_id": "dev-otp-bad",
        "device_name": "Phone Bad",
        "device_type": "android",
        "os_version": "14",
        "app_version": "1.0.0",
        "otp_code": "000000",
    }
    r2 = client.post("/phone/pairing/accept-invite", json=bad)
    # Should be 400 invalid OTP
    assert r2.status_code == 400
    assert "Invalid OTP" in r2.text


def test_qr_pairing_otp_flag_enforced(monkeypatch):
    # Require OTP for QR pairing
    monkeypatch.setenv("PAIRING_QR_REQUIRE_OTP", "1")
    # Ensure a fresh service instance is created with the env
    from backend.services import phone_pairing_service as pps
    pps._pairing_service = None

    client = TestClient(app)

    # Generate QR
    r = client.post("/phone/pairing/generate-qr", json={"user_id": "user-qr"})
    assert r.status_code == 200, r.text
    data = r.json()

    # Try to pair without OTP -> expect failure
    pair_req = {
        "pairing_token": data["pairing_token"],
        "device_id": "qr-dev-1",
        "device_name": "QR Phone",
        "device_type": "ios",
    }
    r2 = client.post("/phone/pairing/pair", json=pair_req)
    assert r2.status_code == 400
    assert "Invalid OTP" in r2.text or "Invalid or expired" in r2.text

    # Now fetch the expected OTP from the service and succeed
    svc = pps.get_pairing_service()
    token_obj = svc.verify_pairing_token(data["pairing_token"])  # still valid
    assert token_obj is not None
    otp = token_obj.otp_code
    assert otp

    pair_req["otp_code"] = otp
    r3 = client.post("/phone/pairing/pair", json=pair_req)
    assert r3.status_code == 200, r3.text
    out = r3.json()
    assert out["device_id"] == "qr-dev-1"
    assert "jwt_token" in out
