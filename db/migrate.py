"""Apply db/migrations/*.sql to DATABASE_URL and register ADMIN_EMAILS.

    python -m db.migrate            # Supabase (or any Postgres that already has the auth schema)
    python -m db.migrate --local    # plain local Postgres: creates Supabase stand-ins first
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import psycopg

from hub.config import settings

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="create auth schema/roles stand-ins (never on Supabase)")
    args = ap.parse_args()

    files = ([HERE / "local_bootstrap.sql"] if args.local else []) + sorted((HERE / "migrations").glob("*.sql"))
    with psycopg.connect(settings.database_url, autocommit=True, prepare_threshold=None) as conn:
        for f in files:
            conn.execute(f.read_text())
            print(f"applied {f.relative_to(HERE.parent)}")
        admins = [e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]
        for email in admins:
            conn.execute("insert into public.admin_emails (email) values (%s) on conflict do nothing", (email,))
            conn.execute("update public.profiles set role = 'admin' where lower(email) = %s", (email,))
        if admins:
            print(f"admins: {', '.join(admins)}")


if __name__ == "__main__":
    main()
