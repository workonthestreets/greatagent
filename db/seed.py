"""Seed the DB from the public Delivery & Logistics cases, cut at the escalation point, plus demo accounts.

    python -m db.seed --reset                 # wipe domain tables, load all cases, create demo accounts
    python -m db.seed --reset --limit 10      # fewer cases
    python -m db.seed --local                 # local Postgres: create demo users directly in auth.users

Demo accounts (password DEMO_PASSWORD, default "greatagent-demo") are linked to the party that
appears in the most cases for each role, so every role has something to look at.
"""
from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import httpx
import psycopg
from psycopg.types.json import Jsonb

from db.seed_rewards import welcome_staff
from deskagent.loader import discover_cases, load_case, split_sections
from hub.config import ROOT, settings

DEFAULT_CASES = ROOT.parent / "HackatonPublicCases" / "Delivery & Logistics"
DETAIL_LINE = re.compile(r"^- \*\*(?P<k>[^:*]+):\*\*\s*(?P<v>.+)$", re.M)


def party_role(party: str) -> str:
    p = party.lower()
    if "rivet delivery desk" in p:
        return "coordinator"
    if re.search(r"\b(driver|crew|courier|rider)\b", p):
        return "driver"
    if re.search(r"\b(depot|pickup|locker|warehouse|hub|dock|counter)\b", p):
        return "depot"
    if re.search(r"\b(recipient|customer|resident|household|sender|neighbou?r)\b", p):
        return "customer"
    return "merchant"   # merchants, carriers, brokers, billing and specialist teams


def parse_ts(ts: str) -> datetime:
    try:
        return datetime.strptime(ts.replace(" UTC", "").strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.now(timezone.utc)


def event_kind(channel: str) -> tuple[str, str]:
    c = channel.lower()
    if "note" in c or "internal" in c:
        return "note", "staff"
    if "call" in c or "phone" in c or "voice" in c:
        return "call", "all"
    return "message", "all"


def load_cases(conn: psycopg.Connection, cases_dir: Path, limit: int) -> Counter:
    party_counts: Counter = Counter()
    paths = discover_cases(cases_dir)[:limit] if limit else discover_cases(cases_dir)
    for path in paths:
        case = load_case(path, public_cutoff=True, media=False)
        index = dict(case.files).get("index.md", "")
        details = {m.group("k").strip().lower(): m.group("v").strip() for m in DETAIL_LINE.finditer(index)}
        sections = {name.lower(): body.strip() for name, body in split_sections(index)}
        source = details.get("source role", "")
        shipment = details.get("primary shipment", "").split()[0].strip(",;") if details.get("primary shipment") else None
        created = parse_ts(details.get("created", case.now))
        conn.execute(
            """insert into cases (id, title, track, status, source_name, source_role, coordinator, shipment_id,
                                  context, initial_request, created_at, updated_at)
               values (%s, %s, %s, 'open', %s, %s, %s, %s, %s, %s, %s, %s)""",
            (case.case_id, case.title, case.track or "Delivery & Logistics", source.split(",")[0].strip(),
             party_role(source) if source else None, details.get("coordinator"), shipment,
             sections.get("context", ""), sections.get("initial request", ""), created, parse_ts(case.now)))
        parties = list(dict.fromkeys(case.parties + ([source] if source else [])))
        for p in parties:
            conn.execute("insert into case_parties (case_id, party_name, role) values (%s, %s, %s) on conflict do nothing",
                         (case.case_id, p, party_role(p)))
            party_counts[(party_role(p), p)] += 1
        if shipment:
            by_role = {party_role(p): p for p in parties}
            conn.execute(
                """insert into shipments (id, case_id, description, status, recipient_name, merchant, depot, driver_name)
                   values (%s, %s, %s, 'in_progress', %s, %s, %s, %s) on conflict (id) do nothing""",
                (shipment, case.case_id, case.title, by_role.get("customer"), by_role.get("merchant"),
                 by_role.get("depot"), by_role.get("driver")))
        for e in case.events:
            channel = e.meta.get("channel", "")
            kind, visibility = event_kind(channel)
            author = e.meta.get("from", "")
            conn.execute(
                """insert into case_events (case_id, ts, channel, author, author_role, to_party, kind, visibility, body, meta)
                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (case.case_id, parse_ts(e.timestamp), channel, author, party_role(author) if author else None,
                 e.meta.get("to"), kind, visibility, e.body or "(no text)", Jsonb({"source_event": e.num, **e.meta})))
        attachments = [a.rel_path for a in case.attachments]
        if attachments:
            conn.execute(
                """insert into case_events (case_id, ts, channel, author, kind, visibility, body, meta)
                   values (%s, %s, 'Case file', 'system', 'system', 'staff', %s, %s)""",
                (case.case_id, created, "Attachments on file: " + ", ".join(attachments), Jsonb({"attachments": attachments})))
    print(f"loaded {len(paths)} cases")
    return party_counts


def demo_accounts(party_counts: Counter) -> list[dict]:
    top: dict[str, str] = {}
    for (role, party), _ in party_counts.most_common():
        top.setdefault(role, party)
    accounts = [{"email": "admin@greatagent.demo", "role": "admin", "party": None, "name": "Demo admin"}]
    for role in ("coordinator", "customer", "driver", "depot", "merchant"):
        if role in top:
            accounts.append({"email": f"{role}@greatagent.demo", "role": role, "party": top[role],
                             "name": top[role].split(",")[0]})
    return accounts


def create_user(conn: psycopg.Connection, email: str, password: str, local: bool) -> str:
    if local:
        row = conn.execute(
            """insert into auth.users (email, encrypted_password) values (%s, crypt(%s, gen_salt('bf')))
               on conflict (email) do update set email = excluded.email returning id""", (email, password)).fetchone()
        return str(row[0])
    headers = {"apikey": settings.supabase_service_key, "Authorization": f"Bearer {settings.supabase_service_key}"}
    r = httpx.post(f"{settings.supabase_url}/auth/v1/admin/users", headers=headers, timeout=20,
                   json={"email": email, "password": password, "email_confirm": True})
    if r.status_code in (200, 201):
        return r.json()["id"]
    existing = conn.execute("select id from auth.users where email = %s", (email,)).fetchone()
    if existing:
        return str(existing[0])
    raise RuntimeError(f"could not create {email}: {r.status_code} {r.text[:200]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default=str(DEFAULT_CASES))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--reset", action="store_true", help="delete existing cases, events, actions and runs first")
    ap.add_argument("--local", action="store_true", help="create demo users directly (local Postgres only)")
    args = ap.parse_args()

    password = os.environ.get("DEMO_PASSWORD", "greatagent-demo")
    with psycopg.connect(settings.database_url, autocommit=True, prepare_threshold=None) as conn:
        if args.reset:
            conn.execute("truncate cases, case_parties, shipments, case_events, actions, agent_events, agent_runs restart identity cascade")
            if conn.execute("select to_regclass('public.ref_aliases')").fetchone()[0]:
                conn.execute("truncate ref_aliases")   # aliases point at refs of the rows just removed
        counts = load_cases(conn, Path(args.cases), args.limit)
        phone = os.environ.get("DEMO_CUSTOMER_PHONE")
        for acc in demo_accounts(counts):
            uid = create_user(conn, acc["email"], password, args.local)
            conn.execute(
                """insert into profiles (id, email, display_name, role, party_name, phone) values (%s, %s, %s, %s, %s, %s)
                   on conflict (id) do update set role = excluded.role, party_name = excluded.party_name,
                       display_name = excluded.display_name, phone = coalesce(excluded.phone, profiles.phone)""",
                (uid, acc["email"], acc["name"], acc["role"], acc["party"], phone if acc["role"] == "customer" else None))
            print(f"  {acc['role']:<12} {acc['email']:<28} {acc['party'] or ''}")
        print(f"welcome coins: credited {welcome_staff(conn)} staff profile(s)")
        print(f"demo password: {password}")


if __name__ == "__main__":
    main()
