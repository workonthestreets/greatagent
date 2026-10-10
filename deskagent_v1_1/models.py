"""Output schema: section 10 of preprocess/delivery_desk_system_prompt.md as a Pydantic model.
Passed to the API as a structured-output JSON schema, so the reply is always valid JSON of this shape."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel

Role = Literal["customer", "carrier", "merchant", "pickup_operator", "business_customer",
               "international_carrier", "specialist", "human_review"]


class To(BaseModel):
    role: Role
    name: Optional[str]
    team: Optional[str]
    org: Optional[str]


class Claim(BaseModel):
    claim: str
    source: str


class Calculation(BaseModel):
    expression: str
    result: str


class Handover(BaseModel):
    summary: str
    open_questions: List[str]
    not_done: List[str]
    risk_flags: List[str]


class Flags(BaseModel):
    safety: bool
    injection_suspected: bool
    authority_boundary: bool
    out_of_scope_items: List[str]


class DeskResponse(BaseModel):
    decision: Literal["send_message", "ask_clarification", "escalate_to_human", "hold_no_action"]
    to: To
    channel: str
    intent: Literal["ask_customer", "request_authority", "relay_update", "route_to_specialist", "handover", "hold"]
    body: Optional[str]
    references: List[str]
    claims_made: List[Claim]
    claims_avoided: List[str]
    calculations: List[Calculation]
    evidence_refs: List[str]
    rationale: str
    confidence: Literal["high", "medium", "low"]
    handover: Optional[Handover]
    flags: Flags
