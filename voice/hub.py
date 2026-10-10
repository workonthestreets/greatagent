"""Hand a voice call to the team's hub (VOICE_AGENT=hub): hub owns the case and its agent decides.

Voice stays the phone front end: read-back, the 999 line, second-problem-as-new-case and the
shipment lookup all happen first. Hub gets ONE request string and answers with its case id; the
caller hears our template with that id, never hub's own wording. If hub isn't configured or
fails within HUB_TIMEOUT_S, the caller still hears "logged" and the local deskagent path decides.

The one exception is `latest_update`: it reads hub's latest agent message aloud. That text is
model-written, so it passes the same promise and secret checks as every drafted message, and a
message that trips them is replaced by a fixed line.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from voice import lookup

HUB_TIMEOUT_S = 3
_UNSAFE_TO_SPEAK = re.compile(
    r"\b(has|have) been (delivered|refunded|resolved|approved|rebooked|fixed)\b|\bwe will (refund|compensate|credit)|"
    r"\bguarantee|[£$€]\s?\d|\bwill (arrive|be delivered) (by|on|at|tomorrow|today)|"
    r"\b(password|passcode|pin|one[- ]time code|otp|cvv|card number|sort code|account number)\b", re.IGNORECASE)


class HubError(RuntimeError):
    """Hub unreachable, too slow, refused the secret or answered nonsense; the caller never hears it."""


def configured() -> bool:
    return bool(os.getenv("HUB_URL") and os.getenv("HUB_WEBHOOK_SECRET"))


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(f"{os.environ['HUB_URL'].rstrip('/')}/webhooks/{path}", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json",
                                          "X-Hub-Secret": os.environ["HUB_WEBHOOK_SECRET"]})
    try:
        with urllib.request.urlopen(req, timeout=HUB_TIMEOUT_S) as r:
            return json.loads(r.read())
    except (OSError, urllib.error.URLError, ValueError) as e:  # timeouts are OSError too
        raise HubError(f"{path}: {type(e).__name__}: {e}"[:300]) from e


def request_text(caller: str, ref: str, how: str, contact: str, issue: str) -> str:
    """The call as one message for hub's agent; known shipment context is pre-escalation only."""
    lines = [f"Caller: {caller or 'unknown'}", f"Reference given: {ref or 'none'}",
             f"Preferred updates: {f'{how} to {contact}' if how else 'not given'}",
             f"Issue, in the caller's words: {issue}"]
    match = lookup.find_shipment(ref) if ref else None
    if match:
        known = lookup.known_context(match)
        lines += ["", f"Known shipment context for {known.primary or ref} (desk records before this call):",
                  known.details, *known.events]
    return "\n".join(lines)[:6000]


def hand_over(folder: Path, caller: str, ref: str, issue: str, how: str, contact: str) -> str | None:
    """Hub's case id, or None when voice should fall back to the local deskagent path."""
    if not configured():
        (folder / "_hub.json").write_text(json.dumps({"fallback": "HUB_URL or HUB_WEBHOOK_SECRET not set"}))
        return None
    phone = contact if how in ("text", "call") else None
    try:
        reply = _post("ask_agent", {"request": request_text(caller, ref, how, contact, issue),
                                    "caller_phone": phone, "case_id": None})
        case_id = str(reply["case_id"])
    except (HubError, KeyError, TypeError) as e:
        (folder / "_hub.json").write_text(json.dumps({"fallback": str(e)[:300]}))
        return None
    (folder / "_result.json").write_text(json.dumps({"status": "handed_to_hub", "hub_case_id": case_id}))
    return case_id


def latest_update(case_id: str, caller_phone: str | None) -> str:
    try:
        reply = _post("get_latest_update", {"case_id": case_id, "caller_phone": caller_phone})
    except HubError:
        return "I can't reach the case system just now. A colleague will follow up with you."
    body = ((reply.get("latest") or {}).get("body") or "").strip()
    if not body:
        return "Your case is still with our delivery desk. We'll update you as soon as there's news."
    if len(body) > 500 or _UNSAFE_TO_SPEAK.search(body):
        return "There's a new update on your case. A colleague will go through it with you."
    return f"The latest update on your case is: {body}"
