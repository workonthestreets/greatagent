"""Deterministic policy checks on outbound actions.

Two levels:
  * BLOCK  - never allowed to leave the desk (executor refuses, case goes to a human).
  * WARN   - suspicious wording; passed to the LLM reviewer, which decides in context
             (e.g. "please do not share a gate code" is fine, "send us the gate code" is not).
"""
from __future__ import annotations

import re
from typing import List

BLOCK_RULES = [
    ("payment_card_number", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("payment_link", re.compile(r"https?://\S*(pay|checkout|invoice|billing|stripe|paypal)\S*", re.I)),
    ("raw_url", re.compile(r"https?://\S+", re.I)),
]

WARN_RULES = [
    ("credential_request", re.compile(
        r"\b(password|passcode|pin\b|pin code|gate code|door code|access code|entry code|key ?safe|lockbox|one[- ]time (pass)?code|otp|cvv|cvc|security code|sort code|account number|card number|login details)\b", re.I)),
    ("delivery_overclaim", re.compile(r"\b(has been|was|is now) (successfully )?(delivered|collected|refunded|returned|cleared|paid)\b", re.I)),
    ("promise_language", re.compile(r"\b(guarantee[sd]?|definitely|will arrive at|exactly at|promise|without fail|100%)\b", re.I)),
    ("money_commitment", re.compile(r"\b(we will refund|you will (be refunded|receive a refund|get your money)|compensat(e|ion) (you|will)|we('| wi)ll (waive|cover|reimburse))\b", re.I)),
    ("accusation", re.compile(r"\b(fraud|fraudulent|lying|lied|stole|stolen|theft|scam(mer)?|dishonest)\b", re.I)),
    ("unsafe_handling_advice", re.compile(
        r"\b(clean (it|the \w+) up|wipe|mop|safe to (eat|consume|drink|use|handle)|still (edible|fine to eat)|lift (it|the)|carry (it|the)|dismantle|drag|open the (parcel|package|box|carton))\b", re.I)),
    ("contact_details", re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}|\+\d{1,3}[ \d-]{7,}\d|\b0\d{3,4}[ -]?\d{3}[ -]?\d{3,4}\b", re.I)),
]

NEGATION = re.compile(r"\b(do not|don't|never|no need to|not|without|please avoid|avoid)\b[^.!?]{0,60}$", re.I)


def _luhn_ok(s: str) -> bool:
    digits = [int(c) for c in s if c.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2:
            d *= 2
            d -= 9 if d > 9 else 0
        total += d
    return total % 10 == 0


def lint_text(text: str) -> List[dict]:
    findings = []
    for name, rx in BLOCK_RULES:
        for m in rx.finditer(text or ""):
            if name == "payment_card_number" and not _luhn_ok(m.group(0)):
                continue
            findings.append({"level": "BLOCK", "rule": name, "match": m.group(0)[:80]})
    for name, rx in WARN_RULES:
        for m in rx.finditer(text or ""):
            prefix = text[max(0, m.start() - 80):m.start()]
            negated = bool(NEGATION.search(prefix))
            findings.append({"level": "WARN", "rule": name, "match": m.group(0)[:80], "negated_context": negated})
    # dedupe raw_url when payment_link already matched
    if any(f["rule"] == "payment_link" for f in findings):
        findings = [f for f in findings if f["rule"] != "raw_url"]
    return findings


def lint_plan(plan: dict, known_channels: List[str]) -> List[dict]:
    out = []
    known = {c.lower() for c in known_channels}
    for i, a in enumerate(plan.get("actions") or []):
        if a.get("tool") == "send_message":
            for f in lint_text((a.get("subject") or "") + "\n" + (a.get("body") or "")):
                out.append({"action_index": i, **f})
            ch = (a.get("channel") or "").strip()
            if not ch:
                out.append({"action_index": i, "level": "WARN", "rule": "missing_channel", "match": ""})
            elif known and ch.lower() not in known:
                out.append({"action_index": i, "level": "WARN", "rule": "channel_not_seen_in_record", "match": ch})
            if not (a.get("to_name") or a.get("to_role")):
                out.append({"action_index": i, "level": "WARN", "rule": "missing_recipient", "match": ""})
    if plan.get("decision_type") in ("act", "request_information") and not any(
            a.get("tool") in ("send_message", "escalate_to_human") for a in plan.get("actions") or []):
        out.append({"action_index": -1, "level": "WARN", "rule": "act_without_outbound_action", "match": ""})
    return out


def blocking(findings: List[dict], action_index: int) -> List[dict]:
    return [f for f in findings if f["level"] == "BLOCK" and f.get("action_index") == action_index]


def format_lint(findings: List[dict]) -> str:
    if not findings:
        return "No automated policy findings."
    lines = []
    for f in findings:
        neg = " (appears in a negated/'do not' context)" if f.get("negated_context") else ""
        lines.append(f"- [{f['level']}] action {f.get('action_index')}: {f['rule']} -> '{f.get('match', '')}'{neg}")
    return "\n".join(lines)
