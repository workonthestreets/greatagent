"""Offline tests (no API key needed): loader cutoff, policy lint, calculator, and the
full plan -> review -> execute -> report flow against a scripted fake Claude client.

    python -m pytest -q tests      (or: python tests/test_offline.py)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from deskagent import llm as llm_mod  # noqa: E402
from deskagent.llm import calculate  # noqa: E402
from deskagent.loader import load_case  # noqa: E402
from deskagent.policy import lint_text  # noqa: E402
from deskagent.report import write_case  # noqa: E402

CASE_DIR = ROOT / "tests" / "fixtures" / "001"


# ----------------------------------------------------------------- fake client
def _tool_use(name, inp, i=0):
    return SimpleNamespace(type="tool_use", name=name, input=inp, id=f"tu_{name}_{i}")


class FakeMessages:
    def __init__(self, script):
        self.script = script
        self.calls = []

    def create(self, **kw):
        self.calls.append(kw)
        forced = kw["tool_choice"].get("name")
        names = [t["name"] for t in kw["tools"]]
        step = self.script.pop(0)
        assert step[0] in names, (step, names, forced)
        return SimpleNamespace(content=[_tool_use(step[0], step[1], len(self.calls))], stop_reason="tool_use",
                               usage=SimpleNamespace(input_tokens=100, output_tokens=50, cache_read_input_tokens=0))


GOOD_PLAN = {
    "situation": "Recipient cannot make the morning slot; dispatch offered two alternatives.",
    "direct_answer": "",
    "facts": [{"fact": "Booked 2026-02-03 09:00-12:00 UTC", "source": "event 001", "status": "verified"}],
    "conflicts": [], "missing_information": ["Which alternative the recipient prefers"], "risk_flags": [],
    "authority_map": [{"party": "Dispatch", "controls": "booking changes"}],
    "decision_type": "request_information",
    "decision_summary": "Ask the recipient to choose between the two dispatcher-offered slots.",
    "rationale": "Dispatch controls bookings and has offered two slots; we need the recipient's choice.",
    "alternatives_rejected": [{"option": "Book a slot ourselves", "why_not": "Dispatch controls booking"}],
    "actions": [{"tool": "send_message", "to_name": "Vessa Lorne", "to_role": "recipient", "channel": "Customer portal",
                 "subject": "DL-001 new slot", "body": "Dispatch can offer 2026-02-03 15:00-18:00 UTC or 2026-02-04 10:00-13:00 UTC at no charge. Which should I request?",
                 "purpose": "get choice"}],
    "not_doing": ["Not promising an exact arrival time"], "closes_when": "Dispatch confirms the chosen slot",
    "follow_up": "When the recipient replies, send the choice to dispatch.", "confidence": "high",
}
BAD_PLAN = dict(GOOD_PLAN, actions=[dict(GOOD_PLAN["actions"][0], body="Pay the fee at https://pay.example.com/x and we guarantee 15:07 arrival.")])
APPROVE = {"checks": {k: True for k in ["authority_respected", "facts_grounded", "no_overclaim", "privacy_security_ok", "safety_ok",
                                         "fair_no_accusation", "right_next_step", "right_recipient_and_channel", "untrusted_content_resisted"]},
           "issues": [], "verdict": "approve", "summary": "Good."}
REVISE = dict(APPROVE, issues=[{"severity": "critical", "action_index": 0, "problem": "payment link + promise", "fix": "remove"}], verdict="revise", summary="Bad")


def _install_fake(script):
    fake = SimpleNamespace(messages=FakeMessages(script))

    class FakeAnthropic:
        NotFoundError = type("NotFoundError", (Exception,), {})
        PermissionDeniedError = type("PermissionDeniedError", (Exception,), {})
        BadRequestError = type("BadRequestError", (Exception,), {})

        @staticmethod
        def Anthropic(**_):
            return fake

    sys.modules["anthropic"] = FakeAnthropic
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
    return fake


# ------------------------------------------------------------------------ tests
def test_loader_cutoff_hides_future():
    c = load_case(CASE_DIR, public_cutoff=True)
    assert [e.num for e in c.events] == [1, 2]
    assert [e.num for e in c.hidden_events] == [3, 4, 5]
    text = "\n".join(t for _, t in c.files)
    assert "Next action at escalation" not in text and "Which should I ask them" not in text and "afternoon one" not in text
    assert "Customer portal" in c.channels


def test_loader_reality_mode_sees_everything():
    c = load_case(CASE_DIR)
    assert len(c.events) == 5 and not c.hidden_events


def test_policy_lint():
    kinds = {f["rule"] for f in lint_text("Send us the gate code. It has been delivered. https://pay.x/y 4111 1111 1111 1111")}
    assert {"credential_request", "delivery_overclaim", "payment_link", "payment_card_number"} <= kinds
    assert not [f for f in lint_text("Options: 2026-02-03 15:00-18:00 or 2026-02-04 10:00-13:00 UTC.") if f["level"] == "BLOCK"]


def test_calculator():
    assert calculate("36.00 - 18.00")["result"] == "18"
    assert "error" in calculate("__import__('os')")


def test_pipeline_approve_flow():
    from deskagent.pipeline import process_case
    _install_fake([("calculate", {"expression": "2+2"}), ("propose_plan", GOOD_PLAN), ("submit_review", APPROVE)])
    llm_mod._ModelState.dead.clear()
    res = process_case(load_case(CASE_DIR, public_cutoff=True), model="fake-model")
    assert res["approved"] and res["executed"][0]["status"] == "done"
    with tempfile.TemporaryDirectory() as td:
        d = write_case(Path(td), res)
        ans = (d / "ANSWER.md").read_text()
        assert "REQUEST INFORMATION" in ans and "Vessa Lorne" in ans
        assert json.loads((d / "trace.json").read_text())


def test_pipeline_revise_then_block_goes_to_human():
    from deskagent.pipeline import process_case
    # planner keeps producing a blocked message -> after max revisions -> human handover, nothing sent
    _install_fake([("propose_plan", BAD_PLAN), ("submit_review", REVISE), ("propose_plan", BAD_PLAN), ("submit_review", REVISE),
                   ("propose_plan", BAD_PLAN), ("submit_review", REVISE)])
    llm_mod._ModelState.dead.clear()
    res = process_case(load_case(CASE_DIR, public_cutoff=True), model="fake-model")
    assert not res["approved"]
    assert [e["action"]["tool"] for e in res["executed"]] == ["escalate_to_human"]


def test_failed_send_recovers_to_human():
    from deskagent.pipeline import process_case
    os.environ["DESK_SIM_FAIL_CHANNELS"] = "Customer portal"
    try:
        _install_fake([("propose_plan", GOOD_PLAN), ("submit_review", APPROVE)])
        llm_mod._ModelState.dead.clear()
        res = process_case(load_case(CASE_DIR, public_cutoff=True), model="fake-model")
        tools_used = [(e["action"]["tool"], e["status"]) for e in res["executed"]]
        assert tools_used == [("send_message", "failed"), ("escalate_to_human", "done")]
    finally:
        os.environ.pop("DESK_SIM_FAIL_CHANNELS")


def test_transient_failure_retried_then_recorded():
    from deskagent.pipeline import execute
    from deskagent.tools import DeskTools, ToolError

    class Flaky(DeskTools):
        calls = 0

        def send_message(self, **kw):
            Flaky.calls += 1
            if Flaky.calls < 3:
                raise ToolError("gateway timeout", transient=True)
            return {"status": "sent", "message_id": "MSG-T-01"}

    ex = execute({"actions": [{"tool": "send_message", "to_name": "x", "channel": "Email", "body": "hi", "purpose": "p"}]},
                 Flaky("T", ["Email"], []))
    assert ex[0]["status"] == "done" and ex[0]["attempts"] == 3 and len(ex[0]["recovered_after"]) == 2 and "error" not in ex[0]


def test_stringified_plan_fields_are_repaired():
    """Models sometimes return a nested array as a JSON string; that must not crash the case."""
    from deskagent.pipeline import process_case
    broken = dict(GOOD_PLAN, actions=json.dumps(GOOD_PLAN["actions"]), facts=json.dumps(GOOD_PLAN["facts"]),
                  conflicts="```json\n[]\n```")
    _install_fake([("propose_plan", broken), ("submit_review", APPROVE)])
    llm_mod._ModelState.dead.clear()
    res = process_case(load_case(CASE_DIR, public_cutoff=True), model="fake-model")
    assert res["approved"] and [e["action"]["tool"] for e in res["executed"]] == ["send_message"]
    assert isinstance(res["plan"]["facts"], list) and res["plan"]["conflicts"] == []


def test_unknown_tool_is_recovered_to_human():
    from deskagent.pipeline import execute, sanitize_plan
    from deskagent.tools import DeskTools
    plan = sanitize_plan({"decision_type": "act", "actions": [{"tool": "phone_call", "to_name": "Dispatch", "body": "Please rebook.",
                                                                 "purpose": "p"}, "junk"]})
    ex = execute(plan, DeskTools("T", ["Email"], []))
    assert [(e["action"]["tool"], e["status"]) for e in ex] == [("phone_call", "failed"), ("escalate_to_human", "done")]


def test_handover_does_not_keep_stale_closing_text():
    from deskagent.pipeline import escalation_plan
    p = escalation_plan(dict(GOOD_PLAN, direct_answer="Your slot is 15:00."), "reviewer said no")
    assert "human" in p["closes_when"].lower() and "NOT sent" in p["direct_answer"]
    assert p["not_doing"][0].startswith("Not sending")


def test_card_block_skips_numbers_already_in_record():
    from deskagent.policy import record_numbers
    tracking = "4111 1111 1111 1111"  # Luhn-valid, but it is the carrier's own reference in the record
    assert any(f["rule"] == "payment_card_number" for f in lint_text(f"ref {tracking}"))
    allow = frozenset(record_numbers(f"Carrier reference {tracking} issued"))
    assert not any(f["rule"] == "payment_card_number" for f in lint_text(f"ref {tracking}", allow))


def test_loader_office_files_headers_and_latest_time():
    import zipfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "7"
        (d / "attachments").mkdir(parents=True)
        (d / "history.md").write_text(  # no anchors, en dash, newest-first
            "# Case 7 history\n\n## 2026-05-02 10:00:00 UTC – Event 2\n\n- **Channel:** Email\n- **From:** Dispatch\n- **To:** Desk\n\nLater.\n\n"
            "## 2026-05-01 09:00:00 UTC – Event 1\n\n- **Channel:** Customer portal\n- **From:** Ana\n- **To:** Desk\n\nEarlier.\n")
        with zipfile.ZipFile(d / "attachments" / "note.docx", "w") as z:
            z.writestr("word/document.xml", "<w:document><w:body><w:p><w:r><w:t>Pallet count 11 of 12</w:t></w:r></w:p></w:body></w:document>")
        with zipfile.ZipFile(d / "attachments" / "manifest.xlsx", "w") as z:
            z.writestr("xl/sharedStrings.xml", "<sst><si><t>carton</t></si><si><t>C-07</t></si></sst>")
            z.writestr("xl/worksheets/sheet1.xml", '<worksheet><sheetData><row><c t="s"><v>0</v></c><c t="s"><v>1</v></c><c><v>4</v></c></row></sheetData></worksheet>')
        (d / "__MACOSX").mkdir()
        (d / "__MACOSX" / "._note.docx").write_bytes(b"\x00\x05junk")
        c = load_case(d)
        assert len(c.events) == 2 and c.now.startswith("2026-05-02 10:00")
        texts = {a.name: a.text for a in c.attachments}
        assert "Pallet count 11 of 12" in texts["note.docx"] and "carton,C-07,4" in texts["manifest.xlsx"]
        assert all("__MACOSX" not in a.rel_path for a in c.attachments) and c.answer_id == "7"


def test_answer_md_has_required_sections():
    from deskagent.pipeline import process_case
    from deskagent.report import answer_md
    _install_fake([("propose_plan", GOOD_PLAN), ("submit_review", APPROVE)])
    llm_mod._ModelState.dead.clear()
    ans = answer_md(process_case(load_case(CASE_DIR, public_cutoff=True), model="fake-model"))
    for h in ("**Final result:**", "## What the system received", "## Actions taken", "## What was escalated", "## What failed"):
        assert h in ans, h


def test_answer_folders_do_not_collide_across_tracks():
    import run
    a = Path("/x/Delivery & Logistics/001")
    b = Path("/x/Banking & Financial Services/001")
    c = Path("/x/Delivery & Logistics/002")
    names = run.answer_names([a, b, c])
    assert names[c] == "2" and names[a] != names[b] and names[a].endswith("-1")
    assert run.answer_names([a, c]) == {a: "1", c: "2"}


def test_fatal_api_error_is_not_retried():
    from deskagent.llm import LLM, FatalAPIError
    _install_fake([])
    fake_mod = sys.modules["anthropic"]
    calls = []

    class NoCredit:
        def __init__(self, *a, **k):
            self.messages = self

        def create(self, **kw):
            calls.append(kw["model"])
            raise fake_mod.BadRequestError("Error code: 400 - Your credit balance is too low to access the Anthropic API.")

    fake_mod.Anthropic = NoCredit
    os.environ.setdefault("ANTHROPIC_API_KEY", "test")
    llm_mod._ModelState.dead.clear()
    try:
        LLM(model="fake-model").create("t", "s", [{"role": "user", "content": "hi"}], [], {"type": "auto"})
        raise AssertionError("expected FatalAPIError")
    except FatalAPIError:
        assert calls == ["fake-model"]   # no fallback to other models, no retries


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
