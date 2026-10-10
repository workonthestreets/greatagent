#!/usr/bin/env python3
"""QA suite for the delivery SQLite DB (stdlib only, read-only).

CLI:    python3 -I test_db.py [path/to/delivery.sqlite]   (exit 1 on any FAIL)
pytest: DELIVERY_DB=... /usr/local/bin/python3.13 -I -m pytest -p no:cacheprovider test_db.py
DB path precedence: CLI arg > DELIVERY_DB env var > data/delivery/database/delivery.sqlite
"""
import os
import sqlite3
import sys
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "delivery" / "database" / "delivery.sqlite"
EXPECTED_LABELLED = 50
EXPECTED_LABELLED_MESSAGES = 228
SAMPLE = 5

SPEC = {
    "actors": "actor_id name party org org_type role is_person",
    "orders": "order_id merchant_id customer_id order_status case_id note",
    "shipments": "shipment_id case_id order_id carrier_id kind milestone_at_escalation "
                 "milestone_final exception destination promised_at model_gap shipper consignee note",
    "parcels": "parcel_id shipment_id barcode parcel_status case_id note",
    "events": "event_id case_id shipment_id event_type location occurred_at source_system "
              "source_message_id visible_at_escalation text extraction",
    # spec elides "..." labelled-parameter columns: only the named ones + `labelled` are required
    "cases": "case_id case_type case_category raised_by raised_by_type channel channel_class "
             "linked_object_id linked_object_type request_or_claim requested_action_by_raiser "
             "recorded_next_action case_state_at_escalation case_state_final operational_effect "
             "priority owner owner_group deadline resolution boundaries labelled",
    "tasks": "task_id case_id task_type description assignee assignee_org_type channel created_at "
             "completed_at status source_message_id is_gold_action",
    "evidence": "evidence_id case_id shipment_id evidence_type reference description source file_name "
                "first_seen_message_id visible_at_escalation",
    "messages": "message_id case_id seq timestamp stage channel from_actor_id to_actor_ids direction "
                "visible_at_escalation body refs amounts_gbp",
    "case_actors": "case_id actor_id role_in_case",
    "reconciliation": "entity field andrey_definition source_in_data coverage_n coverage_pct na_policy note",
}
SPEC = {t: c.split() for t, c in SPEC.items()}
VIEWS = ["v_shipment_dashboard", "v_case_timeline"]
NA_TABLES = ["actors", "orders", "shipments", "parcels", "events", "cases", "tasks", "evidence"]
# (child table, child column, parent table, parent column, required?)
FKS = [
    ("shipments", "case_id", "cases", "case_id", True),
    ("parcels", "shipment_id", "shipments", "shipment_id", True),
    ("events", "case_id", "cases", "case_id", True),
    ("tasks", "case_id", "cases", "case_id", True),
    ("evidence", "case_id", "cases", "case_id", True),
    ("messages", "case_id", "cases", "case_id", True),
    ("messages", "from_actor_id", "actors", "actor_id", True),
    ("orders", "case_id", "cases", "case_id", False),
    ("case_actors", "case_id", "cases", "case_id", False),
    ("case_actors", "actor_id", "actors", "actor_id", False),
]

PASS, FAIL, INFO = "PASS", "FAIL", "INFO"


def q(name):
    return '"' + name.replace('"', '""') + '"'


def open_ro(path):
    uri = "file:" + str(Path(path).resolve()).replace("?", "%3f").replace("#", "%23") + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def table_cols(conn, name):
    """Return [(name, decl_type, pk_pos)] or None if the object doesn't exist."""
    rows = conn.execute(f"PRAGMA table_info({q(name)})").fetchall()
    return [(r[1], r[2] or "", r[5]) for r in rows] if rows else None


def objects(conn, kind):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type=?", (kind,))}


def is_text(decl):
    d = decl.upper()
    return d == "" or any(k in d for k in ("TEXT", "CHAR", "CLOB"))


def pk_expr(conn, table):
    cols = table_cols(conn, table)
    pks = sorted((c for c in cols if c[2]), key=lambda c: c[2])
    return q(pks[0][0]) if pks else "rowid"


# Each check returns (status, [detail lines])

def check_1_labelled_cases(conn):
    if not table_cols(conn, "cases") or "labelled" not in [c[0] for c in table_cols(conn, "cases")]:
        return FAIL, ["cases.labelled missing; cannot count"]
    n1 = conn.execute("SELECT COUNT(*) FROM cases WHERE labelled=1").fetchone()[0]
    n0 = conn.execute("SELECT COUNT(*) FROM cases WHERE labelled=0").fetchone()[0]
    other = conn.execute("SELECT COUNT(*) FROM cases WHERE labelled IS NULL OR labelled NOT IN (0,1)").fetchone()[0]
    d = [f"labelled=1: {n1} (expected {EXPECTED_LABELLED}); labelled=0 (stress): {n0}"]
    st = PASS
    if n1 != EXPECTED_LABELLED:
        st = FAIL
    if n0 > 20:
        st = FAIL
        d.append(f"labelled=0 cases {n0} exceeds allowed 20")
    if other:
        st = FAIL
        d.append(f"{other} cases have labelled NULL or not in (0,1)")
    return st, d


def check_2_labelled_messages(conn):
    for t in ("messages", "cases"):
        if not table_cols(conn, t):
            return FAIL, [f"table {t} missing"]
    n = conn.execute("SELECT COUNT(*) FROM messages m JOIN cases c ON c.case_id=m.case_id "
                     "WHERE c.labelled=1").fetchone()[0]
    tot = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    return (PASS if n == EXPECTED_LABELLED_MESSAGES else FAIL,
            [f"messages in labelled cases: {n} (expected {EXPECTED_LABELLED_MESSAGES}); total messages: {tot}"])


def check_3_na_policy(conn):
    d, bad = [], False
    for t in NA_TABLES:
        cols = table_cols(conn, t)
        if cols is None:
            d.append(f"{t}: table missing, skipped (see schema check)")
            continue
        pk = pk_expr(conn, t)
        nrows = conn.execute(f"SELECT COUNT(*) FROM {q(t)}").fetchone()[0]
        for name, decl, _ in cols:
            if not is_text(decl):
                continue
            c = q(name)
            n_null = conn.execute(f"SELECT COUNT(*) FROM {q(t)} WHERE {c} IS NULL").fetchone()[0]
            # non-NULL values that are not text storage (e.g. blob) are ignored; empty = '' or whitespace only
            n_empty = conn.execute(f"SELECT COUNT(*) FROM {q(t)} WHERE typeof({c})='text' AND TRIM({c})=''").fetchone()[0]
            for label, n, cond in (("NULL", n_null, f"{c} IS NULL"),
                                   ("empty", n_empty, f"typeof({c})='text' AND TRIM({c})=''")):
                if n:
                    bad = True
                    s = [r[0] for r in conn.execute(f"SELECT {pk} FROM {q(t)} WHERE {cond} LIMIT {SAMPLE}")]
                    d.append(f"{t}.{name}: {n} {label} of {nrows} rows; sample PKs: {s}")
    if not bad:
        d.append("all TEXT-affinity cells in " + ", ".join(NA_TABLES) + " are non-NULL and non-empty")
    return (FAIL if bad else PASS), d


def check_4_referential(conn):
    d, bad = [], False
    for ct, cc, pt, pc, required in FKS:
        ccols, pcols = table_cols(conn, ct), table_cols(conn, pt)
        tag = f"{ct}.{cc} -> {pt}.{pc}"
        if not ccols or cc not in [c[0] for c in ccols] or not pcols or pc not in [c[0] for c in pcols]:
            if required:
                bad = True
                d.append(f"{tag}: cannot check, table/column missing")
            else:
                d.append(f"{tag}: optional, table/column absent, skipped")
            continue
        pk = pk_expr(conn, ct)
        c, p = q(cc), q(pc)
        na = conn.execute(f"SELECT COUNT(*) FROM {q(ct)} WHERE {c}='N/A'").fetchone()[0]
        cond = f"({c} IS NULL OR {c} <> 'N/A') AND NOT EXISTS (SELECT 1 FROM {q(pt)} x WHERE x.{p} = {q(ct)}.{c})"
        n = conn.execute(f"SELECT COUNT(*) FROM {q(ct)} WHERE {cond}").fetchone()[0]
        line = f"{tag}: {n} dangling"
        if n:
            bad = True
            s = [r for r in conn.execute(f"SELECT {pk}, {c} FROM {q(ct)} WHERE {cond} LIMIT {SAMPLE}")]
            line += f" (PK, value samples: {s})"
        if na:
            line += f"; {na} 'N/A' (allowed, reported)"
        d.append(line)
    return (FAIL if bad else PASS), d


def _cutoff_cte(conn):
    """Per-case visibility cutoff (highest seq the agent may see).

    Public labelled cases (labelled=1): seq <= 2.
    Stress cases (labelled=0): every message before the first desk-authored message
    (messages.from_org_type = 'desk'); all messages if the desk never writes.
    Without a from_org_type column, stress cases fall back to seq <= 2.
    """
    mcols = [c[0] for c in table_cols(conn, "messages")]
    ccols = [c[0] for c in table_cols(conn, "cases")]
    lab = "COALESCE(CAST(c.labelled AS INTEGER), 1)" if "labelled" in ccols else "1"
    if "from_org_type" in mcols:
        stress = ("COALESCE((SELECT MIN(CAST(m.seq AS INTEGER)) - 1 FROM messages m "
                  "WHERE m.case_id = c.case_id AND m.from_org_type = 'desk'), 1000000)")
    else:
        stress = "2"
    return (f"WITH cut AS (SELECT c.case_id AS case_id, CASE WHEN {lab} = 1 THEN 2 "
            f"ELSE {stress} END AS cut FROM cases c) ")


def check_5_leakage(conn):
    d, bad = [], False
    if not table_cols(conn, "messages") or not table_cols(conn, "cases"):
        return FAIL, ["messages or cases table missing"]
    cte = _cutoff_cte(conn)
    d.append("rule: labelled cases seq<=2; stress cases = before first desk-authored message")
    for t, srccol in (("events", "source_message_id"), ("evidence", "first_seen_message_id")):
        cols = [c[0] for c in table_cols(conn, t)]
        if not cols or srccol not in cols or "visible_at_escalation" not in cols:
            bad = True
            d.append(f"{t}: cannot check, columns/tables missing")
            continue
        pk, s = pk_expr(conn, t), q(srccol)
        nvis = conn.execute(f"SELECT COUNT(*) FROM {q(t)} WHERE visible_at_escalation=1").fetchone()[0]
        # leak: visible row whose source message is missing/'N/A' (unverifiable) or lies after the case cutoff
        cond = (f"visible_at_escalation=1 AND NOT EXISTS (SELECT 1 FROM messages m JOIN cut ON cut.case_id = m.case_id "
                f"WHERE m.message_id = {q(t)}.{s} AND m.seq IS NOT NULL AND CAST(m.seq AS INTEGER) <= cut.cut)")
        n = conn.execute(f"{cte}SELECT COUNT(*) FROM {q(t)} WHERE {cond}").fetchone()[0]
        line = f"{t}: {n} of {nvis} visible rows lack a source message at or before the case cutoff"
        if n:
            bad = True
            line += f"; samples (PK, {srccol}): {conn.execute(f'{cte}SELECT {pk}, {s} FROM {q(t)} WHERE {cond} LIMIT {SAMPLE}').fetchall()}"
        d.append(line)
    cond = ("EXISTS (SELECT 1 FROM cut WHERE cut.case_id = messages.case_id AND CAST(messages.seq AS INTEGER) > cut.cut) "
            "AND (visible_at_escalation IS NULL OR visible_at_escalation <> 0)")
    n = conn.execute(f"{cte}SELECT COUNT(*) FROM messages WHERE {cond}").fetchone()[0]
    line = f"messages: {n} rows after the case cutoff with visible_at_escalation<>0"
    if n:
        bad = True
        line += f"; sample message_ids: {[r[0] for r in conn.execute(f'{cte}SELECT message_id FROM messages WHERE {cond} LIMIT {SAMPLE}')]}"
    d.append(line)
    # the reverse direction: messages inside the cutoff that are hidden (over-hiding, not leakage)
    cond2 = ("EXISTS (SELECT 1 FROM cut WHERE cut.case_id = messages.case_id AND CAST(messages.seq AS INTEGER) <= cut.cut) "
             "AND visible_at_escalation = 0")
    n2 = conn.execute(f"{cte}SELECT COUNT(*) FROM messages WHERE {cond2}").fetchone()[0]
    d.append(f"INFO messages inside the cutoff but hidden: {n2}")
    return (FAIL if bad else PASS), d


def check_6_views(conn):
    d, bad = [], False
    if "v_shipment_dashboard" not in objects(conn, "view"):
        return FAIL, ["v_shipment_dashboard missing"]
    if not table_cols(conn, "shipments"):
        return FAIL, ["shipments missing"]
    try:
        cur = conn.execute("SELECT * FROM v_shipment_dashboard")
        names = [x[0] for x in cur.description]
        rows = cur.fetchall()
    except sqlite3.Error as e:
        return FAIL, [f"v_shipment_dashboard not queryable: {e}"]
    nship = conn.execute("SELECT COUNT(*) FROM shipments").fetchone()[0]
    if "shipment_id" in names:
        i = names.index("shipment_id")
        ids = [r[i] for r in rows]
        sids = {r[0] for r in conn.execute("SELECT shipment_id FROM shipments")}
        from collections import Counter
        cnt = Counter(ids)
        dups = {k: v for k, v in cnt.items() if v > 1}
        missing = sorted(map(str, sids - set(ids)))
        extra = sorted(map(str, set(ids) - sids))
        d.append(f"dashboard rows {len(rows)} vs shipments {nship}; matched on shipment_id")
        if dups or missing or extra or len(rows) != nship:
            bad = True
            d.append(f"  duplicates={dict(list(dups.items())[:SAMPLE])} missing={missing[:SAMPLE]} extra={extra[:SAMPLE]}")
    else:
        d.append(f"dashboard rows {len(rows)} vs shipments {nship}; no shipment_id column, compared counts only")
        if len(rows) != nship:
            bad = True
    nulls = {}
    for r in rows:
        for n, v in zip(names, r):
            if v is None:
                nulls[n] = nulls.get(n, 0) + 1
    if nulls:
        bad = True
        d.append(f"NULL cells in v_shipment_dashboard: {nulls}")
    else:
        d.append("no NULL cells in v_shipment_dashboard")
    if "v_case_timeline" not in objects(conn, "view"):
        bad = True
        d.append("v_case_timeline missing")
    else:
        try:
            n = conn.execute("SELECT COUNT(*) FROM (SELECT * FROM v_case_timeline)").fetchone()[0]
            d.append(f"v_case_timeline queryable ({n} rows)")
        except sqlite3.Error as e:
            bad = True
            d.append(f"v_case_timeline not queryable: {e}")
    return (FAIL if bad else PASS), d


def check_7_schema(conn):
    d, bad = [], False
    tables, views = objects(conn, "table"), objects(conn, "view")
    for t, want in SPEC.items():
        if t not in tables:
            bad = True
            d.append(f"table {t}: MISSING")
            continue
        have = [c[0] for c in table_cols(conn, t)]
        missing = [c for c in want if c not in have]
        extra = [c for c in have if c not in want]
        if missing:
            bad = True
            d.append(f"{t}: missing/renamed columns {missing}")
        if extra:
            d.append(f"{t}: INFO extra columns ({len(extra)}): {extra[:12]}{'...' if len(extra) > 12 else ''}")
    for v in VIEWS:
        if v not in views:
            bad = True
            d.append(f"view {v}: MISSING")
    if not bad:
        d.insert(0, f"all {len(SPEC)} tables and {len(VIEWS)} views present with required columns")
    return (FAIL if bad else PASS), d


CHECKS = [
    ("1 labelled cases == 50", check_1_labelled_cases),
    ("2 228 msgs in labelled cases", check_2_labelled_messages),
    ("3 NA policy (no NULL/empty TEXT)", check_3_na_policy),
    ("4 referential integrity", check_4_referential),
    ("5 leakage (visible_at_escalation)", check_5_leakage),
    ("6 views (dashboard/timeline)", check_6_views),
    ("7 schema presence", check_7_schema),
]


def resolve_db(argv=None):
    if argv:
        return argv[0]
    return os.environ.get("DELIVERY_DB") or str(DEFAULT_DB)


def main(argv):
    path = resolve_db(argv)
    if not Path(path).is_file():
        print(f"DB not found: {path}")
        return 2
    conn = open_ro(path)
    print(f"DB: {path}\n")
    results = []
    for name, fn in CHECKS:
        try:
            st, det = fn(conn)
        except sqlite3.Error as e:
            st, det = FAIL, [f"sqlite error: {e}"]
        results.append((name, st, det))
    w = max(len(n) for n, _, _ in results)
    print(f"{'CHECK'.ljust(w)}  RESULT")
    print(f"{'-' * w}  ------")
    for n, st, _ in results:
        print(f"{n.ljust(w)}  {st}")
    print()
    for n, st, det in results:
        print(f"[{st}] {n}")
        for line in det:
            print(f"    {line}")
    nfail = sum(1 for _, st, _ in results if st == FAIL)
    print(f"\nSUMMARY: {len(results) - nfail}/{len(results)} checks passed, {nfail} failed")
    return 1 if nfail else 0


# ---------------- pytest interface ----------------
try:
    import pytest
except ImportError:
    pytest = None

if pytest is not None:
    @pytest.fixture(scope="module")
    def conn():
        path = resolve_db()
        if not Path(path).is_file():
            pytest.skip(f"DB not found: {path}")
        c = open_ro(path)
        yield c
        c.close()

    def _run(fn, conn):
        st, det = fn(conn)
        assert st != FAIL, "\n".join(det)

    def test_1_labelled_cases(conn): _run(check_1_labelled_cases, conn)
    def test_2_labelled_messages(conn): _run(check_2_labelled_messages, conn)
    def test_3_na_policy(conn): _run(check_3_na_policy, conn)
    def test_4_referential_integrity(conn): _run(check_4_referential, conn)
    def test_5_leakage(conn): _run(check_5_leakage, conn)
    def test_6_views(conn): _run(check_6_views, conn)
    def test_7_schema(conn): _run(check_7_schema, conn)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
