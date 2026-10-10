import hashlib
import hmac
import json
import time

import pytest

pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from voice import app as voice


def test_tool_speaks_template_and_post_call_checks_signature(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "triage")
    monkeypatch.setenv("ELEVENLABS_WEBHOOK_SECRET", "wh")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(voice, "decide", lambda case: {
        "action": "request", "party": "carrier", "team": "Parcel trace team", "org": "Plover Arc Logistics",
        "missing": "a trace of DL-1", "escalate": False, "message": "We will refund you £20"})
    client = TestClient(voice.app)
    body = {"conversation_id": "c1", "caller_name": "Ana", "order_ref": "DL-1", "issue": "Parcel missing", "update_by": "text", "contact": "07700 900 123"}
    assert client.post("/voice/tool", json=body).status_code == 401
    say = client.post("/voice/tool", json=body, headers={"X-Tool-Secret": "s3"}).json()["say"]
    assert "Plover Arc Logistics" in say and "text you on 07700, 900, 123" in say and "£" not in say
    again = client.post("/voice/tool", json=body, headers={"X-Tool-Secret": "s3"}).json()
    assert again.get("repeat") and again["say"] == say  # a double tool call repeats, never "updated"
    fix = client.post("/voice/tool", headers={"X-Tool-Secret": "s3"},
                      json=body | {"update_by": "email", "contact": "ana at example dot com"}).json()
    assert fix["status"] == "contact_updated" and "a, n, a, at example dot com" in fix["say"]
    raw = json.dumps({"type": "post_call_transcription", "data": {"conversation_id": "c1", "transcript": []}})
    t = str(int(time.time()))
    sig = hmac.new(b"wh", f"{t}.{raw}".encode(), hashlib.sha256).hexdigest()
    ok = client.post("/voice/post-call", content=raw, headers={"ElevenLabs-Signature": f"t={t},v0={sig}"})
    bad = client.post("/voice/post-call", content=raw, headers={"ElevenLabs-Signature": f"t={t},v0=00"})
    assert (ok.status_code, bad.status_code) == (200, 401) and (tmp_path / "c1-transcript.json").exists()
    assert voice.checked_contact("email", "ana dot vell at example dot com") == ("email", "ana.vell@example.com")
    assert voice.checked_contact("email", "ana at example") == ("", "")
    assert voice.checked_contact("call", "123") == ("", "")


def _assist_client(monkeypatch, tmp_path, decision):
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_ASSIST", "1")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    if callable(decision):
        monkeypatch.setattr(voice, "decide", decision)
    else:
        monkeypatch.setattr(voice, "decide", lambda case: decision)
    return TestClient(voice.app)


def _turn(client, conv, utterance, **kw):
    return client.post("/voice/turn", json={"conversation_id": conv, "utterance": utterance, **kw},
                       headers={"X-Tool-Secret": "s3"})


def test_turn_asks_customer_and_keeps_going(monkeypatch, tmp_path):
    monkeypatch.delenv("VOICE_ASSIST", raising=False)
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    body = {"conversation_id": "t1", "utterance": "my parcel hasn't arrived"}
    assert TestClient(voice.app).post("/voice/turn", json=body,
                                     headers={"X-Tool-Secret": "s3"}).status_code == 404
    client = _assist_client(monkeypatch, tmp_path, {
        "action": "ask", "party": "customer", "missing": "order or tracking reference",
        "escalate": False})
    assert client.post("/voice/turn", json=body).status_code == 401
    out = _turn(client, "t1", "my parcel hasn't arrived").json()
    assert out["status"] == "continue" and out["say"] == voice.ASKS["ref"]


def test_turn_ends_on_escalation_and_on_third_party(monkeypatch, tmp_path):
    client = _assist_client(monkeypatch, tmp_path, {
        "action": "escalate", "party": "internal", "team": "Operations lead", "escalate": True})
    out = _turn(client, "t2", "it's an emergency").json()
    assert out["status"] == "end_call" and out["reason"] == "escalated" and "passed it to" in out["say"]
    client = _assist_client(monkeypatch, tmp_path, {
        "action": "request", "party": "carrier", "org": "Plover Arc Logistics", "escalate": False})
    out = _turn(client, "t3", "where is it?", update_by="text", contact="07700 900 123").json()
    assert (out["status"], out["reason"]) == ("end_call", "handed_to_third_party")
    assert "Plover Arc Logistics" in out["say"] and "text you on 07700, 900, 123" in out["say"]


def test_turn_state_accumulates_across_turns(monkeypatch, tmp_path):
    seen = []

    def decide(case):
        seen.append(case.text)
        return {"action": "ask", "party": "customer", "missing": "order or tracking reference",
                "escalate": False}

    client = _assist_client(monkeypatch, tmp_path, decide)
    _turn(client, "t4", "hi, it's Ana, my parcel is missing", caller_name="Ana")
    _turn(client, "t4", "the number is DL-9", order_ref="DL-9")
    assert len(seen) == 2 and "my parcel is missing" in seen[1] and "the number is DL-9" in seen[1]
    assert "event 002" in seen[1] and "**Primary shipment:** DL-9" in seen[1]
    state = json.loads((tmp_path / "t4-state.json").read_text())
    assert state["order_ref"] == "DL-9" and state["caller_name"] == "Ana"
    assert state["turns"] == ["hi, it's Ana, my parcel is missing", "the number is DL-9"]


def test_turn_never_speaks_the_missing_field(monkeypatch, tmp_path):
    client = _assist_client(monkeypatch, tmp_path, {
        "action": "ask", "party": "customer", "missing": "the CVV from your payment card",
        "escalate": False})
    say = _turn(client, "t5", "what do you need?").json()["say"]
    assert say == voice.ASKS["generic"] and "CVV" not in say and "card" not in say


def test_turn_timeout_gives_safe_close(monkeypatch, tmp_path):
    monkeypatch.setattr(voice, "DECIDE_BUDGET_S", 0.05)

    def slow(case):
        time.sleep(0.2)
        return {"action": "ask", "party": "customer"}

    client = _assist_client(monkeypatch, tmp_path, slow)
    out = _turn(client, "t6", "hello?").json()
    assert out["status"] == "end_call" and "logged" in out["say"]
    time.sleep(0.3)  # let the over-budget decide finish while LOG_DIR still points at tmp_path


def test_tool_asks_only_from_whitelist(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "triage")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    client = TestClient(voice.app)
    for missing, key in [("the brother's full name, so the delivery can be authorised to him as an alternative recipient", "receiver"),
                         ("the specific address detail the carrier needs clarified (e.g. unit, floor or access information)", "access"),
                         ("the CVV from your payment card so the refund can be processed", "generic")]:
        monkeypatch.setattr(voice, "decide", lambda case, m=missing: {"action": "ask", "party": "customer", "missing": m, "escalate": False})
        say = client.post("/voice/tool", json={"conversation_id": f"w-{key}", "issue": "x"}, headers={"X-Tool-Secret": "s3"}).json()["say"]
        assert say == voice.ASKS[key] and "CVV" not in say and "brother" not in say


def test_tool_hands_call_to_deskagent_and_speaks_only_templates(monkeypatch, tmp_path):
    from voice import desk
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "deskagent")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    seen = {}

    def fake_process(case, model=None):
        seen["case"] = case
        return {"plan": {"decision_type": "request_information", "decision_summary": "Ask carrier to trace."},
                "approved": True, "answer_id": "x", "trace": [],
                "executed": [{"index": 0, "status": "done", "action": {
                    "tool": "send_message", "to_name": "Parcel trace team", "channel": "Email",
                    "subject": "Trace DL-204", "body": "Please trace DL-204."}}]}
    monkeypatch.setattr(desk, "_deskagent", lambda: (lambda path, track="": str(path), fake_process,
                                                     lambda out, res: None))
    client = TestClient(voice.app)
    body = {"conversation_id": "conv_ab12", "caller_name": "Ana", "order_ref": "DL-204",
            "issue": "My parcel never arrived.", "update_by": "text", "contact": "07700 900123"}
    started = time.time()
    reply = client.post("/voice/tool", json=body, headers={"X-Tool-Secret": "s3"}).json()
    assert time.time() - started < 2 and reply["status"] == "logged" and "case AB12" in reply["say"]
    folder = tmp_path / "cases" / "conv-ab12"
    assert "Primary shipment:** DL-204" in (folder / "index.md").read_text()
    assert '<a id="event-001"></a>' in (folder / "history.md").read_text()
    desk._threads["conv_ab12"].join(5)
    assert seen["case"] == str(folder)
    update = client.post("/voice/update", json={"conversation_id": "conv_ab12"},
                         headers={"X-Tool-Secret": "s3"}).json()["say"]
    assert update.startswith("Our desk has contacted Parcel trace team. We'll update you when they reply")


def test_deskagent_runs_are_capped_but_cases_still_saved(monkeypatch, tmp_path):
    from voice import desk
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "deskagent")
    monkeypatch.setenv("VOICE_DESK_MAX_PER_HOUR", "1")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    monkeypatch.setattr(desk, "_starts", desk.deque())
    runs = []
    monkeypatch.setattr(desk, "run", lambda conv, folder: runs.append(conv))
    client = TestClient(voice.app)
    for conv in ("conv_one1", "conv_two2"):
        reply = client.post("/voice/tool", headers={"X-Tool-Secret": "s3"}, json={
            "conversation_id": conv, "caller_name": "Ana", "order_ref": "DL-1", "issue": "Parcel late."}).json()
        assert reply["status"] == "logged"
    desk._threads["conv_one1"].join(5)
    assert runs == ["conv_one1"]
    capped = json.loads((tmp_path / "cases" / "conv-two2" / "_result.json").read_text())
    assert capped["status"] == "capped" and (tmp_path / "cases" / "conv-two2" / "index.md").exists()
    assert client.get("/health").json() == {"ok": True, "agent": "deskagent"}


def test_second_problem_in_one_call_is_a_new_case_and_hazard_words_get_999(monkeypatch, tmp_path):
    from voice import desk
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "deskagent")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    started = []
    monkeypatch.setattr(desk, "start", lambda conv, folder: started.append(conv))
    client = TestClient(voice.app)
    base = {"conversation_id": "conv_w23j", "caller_name": "Cash", "order_ref": "DL204",
            "update_by": "text", "contact": "07700 900123"}
    first = client.post("/voice/tool", headers={"X-Tool-Secret": "s3"},
                        json=base | {"issue": "My parcel hasn't arrived."}).json()
    again = client.post("/voice/tool", headers={"X-Tool-Secret": "s3"},
                        json=base | {"issue": "My parcel hasn't arrived."}).json()
    hazard = client.post("/voice/tool", headers={"X-Tool-Secret": "s3"}, json=base | {
        "issue": "Another package smells really weird and my son touched it."}).json()
    assert again.get("repeat") and again["say"] == first["say"]
    assert started == ["conv_w23j", "conv_w23j-2"]
    assert "call 999" in hazard["say"] and hazard["say"] != first["say"]



def test_shipment_lookup_adds_only_pre_escalation_context(monkeypatch, tmp_path):
    from voice import desk, lookup
    case = tmp_path / "data" / "025"
    case.mkdir(parents=True)
    (case / "index.md").write_text(
        "# Case 025: Lost parcel\n\n## Case details\n- **Status:** Completed\n- **Primary shipment:** DL-025\n"
        "- **Coordinator:** Desk\n\n## Initial request\nPlease ask the merchant.\n\n"
        "## Next action at escalation\nSECRET-LABEL\n")
    (case / "history.md").write_text(
        '# h\n\n<a id="event-001"></a>\n## t — event 001\n- **Stage:** Context\n\nCarrier confirms loss.\n\n'
        '<a id="event-002"></a>\n## t — event 002\n- **Stage:** Escalation\n\nRecipient wants a replacement.\n\n'
        '<a id="event-003"></a>\n## t — event 003\n- **Stage:** Agent action\n\nSECRET-LATER\n')
    monkeypatch.setattr(lookup, "DATA", tmp_path / "data")
    lookup._index.cache_clear()
    assert lookup.find_shipment("dl 025") == lookup.find_shipment("DL025") == case
    task = tmp_path / "data" / "039"
    task.mkdir()
    (task / "index.md").write_text("# Case 039\n\n## Case details\n- **Primary task reference:** TG-039\n")
    (task / "history.md").write_text('<a id="event-001"></a>\n## t — event 001\n- **Stage:** Escalation\n\n'
                                     "Parcel DL-039-O and DL-025 never came.\n")
    lookup._index.cache_clear()
    assert lookup.find_shipment("TG-039") == lookup.find_shipment("DL-039-O") == task  # task ref + event ref
    assert lookup.find_shipment("DL-025") == case  # its own Primary beats a mention elsewhere
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    folder = desk.write_case_folder("conv_x", "Ana", "DL025", "Any news on my kettle?", "", "")
    built = (folder / "index.md").read_text() + (folder / "history.md").read_text()
    assert "Carrier confirms loss" in built and "Any news on my kettle?" in built
    assert "SECRET" not in built and "Completed" not in built and "event 003" in built  # the call is event 003
    assert desk.lookup_info(folder) == {"matched": True, "source_case": "025", "primary": "DL-025",
                                        "events_used": 2}
    lookup._index.cache_clear()


def test_hub_mode_sends_one_request_and_falls_back_on_error(monkeypatch, tmp_path):
    from voice import desk, hub
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_AGENT", "hub")
    monkeypatch.setenv("HUB_URL", "http://hub.test")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "hubsecret")
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    started, sent = [], []
    monkeypatch.setattr(desk, "start", lambda conv, folder: started.append(conv))

    class Reply:
        def __init__(self, body): self.body = body
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return json.dumps(self.body).encode()

    def fake_urlopen(req, timeout):
        sent.append((req.full_url, req.get_header("X-hub-secret"), json.loads(req.data), timeout))
        if "get_latest_update" in req.full_url:
            return Reply({"latest": {"body": "We have asked the carrier to trace DL-204."}})
        return Reply({"case_id": "C-000123", "say": "hub's own words"})
    monkeypatch.setattr(hub.urllib.request, "urlopen", fake_urlopen)
    client = TestClient(voice.app)
    body = {"conversation_id": "conv_hub1", "caller_name": "Ana", "order_ref": "DL-204",
            "issue": "Parcel never came.", "update_by": "text", "contact": "07700 900123"}
    reply = client.post("/voice/tool", json=body, headers={"X-Tool-Secret": "s3"}).json()
    url, secret, payload, timeout = sent[0]
    assert url == "http://hub.test/webhooks/ask_agent" and secret == "hubsecret" and timeout == 3
    assert payload["caller_phone"] == "07700900123" and "Parcel never came." in payload["request"]
    assert "case C-000123" in reply["say"] and "hub's own words" not in reply["say"] and started == []
    update = client.post("/voice/update", json={"conversation_id": "conv_hub1"},
                         headers={"X-Tool-Secret": "s3"}).json()["say"]
    assert update == "The latest update on your case is: We have asked the carrier to trace DL-204."

    def down(req, timeout):
        raise OSError("connection refused")
    monkeypatch.setattr(hub.urllib.request, "urlopen", down)
    fallback = client.post("/voice/tool", json=body | {"conversation_id": "conv_hub2"},
                           headers={"X-Tool-Secret": "s3"}).json()
    assert fallback["status"] == "logged" and started == ["conv_hub2"] and "C-" not in fallback["say"]
    assert hub._UNSAFE_TO_SPEAK.search("Your refund of £40 has been approved")


def test_finished_case_is_mirrored_to_hub_and_failures_are_swallowed(monkeypatch, tmp_path):
    from voice import desk, hub_mirror
    monkeypatch.setenv("HUB_URL", "http://hub.test")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "hubsecret")
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    fake = {"plan": {"decision_type": "act", "decision_summary": "Ask carrier to trace."}, "approved": True,
            "answer_id": "x", "trace": [], "executed": [{"index": 0, "status": "done", "action": {
                "tool": "send_message", "to_name": "Parcel trace team", "channel": "Email", "body": "Trace DL-204."}}]}
    monkeypatch.setattr(desk, "_deskagent", lambda: (lambda path, track="": path, lambda case, model=None: fake,
                                                     lambda out, res: None))
    sent = []

    class Reply:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"case_id": "C-ABC123"}'

    def ok(req, timeout):
        sent.append((req.full_url, req.get_header("X-hub-secret"), json.loads(req.data), timeout))
        return Reply()
    monkeypatch.setattr(hub_mirror.urllib.request, "urlopen", ok)
    folder = desk.write_case_folder("conv_m1", "Ana", "DL-204", "Never came.", "text", "07700900123")
    out = desk.run("conv_m1", folder)
    url, secret, body, timeout = sent[0]
    assert (url, secret, timeout) == ("http://hub.test/webhooks/record_case", "hubsecret", 5)
    assert body["caller_phone"] == "07700900123" and body["request"] == "Never came."
    assert body["decision"]["messages"] == [{"to": "Parcel trace team", "channel": "Email", "body": "Trace DL-204."}]
    assert out["hub_mirror"] == {"ok": True, "case_id": "C-ABC123"}

    def missing(req, timeout):
        raise hub_mirror.urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)
    monkeypatch.setattr(hub_mirror.urllib.request, "urlopen", missing)
    out = desk.run("conv_m1", folder)
    assert out["status"] == "done" and out["hub_mirror"] == {"ok": False, "error": "HTTP 404 from hub"}


def test_case_update_waits_while_pending_then_speaks_only_a_template(monkeypatch, tmp_path):
    from voice import desk
    monkeypatch.setenv("VOICE_TOOL_SECRET", "s3")
    monkeypatch.setenv("VOICE_UPDATE_WAIT_S", "0")
    monkeypatch.setattr(voice, "UPDATE_WAIT_S", 0)
    monkeypatch.setattr(voice, "LOG_DIR", tmp_path)
    monkeypatch.setattr(desk, "CASES_DIR", tmp_path / "cases")
    folder = desk.write_case_folder("conv_u1", "Cash", "DL-204", "Never came.", "text", "07700900123")
    (folder / "_result.json").write_text(json.dumps({"status": "pending"}))
    client = TestClient(voice.app)
    ask = lambda: client.post("/voice/update", json={"conversation_id": "conv_u1"},
                              headers={"X-Tool-Secret": "s3"}).json()
    assert ask() == {"say": "Still working on it.", "status": "pending"}
    (folder / "_result.json").write_text(json.dumps({
        "status": "done", "decision_type": "act",
        "decision_summary": "Refund £40 approved; it will arrive tomorrow",  # must never be spoken
        "contacted": ["Returns team, Tallowmere Goods (order TG-025)", "Cash"]}))
    done = ask()
    assert done["status"] == "done"
    assert done["say"] == ("Our desk has contacted Returns team, Tallowmere Goods, and sent you a message. "
                           "We'll update you when they reply. I can't promise a time or outcome yet.")
    assert "£" not in done["say"] and "tomorrow" not in done["say"] and "TG-025" not in done["say"]

