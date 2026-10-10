"""Mirror a finished phone case into the team's hub so it shows in /ops (option B).

deskagent decides; hub only records. After deskagent's run, voice POSTs the call and the decision to
`{HUB_URL}/webhooks/record_case`, which creates the case and its events without waking hub's own
agent (spec: voice/HUB_MIRROR.md). Active only when HUB_URL and HUB_WEBHOOK_SECRET are set. Any
failure, including a 404 before hub has the endpoint, is recorded and never touches the call or
deskagent's result.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

MIRROR_TIMEOUT_S = 5


def configured() -> bool:
    return bool(os.getenv("HUB_URL") and os.getenv("HUB_WEBHOOK_SECRET"))


def payload(voice_case_id: str, call: dict, lookup: dict, decision: dict, messages: list[dict]) -> dict:
    phone = call.get("contact") if call.get("update_by") in ("text", "call") else None
    return {"voice_case_id": voice_case_id, "caller_name": call.get("caller") or None, "caller_phone": phone,
            "shipment_ref": lookup.get("primary") or call.get("ref") or None, "request": call.get("issue", ""),
            "lookup_source_case": lookup.get("source_case"),
            "decision": {"type": decision.get("decision_type"), "summary": decision.get("decision_summary"),
                         "approved": decision.get("approved"), "contacted": decision.get("contacted") or [],
                         "messages": messages}}


def post_case(body: dict) -> dict:
    """{"ok": True, "case_id": ...} or {"ok": False, "error": ...}; never raises."""
    if not configured():
        return {"ok": False, "error": "HUB_URL or HUB_WEBHOOK_SECRET not set"}
    req = urllib.request.Request(f"{os.environ['HUB_URL'].rstrip('/')}/webhooks/record_case", method="POST",
                                 data=json.dumps(body, default=str).encode(),
                                 headers={"content-type": "application/json",
                                          "X-Hub-Secret": os.environ["HUB_WEBHOOK_SECRET"]})
    try:
        with urllib.request.urlopen(req, timeout=MIRROR_TIMEOUT_S) as r:
            return {"ok": True, "case_id": json.loads(r.read()).get("case_id")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code} from hub"}
    except Exception as e:  # noqa: BLE001 — a mirror failure must never affect the case
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
