"""REST API for the web app. Reads go straight to Supabase under RLS; this covers the writes and agent triggers.
Auth: the Supabase access token as a Bearer header (or X-Dev-User: <email> when HUB_DEV_AUTH=1)."""
from __future__ import annotations

import logging
import secrets
from typing import Literal, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from . import db, driver, rewards
from .config import settings

log = logging.getLogger("hub.api")
router = APIRouter(prefix="/api")


def current_user(authorization: Optional[str] = Header(None), x_dev_user: Optional[str] = Header(None)) -> dict:
    if settings.dev_auth and x_dev_user:
        profile = db.one("select * from profiles where lower(email) = lower(%s)", (x_dev_user,))
    else:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(401, "missing bearer token")
        r = httpx.get(f"{settings.supabase_url}/auth/v1/user", timeout=10,
                      headers={"Authorization": authorization, "apikey": settings.supabase_anon_key})
        if r.status_code != 200:
            raise HTTPException(401, "invalid session")
        profile = db.one("select * from profiles where id = %s", (r.json()["id"],))
    if not profile:
        raise HTTPException(403, "no profile for this account")
    return profile


def staff(user: dict = Depends(current_user)) -> dict:
    if user["role"] not in ("admin", "coordinator"):
        raise HTTPException(403, "staff only")
    return user


def _can_see(user: dict, case_id: str) -> bool:
    if user["role"] in ("admin", "coordinator"):
        return True
    return db.one("select 1 from case_parties where case_id = %s and party_name = %s",
                  (case_id, user["party_name"])) is not None


def _speaker(user: dict) -> str:
    return user["party_name"] or user["display_name"] or user["email"]


def _safe_wake(case_id: str, text: str) -> Optional[str]:
    """Wake the agent; the caller's write is already saved, so a failed wake is logged, not raised. None on failure."""
    try:
        return driver.wake(case_id, text)
    except Exception:  # noqa: BLE001
        log.exception("waking the agent on case %s failed", case_id)
        return None


def _channel(user: dict) -> str:
    return {"customer": "Customer portal", "driver": "Driver app", "depot": "Depot portal",
            "merchant": "Partner portal"}.get(user["role"], "Desk console")


@router.get("/health")
def health() -> dict:
    db.one("select 1 as ok")
    return {"ok": True}


@router.get("/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {k: user[k] for k in ("id", "email", "display_name", "role", "party_name")}


class MessageIn(BaseModel):
    body: str


@router.post("/cases/{case_id}/messages")
def post_message(case_id: str, msg: MessageIn, user: dict = Depends(current_user)) -> dict:
    """A party (or staff) writes on a case; the agent is woken with it."""
    if not _can_see(user, case_id):
        raise HTTPException(404, "case not found")
    who, channel = _speaker(user), _channel(user)
    db.query(
        """insert into case_events (case_id, channel, author, author_role, to_party, kind, body)
           values (%s, %s, %s, %s, 'Rivet Delivery Desk', 'message', %s)""",
        (case_id, channel, who, user["role"], msg.body))
    session_id = _safe_wake(case_id, f"New message on the case from {who} via {channel}:\n\n{msg.body}")
    return {"ok": True, "session_id": session_id}


class NewCaseIn(BaseModel):
    title: str
    body: str
    shipment_id: Optional[str] = None


@router.post("/cases")
def open_case(req: NewCaseIn, user: dict = Depends(current_user)) -> dict:
    """Open a new case (customer request from the portal, or staff creating one) and wake the agent."""
    case_id = new_case(user, req.title, req.body, req.shipment_id, _channel(user))
    return {"case_id": case_id, "session_id": _safe_wake(case_id, "A new case was opened. Work out the next step.")}


def new_case(user: dict, title: str, body: str, shipment_id: Optional[str], channel: str) -> str:
    case_id = f"C-{secrets.token_hex(3).upper()}"
    who = _speaker(user)
    db.query(
        """insert into cases (id, title, status, source_name, source_role, coordinator, shipment_id, initial_request)
           values (%s, %s, 'open', %s, %s, 'Iona Quill, Rivet Delivery Desk', %s, %s)""",
        (case_id, title[:200], who, user["role"], shipment_id, body))
    db.query("insert into case_parties (case_id, party_name, role) values (%s, %s, %s), (%s, 'Iona Quill, Rivet Delivery Desk', 'coordinator') on conflict do nothing",
             (case_id, who, user["role"], case_id))
    db.query(
        """insert into case_events (case_id, channel, author, author_role, to_party, kind, body)
           values (%s, %s, %s, %s, 'Rivet Delivery Desk', %s, %s)""",
        (case_id, channel, who, user["role"], "call" if channel == "Phone call" else "message", body))
    return case_id


@router.post("/cases/{case_id}/run")
def rerun(case_id: str, user: dict = Depends(staff)) -> dict:
    """Staff asks the agent to re-assess the case now."""
    return {"session_id": driver.wake(case_id, f"{_speaker(user)} (desk staff) asks you to re-assess this case now.")}


class DecisionIn(BaseModel):
    reason: str = ""


def _decide(action_id: int, allow: bool, reason: str, user: dict) -> dict:
    try:
        out = driver.confirm(action_id, allow, _speaker(user), reason)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    try:   # the decision is already made; rewards are a bonus and must never fail it
        out["rewards"] = rewards.award_decision(user, {"id": action_id}, allow, reason)
    except Exception:  # noqa: BLE001
        log.exception("rewards for action %s failed", action_id)
        out["rewards"] = None
    return out


@router.post("/actions/{action_id}/approve")
def approve(action_id: int, req: DecisionIn, user: dict = Depends(staff)) -> dict:
    return _decide(action_id, True, req.reason, user)


@router.post("/actions/{action_id}/reject")
def reject(action_id: int, req: DecisionIn, user: dict = Depends(staff)) -> dict:
    return _decide(action_id, False, req.reason, user)


# ------------------------------------------------------------------ rewards and merch (staff)
@router.get("/rewards/me")
def rewards_me(user: dict = Depends(staff)) -> dict:
    return rewards.me(user)


@router.get("/rewards/team")
def rewards_team(user: dict = Depends(staff)) -> list[dict]:
    if user["role"] != "admin":
        raise HTTPException(403, "admins only")
    return rewards.team()


@router.get("/merch")
def merch(user: dict = Depends(staff)) -> list[dict]:
    return rewards.merch()


@router.post("/merch/{item_id}/redeem")
def redeem(item_id: str, user: dict = Depends(staff)) -> dict:
    try:
        return rewards.redeem(user, item_id)
    except rewards.RedeemError as exc:
        raise HTTPException(exc.status, str(exc))


# ------------------------------------------------------------------ party actions
SHIPMENT_STATUSES = {
    "driver": {"out_for_delivery": "Out for delivery", "attempted": "Delivery attempted", "delivered": "Delivered"},
    "depot": {"arrived_at_depot": "Arrived at depot", "ready_for_collection": "Ready for collection",
              "collected": "Collected"},
}


class ShipmentStatusIn(BaseModel):
    status: str
    note: str = ""


def _post_and_wake(case_id: str, user: dict, body: str) -> bool:
    """Record a party's update on the case timeline and wake the agent with it (as post_message does).
    The event is saved first; returns False (and logs) if the wake failed."""
    who, channel = _speaker(user), _channel(user)
    db.query(
        """insert into case_events (case_id, channel, author, author_role, to_party, kind, body)
           values (%s, %s, %s, %s, 'Rivet Delivery Desk', 'message', %s)""",
        (case_id, channel, who, user["role"], body))
    try:
        driver.wake(case_id, f"New message on the case from {who} via {channel}:\n\n{body}")
    except Exception:  # noqa: BLE001
        log.exception("waking the agent on case %s failed", case_id)
        return False
    return True


@router.post("/shipments/{shipment_id}/status")
def shipment_status(shipment_id: str, req: ShipmentStatusIn, user: dict = Depends(current_user)) -> dict:
    """A driver or depot moves one of its own shipments along."""
    allowed = SHIPMENT_STATUSES.get(user["role"])
    if allowed is None:
        raise HTTPException(403, "drivers and depots only")
    column = "driver_name" if user["role"] == "driver" else "depot"
    ship = db.one(f"select id, case_id from shipments where id = %s and {column} = %s",
                  (shipment_id, user["party_name"]))
    if not user["party_name"] or not ship:
        raise HTTPException(404, "shipment not found")
    if req.status not in allowed:
        raise HTTPException(422, f"status must be one of: {', '.join(allowed)}")
    db.query("update shipments set status = %s, updated_at = now() where id = %s", (req.status, shipment_id))
    woken = False   # no case on the shipment: nothing to wake
    if ship["case_id"]:
        woken = _post_and_wake(ship["case_id"], user, f"{allowed[req.status]}. {req.note.strip()}".strip())
    return {"ok": True, "status": req.status, "woken": woken}


MERCHANT_DECISIONS = {"approve_replacement": "Approve replacement", "approve_refund": "Approve refund",
                      "decline": "Decline"}


class MerchantDecisionIn(BaseModel):
    decision: Literal["approve_replacement", "approve_refund", "decline"]
    note: str = ""


@router.post("/cases/{case_id}/merchant_decision")
def merchant_decision(case_id: str, req: MerchantDecisionIn, user: dict = Depends(current_user)) -> dict:
    """The merchant answers on a case about one of its orders: replacement, refund or decline."""
    if user["role"] != "merchant":
        raise HTTPException(403, "merchants only")
    if not _can_see(user, case_id):
        raise HTTPException(404, "case not found")
    woken = _post_and_wake(case_id, user, f"Merchant decision: {MERCHANT_DECISIONS[req.decision]}. {req.note.strip()}".strip())
    return {"ok": True, "woken": woken}
