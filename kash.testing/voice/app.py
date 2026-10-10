"""Voice channel: an ElevenLabs agent takes the call, this service decides.

The ElevenLabs agent calls `POST /voice/tool` mid-call with what the caller said. We turn it
into the same `AgentInput` every other case uses, run `agent.decide`, and send back a reply
built from a fixed template. The spoken words never come from free LLM text, so the call can't
promise money, a date or an outcome the decision didn't make.

With VOICE_ASSIST set, `POST /voice/turn` also serves a live-assist mode: the voice agent calls it
after every caller utterance, each turn's decision comes from the same fixed templates, and the
call continues only while the next step is a question the caller can answer.

Run: VOICE_TOOL_SECRET=... uv run uvicorn voice.app:app --port 8000
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from agent.decide import decide
from agent.outbox import deliver
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
    contact: str = Field("", max_length=200)  # confirmed email or phone for updates
    update_by: str = Field("", max_length=10)  # "email", "text" or "call"; "" if they declined


class CallerTurn(BaseModel):
    """One caller utterance in a live-assist call; the known fields accumulate in the state file."""
    conversation_id: str = Field(max_length=200)
    utterance: str = Field(max_length=4000)
    caller_name: str = Field("", max_length=200)
    order_ref: str = Field("", max_length=100)
    contact: str = Field("", max_length=200)
    update_by: str = Field("", max_length=10)


def case_text(r: CallReport) -> str:
    caller = r.caller_name or "Caller"
    ref = r.order_ref or "[reference not given]"
    how, contact = checked_contact(r.update_by, r.contact)
    reach = f"\n- **Updates by:** {how} to {contact}" if how else ""
    return (f"## Case details\n- **Source role:** {caller}, recipient\n- **Primary shipment:** {ref}{reach}\n\n"
            f"## Initial request\n{r.issue}\n\n### event 001\n"
            f"Channel: Phone call | From: {caller}, recipient | To: Delivery desk\n{r.issue}")


_EMAIL = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+$")


def checked_contact(update_by: str, contact: str) -> tuple[str, str]:
    """(channel, contact) only when the contact is a well-formed email or phone number, else ("", "").

    The voice agent reads details back before sending them; this is the code check behind it, so a
    misheard address never becomes somewhere we'd send updates.
    """
    how = update_by.strip().lower()
    if how == "email":
        spoken_form = re.sub(r"\s+at\s+", "@", contact.strip().lower())
        email = re.sub(r"\s+dot\s+", ".", spoken_form).replace(" ", "")
        return ("email", email) if _EMAIL.match(email) else ("", "")
    if how in ("text", "call"):
        digits = re.sub(r"[^\d+]", "", contact)
        return (how, digits) if 10 <= sum(c.isdigit() for c in digits) <= 15 else ("", "")
    return "", ""


def read_back(how: str, contact: str) -> str:
    """The stored contact as it should be spoken: an email's name spelled out, a number in groups."""
    if how == "email":
        name, domain = contact.split("@", 1)
        return f"{', '.join(name)}, at {domain.replace('.', ' dot ')}"
    digits = contact.lstrip("+")
    if len(digits) == 11 and digits.startswith("0"):  # UK mobile style: 07700 900 123
        return f"{digits[:5]}, {digits[5:8]}, {digits[8:]}"
    return ", ".join(digits[i:i + 3] for i in range(0, len(digits), 3))


def update_line(update_by: str, contact: str) -> str:
    """How we'll follow up, read back from what we stored, never a time."""
    how, stored = checked_contact(update_by, contact)
    if not how:
        return "A colleague will follow up as soon as they reply"
    verb = {"email": "email you at", "text": "text you on", "call": "call you back on"}[how]
    return f"We'll {verb} {read_back(how, stored)} as soon as they reply. If that's not right, tell me now"


def spoken(d: dict, update_by: str = "", contact: str = "") -> str:
    """What the voice agent says. Templates only; every slot is a field code already checked."""
    if d.get("escalate") and d.get("party") == "safety":  # emergency help is not substance advice
        return ("Thank you. If anyone feels unwell, call 999 now. I've passed this to our safety lead "
                "as an urgent incident, and they'll contact you; I can't give a time or outcome yet.")
    if d.get("escalate"):
        who = "a member of our team"
        return (f"Thank you. I can't settle this on the call, so I've passed it to {who} to check. "
                f"They'll contact you; I can't give a time or outcome yet.")
    if d.get("party") == "customer":
        return f"Thank you. To move this on we need {d.get('missing') or 'a little more detail'}. Could you give me that now?"
    who = d.get("org") or ROLE_WORDS.get(d.get("party", ""), "our delivery team")
    return (f"Thank you. I'm asking {who} to look into this. {update_line(update_by, contact)}; "
            f"I can't promise a time or outcome yet.")


ROLE_WORDS = {"carrier": "the carrier", "merchant": "the retailer", "shipper": "the sender",
              "depot": "the depot", "other_business": "our delivery team"}

# The only questions a live call can ask. Credentials, codes and card numbers have no key here,
# so no decision can ever make the voice agent ask for one.
ASKS = {
    "ref": "Could you give me the order or tracking number?",
    "confirm_ref": "Sorry, could you confirm those details for me once more?",
    "contact": "What's the best email address or phone number for updates?",
    "slot": "Which day or time would suit you best for delivery?",
    "access": "Is there anything we should know for getting the parcel to you, "
              "like a safe place or a neighbour?",
    "photo": "If you're able to, could you take a photo of it for our team?",
    "generic": "Could you tell me a little more about what happened?",
}

_ASK_RULES = [  # first keyword hit in `missing` picks the template; no hit -> generic
    ("confirm_ref", r"confirm|which|correct|wrong"),
    ("ref", r"reference|tracking|order|consignment|parcel (number|id)"),
    ("contact", r"contact|email|phone|reach you|updates?"),
    ("slot", r"slot|deliver|when|day|time|date|reschedul|rebook|availab"),
    ("access", r"access|safe place|neighbou?r|gate|door|entry|buzz|flat|floor|leave"),
    ("photo", r"photo|picture|image|evidence"),
]


def ask_key(d: dict) -> str:
    """The whitelist key for what the decision wants from the caller. Never returns free text."""
    missing = (d.get("missing") or "").lower()
    return next((k for k, pattern in _ASK_RULES if re.search(pattern, missing)), "generic")


def spoken_turn(d: dict, update_by: str = "", contact: str = "") -> dict:
    """Map a decision to the live-call reply: `say` is always a fixed template, `status` tells the
    voice agent whether the call continues (the caller can supply what's needed) or ends."""
    if d.get("escalate"):  # spoken()'s escalation branches are already fixed templates
        return {"say": spoken(d), "status": "end_call", "reason": "escalated"}
    if d.get("party") == "customer" or d.get("action") == "ask":
        return {"say": ASKS[ask_key(d)], "status": "continue"}
    who = d.get("org") or ROLE_WORDS.get(d.get("party", ""), "our delivery team")
    return {"say": f"Thank you. I'm asking {who} to look into this. {update_line(update_by, contact)}.",
            "status": "end_call", "reason": "handed_to_third_party"}


def turn_text(state: dict) -> str:
    """The call so far, in the same case shape `case_text` produces: each caller turn is an event."""
    caller = state.get("caller_name") or "Caller"
    ref = state.get("order_ref") or "[reference not given]"
    how, contact = checked_contact(state.get("update_by", ""), state.get("contact", ""))
    reach = f"\n- **Updates by:** {how} to {contact}" if how else ""
    events = "\n\n".join(f"### event {i + 1:03d}\nChannel: Phone call | From: {caller}, recipient | "
                         f"To: Delivery desk\n{u}" for i, u in enumerate(state["turns"]))
    return (f"## Case details\n- **Source role:** {caller}, recipient\n- **Primary shipment:** "
            f"{ref}{reach}\n\n## Initial request\n{state['turns'][0]}\n\n{events}")


def update_turn_state(t: CallerTurn) -> dict:
    """Load the call's state file, fold this turn's fields and utterance in, write it back."""
    path = LOG_DIR / f"{_safe(t.conversation_id)}-state.json"
    state = json.loads(path.read_text()) if path.exists() else {}
    for k in ("caller_name", "order_ref", "contact", "update_by"):
        if getattr(t, k):
            state[k] = getattr(t, k)
    state.setdefault("turns", []).append(t.utterance)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, default=str))
    return state


def _safe(conversation_id: str) -> str:
    return "".join(c for c in conversation_id if c.isalnum() or c in "-_")[:80] or "unknown"


def _log(conversation_id: str, suffix: str, data: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{_safe(conversation_id)}{suffix}.json").write_text(json.dumps(data, indent=2, default=str))


def _decide_and_log(r: CallReport) -> dict:
    case = AgentInput(f"voice-{r.conversation_id}", "delivery", case_text(r))
    d = decide(case)
    mail = deliver(case.case_id, d, LOG_DIR / "outbox" / case.case_id)  # sends only with SEND_EMAIL=1
    _log(r.conversation_id, "", {"input": case.text, "decision": d, "email": mail})
    return d


def _decide_turn(t: CallerTurn, state: dict) -> dict:
    case = AgentInput(f"voice-{t.conversation_id}", "delivery", turn_text(state))
    d = decide(case)
    mail = deliver(case.case_id, d, LOG_DIR / "outbox" / case.case_id)  # sends only with SEND_EMAIL=1
    _log(t.conversation_id, f"-turn-{len(state['turns']):02d}",
         {"input": case.text, "decision": d, "email": mail})
    return d


def _auth(x_tool_secret: str) -> None:
    secret = os.getenv("VOICE_TOOL_SECRET", "")
    if not secret or not hmac.compare_digest(x_tool_secret, secret):
        raise HTTPException(401, "bad tool secret")


@app.post("/voice/tool")
def tool(report: CallReport, x_tool_secret: str = Header("")) -> dict:
    _auth(x_tool_secret)
    logged = LOG_DIR / f"{_safe(report.conversation_id)}.json"
    if logged.exists():  # a second call in the same conversation corrects the contact, nothing else
        how, stored = checked_contact(report.update_by, report.contact)
        record = json.loads(logged.read_text())
        record["contact"] = {"update_by": how, "contact": stored}
        logged.write_text(json.dumps(record, indent=2, default=str))
        return {"say": f"Thanks, I've updated that. {update_line(report.update_by, report.contact)}.",
                "status": "contact_updated"}
    future = _pool.submit(_decide_and_log, report)
    try:
        d = future.result(timeout=DECIDE_BUDGET_S)
    except FutureTimeout:  # keeps running and logs; the caller isn't left waiting
        return {"say": "Thank you, I've logged this for the delivery team. They'll contact you with "
                       "the next step; I can't give a time or outcome yet.", "status": "logged"}
    return {"say": spoken(d, report.update_by, report.contact), "status": "decided", "action": d.get("action"),
            "escalate": d.get("escalate", False)}


@app.post("/voice/turn")
def turn(t: CallerTurn, x_tool_secret: str = Header("")) -> dict:
    if not os.getenv("VOICE_ASSIST"):
        raise HTTPException(404, "live assist mode is not enabled")
    _auth(x_tool_secret)
    state = update_turn_state(t)
    future = _pool.submit(_decide_turn, t, state)
    try:
        d = future.result(timeout=DECIDE_BUDGET_S)
    except FutureTimeout:  # keeps running and logs; the caller isn't left waiting
        return {"say": "Thank you, I've logged this for the delivery team. They'll contact you with "
                       "the next step; I can't give a time or outcome yet.",
                "status": "end_call", "reason": "timeout"}
    return spoken_turn(d, state.get("update_by", ""), state.get("contact", ""))


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
