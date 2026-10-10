"""Turn a decision into the email it implies; write it, and send it only for the demo.

Batch and Reality Test runs never send: they write `outbox.eml` next to the answer. With
SEND_EMAIL=1 the same message also goes to a local Mailpit inbox (SMTP localhost:1025). Only
`.local` / `example.com` recipients are ever sent to, each (case, recipient) once, and a send
failure is recorded, never raised.
"""
from __future__ import annotations

import os
import re
import smtplib
from email.message import EmailMessage
from pathlib import Path

FROM = "ops-agent@demo.local"
ALLOWED = (".local", "@example.com")
SENT_DIR = Path(os.getenv("OUTBOX_SENT_DIR", "runs/sent"))


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "unknown"


def address(decision: dict) -> str:
    if decision.get("escalate") and decision.get("party") == "internal":
        return "operations-lead@demo.local"
    team, org = decision.get("team", ""), decision.get("org", "")
    return f"{slug(team)}.{slug(org)}@demo.local" if org else f"{slug(team)}@demo.local"


def build(case_id: str, decision: dict) -> EmailMessage:
    msg = EmailMessage()
    msg["From"], msg["To"] = FROM, address(decision)
    kind = "Escalation" if decision.get("escalate") else "Request"
    msg["Subject"] = f"[{case_id}] {kind}: {decision.get('missing') or decision.get('action', '')}"[:150]
    body = decision.get("message", "")
    if decision.get("question_for_human"):
        body += f"\n\nQuestion for you: {decision['question_for_human']}"
    msg.set_content(body + f"\n\nChannel: {decision.get('channel', '')}\nCase: {case_id}\n")
    return msg


def deliver(case_id: str, decision: dict, out_dir: Path) -> dict:
    """Write outbox.eml into `out_dir`; also send it when SEND_EMAIL=1. Returns what happened."""
    msg = build(case_id, decision)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "outbox.eml").write_bytes(bytes(msg))
    result = {"to": msg["To"], "written": str(out_dir / "outbox.eml"), "sent": False}
    if os.getenv("SEND_EMAIL") != "1":
        return result
    if not msg["To"].endswith(ALLOWED):
        return result | {"error": "recipient not on the demo allowlist"}
    key = SENT_DIR / f"{slug(case_id)}--{slug(msg['To'])}"
    if key.exists():
        return result | {"sent": True, "duplicate": True}
    try:
        with smtplib.SMTP(os.getenv("SMTP_HOST", "localhost"), int(os.getenv("SMTP_PORT", "1025")),
                          timeout=5) as smtp:
            smtp.send_message(msg)
    except (OSError, smtplib.SMTPException) as e:
        return result | {"error": f"not sent: {type(e).__name__}"}
    SENT_DIR.mkdir(parents=True, exist_ok=True)
    key.touch()
    return result | {"sent": True}
