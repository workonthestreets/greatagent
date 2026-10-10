"""Rewards logic (hub/rewards.py) against an in-memory fake of hub.db: no Postgres, no pytest, no psycopg.

    python3 tests/test_rewards.py      (or: python -m pytest -q tests/test_rewards.py)

The fake answers the `-- rewards:<name>` tagged statements rewards.py issues, with the same semantics as the SQL.
"""
from __future__ import annotations

import re
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MEDALS = [
    {"id": "first_call", "title": "First call", "description": "Your first approval or rejection on the desk.",
     "icon": "check", "metric": "decisions", "threshold": 1, "sort": 10},
    {"id": "steady_hand", "title": "Steady hand", "description": "", "icon": "check", "metric": "decisions",
     "threshold": 10, "sort": 20},
    {"id": "desk_veteran", "title": "Desk veteran", "description": "", "icon": "user", "metric": "decisions",
     "threshold": 50, "sort": 30},
    {"id": "gatekeeper", "title": "Gatekeeper", "description": "Rejected a draft and told the agent why.",
     "icon": "x", "metric": "reasoned_rejections", "threshold": 1, "sort": 40},
    {"id": "clean_desk", "title": "Clean desk", "description": "Cleared the approvals queue.", "icon": "pause",
     "metric": "queue_cleared", "threshold": 1, "sort": 50},
    {"id": "early_bird", "title": "Early bird", "description": "", "icon": "clock", "metric": "fast_decisions",
     "threshold": 5, "sort": 60},
]


class FakeDB:
    def __init__(self):
        self.actions: list[dict] = []
        self.ledger: list[dict] = []
        self.medals: dict[tuple, datetime] = {}
        self.items = {"cap": {"id": "cap", "name": "Rivet cap", "description": "", "price_coins": 60, "stock": 25, "sort": 10},
                      "hoodie": {"id": "hoodie", "name": "Rivet hoodie", "description": "", "price_coins": 160, "stock": 0,
                                 "sort": 50}}
        self.orders: list[dict] = []
        self.statements: list[str] = []
        self.in_tx = False                     # True while a pool().connection().transaction() block is open
        self.tx_statements: list[str] = []     # tags run inside a transaction

    # helpers for the tests
    def add_action(self, status="pending_approval", decided_by=None, reason=None, minutes=1):
        now = datetime.now(timezone.utc)
        a = {"id": len(self.actions) + 1, "status": status, "decided_by": decided_by,
             "result": {"reason": reason} if reason else None, "created_at": now - timedelta(minutes=minutes),
             "updated_at": now}
        self.actions.append(a)
        return a

    def decide(self, action, allow, by, reason=""):
        """What driver.confirm records before rewards run."""
        action.update(status="approved" if allow else "rejected", decided_by=by,
                      result={"reason": reason} if reason else None, updated_at=datetime.now(timezone.utc))

    def bal(self, pid):
        return sum(r["delta"] for r in self.ledger if r["profile_id"] == pid)

    # hub.db surface
    def query(self, sql, params=None):
        tag = re.match(r"\s*-- rewards:(\w+)", sql)
        assert tag, f"untagged statement: {sql[:60]}"
        name, p = tag.group(1), params or ()
        self.statements.append(name)
        if self.in_tx:
            self.tx_statements.append(name)
        if name == "lock_profile":
            return [{"id": p[0]}]
        if name == "balance":
            return [{"balance": self.bal(p[0])}]
        if name == "earned_total":
            return [{"total": sum(r["delta"] for r in self.ledger if r["profile_id"] == p[0] and r["delta"] > 0)}]
        if name == "metrics":
            mine = [a for a in self.actions if a["decided_by"] == p[0] and a["status"] in ("approved", "rejected")]
            return [{"decisions": len(mine),
                     "reasoned_rejections": sum(1 for a in mine if a["status"] == "rejected"
                                                and ((a["result"] or {}).get("reason") or "").strip()),
                     "fast_decisions": sum(1 for a in mine if a["updated_at"] - a["created_at"] <= timedelta(minutes=10))}]
        if name == "pending_count":
            return [{"n": sum(1 for a in self.actions if a["status"] == "pending_approval")}]
        if name == "medals":
            return sorted((dict(m) for m in MEDALS), key=lambda m: (m["sort"], m["id"]))
        if name == "earned_medals":
            return [{"medal_id": m, "awarded_at": t} for (pid, m), t in self.medals.items() if pid == p[0]]
        if name == "credit":
            pid, delta, reason, ref = p[:4]
            if any(r["profile_id"] == pid and r["reason"] == reason and r["ref"] == ref for r in self.ledger):
                return []
            self.ledger.append({"id": len(self.ledger) + 1, "profile_id": pid, "delta": delta, "reason": reason, "ref": ref})
            return [{"id": len(self.ledger)}]
        if name == "award_medal":
            key = (p[0], p[1])
            if key in self.medals:
                return []
            self.medals[key] = datetime.now(timezone.utc)
            return [{"medal_id": p[1]}]
        if name == "merch_item":
            it = self.items.get(p[0])
            return [{k: it[k] for k in ("id", "name", "price_coins", "stock")}] if it else []
        if name == "merch":
            return [{k: i[k] for k in ("id", "name", "description", "price_coins", "stock")}
                    for i in sorted(self.items.values(), key=lambda i: i["sort"])]
        if name == "redeem":
            item_id, pid = p[0], p[1]
            it = self.items.get(item_id)
            if not it or it["stock"] <= 0 or it["price_coins"] > self.bal(pid):
                return []
            it["stock"] -= 1
            order = {"id": len(self.orders) + 1, "profile_id": pid, "item_id": item_id, "coins": it["price_coins"]}
            self.orders.append(order)
            self.ledger.append({"id": len(self.ledger) + 1, "profile_id": pid, "delta": -it["price_coins"],
                                "reason": "redeem", "ref": f"order:{order['id']}"})
            return [{"order_id": order["id"], "item_name": it["name"]}]
        if name == "orders":
            return [{"id": o["id"], "item_id": o["item_id"], "item_name": self.items[o["item_id"]]["name"],
                     "coins": o["coins"], "status": "placed", "created_at": datetime.now(timezone.utc)}
                    for o in self.orders if o["profile_id"] == p[0]]
        raise AssertionError(f"fake DB does not know statement {name}")

    def one(self, sql, params=None):
        rows = self.query(sql, params)
        return rows[0] if rows else None


class _Cursor:
    def __init__(self, rows):
        self._rows, self.description = rows, ("row",) if rows is not None else None

    def fetchall(self):
        return list(self._rows)


class _Tx:
    """conn.transaction(): marks the fake as in a transaction; on an exception, rolls back by restoring a snapshot."""

    def __enter__(self):
        import copy
        self._snap = copy.deepcopy((FAKE.ledger, FAKE.items, FAKE.orders))
        FAKE.in_tx = True

    def __exit__(self, exc_type, *_):
        FAKE.in_tx = False
        if exc_type:
            FAKE.ledger, FAKE.items, FAKE.orders = self._snap
        return False


class _Conn:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def transaction(self):
        return _Tx()

    def execute(self, sql, params=None):
        return _Cursor(FAKE.query(sql, params))


class _Pool:
    def connection(self):
        return _Conn()


FAKE = FakeDB()
fake_mod = types.ModuleType("hub.db")
fake_mod.query = lambda sql, params=None: FAKE.query(sql, params)
fake_mod.one = lambda sql, params=None: FAKE.one(sql, params)
fake_mod.pool = lambda: _Pool()
sys.modules["hub.db"] = fake_mod   # before hub.rewards imports it; the real one needs psycopg and a database

from hub import rewards  # noqa: E402

USER = {"id": "u-iona", "role": "coordinator", "party_name": "Iona Quill, Rivet Delivery Desk",
        "display_name": "Iona Quill", "email": "coordinator@greatagent.demo"}
NAME = rewards.speaker(USER)


def _fresh() -> FakeDB:
    global FAKE
    FAKE = FakeDB()
    return FAKE


def _decide(fake, allow, reason="", pending_after=0, minutes=1):
    a = fake.add_action(minutes=minutes)
    for _ in range(pending_after):
        fake.add_action()
    fake.decide(a, allow, NAME, reason)
    return rewards.award_decision(USER, a, allow, reason)


def _ids(out):
    return {m["id"] for m in out["new_medals"]}


# ------------------------------------------------------------------ coins
def test_approve_gives_15():
    fake = _fresh()
    out = _decide(fake, True, pending_after=1)
    assert out["coins"] == 15 and out["balance"] == 15, out
    assert fake.ledger[0]["reason"] == "approve" and fake.ledger[0]["ref"] == "action:1"


def test_reject_with_reason_gives_10():
    fake = _fresh()
    out = _decide(fake, False, "wrong recipient", pending_after=1)
    assert out["coins"] == 10 and out["balance"] == 10, out
    assert fake.ledger[0]["reason"] == "reject"


def test_reject_without_reason_gives_5():
    fake = _fresh()
    out = _decide(fake, False, "   ", pending_after=1)
    assert out["coins"] == 5 and out["balance"] == 5, out


def test_same_decision_not_paid_twice():
    fake = _fresh()
    a = fake.add_action()
    fake.add_action()
    fake.decide(a, True, NAME)
    rewards.award_decision(USER, a, True)
    again = rewards.award_decision(USER, a, True)
    assert again["coins"] == 0 and again["balance"] == 15, again


# ------------------------------------------------------------------ medals
def test_first_call_awarded_once():
    fake = _fresh()
    first = _decide(fake, True, pending_after=1)
    assert "first_call" in _ids(first), first
    second = _decide(fake, True, pending_after=1)
    assert "first_call" not in _ids(second), second
    assert sum(1 for (_, m) in fake.medals if m == "first_call") == 1


def test_gatekeeper_on_reasoned_rejection_only():
    fake = _fresh()
    bare = _decide(fake, False, "", pending_after=1)
    assert "gatekeeper" not in _ids(bare), bare
    reasoned = _decide(fake, False, "the bank details changed, verify first", pending_after=1)
    assert "gatekeeper" in _ids(reasoned), reasoned
    medal = next(m for m in reasoned["new_medals"] if m["id"] == "gatekeeper")
    assert set(medal) == {"id", "title", "description", "icon"}


def test_clean_desk_when_queue_empty_after():
    fake = _fresh()
    busy = _decide(fake, True, pending_after=1)
    assert "clean_desk" not in _ids(busy), busy
    remaining = next(a for a in fake.actions if a["status"] == "pending_approval")
    fake.decide(remaining, False, NAME, "")
    last = rewards.award_decision(USER, remaining, False, "")
    assert "clean_desk" in _ids(last), last


def test_early_bird_after_five_fast_decisions():
    fake = _fresh()
    for _ in range(3):
        _decide(fake, True, pending_after=1, minutes=30)   # slow ones do not count
    outs = [_decide(fake, True, pending_after=1, minutes=2) for _ in range(5)]
    assert all("early_bird" not in _ids(o) for o in outs[:4])
    assert "early_bird" in _ids(outs[4])


def test_medal_status_progress():
    fake = _fresh()
    for _ in range(3):
        _decide(fake, True, pending_after=1)
    status = {m["id"]: m for m in rewards.medal_status(USER["id"], NAME)}
    assert status["steady_hand"]["progress"] == 3 and status["steady_hand"]["earned_at"] is None
    assert status["first_call"]["earned_at"] is not None
    assert status["clean_desk"]["progress"] == 0
    assert [m["id"] for m in rewards.medal_status(USER["id"], NAME)][0] == "first_call"


# ------------------------------------------------------------------ merch
def _expect_refusal(item_id, message):
    try:
        rewards.redeem(USER, item_id)
    except rewards.RedeemError as exc:
        assert str(exc) == message and exc.status == 409, (str(exc), exc.status)
    else:
        raise AssertionError(f"redeem {item_id} should refuse with {message!r}")


def test_redeem_refuses_when_short():
    fake = _fresh()
    fake.ledger.append({"id": 1, "profile_id": USER["id"], "delta": 50, "reason": "welcome", "ref": None})
    _expect_refusal("cap", "not enough coins")
    assert fake.items["cap"]["stock"] == 25 and not fake.orders and fake.bal(USER["id"]) == 50


def test_redeem_refuses_out_of_stock():
    fake = _fresh()
    fake.ledger.append({"id": 1, "profile_id": USER["id"], "delta": 500, "reason": "welcome", "ref": None})
    _expect_refusal("hoodie", "out of stock")
    assert not fake.orders and fake.bal(USER["id"]) == 500


def test_redeem_unknown_item_404():
    _fresh()
    try:
        rewards.redeem(USER, "yacht")
    except rewards.RedeemError as exc:
        assert exc.status == 404
    else:
        raise AssertionError("unknown item should refuse")


def test_redeem_debits_and_decrements():
    fake = _fresh()
    fake.ledger.append({"id": 1, "profile_id": USER["id"], "delta": 120, "reason": "welcome", "ref": None})
    out = rewards.redeem(USER, "cap")
    assert out == {"order_id": 1, "balance": 60, "item_name": "Rivet cap"}, out
    assert fake.items["cap"]["stock"] == 24
    assert fake.ledger[-1] == {"id": 2, "profile_id": USER["id"], "delta": -60, "reason": "redeem", "ref": "order:1"}
    me = rewards.me(USER)
    assert me["balance"] == 60 and me["earned_total"] == 120 and me["orders"][0]["item_name"] == "Rivet cap"
    assert isinstance(me["orders"][0]["created_at"], str)


def test_redeem_runs_in_one_transaction_with_profile_lock():
    fake = _fresh()
    fake.ledger.append({"id": 1, "profile_id": USER["id"], "delta": 120, "reason": "welcome", "ref": None})
    rewards.redeem(USER, "cap")
    assert fake.tx_statements[0] == "lock_profile", fake.tx_statements
    assert "redeem" in fake.tx_statements and "balance" in fake.tx_statements, fake.tx_statements
    assert "redeem" not in [s for s in fake.statements if s not in fake.tx_statements]


def test_second_redeem_refused_when_first_spent_the_coins():
    fake = _fresh()
    fake.ledger.append({"id": 1, "profile_id": USER["id"], "delta": 100, "reason": "welcome", "ref": None})
    assert rewards.redeem(USER, "cap")["balance"] == 40
    _expect_refusal("cap", "not enough coins")
    assert len(fake.orders) == 1 and fake.items["cap"]["stock"] == 24 and fake.bal(USER["id"]) == 40


def test_last_item_goes_to_one_buyer():
    fake = _fresh()
    fake.items["cap"]["stock"] = 1
    other = {**USER, "id": "u-other"}
    for pid in (USER["id"], other["id"]):
        fake.ledger.append({"id": len(fake.ledger) + 1, "profile_id": pid, "delta": 200, "reason": "welcome", "ref": None})
    rewards.redeem(other, "cap")
    _expect_refusal("cap", "out of stock")
    assert fake.items["cap"]["stock"] == 0 and len(fake.orders) == 1 and fake.bal(USER["id"]) == 200


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {name}: {exc!r}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
