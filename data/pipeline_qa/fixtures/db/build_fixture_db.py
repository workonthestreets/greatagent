#!/usr/bin/env python3
"""Build synthetic delivery DBs: good.sqlite and bad.sqlite (stdlib only).

Usage: python3 -I build_fixture_db.py [outdir]   (default: this script's directory)
Writes only inside outdir. Existing good/bad files are replaced.
"""
import sqlite3
import sys
from pathlib import Path

T = "TEXT"
DDL = {
 "actors": [("actor_id", T, 1), ("name", T), ("party", T), ("org", T), ("org_type", T), ("role", T), ("is_person", "INTEGER")],
 "orders": [("order_id", T, 1), ("merchant_id", T), ("customer_id", T), ("order_status", T), ("case_id", T), ("note", T)],
 "shipments": [("shipment_id", T, 1), ("case_id", T), ("order_id", T), ("carrier_id", T), ("kind", T),
               ("milestone_at_escalation", T), ("milestone_final", T), ("exception", T), ("destination", T),
               ("promised_at", T), ("model_gap", T), ("shipper", T), ("consignee", T), ("note", T)],
 "parcels": [("parcel_id", T, 1), ("shipment_id", T), ("barcode", T), ("parcel_status", T), ("case_id", T), ("note", T)],
 "events": [("event_id", T, 1), ("case_id", T), ("shipment_id", T), ("event_type", T), ("location", T), ("occurred_at", T),
            ("source_system", T), ("source_message_id", T), ("visible_at_escalation", "INTEGER"), ("text", T), ("extraction", T)],
 "cases": [("case_id", T, 1), ("case_type", T), ("case_category", T), ("raised_by", T), ("raised_by_type", T), ("channel", T),
           ("channel_class", T), ("linked_object_id", T), ("linked_object_type", T), ("request_or_claim", T),
           ("requested_action_by_raiser", T), ("recorded_next_action", T), ("case_state_at_escalation", T),
           ("case_state_final", T), ("operational_effect", T), ("priority", T), ("owner", T), ("owner_group", T),
           ("deadline", T), ("resolution", T), ("boundaries", T), ("param_claim_value_gbp", T), ("param_delay_days", T),
           ("labelled", "INTEGER")],
 "tasks": [("task_id", T, 1), ("case_id", T), ("task_type", T), ("description", T), ("assignee", T), ("assignee_org_type", T),
           ("channel", T), ("created_at", T), ("completed_at", T), ("status", T), ("source_message_id", T), ("is_gold_action", "INTEGER")],
 "evidence": [("evidence_id", T, 1), ("case_id", T), ("shipment_id", T), ("evidence_type", T), ("reference", T), ("description", T),
              ("source", T), ("file_name", T), ("first_seen_message_id", T), ("visible_at_escalation", "INTEGER")],
 "messages": [("message_id", T, 1), ("case_id", T), ("seq", "INTEGER"), ("timestamp", T), ("stage", T), ("channel", T),
              ("from_actor_id", T), ("to_actor_ids", T), ("direction", T), ("visible_at_escalation", "INTEGER"),
              ("body", T), ("refs", T), ("amounts_gbp", "REAL")],
 "case_actors": [("case_id", T), ("actor_id", T), ("role_in_case", T)],
 "reconciliation": [("entity", T), ("field", T), ("andrey_definition", T), ("source_in_data", T),
                    ("coverage_n", "INTEGER"), ("coverage_pct", "REAL"), ("na_policy", T), ("note", T)],
}
VIEWS = """
CREATE VIEW v_shipment_dashboard AS
SELECT s.shipment_id, s.case_id, s.carrier_id, s.destination, s.milestone_final,
       (SELECT COUNT(*) FROM parcels p WHERE p.shipment_id = s.shipment_id) AS n_parcels,
       (SELECT MAX(e.occurred_at) FROM events e WHERE e.shipment_id = s.shipment_id) AS last_event_at
FROM shipments s;
CREATE VIEW v_case_timeline AS
SELECT e.case_id, e.occurred_at, 'event' AS kind, e.event_type AS what FROM events e
UNION ALL
SELECT m.case_id, m.timestamp, 'message', m.stage FROM messages m;
"""


def create(db):
    for t, cols in DDL.items():
        defs = ", ".join(f'"{c[0]}" {c[1]}' + (" PRIMARY KEY" if len(c) > 2 else "") for c in cols)
        db.execute(f'CREATE TABLE "{t}" ({defs})')
    db.executescript(VIEWS)


def ins(db, table, **kw):
    """Insert a row; unspecified TEXT cols become 'N/A', INTEGER/REAL 0."""
    row = {}
    for c in DDL[table]:
        row[c[0]] = kw.get(c[0], "N/A" if c[1] == T else 0)
    cols = list(row)
    db.execute(f'INSERT INTO "{table}" ({",".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({",".join("?"*len(cols))})',
               [row[c] for c in cols])


def populate(db):
    for i in range(1, 6):
        ins(db, "actors", actor_id=f"A{i}", name=f"Actor {i}", org=f"Org {i}", role="agent", is_person=1)
    # 50 labelled cases / 228 messages (28 cases x5 + 22 cases x4), plus 2 stress cases
    plan = [(f"C{i:03d}", 1, 5 if i <= 28 else 4) for i in range(1, 51)] + [("S001", 0, 3), ("S002", 0, 3)]
    for k, (cid, lab, nmsg) in enumerate(plan):
        ins(db, "cases", case_id=cid, case_type="delay", priority="high", labelled=lab, param_delay_days="2")
        ins(db, "case_actors", case_id=cid, actor_id="A1", role_in_case="raiser")
        for seq in range(1, nmsg + 1):
            ins(db, "messages", message_id=f"{cid}-M{seq}", case_id=cid, seq=seq, timestamp=f"2026-01-01T0{seq}:00",
                stage="escalation" if seq <= 2 else "post", from_actor_id=f"A{1 + seq % 5}",
                visible_at_escalation=1 if seq <= 2 else 0, body="hello", amounts_gbp=0)
        sid = None
        if k < 30:
            sid = f"SHP{k:03d}"
            ins(db, "shipments", shipment_id=sid, case_id=cid, carrier_id="CAR1", destination="Leeds", milestone_final="delivered")
            ins(db, "parcels", parcel_id=f"P{k:03d}", shipment_id=sid, case_id=cid, barcode=f"BC{k}", parcel_status="held")
            ins(db, "orders", order_id=f"O{k:03d}", case_id=cid if k else "N/A", order_status="open")
        ins(db, "events", event_id=f"{cid}-E1", case_id=cid, shipment_id=sid or "N/A", event_type="scan",
            occurred_at=f"2026-01-01T0{1}:30", source_message_id=f"{cid}-M1", visible_at_escalation=1, text="scanned")
        ins(db, "events", event_id=f"{cid}-E2", case_id=cid, shipment_id=sid or "N/A", event_type="deliver",
            occurred_at="2026-01-02T09:00", source_message_id=f"{cid}-M3" if nmsg >= 3 else "N/A", visible_at_escalation=0)
        ins(db, "evidence", evidence_id=f"{cid}-V1", case_id=cid, shipment_id=sid or "N/A", evidence_type="photo",
            first_seen_message_id=f"{cid}-M2", visible_at_escalation=1)
        ins(db, "tasks", task_id=f"{cid}-T1", case_id=cid, task_type="call", description="call carrier",
            source_message_id=f"{cid}-M3" if nmsg >= 3 else "N/A", is_gold_action=1)
    ins(db, "reconciliation", entity="cases", field="labelled", coverage_n=50, coverage_pct=100.0)


def inject_bad(db):
    # 1. NULL TEXT cell
    db.execute("UPDATE shipments SET note=NULL WHERE shipment_id='SHP000'")
    # 2. empty string
    db.execute("UPDATE tasks SET description='' WHERE task_id='C002-T1'")
    # 3. dangling foreign key
    db.execute("UPDATE parcels SET shipment_id='SHP-GHOST' WHERE parcel_id='P003'")
    # 4. leaked event: visible at escalation but sourced from seq 3
    db.execute("UPDATE events SET visible_at_escalation=1 WHERE event_id='C001-E2'")
    # 5. dashboard NULL: shipment loses all events -> last_event_at NULL
    db.execute("UPDATE events SET shipment_id='N/A' WHERE shipment_id='SHP029'")


def build(path, bad):
    path = Path(path)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    create(db)
    populate(db)
    if bad:
        inject_bad(db)
    db.commit()
    db.close()


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    build(out / "good.sqlite", False)
    build(out / "bad.sqlite", True)
    print(f"wrote {out / 'good.sqlite'} and {out / 'bad.sqlite'}")
