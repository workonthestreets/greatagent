"""HTTP layer for rewards, merch and the party actions (hub/api.py) with hub.db and hub.driver faked.

    .venv/bin/python tests/test_rewards_api.py      (or: .venv/bin/python -m pytest -q tests/test_rewards_api.py)

Needs fastapi (and httpx for TestClient), which the hub venv has. No database, no Supabase, no agent.
Auth goes through the X-Dev-User header (dev auth is switched on for the test's copy of the settings).
"""
from __future__ import annotations

import dataclasses
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from hub import api, db, driver, rewards  # noqa: E402

USERS = {
    "coord@x": {"id": "u-coord", "email": "coord@x", "display_name": "Iona Quill", "role": "coordinator",
                "party_name": "Iona Quill, Rivet Delivery Desk"},
    "admin@x": {"id": "u-admin", "email": "admin@x", "display_name": "Ada Admin", "role": "admin", "party_name": None},
    "driver@x": {"id": "u-driver", "email": "driver@x", "display_name": "Ola", "role": "driver", "party_name": "Ola, driver"},
    "merchant@x": {"id": "u-merch", "email": "merchant@x", "display_name": "Greywick", "role": "merchant",
                   "party_name": "Greywick Home"},
}
SHIPMENTS = {"S1": {"id": "S1", "case_id": "C1", "driver_name": "Ola, driver"},
             "S2": {"id": "S2", "case_id": "C2", "driver_name": "Someone else"}}
CASE_PARTIES = {("C1", "Greywick Home")}


class Fake:
    """Answers the statements api.py and rewards.py issue; records writes and wakes."""

    def __init__(self):
        self.writes: list[tuple] = []
        self.wakes: list[tuple] = []
        self.balance = 0
        self.wake_error: Exception | None = None

    def query(self, sql, params=None):
        p = params or ()
        tag = re.match(r"\s*-- rewards:(\w+)", sql)
        if tag:
            return self._rewards(tag.group(1), p)
        if "from profiles" in sql:
            u = USERS.get(p[0])
            return [u] if u else []
        if "from shipments" in sql:
            s = SHIPMENTS.get(p[0])
            return [{"id": s["id"], "case_id": s["case_id"]}] if s and s["driver_name"] == p[1] else []
        if "from case_parties" in sql:
            return [{"?column?": 1}] if (p[0], p[1]) in CASE_PARTIES else []
        self.writes.append((sql.split()[0].lower(), sql, p))
        return []

    def _rewards(self, name, p):
        if name == "credit":
            self.balance += p[1]
            return [{"id": 1}]
        if name == "balance":
            return [{"balance": self.balance}]
        if name == "metrics":
            return [{"decisions": 1, "reasoned_rejections": 0, "fast_decisions": 1}]
        if name == "pending_count":
            return [{"n": 3}]
        if name in ("medals", "earned_medals", "award_medal", "lock_profile", "redeem"):
            return [{"id": p[0]}] if name == "lock_profile" else []
        if name == "merch_item":
            return [{"id": "mug", "name": "Desk mug", "price_coins": 40, "stock": 25}] if p[0] == "mug" else []
        if name == "team":
            return [{"profile_id": "u-admin", "display_name": "Ada Admin", "role": "admin", "balance": 120,
                     "medals": 0, "decisions": 0}]
        raise AssertionError(f"fake does not know rewards:{name}")

    def one(self, sql, params=None):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def pool(self):
        fake = self

        class Conn:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def transaction(self):
                return self

            def execute(self, sql, params=None):
                rows = fake.query(sql, params)
                return type("Cur", (), {"description": ("row",), "fetchall": lambda _self: rows})()

        return type("Pool", (), {"connection": lambda _self: Conn()})()

    def wake(self, case_id, text, **_):
        if self.wake_error:
            raise self.wake_error
        self.wakes.append((case_id, text))
        return "sess-1"


FAKE = Fake()


_PATCHES = [(db, "query"), (db, "one"), (db, "pool"), (driver, "wake"), (driver, "confirm"), (api, "settings"),
            (rewards, "award_decision")]
_ORIGINALS = {(id(m), n): getattr(m, n, None) for m, n in _PATCHES}
_ORIGINAL_AWARD = rewards.award_decision


def _install():
    """Patch per test, not at import: under pytest, collection imports every test module before any test runs."""
    db.query = lambda sql, params=None: FAKE.query(sql, params)
    db.one = lambda sql, params=None: FAKE.one(sql, params)
    db.pool = lambda: FAKE.pool()
    driver.wake = lambda case_id, text, **k: FAKE.wake(case_id, text, **k)
    driver.confirm = lambda action_id, allow, by, reason="": {"action_id": action_id,
                                                              "result": "allow" if allow else "deny"}
    api.settings = dataclasses.replace(_ORIGINALS[(id(api), "settings")], dev_auth=True)
    rewards.award_decision = _ORIGINAL_AWARD


def teardown_module(_module=None):
    for m, n in _PATCHES:
        setattr(m, n, _ORIGINALS[(id(m), n)])


app = FastAPI()
app.include_router(api.router)
client = TestClient(app, raise_server_exceptions=False)


def _h(email):
    return {"X-Dev-User": email}


def _fresh() -> Fake:
    global FAKE
    FAKE = Fake()
    _install()
    return FAKE


# ------------------------------------------------------------------ decisions
def test_approve_returns_rewards_15():
    _fresh()
    r = client.post("/api/actions/5/approve", json={}, headers=_h("coord@x"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["rewards"]["coins"] == 15 and body["rewards"]["balance"] == 15, body
    assert body["rewards"]["new_medals"] == [] and body["action_id"] == 5


def test_approve_with_failing_rewards_still_200():
    _fresh()

    def boom(*_a, **_k):
        raise RuntimeError("db down")
    rewards.award_decision = boom
    try:
        r = client.post("/api/actions/6/approve", json={}, headers=_h("coord@x"))
    finally:
        rewards.award_decision = _ORIGINAL_AWARD
    assert r.status_code == 200, r.text
    assert r.json()["rewards"] is None and r.json()["result"] == "allow"


# ------------------------------------------------------------------ rewards and merch
def test_team_forbidden_for_coordinator():
    _fresh()
    assert client.get("/api/rewards/team", headers=_h("coord@x")).status_code == 403


def test_team_ok_for_admin():
    _fresh()
    r = client.get("/api/rewards/team", headers=_h("admin@x"))
    assert r.status_code == 200 and r.json()[0]["profile_id"] == "u-admin", r.text


def test_redeem_409_when_short():
    _fresh()
    r = client.post("/api/merch/mug/redeem", headers=_h("coord@x"))
    assert r.status_code == 409 and r.json()["detail"] == "not enough coins", r.text


def test_redeem_404_unknown_item():
    _fresh()
    assert client.post("/api/merch/yacht/redeem", headers=_h("coord@x")).status_code == 404


# ------------------------------------------------------------------ driver status
def test_driver_status_ok():
    fake = _fresh()
    r = client.post("/api/shipments/S1/status", json={"status": "delivered", "note": "left with neighbour"},
                    headers=_h("driver@x"))
    assert r.status_code == 200, r.text
    assert r.json() == {"ok": True, "status": "delivered", "woken": True}
    assert [w[0] for w in fake.writes] == ["update", "insert"], fake.writes
    assert fake.wakes and fake.wakes[0][0] == "C1" and "Delivered. left with neighbour" in fake.wakes[0][1]


def test_driver_wrong_status_422():
    fake = _fresh()
    r = client.post("/api/shipments/S1/status", json={"status": "collected"}, headers=_h("driver@x"))
    assert r.status_code == 422 and not fake.writes, r.text


def test_driver_someone_elses_shipment_404():
    fake = _fresh()
    r = client.post("/api/shipments/S2/status", json={"status": "delivered"}, headers=_h("driver@x"))
    assert r.status_code == 404 and not fake.writes, r.text


def test_merchant_cannot_set_shipment_status_403():
    _fresh()
    r = client.post("/api/shipments/S1/status", json={"status": "delivered"}, headers=_h("merchant@x"))
    assert r.status_code == 403, r.text


# ------------------------------------------------------------------ merchant decision
def test_merchant_decision_ok():
    fake = _fresh()
    r = client.post("/api/cases/C1/merchant_decision", json={"decision": "approve_refund", "note": "sorry"},
                    headers=_h("merchant@x"))
    assert r.status_code == 200 and r.json() == {"ok": True, "woken": True}, r.text
    assert fake.writes[0][0] == "insert" and "Merchant decision: Approve refund. sorry" in fake.writes[0][2]


def test_merchant_decision_404_on_unseen_case():
    _fresh()
    r = client.post("/api/cases/C2/merchant_decision", json={"decision": "decline"}, headers=_h("merchant@x"))
    assert r.status_code == 404, r.text


# ------------------------------------------------------------------ failed wake
def test_failing_wake_still_200_status():
    fake = _fresh()
    fake.wake_error = RuntimeError("agent unreachable")
    r = client.post("/api/shipments/S1/status", json={"status": "out_for_delivery"}, headers=_h("driver@x"))
    assert r.status_code == 200 and r.json() == {"ok": True, "status": "out_for_delivery", "woken": False}, r.text
    assert [w[0] for w in fake.writes] == ["update", "insert"], "status and case event must be saved before the wake"


def test_failing_wake_still_200_merchant():
    fake = _fresh()
    fake.wake_error = RuntimeError("agent unreachable")
    r = client.post("/api/cases/C1/merchant_decision", json={"decision": "decline"}, headers=_h("merchant@x"))
    assert r.status_code == 200 and r.json() == {"ok": True, "woken": False}, r.text
    assert fake.writes and fake.writes[0][0] == "insert"


def test_failing_wake_post_message_keeps_shape():
    fake = _fresh()
    fake.wake_error = RuntimeError("agent unreachable")
    r = client.post("/api/cases/C1/messages", json={"body": "where is it?"}, headers=_h("merchant@x"))
    assert r.status_code == 200 and r.json() == {"ok": True, "session_id": None}, r.text


if __name__ == "__main__":
    import logging
    logging.disable(logging.CRITICAL)   # the failure paths log tracebacks on purpose
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {exc!r}")
    teardown_module()
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
