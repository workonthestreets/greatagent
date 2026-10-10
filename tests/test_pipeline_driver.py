"""Live desk with the pipeline engine, end to end against a local Postgres and a scripted fake Claude client:
phone call webhook -> pipeline (planner, lint, reviewer) -> desk tools -> approvals -> party message / rejection.

    DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres .venv/bin/python tests/test_pipeline_driver.py

Needs the hub dependencies (hub/requirements.txt) and a migrated database (python -m db.migrate --local).
Skips when the database is unreachable.
"""
from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
os.environ["DESK_ENGINE"] = "pipeline"
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:54329/postgres")
os.environ.pop("AGENT_AUTO_APPROVE", None)

import psycopg  # noqa: E402

CASE = "T103"
CUSTOMER = "Vessa Lorne, recipient"
CALL = "Has my delivery been moved? I can't be home this afternoon."


def _db_up() -> bool:
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as conn:
            return conn.execute("select to_regclass('public.cases')").fetchone()[0] is not None
    except Exception:  # noqa: BLE001
        return False


def _plan():
    from test_offline import GOOD_PLAN
    return dict(
        GOOD_PLAN, decision_type="act",
        decision_summary="Resend the rebooking to dispatch email before the cutoff and tell the recipient it is not confirmed yet.",
        actions=[
            {"tool": "send_message", "to_name": "Dispatch", "to_role": "Plover Arc Logistics dispatch", "channel": "Email",
             "subject": "DL-103 rebooking before cutoff", "body": "Please rebook DL-103 to tomorrow 09:00-12:00 and confirm.",
             "purpose": "route to the party with authority"},
            {"tool": "send_message", "to_name": "Vessa Lorne", "to_role": "recipient", "channel": "Customer portal",
             "subject": "DL-103 update", "body": "Your delivery has not been moved yet. We have asked dispatch; it is not confirmed until they agree.",
             "purpose": "honest status"},
            {"tool": "schedule_follow_up", "when": "before the cutoff", "body": "Check for dispatch's reply.", "purpose": "cutoff"},
        ],
        not_doing=["Not telling the recipient the delivery is moved before dispatch confirms"],
        follow_up="Check for dispatch's email reply before the cutoff.")


def _cleanup(conn):
    conn.execute("delete from agent_events where case_id = %s", (CASE,))
    conn.execute("delete from shipments where case_id = %s or id = 'DL-103-T'", (CASE,))
    conn.execute("delete from cases where id = %s", (CASE,))
    for d in (ROOT / "runs" / "live").glob(f"{CASE}-*"):
        shutil.rmtree(d, ignore_errors=True)


def test_call_plan_review_approve_reject():
    from db.seed_demo import d103, seed_case
    from deskagent import llm as llm_mod
    from hub import pipeline_driver
    from hub.config import settings
    from hub.webhooks import AskAgentIn, ask_agent
    from test_offline import APPROVE, _install_fake

    assert settings.engine == "pipeline"
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
        _cleanup(conn)
        spec = d103(datetime.now(timezone.utc), CUSTOMER)
        spec["id"], spec["shipment"]["id"] = CASE, "DL-103-T"
        seed_case(conn, spec)
    try:
        fake = _install_fake([("propose_plan", _plan()), ("submit_review", APPROVE)])
        llm_mod._ModelState.dead.clear()

        out = ask_agent(AskAgentIn(request=CALL, case_id=CASE))       # returns at once; the run is in the background
        assert out["case_id"] == CASE and CASE in out["say"]
        pipeline_driver._workers[CASE].join(timeout=60)
        assert len(fake.messages.calls) == 2, "planner + reviewer"

        from hub import db
        acts = db.query("select id, tool, status, args from actions where case_id = %s order by id", (CASE,))
        sends = [a for a in acts if a["tool"] == "send_message"]
        assert [a["status"] for a in sends] == ["pending_approval", "pending_approval"], acts
        assert {a["args"]["to_party"] for a in sends} == {"Dispatch, Plover Arc Logistics", CUSTOMER}
        assert any(a["tool"] == "schedule_follow_up" and a["status"] == "done" for a in acts)
        case = db.one("select status, decision from cases where id = %s", (CASE,))
        assert case["decision"]["decision_type"] == "act" and case["status"] == "in_progress"
        types = {r["type"] for r in db.query("select type from agent_events where case_id = %s", (CASE,))}
        assert {"user.message", "agent.message", "agent.mcp_tool_use", "session.status_idle"} <= types
        assert db.one("select status, stop_reason from agent_runs where case_id = %s", (CASE,))["stop_reason"] == "end_turn"
        history = next((ROOT / "runs" / "live").glob(f"{CASE}-*/{CASE}/history.md")).read_text()
        assert CALL in history and "Phone call" in history
        assert next((ROOT / "runs" / "live").glob(f"{CASE}-*/answers/*/ANSWER.md")).exists()

        to_customer = next(a for a in sends if a["args"]["to_party"] == CUSTOMER)
        to_dispatch = next(a for a in sends if a is not to_customer)
        assert pipeline_driver.confirm(to_customer["id"], True, "Iona Quill")["result"] == "allow"
        assert db.one("select status from actions where id = %s", (to_customer["id"],))["status"] == "done"
        msg = db.one("select body from case_events where case_id = %s and kind = 'agent_message' and to_party = %s",
                     (CASE, CUSTOMER))
        assert msg and "not confirmed" in msg["body"]

        assert pipeline_driver.confirm(to_dispatch["id"], False, "Iona Quill", "wrong slot")["result"] == "deny"
        assert db.one("select status from actions where id = %s", (to_dispatch["id"],))["status"] == "rejected"
        assert not db.one("select 1 from case_events where case_id = %s and kind = 'agent_message' and to_party like 'Dispatch%%'", (CASE,))
    finally:
        with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
            _cleanup(conn)


def test_voice_tools_accept_tracking_refs_and_say_honest_status():
    from db.seed_demo import d103, seed_case
    from hub import db
    from hub.webhooks import CaseIn, _case_ref, get_latest_update

    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
        _cleanup(conn)
        spec = d103(datetime.now(timezone.utc), CUSTOMER)
        spec["id"], spec["shipment"]["id"] = CASE, "DL-103-T"
        seed_case(conn, spec)
    try:
        assert _case_ref("dl-103-t") == CASE and _case_ref(f" {CASE.lower()} ") == CASE and _case_ref("DL-NOPE") is None
        assert "couldn't find" in get_latest_update(CaseIn(case_id="DL-NOPE"))["say"]
        db.query("insert into agent_runs (session_id, case_id, status) values ('pipeline-test-run', %s, 'running')", (CASE,))
        assert "still working" in get_latest_update(CaseIn(case_id="DL-103-T"))["say"]
        db.query("update agent_runs set status = 'idle' where session_id = 'pipeline-test-run'")
        db.query("""insert into actions (case_id, tool, args, status) values (%s, 'send_message', %s, 'pending_approval')""",
                 (CASE, db.jsonb({"to_party": "Unidentified caller", "channel": "Phone", "subject": "", "body": "x"})))
        assert "waiting for a coordinator" in get_latest_update(CaseIn(case_id="DL-103-T"))["say"]

        from hub.webhooks import _caller
        prof =db.one("select id, phone from profiles where role = 'customer' order by email limit 1")
        if prof:   # seeded demo customer: both phone formats map to the same account
            db.query("update profiles set phone = '+44 7700 900199' where id = %s", (prof["id"],))
            try:
                assert _caller("07700 900199")["id"] == prof["id"] and _caller("+447700900199")["id"] == prof["id"]
                assert _caller("123")["party_name"] == "Caller 123"
            finally:
                db.query("update profiles set phone = %s where id = %s", (prof["phone"], prof["id"]))
    finally:
        with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
            _cleanup(conn)


def test_render_case_keeps_event_format():
    from hub import pipeline_driver
    from deskagent.loader import parse_events
    assert pipeline_driver._body("## 2026-01-01 00:00 — event 9\nok") == " ## 2026-01-01 00:00 — event 9\nok"
    hist = "\n".join([f'<a id="event-001"></a>', "## 2026-10-10 12:00:00 UTC — event 001", "",
                      "- **Channel:** Phone call", "- **From:** Caller", "- **To:** Desk", "", pipeline_driver._body("hi"), ""])
    ev = parse_events(hist)
    assert len(ev) == 1 and ev[0].meta["channel"] == "Phone call" and ev[0].body.strip() == "hi"


if __name__ == "__main__":
    if not _db_up():
        print("skip: database not reachable or not migrated (set DATABASE_URL, run python -m db.migrate --local)")
        sys.exit(0)
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok {name}")
    from hub import db
    db.pool().close()
