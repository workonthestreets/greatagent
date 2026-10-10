"""Deterministic agreement checks between the preprocess hints and the agent's response (no model call).
Each check: {id, label, status: pass|warn|fail|na, detail}. Shown on the Investigate page."""
from __future__ import annotations

import re
from typing import List

CHANNELS = {"customer_portal": "Customer portal", "business_portal": "Business portal", "email": "Email", "phone_call": "Call transcript"}
QUEUES = {"Dispatch chat", "Depot work queue", "Warehouse work queue", "Safety incident queue"}
LEAKS = re.compile(r"classifier|pre-?processing|probabilit|\bflags?\b", re.I)
URL = re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|net|org|io|co\.uk)\b", re.I)
MARKDOWN = re.compile(r"(^|\n)\s*(#{1,6}\s|[-*]\s|\d+\.\s)|\*\*|`")


def _c(id_, label, status, detail=""):
    return {"id": id_, "label": label, "status": status, "detail": detail}


def expected_intent(pre: dict, escalating: bool, holding: bool = False) -> str:
    if holding:
        return "hold"
    if escalating:
        return "handover"
    r = pre.get("routing") or {}
    if (r.get("target") or {}).get("kind") == "customer":
        return "ask_customer"
    if r.get("party") == "specialist":
        return "route_to_specialist"
    return "request_authority"


def run_checks(pre: dict, resp, events: List[dict]) -> List[dict]:
    r = resp
    ok = pre.get("status") != "error"
    route = pre.get("routing") or {}
    flags = pre.get("flags") or {}
    esc = r.decision == "escalate_to_human"
    hold = r.decision == "hold_no_action"
    ids = {f"event-{e['event_no']}" for e in events}
    out: List[dict] = []

    # decision vs classifier
    want_esc = bool(pre.get("needs_human_review")) or (route.get("target") or {}).get("kind") == "human_review"
    if hold:
        out.append(_c("decision", "Escalation matches classifier", "warn" if want_esc else "pass",
                      "Held, nothing sent (the wait test overrides the classifier's target)." + (f" Classifier asked for human review: {'; '.join(pre.get('review_reasons') or [])}." if want_esc else "")))
    elif esc == want_esc:
        out.append(_c("decision", "Escalation matches classifier", "pass", "Escalated" if esc else "Sent a message, as the classifier suggested."))
    else:
        out.append(_c("decision", "Escalation matches classifier", "warn",
                      f"Classifier {'asked for human review' if want_esc else 'did not ask for human review'} ({'; '.join(pre.get('review_reasons') or []) or 'no reasons'}), agent chose {r.decision}."))

    # recipient
    if ok and not esc and not hold:
        tgt = route.get("target") or {}
        want_role = "customer" if tgt.get("kind") == "customer" else route.get("party")
        out.append(_c("role", "Recipient role matches routing", "pass" if r.to.role == want_role else "warn",
                      f"Classifier: {want_role}. Agent: {r.to.role}."))
        want_team = None if r.to.role == "customer" else (route.get("team") or {}).get("label")
        out.append(_c("team", "Team matches routing", "pass" if (r.to.team or None) == want_team else "warn",
                      f"Classifier: {want_team or 'none'}. Agent: {r.to.team or 'none'}."))
        ck = (pre.get("channel") or {}).get("kind")
        alt = (pre.get("channel") or {}).get("generator_alternate")
        allowed = {CHANNELS.get(ck, ck)}
        if ck == "internal_queue":
            allowed = QUEUES
        if alt:
            allowed |= {"Email", "Dispatch chat"}
        out.append(_c("channel", "Channel matches routing", "pass" if r.channel in allowed else "warn",
                      f"Classifier: {CHANNELS.get(ck, ck)}. Agent: {r.channel}."))
        if r.to.role == "customer" and r.channel in QUEUES:
            out.append(_c("channel_customer", "No internal queue for a customer", "fail", f"Customer addressed on {r.channel}."))
    want_intent = expected_intent(pre, esc, hold) if ok else None
    if want_intent:
        out.append(_c("intent", "Intent matches routing", "pass" if r.intent == want_intent else "warn",
                      f"Expected {want_intent}. Agent: {r.intent}."))

    # flags carried through
    for fid, key in (("safety_or_specialist_matter", "safety"), ("injection_instruction_override", "injection_suspected")):
        f = flags.get(fid) or {}
        if f.get("fired"):
            got = getattr(r.flags, key)
            out.append(_c(f"flag_{key}", f"{key.replace('_', ' ').capitalize()} flag carried", "pass" if got else "fail",
                          f"Classifier fired ({f.get('p')}); agent set {key} = {got}."))
    if (flags.get("safety_or_specialist_matter") or {}).get("fired") or r.flags.safety:
        out.append(_c("hazard_recipient", "Hazard not sent to the customer", "fail" if r.to.role == "customer" else "pass",
                      f"Recipient role: {r.to.role}."))

    # structure
    out.append(_c("body_rule", "Body and handover match the decision", "pass" if (esc and r.body is None and r.handover) or (hold and r.body is None and not r.handover) or (not esc and not hold and r.body and not r.handover) else "fail",
                  "Escalation has a handover and no body." if esc else "A hold sends nothing: no body, no handover." if hold else "Message has a body and no handover."))
    bad = [s for s in [c.source for c in r.claims_made] + list(r.evidence_refs) if s not in ids]
    out.append(_c("sources", "Every claim cites a real event", "fail" if bad else ("pass" if r.claims_made or esc or hold else "warn"),
                  f"Unknown event ids: {', '.join(sorted(set(bad)))}." if bad else f"{len(r.claims_made)} claims, all sourced."))

    # message hygiene
    if r.body:
        issues = []
        if URL.search(r.body): issues.append("contains a URL or domain")
        leak = LEAKS.search(r.body)
        if leak: issues.append(f"uses the word \"{leak.group(0)}\" (the prompt reserves it for the rationale)")
        if MARKDOWN.search(r.body): issues.append("uses markdown")
        n = len([s for s in re.split(r"(?<=[.!?])\s+", r.body.strip()) if s])
        if not 2 <= n <= 5: issues.append(f"{n} sentences (asked for 2 to 5)")
        out.append(_c("hygiene", "Message follows the style rules", "warn" if issues else "pass", "; ".join(issues) or "No links, no classifier talk, 2 to 5 sentences."))
    return out
