import pytest
pytestmark = pytest.mark.skip(reason="Assistant inbox admin ops deprecated; spool ingestion active.")
from fastapi.testclient import TestClient


def _add(client: TestClient, user: str, text: str, source: str = "api") -> str:
    r = client.post("/assistant-inbox/add", json={"user_id": user, "source": source, "text": text})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("status") == "ok"
    mid = j["message"]["id"]
    assert mid
    return mid


def _list(client: TestClient, user: str, include_consumed: bool = False) -> list[dict]:
    r = client.get("/assistant-inbox/list", params={"user_id": user, "limit": 100, "include_consumed": str(include_consumed).lower()})
    assert r.status_code == 200
    return r.json().get("messages", [])


def test_delete_single_message(test_client: TestClient):
    client = test_client
    uid = "ops-user"
    mid1 = _add(client, uid, "first message")
    mid2 = _add(client, uid, "second message")
    before = _list(client, uid)
    assert len(before) == 2

    # Delete one
    r = client.delete(f"/assistant-inbox/delete/{mid1}")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

    after = _list(client, uid)
    ids = {m["id"] for m in after}
    assert mid1 not in ids and mid2 in ids

    # Delete again should return not_found
    r2 = client.delete(f"/assistant-inbox/delete/{mid1}")
    assert r2.status_code == 200
    assert r2.json().get("status") == "error"


def test_clear_scoped_user(test_client: TestClient):
    client = test_client
    uidA = "userA"
    uidB = "userB"
    for i in range(3):
        _add(client, uidA, f"A msg {i}")
    for i in range(2):
        _add(client, uidB, f"B msg {i}")

    listA = _list(client, uidA)
    listB = _list(client, uidB)
    assert len(listA) == 3
    assert len(listB) == 2

    # Clear only userA
    r = client.post("/assistant-inbox/clear", json={"user_id": uidA})
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"
    assert j.get("removed") == 3
    assert j.get("scoped") is True

    listA_after = _list(client, uidA)
    listB_after = _list(client, uidB)
    assert len(listA_after) == 0
    assert len(listB_after) == 2


def test_clear_global(test_client: TestClient):
    client = test_client
    uidA = "globalA"
    uidB = "globalB"
    _add(client, uidA, "ga1")
    _add(client, uidB, "gb1")

    # Global clear
    r = client.post("/assistant-inbox/clear", json={})
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"
    assert j.get("removed") >= 2  # At least the two we added
    assert j.get("scoped") is False

    assert _list(client, uidA) == []
    assert _list(client, uidB) == []
