"""Hand a voice call to the team's deskagent: the call becomes a case folder, deskagent decides.

Capture-line mode. The call is written in the same index.md + history.md shape the organisers'
cases use, then `deskagent.loader.load_case` and `deskagent.pipeline.process_case` run in a
background thread with the reviewer on. The caller only ever hears fixed templates; deskagent's
decision lands in `<case>/_result.json` (underscore: deskagent never reads it as input), `<case>/answer/<id>/ANSWER.md` and the outbox.

deskagent is imported, never edited. Before the merge it comes from a read-only checkout of main
(`DESKAGENT_PATH`); after the merge it is a normal package at the repo root.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections import deque
from datetime import UTC, datetime
from pathlib import Path

from triage.outbox import deliver, slug
from voice import hub_mirror, lookup

CASES_DIR = Path(os.getenv("VOICE_CASES_DIR", "runs/voice/cases"))
DESK_MODEL = "claude-sonnet-5-5"  # cheaper than deskagent's Opus default; VOICE_DESK_MODEL overrides
MAX_AT_ONCE = 2
_threads: dict[str, threading.Thread] = {}  # conversation id -> worker, so tests can join
_running = threading.BoundedSemaphore(MAX_AT_ONCE)
_starts: deque[float] = deque()  # start times of recent runs, for the hourly cap
_cap_lock = threading.Lock()

DECISION_WORDS = {
    "act": "Our desk has acted on it",
    "request_information": "Our desk has asked for the information it needs",
    "escalate_to_human": "Our desk has passed it to a colleague to review",
    "hold_no_action": "Our desk is holding it for now",
    "decline": "Our desk can't action this request as it stands",
}


def _deskagent():
    """deskagent's public functions, plus its API key set for this process only (never a shell)."""
    path = os.getenv("DESKAGENT_PATH")
    if path and path not in sys.path:
        sys.path.insert(0, path)
    if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("APP_ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = os.environ["APP_ANTHROPIC_API_KEY"]
    from deskagent.loader import load_case
    from deskagent.pipeline import process_case
    from deskagent.report import write_case
    return load_case, process_case, write_case


def short_id(conversation_id: str) -> str:
    """A case number a caller can say back: the last four letters or digits of the conversation id."""
    base, _, n = conversation_id.rpartition("-")
    if base and n.isdigit():  # a second problem in the same call: case 6000-2
        return f"{short_id(base)}-{n}"
    tail = "".join(c for c in conversation_id if c.isalnum())[-4:]
    return tail.upper() or "0000"


def write_case_folder(conversation_id: str, caller: str, ref: str, issue: str, how: str, contact: str) -> Path:
    """The call as a case. When the reference matches a known shipment, the desk's own records up to
    the escalation come first and the call is appended as the latest event; otherwise the call alone."""
    folder = CASES_DIR / slug(conversation_id)
    folder.mkdir(parents=True, exist_ok=True)
    caller = caller or "Caller"
    sid = short_id(conversation_id)
    when = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    reach = f"\n- **Updates by:** {how} to {contact}" if how else ""
    match = lookup.find_shipment(ref) if ref else None
    known = lookup.known_context(match) if match else None
    n = len(known.events) + 1 if known else 1
    call_event = (f'<a id="event-{n:03d}"></a>\n## {when} — event {n:03d}\n- **Channel:** Phone call\n'
                  f"- **From:** {caller}, recipient\n- **To:** Delivery desk\n- **Stage:** Escalation\n\n{issue}\n")
    if known:
        (folder / "index.md").write_text(
            f"# Case {sid}: Phone call about shipment {known.primary or ref}\n\n"
            f"## Case details\n{known.details}\n- **Phone call from:** {caller}{reach}\n\n"
            f"## Initial request\n{known.initial_request}\n")
        (folder / "history.md").write_text(
            f"# Case {sid} history\n\n" + "\n\n".join(known.events) + "\n\n" + call_event)
        for rel in known.attachments:  # only files the pre-escalation events link to
            (folder / rel).parent.mkdir(parents=True, exist_ok=True)
            (folder / rel).write_bytes((match / rel).read_bytes())
    else:
        (folder / "index.md").write_text(
            f"# Case {sid}: Phone call to the delivery desk\n\n"
            f"## Case details\n- **Source role:** {caller}, recipient\n"
            f"- **Primary shipment:** {ref or '[reference not given]'}\n- **Created:** {when}{reach}\n\n"
            f"## Initial request\n{issue}\n")
        (folder / "history.md").write_text(f"# Case {sid} history\n\n{call_event}")
    (folder / "_call.json").write_text(json.dumps({"caller": caller, "ref": ref, "issue": issue,
                                                   "update_by": how, "contact": contact}))
    (folder / "_lookup.json").write_text(json.dumps({
        "matched": bool(known), "source_case": known.source_case if known else None,
        "primary": known.primary if known else "", "events_used": len(known.events) if known else 0}))
    return folder


def lookup_info(folder: Path) -> dict:
    path = folder / "_lookup.json"
    return json.loads(path.read_text()) if path.exists() else {"matched": False}


def _deliver_actions(case_id: str, executed: list, folder: Path) -> list:
    """Each message deskagent sent goes to the outbox; the same allowlist rules as every other email."""
    sent = []
    for rec in executed:
        a = rec.get("action") or {}
        if rec.get("status") != "done" or a.get("tool") not in ("send_message", "escalate_to_human"):
            continue
        as_decision = {"team": a.get("to_name") or a.get("to_role") or "desk supervisor", "org": "",
                       "message": a.get("body", ""), "channel": a.get("channel", ""),
                       "missing": a.get("subject") or f"{a.get('channel') or 'message'} update", "escalate": a.get("tool") == "escalate_to_human",
                       "party": "internal" if a.get("tool") == "escalate_to_human" else "other_business"}
        sent.append(deliver(case_id, as_decision, folder / "outbox" / str(rec.get("index"))))
    return sent


def run(conversation_id: str, folder: Path) -> dict:
    """Run deskagent on one call folder and record the outcome. Never raises: a failure is a result."""
    t0 = time.time()
    out: dict
    try:
        load_case, process_case, write_case = _deskagent()
        case = load_case(folder, track="Delivery & Logistics")
        res = process_case(case, model=os.getenv("VOICE_DESK_MODEL") or DESK_MODEL)
        write_case(folder / "answer", res)
        plan = res.get("plan") or {}
        out = {"status": "done", "decision_type": plan.get("decision_type"),
               "decision_summary": plan.get("decision_summary"), "approved": res.get("approved"),
               "contacted": [r["action"].get("to_name") or r["action"].get("to_role")
                             for r in res.get("executed", []) if r.get("status") == "done"
                             and (r.get("action") or {}).get("tool") == "send_message"],
               "emails": _deliver_actions(f"voice-{short_id(conversation_id)}", res.get("executed", []), folder)}
        messages = [{"to": r["action"].get("to_name") or r["action"].get("to_role"),
                     "channel": r["action"].get("channel"), "body": r["action"].get("body", "")}
                    for r in res.get("executed", []) if r.get("status") == "done"
                    and (r.get("action") or {}).get("tool") in ("send_message", "escalate_to_human")]
    except Exception as exc:  # noqa: BLE001 — the caller has already hung up; record it for a human
        out = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"[:500]}
    out["lookup"] = lookup_info(folder)
    if out["status"] == "done" and hub_mirror.configured():  # hub records; it never decides or blocks
        call_path = folder / "_call.json"
        call = json.loads(call_path.read_text()) if call_path.exists() else {}
        out["hub_mirror"] = hub_mirror.post_case(
            hub_mirror.payload(short_id(conversation_id), call, out["lookup"], out, messages))
    out["elapsed_s"] = round(time.time() - t0, 1)
    (folder / "_result.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def _cap_reason() -> str:
    """'' when a run may start; otherwise why not. Protects the API credit the Reality Test needs."""
    per_hour = int(os.getenv("VOICE_DESK_MAX_PER_HOUR", "20"))
    with _cap_lock:
        now = time.time()
        while _starts and now - _starts[0] > 3600:
            _starts.popleft()
        if len(_starts) >= per_hour:
            return f"hourly cap of {per_hour} deskagent runs reached"
        if not _running.acquire(blocking=False):
            return f"{MAX_AT_ONCE} deskagent runs already in progress"
        _starts.append(now)
        return ""


def _run_and_release(conversation_id: str, folder: Path) -> None:
    try:
        run(conversation_id, folder)
    finally:
        _running.release()


def start(conversation_id: str, folder: Path) -> None:
    """Start deskagent on the call unless a cap says no; a capped case stays saved for a human."""
    reason = _cap_reason()
    if reason:
        (folder / "_result.json").write_text(json.dumps({"status": "capped", "reason": reason}))
        return
    (folder / "_result.json").write_text(json.dumps({"status": "pending"}))
    worker = threading.Thread(target=_run_and_release, args=(conversation_id, folder), daemon=True)
    _threads[conversation_id] = worker
    worker.start()


def update_line(conversation_id: str) -> str:
    """What a later call hears about the case. Templates only; names are short and digit-free."""
    path = CASES_DIR / slug(conversation_id) / "_result.json"
    if not path.exists():
        return "I can't find that case. A colleague will follow up."
    r = json.loads(path.read_text())
    if r.get("status") == "pending":
        return "Your case is still with our delivery desk. We'll update you as soon as there's news."
    if r.get("status") != "done":
        return "Your case has been passed to a colleague, who will follow up with you."
    said = DECISION_WORDS.get(r.get("decision_type") or "", "Our desk has reviewed it")
    who = next((n for n in r.get("contacted") or [] if n and len(n) <= 60 and not any(c.isdigit() for c in n)), "")
    return f"{said}{f', and has contacted {who}' if who else ''}. I can't promise a time or outcome yet."
