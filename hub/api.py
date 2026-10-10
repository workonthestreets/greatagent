"""REST API for the web app. Reads go straight to Supabase under RLS; this covers the writes and agent triggers.
Auth: the Supabase access token as a Bearer header (or X-Dev-User: <email> when HUB_DEV_AUTH=1)."""
from __future__ import annotations

import secrets
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from . import db, driver
from .config import settings

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
    session_id = driver.wake(case_id, f"New message on the case from {who} via {channel}:\n\n{msg.body}")
    return {"ok": True, "session_id": session_id}


class NewCaseIn(BaseModel):
    title: str
    body: str
    shipment_id: Optional[str] = None


@router.post("/cases")
def open_case(req: NewCaseIn, user: dict = Depends(current_user)) -> dict:
    """Open a new case (customer request from the portal, or staff creating one) and wake the agent."""
    case_id = new_case(user, req.title, req.body, req.shipment_id, _channel(user))
    return {"case_id": case_id, "session_id": driver.wake(case_id, "A new case was opened. Work out the next step.")}


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


@router.post("/actions/{action_id}/approve")
def approve(action_id: int, req: DecisionIn, user: dict = Depends(staff)) -> dict:
    try:
        return driver.confirm(action_id, True, _speaker(user), req.reason)
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.post("/actions/{action_id}/reject")
def reject(action_id: int, req: DecisionIn, user: dict = Depends(staff)) -> dict:
    try:
        return driver.confirm(action_id, False, _speaker(user), req.reason)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
