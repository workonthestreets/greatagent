"""Pipeline engine for the live desk (DESK_ENGINE=pipeline).

Runs the evaluated deskagent pipeline (planner -> policy lint -> independent reviewer) on a case read from the
database, then carries out the approved plan through the same desk tools the Managed Agent uses (hub/mcp_tools.py).
So /ops, approvals, the party views and the voice webhooks behave the same with either engine.

Same interface as hub/driver.py: wake() and confirm(). Outbound messages wait in the approvals queue
(AGENT_APPROVAL_TOOLS, default send_message) unless AGENT_AUTO_APPROVE=1. Every run keeps its input
(index.md, history.md) and ANSWER.md / REASONING.md / trace.json under runs/live/<run_id>/ for audit.
"""
from __future__ import annotations

import logging
import os
import threading
import uuid
from datetime import datetime, timezone

from deskagent.loader import load_case
from deskagent.pipeline import process_case
from deskagent.policy import lint_text
from deskagent.report import write_case

from . import db, mcp_tools
from .config import ROOT, settings

log = logging.getLogger("hub.pipeline")

RUNS_DIR = ROOT / "runs" / "live"
PRIORITIES = {"low", "normal", "high", "urgent"}

_lock = threading.Lock()
_workers: dict[str, threading.Thread] = {}
_again: dict[str, str] = {}             # case_id -> wake text that arrived while a run was in progress
_slots = threading.Semaphore(3)         # at most 3 cases planning at once


# ------------------------------------------------------------------ case -> deskagent input
def _ts(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _body(text: str) -> str:
    # A body line that looks like an event heading would split the event in the loader; indent it.
    return "\n".join(" " + line if line.startswith("#") or line.startswith("<a id=") else line
                     for line in (text or "").strip().splitlines())


def render_case(case_id: str) -> tuple[str, str]:
    """index.md and history.md for one case, in the same format as the case folders the CLI reads."""
    case = db.one("select * from cases where id = %s", (case_id,))
    if not case:
        raise ValueError(f"unknown case {case_id}")
    parties = db.query("select party_name, role from case_parties where case_id = %s order by role, party_name", (case_id,))
    shipment = db.one("select * from shipments where id = %s", (case["shipment_id"],)) if case.get("shipment_id") else None
    events = db.query(
        """select ts, channel, author, author_role, to_party, kind, visibility, body from case_events
           where case_id = %s order by ts, id""", (case_id,))
    desk = case.get("coordinator") or "Rivet Delivery Desk"

    idx = [f"# Case {case_id}: {case['title']}", "", "## Case details", ""]
    if case.get("source_name"):
        idx.append(f"- **Source role:** {case['source_name']}" + (f", {case['source_role']}" if case.get("source_role") else ""))
    if case.get("shipment_id"):
        idx.append(f"- **Primary shipment:** {case['shipment_id']}")
    idx += [f"- **Coordinator:** {desk}", "- **Data:** live desk record; all times UTC"]
    if case.get("context"):
        idx += ["", "## Context", "", case["context"].strip()]
    if case.get("initial_request"):
        idx += ["", "## Initial request", "", case["initial_request"].strip()]
    if parties:
        idx += ["", "## Parties on file", ""] + [f"- {p['party_name']} ({p['role'] or 'role unknown'})" for p in parties]
    if shipment:
        idx += ["", "## Shipment record", "",
                f"- {shipment['id']}: status {shipment.get('status') or 'unknown'}" + (f"; {shipment['eta']}" if shipment.get("eta") else "")]
    idx += ["", "## History", "", "[Read the complete dated history](history.md)."]

    hist = [f"# Case {case_id} history — {case['title']}", "", f"Total events: {len(events)}.", ""]
    for n, e in enumerate(events, 1):
        author = desk if e["author_role"] == "agent" else (e["author"] or "Unknown sender")
        channel = e["channel"] or "Not specified"
        if e["visibility"] == "staff" and "internal" not in channel.lower():
            channel += " (internal, staff only)"
        hist += [f'<a id="event-{n:03d}"></a>', f"## {_ts(e['ts'])} — event {n:03d}", "",
                 f"- **Channel:** {channel}", f"- **From:** {author}", f"- **To:** {e['to_party'] or desk}", "",
                 _body(e["body"]), ""]
    return "\n".join(idx) + "\n", "\n".join(hist) + "\n"


def _party(case_id: str, to_name: str, to_role: str) -> str:
    """Map the planner's recipient to the exact party name on file, so party views and voice lookups find it."""
    names = [p["party_name"] for p in db.query("select party_name from case_parties where case_id = %s", (case_id,))]
    want = (to_name or "").strip().lower()
    if want:
        for n in names:
            if n.lower() == want:
                return n
        for n in names:
            head = n.split(",")[0].strip().lower()
            if head == want or want in n.lower() or (head and head in want):
                return n
    return to_name or to_role or "Unknown party"


# ------------------------------------------------------------------ run bookkeeping (mirrors the Managed Agents events)
def _event(run: dict, etype: str, payload: dict) -> None:
    db.query(
        """insert into agent_events (event_id, session_id, case_id, type, payload) values (%s, %s, %s, %s, %s)
           on conflict (event_id) do nothing""",
        (f"{run['session_id']}:{uuid.uuid4().hex[:12]}", run["session_id"], run["case_id"], etype, db.jsonb(payload)))


def _say(run: dict, text: str) -> None:
    _event(run, "agent.message", {"content": [{"type": "text", "text": text}]})


def _new_run(case_id: str, text: str) -> dict:
    run_id = f"{case_id}-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:4]}"
    run = {"run_id": run_id, "session_id": f"pipeline-{run_id}", "case_id": case_id, "dir": RUNS_DIR / run_id}
    db.query("update cases set session_id = %s where id = %s", (run["session_id"], case_id))
    db.query("""insert into agent_runs (session_id, case_id, status) values (%s, %s, 'running')
                on conflict (session_id) do nothing""", (run["session_id"], case_id))
    _event(run, "user.message", {"content": [{"type": "text", "text": text}]})
    return run


def _finish(run: dict, stop_reason: str) -> None:
    db.query("update agent_runs set status = 'idle', stop_reason = %s, updated_at = now() where session_id = %s",
             (stop_reason, run["session_id"]))
    _event(run, "session.status_idle", {"stop_reason": {"type": stop_reason}})


# ------------------------------------------------------------------ one pipeline run
def _process(run: dict) -> None:
    case_id = run["case_id"]
    index_md, history_md = render_case(case_id)
    folder = run["dir"] / case_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.md").write_text(index_md, encoding="utf-8")
    (folder / "history.md").write_text(history_md, encoding="utf-8")

    _say(run, "Reading the case and planning the next step (planner, then policy lint, then an independent reviewer).")
    res = process_case(load_case(folder), model=os.environ.get("DESK_MODEL") or None, review=True, trace=[])
    write_case(run["dir"] / "answers", res)

    for r in res["review_rounds"]:
        _say(run, f"Planner, round {r['round']}: {r.get('plan_decision')} — {r.get('plan_summary') or ''}")
        lint = [l for l in r.get("lint") or [] if not l.get("negated_context")]
        if lint:
            _say(run, "Policy lint: " + "; ".join(f"{l['level']} {l['rule']} '{l.get('match', '')}'" for l in lint)[:600])
        rv = r.get("review") or {}
        serious = [i for i in rv.get("issues") or [] if i.get("severity") in ("critical", "major")]
        _say(run, f"Independent reviewer, round {r['round']}: {rv.get('verdict')} — {rv.get('summary', '')}"
             + ("".join(f" [{i['severity']}] {i.get('problem')}" for i in serious)))
    plan = res["plan"]
    if not res["approved"]:
        _say(run, "No plan was approved as safe, so the case goes to a human with the drafts attached (nothing sent).")
    _say(run, f"Decision: {plan.get('decision_type')} — {plan.get('decision_summary')}")

    for e in res["executed"]:
        _carry_out(run, e)

    not_doing = plan.get("not_doing") or []
    decision = dict(decision_type=plan.get("decision_type") or "escalate_to_human",
                    summary=plan.get("decision_summary") or "",
                    rationale=plan.get("rationale") or "",
                    not_doing="; ".join(not_doing) if isinstance(not_doing, list) else str(not_doing),
                    next_trigger=plan.get("follow_up") or plan.get("proof_standard") or "")
    mcp_tools.submit_decision(case_id, **decision)
    _event(run, "agent.mcp_tool_use", {"name": "submit_decision", "input": decision, "evaluated_permission": "allow"})
    log.info("case %s: pipeline run %s done (%s, approved=%s)", case_id, run["run_id"], decision["decision_type"], res["approved"])


def _carry_out(run: dict, e: dict) -> None:
    """Replay one executed pipeline action through the desk tools; outbound messages wait for approval."""
    a, case_id = e["action"], run["case_id"]
    tool = a.get("tool")
    if tool == "send_message":
        args = {"to_party": _party(case_id, a.get("to_name", ""), a.get("to_role", "")),
                "channel": a.get("channel") or "Email", "subject": a.get("subject") or "", "body": a.get("body") or ""}
        if e["status"] != "done":
            db.query("""insert into actions (case_id, session_id, tool, args, status, result)
                        values (%s, %s, 'send_message', %s, 'failed', %s)""",
                     (case_id, run["session_id"], db.jsonb(args), db.jsonb({"error": e.get("error")})))
            return   # the pipeline already added a recovery handover, replayed next
        if tool in settings.approval_tools and not settings.auto_approve:
            row = db.one("""insert into actions (case_id, session_id, tool, args, status, policy)
                            values (%s, %s, 'send_message', %s, 'pending_approval', %s) returning id""",
                         (case_id, run["session_id"], db.jsonb(args), db.jsonb(lint_text(f"{args['subject']}\n{args['body']}"))))
            _event(run, "agent.mcp_tool_use", {"name": "send_message", "input": args, "evaluated_permission": "ask",
                                               "action_id": row["id"]})
            return
        out = mcp_tools.send_message(case_id, **args)
    elif tool == "escalate_to_human":
        priority = (a.get("priority") or "high").lower()
        args = {"to_name": a.get("to_name") or "Desk supervisor",
                "subject": a.get("subject") or f"Case {case_id} needs a human decision",
                "body": a.get("body") or "", "priority": priority if priority in PRIORITIES else "high"}
        out = mcp_tools.escalate_to_human(case_id, **args)
    elif tool == "schedule_follow_up":
        args = {"when": a.get("when") or "next desk check", "body": a.get("body") or a.get("purpose") or ""}
        out = mcp_tools.schedule_follow_up(case_id, **args)
    elif tool == "record_case_note":
        args = {"body": a.get("body") or ""}
        out = mcp_tools.record_case_note(case_id, **args)
    else:
        log.warning("case %s: skipping unknown tool %s", case_id, tool)
        return
    _event(run, "agent.mcp_tool_use", {"name": tool, "input": args, "evaluated_permission": "allow"})
    _event(run, "agent.mcp_tool_result", {"content": out})


def _worker(case_id: str, run: dict) -> None:
    while True:
        try:
            with _slots:
                _process(run)
            _finish(run, "end_turn")
        except Exception as exc:  # noqa: BLE001 - never fail silently: the case goes to a human
            log.exception("case %s: pipeline run %s failed", case_id, run["run_id"])
            _event(run, "session.error", {"error": {"message": f"{type(exc).__name__}: {exc}"[:500]}})
            _finish(run, "error")
            try:
                mcp_tools.escalate_to_human(
                    case_id, "Desk supervisor", f"Agent run failed on case {case_id}",
                    f"The pipeline run {run['run_id']} failed ({type(exc).__name__}: {exc}). Nothing was sent. "
                    "Please handle this case or ask the agent to re-assess.", "high")
            except Exception:  # noqa: BLE001
                log.exception("case %s: could not record the failure handover", case_id)
        with _lock:
            text = _again.pop(case_id, None)
            if text is None:
                _workers.pop(case_id, None)
                return
        run = _new_run(case_id, text)


# ------------------------------------------------------------------ driver interface
def wake(case_id: str, text: str, *, wait: bool = False) -> str:
    """Plan the case now (in the background). If a run is already going, plan once more when it ends."""
    if not db.one("select 1 from cases where id = %s", (case_id,)):
        raise ValueError(f"unknown case {case_id}")
    with _lock:
        worker = _workers.get(case_id)
        if worker and worker.is_alive():
            _again[case_id] = text
            session_id = db.one("select session_id from cases where id = %s", (case_id,))["session_id"]
        else:
            run = _new_run(case_id, text)
            session_id = run["session_id"]
            worker = threading.Thread(target=_worker, args=(case_id, run), daemon=True, name=f"pipeline-{case_id}")
            _workers[case_id] = worker
            worker.start()
    if wait:
        worker.join()
    return session_id


def confirm(action_id: int, allow: bool, by: str, reason: str = "") -> dict:
    """Answer a pending action from the approvals queue: send it through the desk tool, or record the rejection."""
    action = db.one("select * from actions where id = %s", (action_id,))
    if not action or action["status"] != "pending_approval":
        raise ValueError("action is not waiting for approval")
    run = {"session_id": action["session_id"] or f"pipeline-{action['case_id']}", "case_id": action["case_id"]}
    args = action["args"]
    if not allow:
        db.query("update actions set status = 'rejected', decided_by = %s, result = %s, updated_at = now() where id = %s",
                 (by, db.jsonb({"reason": reason} if reason else None), action_id))
        _event(run, "user.tool_confirmation", {"result": "deny", "deny_message": f"Rejected by {by}: {reason or 'no reason given'}"})
        mcp_tools.record_case_note(action["case_id"], f"{by} rejected the drafted {action['tool']} to {args.get('to_party')} "
                                                      f"({reason or 'no reason given'}). It was not sent.")
        return {"action_id": action_id, "result": "deny"}
    db.query("update actions set status = 'approved', decided_by = %s, updated_at = now() where id = %s", (by, action_id))
    _event(run, "user.tool_confirmation", {"result": "allow"})
    out = mcp_tools.send_message(action["case_id"], args["to_party"], args["channel"], args.get("subject", ""), args["body"])
    _event(run, "agent.mcp_tool_result", {"content": out})
    return {"action_id": action_id, "result": "allow", "detail": out}
