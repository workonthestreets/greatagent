"""Pre-processing block for the delivery desk agent.

Takes a case history (markdown in the case-file format, or plain text) and returns a dict (and JSON) of classifications
from clef-flash via OpenRouter, derived routing, a channel decision and guardrails. The JSON goes to the LLM that writes the response.

Library:  from preprocess import preprocess;  result = preprocess(text)          # dict
CLI:      python3 preprocess.py case.md [more.md ...] [--compact] [--debug]    # prints JSON ('-' reads stdin)

Needs OPENROUTER_API_KEY in the environment or in a .env file. Spec: delivery_classifications_v2_4.json (next to this script). Response prompt: delivery_desk_system_prompt.md.
Provider is pinned (default Cloudflare, override with CLEF_PROVIDER): OpenRouter otherwise alternates between providers
that return different probabilities for the same input.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_SPEC = HERE / "delivery_classifications_v2_4.json"  # shipped next to this script
URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "cloudflare/clef-flash"
PROVIDER = os.environ.get("CLEF_PROVIDER", "Cloudflare")
LOW_MARGIN = 0.15  # top-two intent gap below which the intent is flagged as uncertain (hint only)
PORTALS = {"Customer portal": "customer_portal", "Business portal": "business_portal"}
_SPEC_CACHE = {}


# ---------- input ----------
def parse_events(text):
    """Events from case-file markdown. Plain text with no event markers becomes a single event."""
    blocks = re.split(r'<a id="event-\d+"></a>', text)[1:]
    if not blocks:
        return [{"event_no": "001", "timestamp": "", "channel": "", "from": "", "to": "", "body": text.strip()}]
    events = []
    for block in blocks:
        field = lambda k: (re.search(rf"- \*\*{k}:\*\* (.*)", block) or [None, ""])[1].strip()
        head = re.search(r"## (.+?) — event (\d+)", block)
        body = [ln for ln in block.splitlines() if ln.strip() and not ln.startswith("## ") and not re.match(r"- \*\*(Channel|From|To|Stage):\*\*", ln)]
        events.append({"event_no": head.group(2) if head else f"{len(events) + 1:03d}", "timestamp": head.group(1) if head else "",
                       "channel": field("Channel"), "from": field("From"), "to": field("To"), "body": "\n".join(body).strip()})
    return events


# ---------- model call ----------
def _api_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"].strip()
    for folder in (HERE, HERE.parent):
        env = folder / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    raise RuntimeError("OPENROUTER_API_KEY not found in the environment or a .env file")


def _call(state, questions, key):
    body = json.dumps({"model": MODEL, "state": state, "questions": questions,
                       "provider": {"order": [PROVIDER], "allow_fallbacks": False}}).encode()
    for attempt in range(3):
        req = urllib.request.Request(URL, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:  # capacity errors were reported for this model
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"API error {e.code}: {e.read().decode()[:400]}")
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"network error: {e}")


def _top(answer, n=3):
    ranked = sorted(answer["probabilities"].items(), key=lambda kv: -kv[1])
    return [{"option": k, "p": v} for k, v in ranked[:n]]


# ---------- rules ----------
def decide_channel(target, team, events, flags):
    """Deterministic channel rules (spec channel_rules). Returns (kind, basis)."""
    if target["kind"] == "customer":
        seen = [PORTALS[e["channel"]] for e in events if e["channel"] in PORTALS]
        if seen:
            return seen[-1], "customer wrote on this portal"
        if flags["urgent_live_contact"]["fired"]:
            return "phone_call", "customer has not written; urgent live contact"
        return "email", "customer has not written; not urgent"
    if team:
        return team["default_channel"], "team default"
    return "email", "fallback"


def _classify(events, spec, key):
    cls = {c["id"]: c for c in spec["classifications"]}
    state = {"context": spec["state"]["preamble"], "events": events}

    # call 1: intent + flags
    flag_ids = [c for c in spec["calls"][0]["classifications"] if c != "request_intent"]
    q1 = {"request_intent": {"type": "choice", "instructions": cls["request_intent"]["instructions"], "criteria": cls["request_intent"]["options"]}}
    for fid in flag_ids:
        q1[fid] = {"type": "noul", "instructions": cls[fid]["instructions"]}
    r1 = _call(state, q1, key)
    a1 = r1["answers"]
    flags = {fid: {"p": a1[fid]["noul"], "threshold": cls[fid]["suggested_threshold"], "fired": a1[fid]["noul"] >= cls[fid]["suggested_threshold"]} for fid in flag_ids}
    intent = a1["request_intent"]["choice"]
    ranked = _top(a1["request_intent"], 3)
    margin = round(ranked[0]["p"] - ranked[1]["p"], 4)

    # call 2: required information + team (only if needed)
    route = spec["routing_map"]["intents"][intent]
    required = spec["intent_registry"]["intents"][intent]["required_info"]
    teams = route["teams"]
    q2 = {f"required__{r['id']}": {"type": "noul", "instructions": r["question"]} for r in required}
    if len(teams) > 1:
        q2["team"] = {"type": "choice", "instructions": cls["team"]["instructions"], "criteria": {t["id"]: t["pick_when"] for t in teams}}
    r2 = _call({**state, "resolved_intent": intent, "party": route["party"]}, q2, key) if q2 else None
    a2 = r2["answers"] if r2 else {}

    req_info = [{"id": r["id"], "question": r["question"], "p_present": a2[f"required__{r['id']}"]["noul"], "present": a2[f"required__{r['id']}"]["noul"] >= 0.5} for r in required]
    missing = any(not r["present"] for r in req_info)
    team_p, team_id = None, (teams[0]["id"] if teams else None)
    if "team" in a2:
        team_id = a2["team"]["choice"]
        team_p = a2["team"]["probabilities"][team_id]
    team = next((t for t in teams if t["id"] == team_id), None)

    # target (spec routing_rules)
    never_customer = bool(route.get("never_customer") or flags["safety_or_specialist_matter"]["fired"])
    if route["party"] == "human_review":
        target = {"kind": "human_review"}
    elif missing and not never_customer and route["party"] != "business_customer":
        target = {"kind": "customer", "note": "the sender of the customer-side events, or the named business contact"}
    else:
        target = {"kind": "team", "label": team["label"], "org_role": team["org"]}
    channel, basis = decide_channel(target, team, events, flags)

    reasons = []
    if intent == "other":
        reasons.append("intent is 'other'")
    for fid in ("injection_instruction_override", "unauthorised_or_sensitive_ask"):
        if flags[fid]["fired"]:
            reasons.append(f"{fid} fired")
    handoff = spec["generator_handoff"]
    cond = handoff["conditional_guardrails"]
    low_margin = margin < LOW_MARGIN
    guardrails = list(handoff["standing_guardrails"])
    for on, key_ in ((flags["safety_or_specialist_matter"]["fired"], "safety_flag"), (flags["injection_instruction_override"]["fired"], "injection_flag"),
                     (flags["unauthorised_or_sensitive_ask"]["fired"], "unauthorised_flag"), (missing, "missing_information"), (low_margin, "low_margin")):
        if on:
            guardrails += cond[key_]

    result = {
        "status": "ok",
        "request": {"intent": intent, "confidence": ranked[0]["p"], "margin": margin, "low_margin": low_margin,
                    "alternatives": [{"intent": r["option"], "p": r["p"]} for r in ranked[1:]]},
        "flags": flags,
        "routing": {"party": route["party"],
                    "team": {"id": team_id, "label": team["label"] if team else None, "org_role": team["org"] if team else None, "p": team_p,
                             "candidates": [{"id": t["id"], "label": t["label"]} for t in teams] if len(teams) > 1 else None},
                    "required_info": req_info, "missing_information": missing, "never_customer": never_customer, "target": target},
        "channel": {"kind": channel, "basis": basis, "generator_alternate": (team or {}).get("generator_alternate")},
        "needs_human_review": bool(reasons),
        "review_reasons": reasons,
        "guardrails": guardrails,
        "usage": {"calls": 1 + (r2 is not None), "input_tokens": r1["usage"]["input_tokens"] + (r2["usage"]["input_tokens"] if r2 else 0),
                  "cost_usd": round(r1["usage"]["cost"] + (r2["usage"]["cost"] if r2 else 0), 8), "provider": PROVIDER},
    }
    return result, {"call1": r1, "call2": r2}


# ---------- public API ----------
def preprocess(text, case="case", spec_path=None, debug=False):
    """Case history (markdown or plain text) -> dict for the LLM. Never raises on model/API failure: returns status 'error'."""
    try:
        path = str(spec_path or DEFAULT_SPEC)
        if path not in _SPEC_CACHE:
            _SPEC_CACHE[path] = json.load(open(path))
        spec = _SPEC_CACHE[path]
        events = parse_events(text)
        result, raw = _classify(events, spec, _api_key())
        result = {"case": case, "spec": spec["meta"]["name"], "events_seen": len(events), **result}
        if debug:
            result["_raw"] = raw
        return result
    except Exception as e:  # the LLM downstream must know classification failed
        return {"case": case, "status": "error", "error": f"{type(e).__name__}: {e}"[:400], "needs_human_review": True,
                "review_reasons": ["pre-processing failed"]}


def preprocess_file(path, **kw):
    text = sys.stdin.read() if str(path) == "-" else Path(path).read_text()
    return preprocess(text, case="stdin" if str(path) == "-" else Path(path).stem, **kw)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("files", nargs="+", help="case .md/.txt files, or - for stdin")
    ap.add_argument("--compact", action="store_true", help="single-line JSON")
    ap.add_argument("--debug", action="store_true", help="include raw model responses under _raw")
    ap.add_argument("--spec", help="path to a spec JSON (default: delivery_classifications_v2_4.json next to this script)")
    args = ap.parse_args()
    out = [preprocess_file(f, spec_path=args.spec, debug=args.debug) for f in args.files]
    print(json.dumps(out[0] if len(out) == 1 else out, indent=None if args.compact else 2, ensure_ascii=False))
