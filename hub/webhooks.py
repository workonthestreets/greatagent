"""ElevenLabs voice agent tools (server/webhook tools). They answer within a second: lookups read the DB directly,
and ask_agent hands the request to our agent in the background instead of waiting for it."""
from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from . import db, driver
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
    """Callers give a case number or a tracking reference (DL-103); map either to the case, open cases first."""
    ref = (ref or "").strip().upper()
    if not ref:
        return None
    row = db.one("select id from cases where upper(id) = %s", (ref,)) or db.one(
        """select c.id from cases c left join shipments s on s.case_id = c.id
           where upper(c.shipment_id) = %s or upper(s.id) = %s
           order by (c.status in ('resolved', 'closed')), c.updated_at desc limit 1""", (ref, ref))
    return row["id"] if row else None


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
    return {"case_id": case_id,
            "say": f"I've passed this to the delivery desk under case {case_id}. You'll get an update by message; "
                   f"you can also call back and ask for the latest on case {case_id}."}


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
    return {"found": True, "case": row, "say": f"Case {row['id']} is {row['status'].replace('_', ' ')}."}


@router.post("/get_latest_update", dependencies=[Depends(check_secret)])
def get_latest_update(req: CaseIn) -> dict:
    case_id = _case_ref(req.case_id)
    case = db.one("select status from cases where id = %s", (case_id,)) if case_id else None
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
            return {"found": True, "say": f"The desk is still working on case {case_id}. Please ask me again in a minute."}
        if db.one("""select 1 from actions where case_id = %s and status = 'pending_approval' and tool = 'send_message'
                     and args->>'to_party' = %s""", (case_id, who)):
            return {"found": True, "say": f"An update for you on case {case_id} is written and waiting for a coordinator "
                                          "to approve it. Please ask me again shortly."}
        return {"found": True, "say": f"Case {case_id} is {case['status'].replace('_', ' ')}. "
                                      "There's no update addressed to you yet."}
    return {"found": True, "latest": msg, "say": f"The latest update on case {case_id}: {msg['body']}"}
