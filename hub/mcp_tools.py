"""The agent's tools, served over MCP at /mcp. Every write is checked by deskagent.policy and recorded in `actions`."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Literal, Optional

from mcp.server.mcpserver import MCPServer

from deskagent.policy import lint_text, record_numbers

from . import db

DOCS_DIR = Path(__file__).resolve().parent / "docs"

mcp = MCPServer(
    "greatagent-desk",
    instructions="Tools for the Rivet Delivery Desk: read the case and the database, act on the case, record the decision.",
)

SCHEMA_HINT = """Tables (Postgres):
- cases(id, title, status, source_name, source_role, coordinator, shipment_id, context, initial_request, decision jsonb, decision_summary, created_at, updated_at)
- case_parties(case_id, party_name, role)   role in customer/driver/depot/merchant/coordinator
- shipments(id, case_id, description, status, recipient_name, merchant, depot, driver_name, eta, updated_at)
- case_events(id, case_id, ts, channel, author, author_role, to_party, kind, visibility, body, meta jsonb)
- actions(id, case_id, tool, args jsonb, status, policy jsonb, result jsonb, created_at)"""


def _json(value) -> str:
    return json.dumps(value, default=str, ensure_ascii=False, indent=1)


def _case(case_id: str) -> dict:
    row = db.one("select * from cases where id = %s", (case_id,))
    if not row:
        raise ValueError(f"unknown case_id {case_id!r}")
    return row


def _record(case: dict, tool: str, args: dict, status: str, policy=None, result=None) -> int:
    """Complete the approved row for this call if a human approved it, else insert a new action row."""
    row = db.one(
        """update actions set status = %s, policy = %s, result = %s, updated_at = now()
           where id = (select id from actions where case_id = %s and tool = %s and status = 'approved'
                       order by id limit 1)
           returning id""",
        (status, db.jsonb(policy or []), db.jsonb(result), case["id"], tool))
    if row:
        return row["id"]
    row = db.one(
        """insert into actions (case_id, session_id, tool, args, status, policy, result)
           values (%s, %s, %s, %s, %s, %s, %s) returning id""",
        (case["id"], case.get("session_id"), tool, db.jsonb(args), status, db.jsonb(policy or []), db.jsonb(result)))
    return row["id"]


def _event(case_id: str, kind: str, body: str, *, channel: str = "", to_party: Optional[str] = None,
           visibility: str = "all", meta: Optional[dict] = None) -> None:
    db.query(
        """insert into case_events (case_id, channel, author, author_role, to_party, kind, visibility, body, meta)
           values (%s, %s, 'Desk AI coordinator', 'agent', %s, %s, %s, %s, %s)""",
        (case_id, channel, to_party, kind, visibility, body, db.jsonb(meta or {})))
    db.query("update cases set updated_at = now() where id = %s", (case_id,))


# ------------------------------------------------------------------ read tools
@mcp.tool()
def get_case(case_id: str) -> str:
    """Get one case: details, parties, shipment, the full dated timeline (oldest first) and the actions already taken."""
    case = _case(case_id)
    parties = db.query("select party_name, role from case_parties where case_id = %s order by role", (case_id,))
    shipment = db.one("select * from shipments where id = %s", (case["shipment_id"],)) if case["shipment_id"] else None
    timeline = db.query(
        """select ts, channel, author, to_party, kind, visibility, body from case_events
           where case_id = %s order by ts, id""", (case_id,))
    actions = db.query(
        "select created_at, tool, status, args, result from actions where case_id = %s order by id", (case_id,))
    case.pop("session_id", None)
    return _json({"case": case, "parties": parties, "shipment": shipment, "timeline": timeline, "actions_taken": actions})


@mcp.tool(description="Run one read-only SQL query (SELECT/WITH) against the desk database. Max 200 rows, 5s timeout.\n" + SCHEMA_HINT)
def read_sql(sql: str) -> str:
    try:
        return _json(db.read_only_query(sql))
    except db.QueryRejected as exc:
        return f"REJECTED: {exc}"
    except Exception as exc:  # noqa: BLE001 - SQL errors go back to the agent to fix its query
        return f"SQL ERROR: {str(exc).splitlines()[0][:300]}"


@mcp.tool()
def search_docs(query: str) -> str:
    """Search desk policies and playbooks (who owns which decision, escalation rules). Returns the best-matching sections."""
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    scored = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        for section in re.split(r"\n(?=#{1,3} )", path.read_text()):
            text = section.lower()
            score = sum(text.count(w) for w in words)
            if score:
                scored.append((score, path.name, section.strip()[:2500]))
    scored.sort(key=lambda s: -s[0])
    if not scored:
        return "No matching sections."
    return "\n\n---\n\n".join(f"[{name}]\n{text}" for _, name, text in scored[:3])


# ------------------------------------------------------------------ action tools
@mcp.tool()
def send_message(case_id: str, to_party: str, channel: str, subject: str, body: str) -> str:
    """Send a message to one party on the case (use the exact party name from get_case). It is delivered as written,
    on the given channel (e.g. "Customer portal", "Email", "SMS", "Depot channel")."""
    case = _case(case_id)
    args = {"to_party": to_party, "channel": channel, "subject": subject, "body": body}
    record_text = " ".join(e["body"] for e in db.query("select body from case_events where case_id = %s", (case_id,)))
    findings = lint_text(f"{subject}\n{body}", frozenset(record_numbers(record_text)))
    blocks = [f for f in findings if f["level"] == "BLOCK"]
    if blocks:
        _record(case, "send_message", args, "blocked", findings, {"error": "policy block"})
        return "BLOCKED by policy: " + "; ".join(f"{f['rule']} ({f['match']})" for f in blocks) + ". Rewrite without it."
    _event(case_id, "agent_message", f"{subject}\n\n{body}".strip(), channel=channel, to_party=to_party,
           meta={"subject": subject})
    action_id = _record(case, "send_message", args, "done", findings, {"delivered_to": to_party})
    warns = [f["rule"] for f in findings if f["level"] == "WARN" and not f.get("negated_context")]
    return f"Sent to {to_party} via {channel} (action {action_id})." + (f" Policy warnings logged: {', '.join(warns)}." if warns else "")


@mcp.tool()
def escalate_to_human(case_id: str, to_name: str, subject: str, body: str,
                      priority: Literal["low", "normal", "high", "urgent"] = "normal") -> str:
    """Hand the case to a human (desk supervisor or a named team) with a complete handover: what happened, verified facts,
    what was done, the risk, and the specific decision needed."""
    case = _case(case_id)
    args = {"to_name": to_name, "subject": subject, "body": body, "priority": priority}
    _event(case_id, "note", f"ESCALATION to {to_name} [{priority}]: {subject}\n\n{body}", channel="Internal",
           to_party=to_name, visibility="staff")
    db.query("update cases set status = 'escalated' where id = %s", (case_id,))
    action_id = _record(case, "escalate_to_human", args, "done", lint_text(body), {"escalated_to": to_name})
    return f"Escalated to {to_name} (action {action_id}); case status is now escalated."


@mcp.tool()
def schedule_follow_up(case_id: str, when: str, body: str) -> str:
    """Schedule a follow-up for the desk (when: ISO time or a plain trigger like "after dispatch replies")."""
    case = _case(case_id)
    _event(case_id, "note", f"Follow-up scheduled for {when}: {body}", channel="Internal", visibility="staff")
    action_id = _record(case, "schedule_follow_up", {"when": when, "body": body}, "done", None, {"when": when})
    return f"Follow-up scheduled for {when} (action {action_id})."


@mcp.tool()
def record_case_note(case_id: str, body: str) -> str:
    """Add an internal note to the case (staff only, never shown to customers or partners)."""
    case = _case(case_id)
    _event(case_id, "note", body, channel="Internal", visibility="staff")
    action_id = _record(case, "record_case_note", {"body": body}, "done")
    return f"Note recorded (action {action_id})."


@mcp.tool()
def update_case_status(case_id: str, status: Literal["open", "in_progress", "waiting", "escalated", "resolved"],
                       reason: str) -> str:
    """Change the case status, with a short reason for the record."""
    case = _case(case_id)
    db.query("update cases set status = %s, updated_at = now() where id = %s", (status, case_id))
    _event(case_id, "system", f"Status changed to {status}: {reason}", channel="Internal", visibility="staff")
    action_id = _record(case, "update_case_status", {"status": status, "reason": reason}, "done")
    return f"Status is now {status} (action {action_id})."


@mcp.tool()
def submit_decision(case_id: str,
                    decision_type: Literal["act", "request_information", "hold_no_action", "escalate_to_human", "decline"],
                    summary: str, rationale: str, not_doing: str, next_trigger: str) -> str:
    """Record your decision for this wake-up. Call exactly once, last. summary: one or two sentences a coordinator reads
    first. not_doing: what you deliberately did not do and why. next_trigger: what event or time moves the case next."""
    case = _case(case_id)
    decision = {"decision_type": decision_type, "summary": summary, "rationale": rationale,
                "not_doing": not_doing, "next_trigger": next_trigger}
    status = {"hold_no_action": "waiting", "request_information": "waiting", "escalate_to_human": "escalated",
              "decline": "resolved"}.get(decision_type, "in_progress")
    if case["status"] == "escalated" and status != "escalated":
        status = "escalated"
    db.query("update cases set decision = %s, decision_summary = %s, status = %s, updated_at = now() where id = %s",
             (db.jsonb(decision), summary, status, case_id))
    _event(case_id, "decision", f"[{decision_type}] {summary}\n\nNext: {next_trigger}", channel="Internal",
           visibility="staff", meta=decision)
    _record(case, "submit_decision", decision, "done")
    return "Decision recorded."
