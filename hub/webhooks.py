"""ElevenLabs voice agent tools (server/webhook tools). They answer within a second: lookups read the DB directly,
and ask_agent hands the request to our agent in the background instead of waiting for it."""
from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from . import db, driver, refs
from .api import new_case
from .config import settings

router = APIRouter(prefix="/webhooks")


def check_secret(x_hub_secret: Optional[str] = Header(None)) -> None:
    if not settings.webhook_secret or x_hub_secret != settings.webhook_secret:
        raise HTTPException(401, "bad webhook secret")


def _caller(phone: Optional[str]) -> dict:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) >= 7:
        # Compare the last 10 digits so "+44 7700 900103" and "07700 900103" are the same caller.
        row = db.one("""select * from profiles where phone is not null
                        and right(regexp_replace(phone, '\\D', '', 'g'), 10) = right(%s, 10)
                        order by email limit 1""", (digits,))
        if row:
            return row
    name = f"Caller {phone}" if phone else "Unidentified caller"
    return {"role": "customer", "party_name": name, "display_name": name, "email": None}


class AskAgentIn(BaseModel):
    request: str
    caller_phone: Optional[str] = None
    case_id: Optional[str] = None


def _case_ref(ref: Optional[str]) -> Optional[str]:
    """Callers give a case reference, a legacy case number or a tracking reference; map any of them to the case."""
    return refs.resolve_case(ref)


@router.post("/ask_agent", dependencies=[Depends(check_secret)])
def ask_agent(req: AskAgentIn) -> dict:
    caller = _caller(req.caller_phone)
    who = caller["party_name"] or caller["display_name"]
    case_id = _case_ref(req.case_id)
    if not case_id:
        latest = db.one(
            """select c.id from cases c join case_parties p on p.case_id = c.id
               where p.party_name = %s and c.status not in ('resolved', 'closed') order by c.updated_at desc limit 1""",
            (who,))
        case_id = latest["id"] if latest else None
    if case_id:
        db.query(
            """insert into case_events (case_id, channel, author, author_role, to_party, kind, body)
               values (%s, 'Phone call', %s, %s, 'Rivet Delivery Desk', 'call', %s)""",
            (case_id, who, caller["role"], req.request))
        driver.wake(case_id, f"{who} called the desk (voice assistant transcript):\n\n{req.request}")
    else:
        case_id = new_case(caller, req.request[:80], req.request, None, "Phone call")
        driver.wake(case_id, f"A new case was opened from a phone call by {who}. Work out the next step.")
    ref = refs.case_ref(case_id)
    return {"case_id": case_id, "case_ref": ref,
            "say": f"I've logged your request as case {ref}. Nothing is confirmed yet; "
                   "you can ask me for the latest at any time."}


class VoiceMessage(BaseModel):
    to: str
    channel: str = ""
    body: str = ""


class VoiceDecision(BaseModel):
    type: Optional[str] = None
    summary: Optional[str] = None
    approved: Optional[bool] = None
    contacted: list[str] = []
    messages: list[VoiceMessage] = []


class RecordCaseIn(BaseModel):
    voice_case_id: str
    caller_name: Optional[str] = None
    caller_phone: Optional[str] = None
    shipment_ref: Optional[str] = None
    request: str = ""
    lookup_source_case: Optional[str] = None
    decision: VoiceDecision = VoiceDecision()


@router.post("/record_case", dependencies=[Depends(check_secret)])
def record_case(req: RecordCaseIn) -> dict:
    """Mirror a phone case the voice line already decided (with deskagent) into the desk, so it shows in /ops.
    Records only: the hub's own agent is not woken. Spec: voice/HUB_MIRROR.md. Idempotent on voice_case_id."""
    from db.seed import party_role   # same role heuristic as the seeded cases

    seen = db.one("select case_id from case_events where meta->>'voice_case_id' = %s limit 1", (req.voice_case_id,))
    if seen:
        return {"case_id": seen["case_id"], "already_recorded": True}
    caller = _caller(req.caller_phone)
    if caller.get("email") is None:   # no matching account: use the name the caller gave
        caller = {**caller, "party_name": req.caller_name or caller["party_name"]}
    who, role = caller["party_name"] or caller["display_name"], caller["role"]
    desk, d = "Iona Quill, Rivet Delivery Desk", req.decision
    case_id = new_case({**caller, "party_name": who, "display_name": who}, (req.request or "Phone call")[:80],
                       req.request or "(no details given)", (req.shipment_ref or "").upper() or None, "Phone call")
    status = "escalated" if d.type == "escalate_to_human" else "open"
    db.query("update cases set status = %s, decision = %s, decision_summary = %s, updated_at = now() where id = %s",
             (status, db.jsonb({"decision_type": d.type, "summary": d.summary, "approved": d.approved,
                                "source": "voice line (deskagent)"}), d.summary, case_id))
    def party(name: str) -> str:   # messages to the caller go to the caller's party, so their views find them
        n = name.strip().lower()
        return who if n and (n == (req.caller_name or "").strip().lower() or who.lower().startswith(n)) else name

    for name in dict.fromkeys(party(m.to) for m in d.messages if m.to):
        db.query("insert into case_parties (case_id, party_name, role) values (%s, %s, %s) on conflict do nothing",
                 (case_id, name, role if name == who else party_role(name)))
    for m in d.messages:
        db.query(
            """insert into case_events (case_id, channel, author, author_role, to_party, kind, body)
               values (%s, %s, 'Rivet Delivery Desk', 'agent', %s, 'agent_message', %s)""",
            (case_id, m.channel or "Message", party(m.to), m.body or "(empty)"))
    db.query(
        """insert into case_events (case_id, channel, author, author_role, to_party, kind, visibility, body, meta)
           values (%s, 'Internal', 'Voice line', 'agent', %s, 'note', 'staff', %s, %s)""",
        (case_id, desk,
         f"Phone case {req.voice_case_id} decided on the voice line by deskagent: [{d.type}] {d.summary or ''}"
         + (f" Shipment matched public case {req.lookup_source_case}." if req.lookup_source_case else ""),
         db.jsonb({"voice_case_id": req.voice_case_id, "approved": d.approved, "contacted": d.contacted})))
    return {"case_id": case_id}


class ShipmentIn(BaseModel):
    order_id: str


@router.post("/lookup_shipment", dependencies=[Depends(check_secret)])
def lookup_shipment(req: ShipmentIn) -> dict:
    ref = req.order_id.strip().upper()
    row = db.one("select id, description, status, eta, depot, updated_at from shipments where upper(id) = %s", (ref,))
    if not row:
        return {"found": False, "say": f"I couldn't find shipment {ref}. Could you read the reference again?"}
    return {"found": True, "shipment": row,
            "say": f"Shipment {row['id']} is {row['status'].replace('_', ' ')}" + (f", expected {row['eta']}." if row['eta'] else ".")}


class CaseIn(BaseModel):
    case_id: str
    caller_phone: Optional[str] = None


@router.post("/get_case_status", dependencies=[Depends(check_secret)])
def get_case_status(req: CaseIn) -> dict:
    case_id = _case_ref(req.case_id)
    row = db.one("select id, title, status, updated_at from cases where id = %s", (case_id,)) if case_id else None
    if not row:
        return {"found": False, "say": "I couldn't find that case number."}
    return {"found": True, "case": row, "say": f"Case {refs.case_ref(row['id'])} is {row['status'].replace('_', ' ')}."}


@router.post("/get_latest_update", dependencies=[Depends(check_secret)])
def get_latest_update(req: CaseIn) -> dict:
    case_id = _case_ref(req.case_id)
    case = db.one("select status from cases where id = %s", (case_id,)) if case_id else None
    ref = refs.case_ref(case_id) if case_id else ""
    if not case:
        return {"found": False, "say": "I couldn't find that case number."}
    # Only messages the desk addressed to this caller are read out; never notes or other parties' messages.
    who = _caller(req.caller_phone)["party_name"]
    msg = db.one(
        """select ts, body from case_events where case_id = %s and kind = 'agent_message' and to_party = %s
           order by ts desc, id desc limit 1""", (case_id, who))
    if not msg:
        run = db.one("select status from agent_runs where case_id = %s order by created_at desc limit 1", (case_id,))
        if run and run["status"] == "running":
            return {"found": True, "say": f"The desk is still working on case {ref}. Please ask me again in a minute."}
        if db.one("""select 1 from actions where case_id = %s and status = 'pending_approval' and tool = 'send_message'
                     and args->>'to_party' = %s""", (case_id, who)):
            return {"found": True, "say": f"An update for you on case {ref} is written and waiting for a coordinator "
                                          "to approve it. Please ask me again shortly."}
        return {"found": True, "say": f"Case {ref} is {case['status'].replace('_', ' ')}. "
                                      "There's no update addressed to you yet."}
    return {"found": True, "latest": msg, "say": f"Latest update: {spoken_update(msg['body'])}"}


SPOKEN_MAX = 150   # about ten seconds of speech; status sentences are kept beyond it
_GREETING = re.compile(r"^(hello|hi|dear|good (morning|afternoon|evening))\b.{0,40}$", re.I)
_SIGNOFF = re.compile(r"^(kind regards|best regards|warm regards|regards|best wishes|many thanks|thanks|thank you|"
                      r"sincerely|cheers)[,.!]?$", re.I)
_GREETING_LEAD = re.compile(r"^(hello|hi|dear|good (morning|afternoon|evening))\b[^,.!?]{0,40}[,.!]\s+", re.I)
_PLEASANTRY = re.compile(r"^(thanks|thank you|sorry|i'm sorry|we're sorry|apologies)\b", re.I)
_STATUS = re.compile(r"\b(not (yet )?(been )?(confirmed|moved|changed|booked|delivered)|isn't confirmed|not yet|"
                     r"not a confirmation|hasn't|has not|have not|haven't|no new)\b", re.I)


def spoken_update(body: str, limit: int = SPOKEN_MAX) -> str:
    """The approved message shortened for the phone, without rewording it: the subject line, greeting, sign-off
    and pleasantries go; the remaining sentences are kept word for word and in order until about `limit`
    characters. A sentence saying what is not done or not confirmed is always kept."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", (body or "").strip()) if p.strip()]
    if len(paras) > 1 and len(paras[0]) <= 120 and not paras[0].endswith((".", "!", "?")):
        paras = paras[1:]   # stored as "subject\n\nbody"
    lines = []
    for line in "\n".join(paras).splitlines():
        s = line.strip()
        if _SIGNOFF.match(s):
            break           # sign-off and signature
        if s and not (len(s) <= 50 and _GREETING.match(s)):
            lines.append(s)
    text = _GREETING_LEAD.sub("", " ".join(lines), count=1)   # "Hello Vessa, thank you for calling. ..."
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s]
    core = [s for s in sentences if _STATUS.search(s) or not _PLEASANTRY.match(s)] or sentences
    out, size = [], 0
    for s in core:
        if out and size + len(s) > limit and not _STATUS.search(s):
            continue
        out.append(s)
        size += len(s) + 1
    return " ".join(out) or (body or "").strip()[:limit]
