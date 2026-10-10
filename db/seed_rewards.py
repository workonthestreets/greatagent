"""Give every staff account (admin, coordinator) its one-off +120 welcome coins. Safe on the live database:
idempotent (skips profiles that already have a `welcome` ledger row) and touches nothing but coin_ledger.

    python -m db.seed_rewards       # after `python -m db.migrate` has applied 002_rewards.sql

db.seed and db.seed_demo call welcome_staff() too.
"""
from __future__ import annotations

import psycopg

from hub.config import settings

WELCOME_COINS = 120   # keep in step with hub.rewards.WELCOME_COINS


def welcome_staff(conn: psycopg.Connection) -> int:
    """Credit the welcome coins to staff profiles that have none yet. Returns how many were credited."""
    if conn.execute("select to_regclass('public.coin_ledger')").fetchone()[0] is None:
        print("coin_ledger missing: apply db/migrations/002_rewards.sql (python -m db.migrate) for welcome coins")
        return 0
    rows = conn.execute(
        """insert into coin_ledger (profile_id, delta, reason)
           select p.id, %s, 'welcome' from profiles p
           where p.role in ('admin', 'coordinator')
             and not exists (select 1 from coin_ledger l where l.profile_id = p.id and l.reason = 'welcome')
           returning profile_id""", (WELCOME_COINS,)).fetchall()
    return len(rows)


def main() -> None:
    with psycopg.connect(settings.database_url, autocommit=True, prepare_threshold=None) as conn:
        n = welcome_staff(conn)
    print(f"welcome coins: credited {n} staff profile(s) with +{WELCOME_COINS}")


if __name__ == "__main__":
    main()
