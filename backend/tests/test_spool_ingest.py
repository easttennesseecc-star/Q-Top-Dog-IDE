import os
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

# Use the test_client fixture from backend/tests/conftest.py
import pytest


def _set_spool_dir(tmp_root: Path):
    os.environ["ASSISTANT_SPOOL_DIR"] = str(tmp_root.resolve())
    (tmp_root / "incoming").mkdir(parents=True, exist_ok=True)
    (tmp_root / "done").mkdir(parents=True, exist_ok=True)


def _clean_spool_dir(tmp_root: Path):
    if tmp_root.exists():
        shutil.rmtree(tmp_root, ignore_errors=True)


@pytest.fixture()
def spool_tmpdir(tmp_path: Path):
    root = tmp_path / "spool"
    _set_spool_dir(root)
    yield root
    _clean_spool_dir(root)


def test_spool_enqueue_and_next_via_api(spool_tmpdir: Path, test_client: TestClient):
    client = test_client
    # Enqueue SMS
    r = client.post(
        "/spool/ingest/sms",
        json={"user_id": "demo", "text": "Add OAuth to the admin panel"},
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("status") == "ok"
    assert j.get("message", {}).get("id")

    # Get next input for demo user
    r2 = client.get("/spool/next-input", params={"user_id": "demo"})
    assert r2.status_code == 200, r2.text
    j2 = r2.json()
    assert j2.get("status") == "ok"
    m = j2.get("message", {})
    assert m.get("user_id") == "demo"
    assert "OAuth" in (m.get("text") or "")


def test_spool_next_empty_returns_empty(spool_tmpdir: Path, test_client: TestClient):
    client = test_client
    r = client.get("/spool/next-input", params={"user_id": "nobody"})
    assert r.status_code == 200
    assert r.json().get("status") == "empty"


def test_spool_corrupt_file_quarantined(spool_tmpdir: Path, test_client: TestClient):
    client = test_client
    incoming = Path(os.environ["ASSISTANT_SPOOL_DIR"]) / "incoming"
    done = Path(os.environ["ASSISTANT_SPOOL_DIR"]) / "done"

    # Create corrupt file
    bad = incoming / "0001-demo-deadbeef.json"
    bad.write_text("{ not: json")

    # Attempt to fetch next input should skip corrupt and return empty
    r = client.get("/spool/next-input", params={"user_id": "demo"})
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") in ("empty", "ok")
    # If ok, it means there were other messages; still ensure corrupt was quarantined

    # Corrupt file moved to done/ with bad- prefix
    moved = list(done.glob("bad-0001-demo-deadbeef.json"))
    assert moved, f"corrupt file was not quarantined: contents={list(done.iterdir())}"
