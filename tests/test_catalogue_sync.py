"""deskagent/catalogue.py must match the normalised Delivery catalogue. Skips when the data folder is absent
(the Railway image ships deskagent/ without data/)."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
CAT = ROOT / "data" / "delivery" / "catalogue"
GOLD = [ROOT / "data" / "pipeline" / "gold_labels_delivery.csv", ROOT / "data" / "pipeline" / "gold_labels_synthetic.csv"]

from deskagent import catalogue as c  # noqa: E402


def _skip() -> bool:
    return not (CAT / "parameters.json").exists()


def test_enums_match_parameters_json():
    if _skip():
        return
    enums = json.loads((CAT / "parameters.json").read_text())["enums"]
    pairs = {"requester_type": c.REQUESTER_TYPE, "issue_type": c.ISSUE_TYPE, "shipment_stage": c.SHIPMENT_STAGE,
             "owner_org_type": c.OWNER_ORG_TYPE, "urgency": c.URGENCY, "risk_flags": c.RISK_FLAGS,
             "verification_state": c.VERIFICATION_STATE, "recipient_function": c.RECIPIENT_FUNCTION,
             "action_class": c.ACTION_CLASS, "proof_standard": c.PROOF_STANDARD, "queue": c.QUEUE, "human_gate": c.HUMAN_GATE}
    for name, ours in pairs.items():
        assert sorted(ours) == sorted(enums[name]), (name, sorted(set(ours) ^ set(enums[name])))
    assert set(c.ACTION_CLASS_TO_DECISION) == set(c.ACTION_CLASS)


def test_routing_pairs_match_gold_labels():
    if _skip():
        return
    gold = set()
    for f in GOLD:
        if f.exists():
            gold |= {(r["owner_org_type"], r["recipient_function"]) for r in csv.DictReader(f.open())}
    ours = {(org, fn) for org, funcs in c.ROUTING.items() for fn in funcs}
    assert ours == gold, {"only_in_catalogue_py": ours - gold, "only_in_gold": gold - ours}


def test_channels_match_event_log_and_routing_table():
    if _skip():
        return
    ev = ROOT / "data" / "delivery" / "agent" / "events.jsonl"
    seen = {json.loads(l).get("channel") for l in ev.open()} if ev.exists() else set(c.CHANNELS)
    assert set(c.CHANNELS) == seen, set(c.CHANNELS) ^ seen
    rt = json.loads((CAT / "routing_table.json").read_text())["channel_by_recipient_org_type"]
    for org, chans in rt.items():
        assert set(chans) == set(c.CHANNEL_BY_ORG[org]), (org, set(chans) ^ set(c.CHANNEL_BY_ORG[org]))


def test_queues_match_escalation_queues_json():
    if _skip():
        return
    q = json.loads((CAT / "escalation_queues.json").read_text())["queues"]
    assert set(q) == set(c.QUEUES)
    for name, (_, chan, sla, gate) in c.QUEUES.items():
        assert q[name]["channel_rule"] == chan, name
        assert q[name]["sla"] == sla, name
        assert q[name]["human_gate"] == gate, name


def test_prompt_uses_catalogue_vocabulary():
    from deskagent import prompts, schemas
    for fn in c.RECIPIENT_FUNCTION:
        assert fn in prompts.PLANNER_SYSTEM, fn
    for ch in c.CHANNELS:
        assert ch in prompts.PLANNER_SYSTEM, ch
    props = schemas.PROPOSE_PLAN_TOOL["input_schema"]["properties"]
    assert props["proof_standard"]["enum"] == c.PROOF_STANDARD
    assert props["case_parameters"]["properties"]["owner_org_type"]["enum"] == c.OWNER_ORG_TYPE
    assert schemas.ACTION_ITEM["properties"]["recipient_function"]["enum"] == c.RECIPIENT_FUNCTION
    for slop in ("alternatives_rejected", "confidence", "closes_when", "direct_answer", "human_handover_notes"):
        assert slop not in props, slop


if __name__ == "__main__":
    import inspect
    for name, fn in list(globals().items()):
        if name.startswith("test_") and inspect.isfunction(fn):
            fn()
            print("ok", name)
