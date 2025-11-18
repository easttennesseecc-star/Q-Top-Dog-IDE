from backend.services.pairing_session_store import PairingSessionStore, SessionStatus
from datetime import datetime, timedelta


def test_pairing_session_create_and_accept(tmp_path):
    store = PairingSessionStore(storage_path=tmp_path)
    # Create QR session
    exp = datetime.utcnow() + timedelta(minutes=5)
    s = store.create_qr_session("u1", "tkn", exp, otp_code="123456", ip="127.0.0.1")
    assert s.session_id
    found = store.find_by_token("tkn")
    assert found is not None
    assert found.status == SessionStatus.PENDING

    # Mark scanned and accepted
    store.mark_scanned("tkn")
    store.mark_accepted("tkn", "dev1", "Pixel", "android")
    s2 = store.find_by_token("tkn")
    assert s2 is not None
    assert s2.status == SessionStatus.ACCEPTED
    assert s2.device_id == "dev1"

    # Revoke
    store.mark_revoked("dev1")
    s3 = store.find_by_token("tkn")
    assert s3 is not None
    assert s3.status == SessionStatus.REVOKED
