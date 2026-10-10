"""End-to-end check of rewards, merch and the driver portal against the LIVE hub, run after a deploy.

    HUB_URL=https://<hub> SUPABASE_URL=https://<ref>.supabase.co SUPABASE_ANON_KEY=... DEMO_PASSWORD=... \
        .venv/bin/python scripts/e2e_rewards.py [--redeem] [--touch]

Signs in as coordinator@, admin@ and driver@greatagent.demo through Supabase Auth (password grant), then prints one
line per check. Read-only by default:
  --redeem   also buys one Desk mug as the coordinator (spends 40 coins, takes one from stock)
  --touch    also marks the driver's first shipment out_for_delivery (wakes the agent if it has a case)
Exits 1 if any check fails. Tokens and keys are never printed.
"""
from __future__ import annotations

import argparse
import os
import sys

import httpx

ACCOUNTS = {"coordinator": "coordinator@greatagent.demo", "admin": "admin@greatagent.demo",
            "driver": "driver@greatagent.demo"}
EXPECTED_MERCH = 6


class Run:
    def __init__(self):
        self.failed = 0

    def check(self, ok: bool, label: str, detail: str = "") -> bool:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  {detail}" if detail else ""))
        if not ok:
            self.failed += 1
        return ok


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"missing environment variable {name}")
    return value


def _short(r: httpx.Response) -> str:
    """Status and a trimmed body for a failure line (bodies from these endpoints never carry tokens)."""
    return f"HTTP {r.status_code} {r.text[:200]!r}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--redeem", action="store_true", help="buy one Desk mug as the coordinator")
    ap.add_argument("--touch", action="store_true", help="mark the driver's first shipment out_for_delivery")
    args = ap.parse_args()

    hub = _env("HUB_URL").rstrip("/")
    supa = _env("SUPABASE_URL").rstrip("/")
    anon = _env("SUPABASE_ANON_KEY")
    password = _env("DEMO_PASSWORD")
    run = Run()
    http = httpx.Client(timeout=30)

    # ---------------------------------------------------------------- sign in
    tokens: dict[str, str] = {}
    for role, email in ACCOUNTS.items():
        try:
            r = http.post(f"{supa}/auth/v1/token", params={"grant_type": "password"},
                          headers={"apikey": anon, "Content-Type": "application/json"},
                          json={"email": email, "password": password})
        except httpx.HTTPError as exc:
            run.check(False, f"sign in {email}", type(exc).__name__)
            continue
        try:
            token = r.json().get("access_token") if r.status_code == 200 else None
        except ValueError:
            token = None
        if run.check(bool(token), f"sign in {email}", "" if token else f"HTTP {r.status_code}"):
            tokens[role] = token
    if len(tokens) < len(ACCOUNTS):
        print(f"{run.failed} check(s) failed; stopping before the API checks")
        return 1

    def hub_call(method: str, role: str, path: str, **kw) -> httpx.Response | None:
        try:
            return http.request(method, f"{hub}{path}", headers={"Authorization": f"Bearer {tokens[role]}"}, **kw)
        except httpx.HTTPError as exc:
            run.check(False, f"{method} {path} as {role}", type(exc).__name__)
            return None

    # ---------------------------------------------------------------- who am I
    for role in ACCOUNTS:
        r = hub_call("GET", role, "/api/me")
        if r is not None:
            ok = r.status_code == 200 and r.json().get("role") == role
            run.check(ok, f"GET /api/me as {role}",
                      f"role={r.json().get('role')} party={r.json().get('party_name')!r}" if r.status_code == 200 else _short(r))

    # ---------------------------------------------------------------- rewards
    r = hub_call("GET", "coordinator", "/api/rewards/me")
    if r is not None:
        if r.status_code == 200:
            me = r.json()
            medals = me.get("medals") or []
            earned = sum(1 for m in medals if m.get("earned_at"))
            run.check(isinstance(me.get("balance"), int) and bool(medals), "GET /api/rewards/me as coordinator",
                      f"balance={me.get('balance')} medals={len(medals)} earned={earned} "
                      f"earned_total={me.get('earned_total')} orders={len(me.get('orders') or [])}")
        else:
            run.check(False, "GET /api/rewards/me as coordinator", _short(r))

    r = hub_call("GET", "coordinator", "/api/merch")
    if r is not None:
        items = r.json() if r.status_code == 200 else []
        run.check(r.status_code == 200 and len(items) == EXPECTED_MERCH, "GET /api/merch",
                  f"items={len(items)} ({', '.join(i['id'] for i in items)})" if r.status_code == 200 else _short(r))

    r = hub_call("GET", "admin", "/api/rewards/team")
    if r is not None:
        rows = r.json() if r.status_code == 200 else []
        run.check(r.status_code == 200 and len(rows) > 0, "GET /api/rewards/team as admin",
                  f"rows={len(rows)}" + (f" top={rows[0].get('display_name')!r} balance={rows[0].get('balance')}"
                                         if rows else "") if r.status_code == 200 else _short(r))

    r = hub_call("GET", "coordinator", "/api/rewards/team")
    if r is not None:
        run.check(r.status_code == 403, "GET /api/rewards/team as coordinator is 403", f"HTTP {r.status_code}")

    if args.redeem:
        r = hub_call("POST", "coordinator", "/api/merch/mug/redeem")
        if r is not None:
            run.check(r.status_code == 200, "POST /api/merch/mug/redeem as coordinator",
                      f"order={r.json().get('order_id')} new balance={r.json().get('balance')}"
                      if r.status_code == 200 else _short(r))
    else:
        print("SKIP  POST /api/merch/mug/redeem (pass --redeem)")

    # ---------------------------------------------------------------- driver
    try:
        r = http.get(f"{supa}/rest/v1/shipments", params={"select": "id,status,driver_name", "order": "id"},
                     headers={"apikey": anon, "Authorization": f"Bearer {tokens['driver']}"})
    except httpx.HTTPError as exc:
        r = None
        run.check(False, "GET shipments as driver (Supabase REST)", type(exc).__name__)
    ships = []
    if r is not None:
        ships = r.json() if r.status_code == 200 else []
        run.check(r.status_code == 200, "GET shipments as driver (Supabase REST)",
                  f"{len(ships)} shipment(s)" + (f", first {ships[0]['id']} {ships[0]['status']} "
                                                 f"driver={ships[0]['driver_name']!r}" if ships else "")
                  if r.status_code == 200 else _short(r))

    if args.touch:
        if run.check(bool(ships), "driver has a shipment to touch"):
            sid = ships[0]["id"]
            r = hub_call("POST", "driver", f"/api/shipments/{sid}/status",
                         json={"status": "out_for_delivery", "note": "e2e check"})
            if r is not None:
                run.check(r.status_code == 200 and r.json().get("ok") is True,
                          f"POST /api/shipments/{sid}/status out_for_delivery as driver",
                          f"response={r.json()}" if r.status_code == 200 else _short(r))
    else:
        print("SKIP  POST /api/shipments/<id>/status (pass --touch)")

    print(f"{'all checks passed' if not run.failed else f'{run.failed} check(s) failed'}")
    return 1 if run.failed else 0


if __name__ == "__main__":
    sys.exit(main())
