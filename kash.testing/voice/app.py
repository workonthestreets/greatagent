"""Voice channel: an ElevenLabs agent takes the call, this service decides.

The ElevenLabs agent calls `POST /voice/tool` mid-call with what the caller said. We turn it
into the same `AgentInput` every other case uses, run `agent.decide`, and send back a reply
built from a fixed template. The spoken words never come from free LLM text, so the call can't
promise money, a date or an outcome the decision didn't make.

Run: VOICE_TOOL_SECRET=... uv run uvicorn voice.app:app --port 8000
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from agent.decide import decide
from scorer.cases import AgentInput

LOG_DIR = Path(os.getenv("VOICE_LOG_DIR", "runs/voice"))
DECIDE_BUDGET_S = 14  # ElevenLabs gives a webhook tool 20 s by default; leave room for the network
_pool = ThreadPoolExecutor(4)
app = FastAPI(title="Delivery voice line")


class CallReport(BaseModel):
    conversation_id: str = Field(max_length=200)
    caller_name: str = Field("", max_length=200)
    order_ref: str = Field("", max_length=100)
    issue: str = Field(max_length=4000)


def case_text(r: CallReport) -> str:
    caller = r.caller_name or "Caller"
    ref = r.order_ref or "[reference not given]"
    return (f"## Case details\n- **Source role:** {caller}, recipient\n- **Primary shipment:** {ref}\n\n"
            f"## Initial request\n{r.issue}\n\n### event 001\n"
            f"Channel: Phone call | From: {caller}, recipient | To: Delivery desk\n{r.issue}")


def spoken(d: dict) -> str:
    """What the voice agent says. Templates only; every slot is a field code already checked."""
    if d.get("escalate"):
        who = "our safety lead" if d.get("party") == "safety" else "a member of our team"
        return (f"Thank you. I can't settle this on the call, so I've passed it to {who} to check. "
                f"They'll contact you; I can't give a time or outcome yet.")
    if d.get("party") == "customer":
        return f"Thank you. To move this on we need {d.get('missing') or 'a little more detail'}. Could you give me that now?"
    who = d.get("org") or ROLE_WORDS.get(d.get("party", ""), "the team responsible")
    return (f"Thank you. I'm asking {who} to look into this. We'll update you as soon as they reply; "
            f"I can't promise a time or outcome yet.")


ROLE_WORDS = {"carrier": "the carrier", "merchant": "the retailer", "shipper": "the sender",
              "depot": "the depot", "other_business": "the business involved"}


def _log(conversation_id: str, suffix: str, data: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in conversation_id if c.isalnum() or c in "-_")[:80] or "unknown"
    (LOG_DIR / f"{safe}{suffix}.json").write_text(json.dumps(data, indent=2, default=str))


def _decide_and_log(r: CallReport) -> dict:
    case = AgentInput(f"voice-{r.conversation_id}", "delivery", case_text(r))
    d = decide(case)
    _log(r.conversation_id, "", {"input": case.text, "decision": d})
    return d


@app.post("/voice/tool")
def tool(report: CallReport, x_tool_secret: str = Header("")) -> dict:
    secret = os.getenv("VOICE_TOOL_SECRET", "")
    if not secret or not hmac.compare_digest(x_tool_secret, secret):
        raise HTTPException(401, "bad tool secret")
    future = _pool.submit(_decide_and_log, report)
    try:
        d = future.result(timeout=DECIDE_BUDGET_S)
    except FutureTimeout:  # keeps running and logs; the caller isn't left waiting
        return {"say": "Thank you, I've logged this for the delivery team. They'll contact you with "
                       "the next step; I can't give a time or outcome yet.", "status": "logged"}
    return {"say": spoken(d), "status": "decided", "action": d.get("action"),
            "escalate": d.get("escalate", False)}


def valid_signature(body: bytes, header: str, secret: str, tolerance_s: int = 1800) -> bool:
    """ElevenLabs-Signature: `t=<unix>,v0=<hex hmac-sha256 of "<t>.<body>">`."""
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    t, sig = parts.get("t", ""), parts.get("v0", "")
    if not t.isdigit() or abs(time.time() - int(t)) > tolerance_s:
        return False
    want = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(want, sig)


@app.post("/voice/post-call")
async def post_call(request: Request, elevenlabs_signature: str = Header("")) -> dict:
    body = await request.body()
    secret = os.getenv("ELEVENLABS_WEBHOOK_SECRET", "")
    if not secret or not valid_signature(body, elevenlabs_signature, secret):
        raise HTTPException(401, "bad signature")
    try:
        event = json.loads(body)
    except ValueError:
        return {"ok": False}  # 200 anyway: repeated failures auto-disable the webhook
    if event.get("type") == "post_call_transcription":
        data = event.get("data", {})
        _log(data.get("conversation_id", "unknown"), "-transcript",
             {"summary": data.get("analysis", {}).get("transcript_summary"),
              "transcript": data.get("transcript", [])})
    return {"ok": True}
