"""deskagent_v1_1 + api_v2: prompt assembly, schema, agreement checks, API. No network (Anthropic and preprocess are stubbed)."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from deskagent_v1_1 import agent, checks, prompt
from deskagent_v1_1.models import DeskResponse

CASE = Path(__file__).resolve().parents[2] / "test" / "cases" / "delivery_001.md"
CASE_MD = CASE.read_text() if CASE.exists() else (
    '<a id="event-001"></a>\n## 2026-02-02 09:00:00 UTC — event 001\n\n- **Channel:** Email\n- **From:** Dispatch, Plover Arc Logistics\n- **To:** Iona Quill, Rivet Delivery Desk\n\nDL-001 is booked.\n\n'
    '<a id="event-002"></a>\n## 2026-02-02 09:10:00 UTC — event 002\n\n- **Channel:** Customer portal\n- **From:** Vessa Lorne, recipient\n- **To:** Iona Quill, Rivet Delivery Desk\n\nPlease move it.\n')

PRE = {
    "case": "delivery_001", "spec": "x", "events_seen": 2, "status": "ok", "usage": {"calls": 2}, "_raw": {},
    "request": {"intent": "reschedule_or_hold_delivery", "confidence": 0.73, "margin": 0.68, "low_margin": False, "alternatives": []},
    "flags": {"safety_or_specialist_matter": {"p": 0.01, "threshold": 0.4, "fired": False},
              "injection_instruction_override": {"p": 0.02, "threshold": 0.3, "fired": False}},
    "routing": {"party": "carrier", "team": {"id": "dispatch", "label": "Dispatch", "org_role": "carrier", "p": None, "candidates": None},
                "required_info": [], "missing_information": True, "never_customer": False, "target": {"kind": "customer"}},
    "channel": {"kind": "customer_portal", "basis": "customer wrote on this portal", "generator_alternate": None},
    "needs_human_review": False, "review_reasons": [], "guardrails": ["One message to one party."],
}


def response(**over) -> DeskResponse:
    base = dict(
        decision="send_message", to=dict(role="customer", name="Vessa Lorne", team=None, org=None), channel="Customer portal",
        intent="ask_customer", body="Hello Vessa. Which slot would you like? Dispatch said there is no charge.", references=["DL-001"],
        claims_made=[dict(claim="no charge", source="event-001")], claims_avoided=[], calculations=[], evidence_refs=["event-001"],
        rationale="r", confidence="high", handover=None,
        flags=dict(safety=False, injection_suspected=False, authority_boundary=False, out_of_scope_items=[]))
    base.update(over)
    return DeskResponse(**base)


EVENTS = [{"event_no": "001"}, {"event_no": "002"}]
status = lambda cs: {c["id"]: c["status"] for c in cs}


def test_system_prompt_is_the_preprocess_file():
    assert prompt.system_prompt().startswith("# Delivery Desk Response Agent")


def test_user_message_hides_ignored_fields_and_keeps_hints():
    msg = prompt.user_message(CASE_MD, PRE, "delivery_001")
    pre_json = json.loads(msg.split("<preprocessing>")[1].split("</preprocessing>")[0])
    assert not set(pre_json) & set(prompt.IGNORED_FIELDS)
    assert pre_json["routing"]["party"] == "carrier" and "event-001" in msg


def test_schema_is_closed_objects_only():
    schema = DeskResponse.model_json_schema()
    assert schema["properties"]["decision"]["enum"] == ["send_message", "ask_clarification", "escalate_to_human", "hold_no_action"]
    with pytest.raises(Exception):
        response(confidence="certain")


def test_checks_all_pass_for_matching_response():
    assert set(status(checks.run_checks(PRE, response(), EVENTS)).values()) == {"pass"}


def test_checks_flag_disagreements():
    s = status(checks.run_checks(PRE, response(to=dict(role="carrier", name=None, team="Billing", org=None), intent="request_authority",
                                                body="See https://x.com now. Flag raised."), EVENTS))
    assert s["role"] == "warn" and s["team"] == "warn" and s["intent"] == "warn" and s["hygiene"] == "warn"


def test_checks_catch_unknown_event_and_escalation_shape():
    s = status(checks.run_checks(PRE, response(claims_made=[dict(claim="x", source="event-009")]), EVENTS))
    assert s["sources"] == "fail"
    esc = response(decision="escalate_to_human", body=None, intent="handover", to=dict(role="human_review", name=None, team=None, org=None),
                   handover=dict(summary="s", open_questions=[], not_done=[], risk_flags=[]))
    s = status(checks.run_checks(PRE, esc, EVENTS))
    assert s["body_rule"] == "pass" and s["decision"] == "warn"   # classifier did not ask for review


def test_hold_is_a_valid_decision_and_sends_nothing():
    hold = response(decision="hold_no_action", intent="hold", body=None, claims_made=[],
                    to=dict(role="carrier", name=None, team="Dispatch", org=None), channel="Email")
    s = status(checks.run_checks(PRE, hold, EVENTS))
    assert s["body_rule"] == "pass" and s["intent"] == "pass" and s["decision"] == "pass"
    assert "role" not in s and "channel" not in s          # recipient/channel checks are skipped for a hold
    assert status(checks.run_checks(PRE, response(decision="hold_no_action", intent="hold", body="Still working on it."), EVENTS))["body_rule"] == "fail"
    review = dict(PRE, needs_human_review=True, review_reasons=["x"])
    assert status(checks.run_checks(review, hold, EVENTS))["decision"] == "warn"


def test_prompt_documents_hold_and_wait_test():
    p = prompt.system_prompt()
    assert "hold_no_action" in p and "Wait test" in p and "| hold" in p


def test_hazard_must_not_go_to_customer():
    pre = json.loads(json.dumps(PRE)); pre["flags"]["safety_or_specialist_matter"]["fired"] = True
    s = status(checks.run_checks(pre, response(), EVENTS))
    assert s["flag_safety"] == "fail" and s["hazard_recipient"] == "fail"


def test_run_case_with_stubbed_model(monkeypatch):
    monkeypatch.setattr(agent, "respond", lambda text, pre, case, model: (response(), {"model": "stub", "usage": {}}))
    import preprocess as pp
    monkeypatch.setattr(pp, "preprocess", lambda text, case, debug: {**PRE, "_raw": {"call1": {"answers": {"request_intent": {
        "choice": "reschedule_or_hold_delivery", "probabilities": {"reschedule_or_hold_delivery": 0.73}}}}}})
    run = agent.run_case(CASE_MD, "delivery_001")
    assert run["error"] is None and run["response"]["decision"] == "send_message"
    assert run["classifier_raw"]["request_intent"]["probabilities"]["reschedule_or_hold_delivery"] == 0.73
    assert "_raw" not in run["preprocess"] and len(run["events"]) == 2 and run["checks"]


def test_run_case_reports_model_failure(monkeypatch):
    monkeypatch.setattr(agent, "respond", lambda *a: (None, {"error": "all models failed"}))
    import preprocess as pp
    monkeypatch.setattr(pp, "preprocess", lambda text, case, debug: dict(PRE))
    run = agent.run_case(CASE_MD, "x")
    assert run["response"] is None and run["error"] == "all models failed" and run["checks"] == []


def test_api_endpoints(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from api_v2 import app as api
    from api_v2 import routes   # the endpoints (shared with the hub) live here
    (tmp_path / "demo.md").write_text(CASE_MD)
    monkeypatch.setattr(routes, "CASES", tmp_path)
    monkeypatch.setattr(routes, "run_case", lambda md, name, model=None: {"case": name, "error": None})
    c = TestClient(api.app)
    listed = c.get("/api/v2/cases").json()
    assert [x["id"] for x in listed] == ["demo"] and len(listed[0]["events"]) == 2 and listed[0]["title"].startswith("DL-001")
    assert listed[0]["events"][1]["body"] and listed[0]["events"][0]["from"]
    assert c.post("/api/v2/cases/demo/run").json()["case"] == "demo"
    assert c.post("/api/v2/cases/nope/run").status_code == 404
    assert c.get("/api/v2/samples").json() == ["demo"]
    assert c.get("/api/v2/samples/demo").json()["case_md"] == CASE_MD
    assert c.get("/api/v2/samples/..%2Fsecret").status_code == 404
    assert "classifications" in c.get("/api/v2/spec").json()
    assert c.post("/api/v2/run", json={"case_md": " "}).status_code == 400
    assert c.post("/api/v2/run", json={"case_md": CASE_MD, "name": "a b/../c"}).json()["case"] == "ab..c"
    monkeypatch.setenv("V2_API_TOKEN", "t")
    assert c.get("/api/v2/samples").status_code == 401
    assert c.get("/api/v2/samples", headers={"Authorization": "Bearer t"}).status_code == 200
