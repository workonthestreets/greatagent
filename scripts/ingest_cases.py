"""Ingest a folder of test cases into the live desk and have the agent work each one.

The folder looks like a track of HackatonPublicCases: one subfolder per case, each with index.md, history.md and
optional attachments/ (for example "HackatonPublicCases/Delivery & Logistics" or a folder of new test cases).
Each case becomes a new desk case (its own fresh id, so it never collides with the seeded public cases), its
history becomes the timeline, and the agent is woken on it with whichever engine the hub uses (DESK_ENGINE). The
cases, the agent's activity and its drafted messages show up live in the dashboard (Desk, Agents, Approvals).

    python scripts/ingest_cases.py "/path/to/Test cases"                 # all cases, cut at the escalation point
    python scripts/ingest_cases.py "/path/to/Test cases" --limit 3
    python scripts/ingest_cases.py "/path/to/Test cases" --full          # keep every event, don't cut at escalation
    python scripts/ingest_cases.py "/path/to/Test cases" --no-agent      # only load them; wake the agent later from /ops
    python scripts/ingest_cases.py "/path/to/Test cases" --dry-run       # show what would be loaded

Uses the same database (DATABASE_URL) and keys as the hub (.env). With DESK_ENGINE=managed the hub must be running
at HUB_PUBLIC_URL, because the agent calls its tools there; with DESK_ENGINE=pipeline the agent runs in this process.
Each agent run is waited for before the next case starts. Running the script again skips folders already ingested
(matched on the folder name); use --again to ingest them as new cases anyway.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from db.seed import DETAIL_LINE, event_kind, parse_ts, party_role  # noqa: E402
from deskagent.loader import discover_cases, load_case, split_sections  # noqa: E402
from hub import db, driver, refs  # noqa: E402
from hub.config import settings  # noqa: E402

SOURCE = "demo"   # cases.source for ingested test cases (only set when the DB has migration 004)


def already_ingested(tag: str) -> str | None:
    row = db.one("select case_id from case_events where meta->>'ingested_from' = %s limit 1", (tag,))
    return row["case_id"] if row else None


def ingest(path: Path, tag: str, full: bool) -> str:
    """Write one case folder into the desk tables under a new case id; returns that id."""
    case = load_case(path, public_cutoff=not full, media=False)
    index = dict(case.files).get("index.md", "")
    details = {m.group("k").strip().lower(): m.group("v").strip() for m in DETAIL_LINE.finditer(index)}
    sections = {name.lower(): body.strip() for name, body in split_sections(index)}
    source = details.get("source role", "")
    shipment = details.get("primary shipment", "").split()[0].strip(",;") if details.get("primary shipment") else None
    created = parse_ts(details.get("created", case.now))
    case_id = refs.new_case_id()

    db.query(
        """insert into cases (id, title, track, status, source_name, source_role, coordinator, shipment_id,
                              context, initial_request, created_at, updated_at)
           values (%s, %s, %s, 'open', %s, %s, %s, %s, %s, %s, %s, now())""",
        (case_id, case.title or path.name, case.track or "Delivery & Logistics", source.split(",")[0].strip() or None,
         party_role(source) if source else None, details.get("coordinator") or "Iona Quill, Rivet Delivery Desk",
         shipment, sections.get("context", ""), sections.get("initial request", ""), created))
    if refs.migrated():
        db.query("update cases set source = %s, legacy_ref = %s where id = %s", (SOURCE, tag, case_id))

    parties = list(dict.fromkeys(case.parties + ([source] if source else [])))
    for p in parties:
        db.query("insert into case_parties (case_id, party_name, role) values (%s, %s, %s) on conflict do nothing",
                 (case_id, p, party_role(p)))
    if shipment:
        # The shipment may already exist (the seeded public cases use the same DL- numbers): keep the existing row.
        by_role = {party_role(p): p for p in parties}
        db.query(
            """insert into shipments (id, case_id, description, status, recipient_name, merchant, depot, driver_name)
               values (%s, %s, %s, 'in_progress', %s, %s, %s, %s) on conflict (id) do nothing""",
            (shipment, case_id, case.title, by_role.get("customer"), by_role.get("merchant"),
             by_role.get("depot"), by_role.get("driver")))

    for e in case.events:
        channel = e.meta.get("channel", "")
        kind, visibility = event_kind(channel)
        author = e.meta.get("from", "")
        db.query(
            """insert into case_events (case_id, ts, channel, author, author_role, to_party, kind, visibility, body, meta)
               values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (case_id, parse_ts(e.timestamp), channel, author, party_role(author) if author else None,
             e.meta.get("to"), kind, visibility, e.body or "(no text)",
             db.jsonb({"source_event": e.num, "ingested_from": tag, **e.meta})))
    attachments = [a.rel_path for a in case.attachments]
    notes = [f"Ingested from test case folder {tag}."] + (["Attachments on file: " + ", ".join(attachments)] if attachments else [])
    db.query(
        """insert into case_events (case_id, ts, channel, author, kind, visibility, body, meta)
           values (%s, %s, 'Case file', 'system', 'system', 'staff', %s, %s)""",
        (case_id, created, "\n".join(notes), db.jsonb({"ingested_from": tag, "attachments": attachments})))
    return case_id


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest test case folders into the live desk and run the agent on them.")
    ap.add_argument("folder", help="folder with one subfolder per case (index.md, history.md, attachments/)")
    ap.add_argument("--limit", type=int, default=0, help="ingest at most this many cases")
    ap.add_argument("--full", action="store_true", help="keep every event instead of cutting at the escalation point")
    ap.add_argument("--no-agent", action="store_true", help="only load the cases; don't wake the agent")
    ap.add_argument("--again", action="store_true", help="ingest folders even if they were ingested before")
    ap.add_argument("--dry-run", action="store_true", help="list what would be ingested and stop")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    paths = discover_cases(folder)
    if args.limit:
        paths = paths[:args.limit]
    if not paths:
        sys.exit(f"no case folders found in {folder}")
    print(f"{len(paths)} case(s) in {folder}  |  engine: {settings.engine}  |  agent: {'off' if args.no_agent else 'on'}")

    done = []
    for path in paths:
        tag = f"{folder.name}/{path.name}"
        seen = already_ingested(tag)
        if seen and not args.again:
            print(f"  skip  {tag}  (already ingested as {refs.case_ref(seen)}; use --again to add it again)")
            continue
        if args.dry_run:
            print(f"  would ingest  {tag}")
            continue
        try:
            case_id = ingest(path, tag, args.full)
        except Exception as exc:  # noqa: BLE001 - one bad folder shouldn't stop the batch
            print(f"  FAIL  {tag}: {exc}")
            continue
        ref = refs.case_ref(case_id)
        print(f"  added {tag}  ->  case {ref}", flush=True)
        if args.no_agent:
            done.append((tag, ref, "loaded"))
            continue
        t0 = time.time()
        try:
            driver.wake(case_id, f"A new case was opened from the test case set ({tag}). Work out the next step.", wait=True)
            row = db.one("select status, decision_summary from cases where id = %s", (case_id,)) or {}
            print(f"        agent done in {time.time() - t0:.0f}s: [{row.get('status')}] {row.get('decision_summary') or ''}"[:200])
            done.append((tag, ref, row.get("status") or "?"))
        except Exception as exc:  # noqa: BLE001
            print(f"        agent failed: {exc}")
            done.append((tag, ref, "agent failed"))

    if done:
        print(f"\n{len(done)} case(s) ingested. Watch them in the dashboard: Desk (cases, approvals) and /agents (live runs).")
        for tag, ref, status in done:
            print(f"  {ref:<10} {status:<14} {tag}")
    db.pool().close()


if __name__ == "__main__":
    main()
