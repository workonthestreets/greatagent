"""Coins and medals for desk staff, and the merch shop. Tables: db/migrations/002_rewards.sql.

Coins: approve +15, reject with a reason +10, reject without one +5, redeem -price, welcome +120 (seed).
Medals are computed from the actions table (decided_by holds the speaker name) and awarded once.
Every statement starts with a `-- rewards:<name>` tag; tests/test_rewards.py fakes the DB by those tags.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

from . import db

APPROVE_COINS = 15
REJECT_REASONED_COINS = 10
REJECT_BARE_COINS = 5
WELCOME_COINS = 120   # credited by db/seed_rewards.py


class RedeemError(Exception):
    """A redemption the shop refuses. `status` is the HTTP status the API should answer with."""

    def __init__(self, message: str, status: int = 409):
        super().__init__(message)
        self.status = status


def speaker(user: dict) -> str:
    """The name decisions are recorded under (same rule as hub.api._speaker)."""
    return user.get("party_name") or user.get("display_name") or user.get("email")


def _iso(value) -> Optional[str]:
    return value.isoformat() if hasattr(value, "isoformat") else value


def _medal_out(m: dict) -> dict:
    return {k: m[k] for k in ("id", "title", "description", "icon")}


# ------------------------------------------------------------------ reads
def balance(profile_id) -> int:
    row = db.one("-- rewards:balance\nselect coalesce(sum(delta), 0)::int as balance from coin_ledger where profile_id = %s",
                 (profile_id,))
    return int(row["balance"]) if row else 0


def earned_total(profile_id) -> int:
    row = db.one("-- rewards:earned_total\nselect coalesce(sum(delta), 0)::int as total from coin_ledger "
                 "where profile_id = %s and delta > 0", (profile_id,))
    return int(row["total"]) if row else 0


def _metrics(name: str) -> dict:
    row = db.one(
        """-- rewards:metrics
           select count(*)::int as decisions,
                  count(*) filter (where status = 'rejected'
                                   and coalesce(btrim(result->>'reason'), '') <> '')::int as reasoned_rejections,
                  count(*) filter (where updated_at - created_at <= interval '10 minutes')::int as fast_decisions
           from actions where decided_by = %s and status in ('approved', 'rejected')""", (name,))
    return {k: int((row or {}).get(k) or 0) for k in ("decisions", "reasoned_rejections", "fast_decisions")}


def _queue_empty() -> bool:
    row = db.one("-- rewards:pending_count\nselect count(*)::int as n from actions where status = 'pending_approval'")
    return not row or int(row["n"]) == 0


def _catalogue() -> list[dict]:
    return db.query("-- rewards:medals\nselect id, title, description, icon, metric, threshold, sort from medals order by sort, id")


def _earned(profile_id) -> dict:
    rows = db.query("-- rewards:earned_medals\nselect medal_id, awarded_at from profile_medals where profile_id = %s",
                    (profile_id,))
    return {r["medal_id"]: r["awarded_at"] for r in rows}


def medal_status(profile_id, name: str) -> list[dict]:
    """Every medal with the user's progress and when it was earned (None if not yet)."""
    metrics, earned = _metrics(name), _earned(profile_id)
    out = []
    for m in _catalogue():
        got = m["id"] in earned
        if m["metric"] == "queue_cleared":
            progress = m["threshold"] if got else 0
        else:
            progress = metrics.get(m["metric"], 0)
        out.append({**_medal_out(m), "threshold": m["threshold"], "metric": m["metric"],
                    "progress": progress, "earned_at": _iso(earned.get(m["id"]))})
    return out


def orders(profile_id) -> list[dict]:
    rows = db.query(
        """-- rewards:orders
           select o.id, o.item_id, i.name as item_name, o.coins, o.status, o.created_at
           from merch_orders o join merch_items i on i.id = o.item_id
           where o.profile_id = %s order by o.created_at desc, o.id desc""", (profile_id,))
    return [{**r, "created_at": _iso(r["created_at"])} for r in rows]


def me(user: dict) -> dict:
    pid = user["id"]
    return {"balance": balance(pid), "earned_total": earned_total(pid),
            "medals": medal_status(pid, speaker(user)), "orders": orders(pid)}


def team() -> list[dict]:
    """Leaderboard of every staff account, richest first."""
    rows = db.query(
        """-- rewards:team
           select p.id as profile_id, p.display_name, p.role,
                  coalesce((select sum(l.delta) from coin_ledger l where l.profile_id = p.id), 0)::int as balance,
                  (select count(*) from profile_medals pm where pm.profile_id = p.id)::int as medals,
                  (select count(*) from actions a
                    where a.decided_by = coalesce(p.party_name, p.display_name, p.email)
                      and a.status in ('approved', 'rejected'))::int as decisions
           from profiles p where p.role in ('admin', 'coordinator')
           order by balance desc, p.display_name""")
    return [{**r, "profile_id": str(r["profile_id"])} for r in rows]


def merch() -> list[dict]:
    return db.query("-- rewards:merch\nselect id, name, description, price_coins, stock from merch_items order by sort, id")


# ------------------------------------------------------------------ writes
def _credit(profile_id, delta: int, reason: str, ref: Optional[str]) -> bool:
    """Add a ledger row unless one with the same reason and ref exists. Returns True if it was added."""
    row = db.one(
        """-- rewards:credit
           insert into coin_ledger (profile_id, delta, reason, ref)
           select %s, %s, %s, %s
           where not exists (select 1 from coin_ledger where profile_id = %s and reason = %s and ref is not distinct from %s)
           returning id""", (profile_id, delta, reason, ref, profile_id, reason, ref))
    return row is not None


def _award(profile_id, medal_id: str) -> bool:
    row = db.one(
        """-- rewards:award_medal
           insert into profile_medals (profile_id, medal_id) values (%s, %s)
           on conflict (profile_id, medal_id) do nothing returning medal_id""", (profile_id, medal_id))
    return row is not None


def decision_coins(allow: bool, reason: str) -> int:
    if allow:
        return APPROVE_COINS
    return REJECT_REASONED_COINS if (reason or "").strip() else REJECT_BARE_COINS


def award_decision(user: dict, action_row: dict, allow: bool, reason: str = "") -> dict:
    """Coins and any new medals for one approve/reject that has already been recorded on the action."""
    pid = user["id"]
    coins = decision_coins(allow, reason)
    if not _credit(pid, coins, "approve" if allow else "reject", f"action:{action_row['id']}"):
        coins = 0   # this decision was already paid
    metrics = _metrics(speaker(user))
    metrics["queue_cleared"] = 1 if _queue_empty() else 0
    earned = _earned(pid)
    new = [_medal_out(m) for m in _catalogue()
           if m["id"] not in earned and metrics.get(m["metric"], 0) >= m["threshold"] and _award(pid, m["id"])]
    return {"coins": coins, "balance": balance(pid), "new_medals": new}


_ITEM_SQL = "-- rewards:merch_item\nselect id, name, price_coins, stock from merch_items where id = %s"


@contextmanager
def _transaction():
    """One transaction on one pooled connection; yields run(sql, params) -> rows."""
    with db.pool().connection() as conn:
        with conn.transaction():
            def run(sql: str, params=None) -> list[dict]:
                cur = conn.execute(sql, params)
                return cur.fetchall() if cur.description else []
            yield run


# The debit is conditional: the stock decrement only happens while stock > 0 and the price is covered by the
# balance (sum of the profile's ledger deltas); the order and the ledger row are inserted only from that update.
# Zero rows back means nothing was written.
_REDEEM_SQL = """-- rewards:redeem
   with item as (
     update merch_items set stock = stock - 1
     where id = %s and stock > 0
       and price_coins <= (select coalesce(sum(delta), 0) from coin_ledger where profile_id = %s)
     returning id, name, price_coins
   ), ord as (
     insert into merch_orders (profile_id, item_id, coins)
     select %s, id, price_coins from item returning id, coins
   ), debit as (
     insert into coin_ledger (profile_id, delta, reason, ref)
     select %s, -coins, 'redeem', 'order:' || id from ord returning id
   )
   select ord.id as order_id, item.name as item_name from ord, item"""


def redeem(user: dict, item_id: str) -> dict:
    """Buy one merch item with coins: order, ledger debit and stock decrement, atomically.

    The profile row is locked first (FOR NO KEY UPDATE), so two redeems by the same person run one after the
    other and the second one's balance check (a fresh statement under read committed) sees the first's debit.
    Two people racing for the last item are settled by the row lock on merch_items and the `stock > 0` re-check.
    """
    pid = user["id"]
    with _transaction() as run:
        run("-- rewards:lock_profile\nselect id from profiles where id = %s for no key update", (pid,))
        if not run(_ITEM_SQL, (item_id,)):
            raise RedeemError("item not found", 404)
        written = run(_REDEEM_SQL, (item_id, pid, pid, pid))
        if not written:   # zero rows affected: nothing was written; re-read the stock to say why
            fresh = run(_ITEM_SQL, (item_id,))
            raise RedeemError("out of stock" if not fresh or fresh[0]["stock"] <= 0 else "not enough coins")
        row = written[0]
        bal = run("-- rewards:balance\nselect coalesce(sum(delta), 0)::int as balance from coin_ledger where profile_id = %s",
                  (pid,))
    return {"order_id": row["order_id"], "balance": int(bal[0]["balance"]) if bal else 0, "item_name": row["item_name"]}
