"""Session driver: one Managed Agents session per case. Starts or continues it, mirrors every session event
into agent_events, turns paused tool calls into pending approvals, and records run status and cost."""
from __future__ import annotations

import logging
import threading
from typing import Optional

import anthropic

from . import db, pipeline_driver
from .config import agent_state, settings

log = logging.getLogger("hub.driver")

_client: Optional[anthropic.Anthropic] = None
_followers: dict[str, threading.Thread] = {}
_lock = threading.Lock()


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=3)
    return _client


def _state() -> dict:
    st = agent_state()
    if not st.get("agent_id") or not st.get("environment_id"):
        raise RuntimeError("agent not set up: run `python -m hub.setup_agent` first")
    return st


# ------------------------------------------------------------------ sessions
def _new_session(case: dict) -> str:
    st = _state()
    session = client().beta.sessions.create(
        agent=st["agent_id"],
        environment_id=st["environment_id"],
        vault_ids=[st["vault_id"]] if st.get("vault_id") else [],
        title=f"Case {case['id']}: {case['title']}"[:200],
        metadata={"case_id": case["id"]},
        budget={"type": "limit", "max_list_cost": {"amount": str(settings.session_budget_cents), "currency": "USD"}},
    )
    db.query("update cases set session_id = %s where id = %s", (session.id, case["id"]))
    db.query(
        """insert into agent_runs (session_id, case_id, status, trace_url) values (%s, %s, %s, %s)
           on conflict (session_id) do nothing""",
        (session.id, case["id"], session.status, settings.trace_url(session.id)))
    log.info("case %s: new session %s  trace %s", case["id"], session.id, settings.trace_url(session.id))
    return session.id


def _usable(session_id: Optional[str]) -> bool:
    if not session_id:
        return False
    try:
        s = client().beta.sessions.retrieve(session_id=session_id)
    except anthropic.NotFoundError:
        return False
    return s.status != "terminated" and not getattr(s, "archived_at", None)


def wake(case_id: str, text: str, *, wait: bool = False) -> str:
    """Wake the agent on a case with a message. Creates the case's session on first use. Returns the session ID."""
    if settings.engine == "pipeline":
        return pipeline_driver.wake(case_id, text, wait=wait)
    case = db.one("select * from cases where id = %s", (case_id,))
    if not case:
        raise ValueError(f"unknown case {case_id}")
    session_id = case["session_id"] if _usable(case["session_id"]) else _new_session(case)
    message = {"type": "user.message", "content": [{"type": "text", "text": f"[case_id: {case_id}]\n{text}"}]}
    _follow(session_id, case_id, send=[message], wait=wait)
    return session_id


def confirm(action_id: int, allow: bool, by: str, reason: str = "") -> dict:
    """Answer a paused tool call from the approvals queue."""
    if settings.engine == "pipeline":
        return pipeline_driver.confirm(action_id, allow, by, reason)
    action = db.one("select * from actions where id = %s", (action_id,))
    if not action or action["status"] != "pending_approval":
        raise ValueError("action is not waiting for approval")
    event = {"type": "user.tool_confirmation", "tool_use_id": action["mcp_event_id"], "result": "allow" if allow else "deny"}
    if not allow:
        event["deny_message"] = f"Rejected by {by}: {reason or 'no reason given'}"
    db.query("update actions set status = %s, decided_by = %s, result = %s, updated_at = now() where id = %s",
             ("approved" if allow else "rejected", by, db.jsonb({"reason": reason} if reason else None), action_id))
    _follow(action["session_id"], action["case_id"], send=[event])
    return {"action_id": action_id, "result": event["result"]}


# ------------------------------------------------------------------ event mirror
def _follow(session_id: str, case_id: str, send: Optional[list] = None, wait: bool = False) -> None:
    """Stream the session until it settles. Opens the stream before sending (stream-first), backfills from history."""
    with _lock:
        running = _followers.get(session_id)
        if running and running.is_alive():
            if send:
                client().beta.sessions.events.send(session_id=session_id, events=send)
            if wait:
                running.join()
            return
        t = threading.Thread(target=_run_follower, args=(session_id, case_id, send), daemon=True,
                             name=f"follow-{session_id[-8:]}")
        _followers[session_id] = t
        t.start()
    if wait:
        t.join()


def _store(event, session_id: str, case_id: str) -> bool:
    payload = event.model_dump(mode="json") if hasattr(event, "model_dump") else dict(event)
    row = db.one(
        """insert into agent_events (event_id, session_id, case_id, type, payload) values (%s, %s, %s, %s, %s)
           on conflict (event_id) do nothing returning id""",
        (payload.get("id") or f"{session_id}:{payload.get('type')}:{id(event)}", session_id, case_id,
         payload.get("type", "unknown"), db.jsonb(payload)))
    return row is not None


def _handle(event, session_id: str, case_id: str) -> Optional[str]:
    """Process one event. Returns 'stop' when the session has settled."""
    if not _store(event, session_id, case_id):
        return None   # already handled (backfill overlap)
    etype = event.type
    if etype in ("agent.mcp_tool_use", "agent.tool_use") and getattr(event, "evaluated_permission", None) == "ask":
        tool = getattr(event, "name", "") or ""
        args = getattr(event, "input", {}) or {}
        db.query(
            """insert into actions (case_id, session_id, tool, args, status, mcp_event_id)
               values (%s, %s, %s, %s, 'pending_approval', %s) on conflict (mcp_event_id) do nothing""",
            (case_id, session_id, tool, db.jsonb(args), event.id))
        log.info("case %s: %s waiting for approval", case_id, tool)
        if settings.auto_approve:
            db.query("update actions set status = 'approved', decided_by = 'auto' where mcp_event_id = %s", (event.id,))
            client().beta.sessions.events.send(session_id=session_id, events=[
                {"type": "user.tool_confirmation", "tool_use_id": event.id, "result": "allow"}])
    elif etype == "session.status_idle":
        reason = getattr(getattr(event, "stop_reason", None), "type", None)
        _update_run(session_id, "idle", reason)
        if reason != "requires_action":
            return "stop"
    elif etype == "session.status_running":
        _update_run(session_id, "running", None)
    elif etype == "session.status_terminated":
        _update_run(session_id, "terminated", None)
        return "stop"
    elif etype == "session.error":
        log.warning("case %s: session error %s", case_id, getattr(event, "error", event))
    return None


def _update_run(session_id: str, status: str, stop_reason: Optional[str]) -> None:
    cost = None
    if status != "running":
        try:
            usage = client().beta.sessions.retrieve(session_id=session_id).usage
            lc = getattr(usage, "list_cost", None)
            cost = int(lc.amount) if lc is not None else None
        except Exception:  # noqa: BLE001 - cost is informational
            pass
    db.query(
        """update agent_runs set status = %s, stop_reason = %s, list_cost_cents = coalesce(%s, list_cost_cents),
               updated_at = now() where session_id = %s""", (status, stop_reason, cost, session_id))


def _run_follower(session_id: str, case_id: str, send: Optional[list]) -> None:
    try:
        with client().beta.sessions.events.stream(session_id=session_id) as stream:
            if send:
                client().beta.sessions.events.send(session_id=session_id, events=send)
            else:
                # Re-attaching (e.g. after an approval or a hub restart): catch up on anything missed.
                for ev in client().beta.sessions.events.list(session_id=session_id):
                    _store(ev, session_id, case_id)
            for ev in stream:
                if _handle(ev, session_id, case_id) == "stop":
                    break
    except Exception:  # noqa: BLE001 - a follower must never take the hub down
        log.exception("follower for %s failed", session_id)
    finally:
        with _lock:
            if _followers.get(session_id) is threading.current_thread():
                _followers.pop(session_id, None)
