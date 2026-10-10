"""Plan -> lint -> independent review -> (revise) -> execute -> result.

Nothing leaves the desk until the reviewer approves. If the plan cannot be made safe
within the revision budget, or the reviewer says no autonomous action is safe, the
case is handed to a human with the full context and the drafted actions.
"""
from __future__ import annotations

import json
import os
import time
from typing import Optional

from .llm import LLM, calculate
from .loader import Case
from .policy import format_lint, lint_plan, record_numbers
from .prompts import PLANNER_SYSTEM, PLANNER_USER_TEMPLATE, REVIEWER_SYSTEM, REVIEWER_USER_TEMPLATE
from .schemas import CALCULATE_TOOL, PROPOSE_PLAN_TOOL, SUBMIT_REVIEW_TOOL
from .tools import DeskTools, ToolError

MAX_REVISIONS = int(os.environ.get("DESK_MAX_REVISIONS", "2"))


# ------------------------------------------------------------------ case -> prompt
def case_body_text(case: Case) -> str:
    parts = []
    for name, text in case.files:
        parts.append(f'<file name="{name}">\n{text.strip()}\n</file>')
    for a in case.attachments:
        if a.kind in ("text", "pdf") and a.text:
            parts.append(f'<attachment name="{a.rel_path}" type="{a.kind}">\n{a.text.strip()}\n</attachment>')
        elif a.kind == "image":
            parts.append(f'<attachment name="{a.rel_path}" type="image">(image provided below)</attachment>')
        elif a.kind == "pdf":
            parts.append(f'<attachment name="{a.rel_path}" type="pdf">(scanned PDF provided below)</attachment>')
        else:
            parts.append(f'<attachment name="{a.rel_path}" type="unreadable">{a.note}</attachment>')
    return "\n\n".join(parts)


def binary_blocks(case: Case) -> list:
    blocks = []
    for a in case.attachments:
        if a.kind == "image" and a.data_b64:
            blocks.append({"type": "text", "text": f"Attachment image: {a.rel_path}"})
            blocks.append({"type": "image", "source": {"type": "base64", "media_type": a.media_type, "data": a.data_b64}})
        elif a.kind == "pdf" and not a.text and a.data_b64:
            blocks.append({"type": "text", "text": f"Attachment PDF (no text layer): {a.rel_path}"})
            blocks.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": a.data_b64}})
    return blocks


# ------------------------------------------------------------------------ phases
def plan_case(llm: LLM, case: Case, body: str, feedback: Optional[str] = None) -> dict:
    revision_block = ""
    if feedback:
        revision_block = f"\n<revision_request>\n{feedback}\n</revision_request>\nProduce a corrected plan that resolves every critical and major issue.\n"
    warnings = ("Loader warnings: " + "; ".join(case.warnings)) if case.warnings else ""
    text = PLANNER_USER_TEMPLATE.format(
        now=case.now or "unknown", revision_block=revision_block, case_id=case.case_id, track=case.track,
        mode=case.mode, case_body=body, channels=", ".join(case.channels) or "(none recorded)",
        parties="; ".join(case.parties) or "(none recorded)", warnings=warnings)
    content = [{"type": "text", "text": text}] + binary_blocks(case)
    return llm.run_tool_loop("plan" if not feedback else "revise", PLANNER_SYSTEM, content, PROPOSE_PLAN_TOOL,
                             aux_tools={"calculate": (CALCULATE_TOOL, calculate)}, max_turns=6, max_tokens=16000)


def review_plan(llm: LLM, case: Case, body: str, plan: dict, lint: list) -> dict:
    text = REVIEWER_USER_TEMPLATE.format(case_id=case.case_id, track=case.track, case_body=body,
                                         plan_json=json.dumps(plan, indent=2, ensure_ascii=False), lint=format_lint(lint))
    content = [{"type": "text", "text": text}] + binary_blocks(case)
    review = llm.run_tool_loop("review", REVIEWER_SYSTEM, content, SUBMIT_REVIEW_TOOL, max_turns=3, max_tokens=12000)
    issues = review.get("issues") or []
    serious = [i for i in issues if i.get("severity") in ("critical", "major")]
    if review.get("verdict") == "approve" and serious:
        review["verdict"] = "revise"
        review["summary"] = (review.get("summary") or "") + " [auto: approve overridden because critical/major issues were listed]"
    if review.get("verdict") == "revise" and not serious and not any(l["level"] == "BLOCK" for l in lint):
        review["verdict"] = "approve"
    return review


def feedback_text(plan: dict, review: dict, lint: list) -> str:
    lines = ["Your previous plan:", json.dumps(plan, indent=2, ensure_ascii=False), "",
             f"Independent reviewer verdict: {review.get('verdict')} - {review.get('summary', '')}"]
    for i in review.get("issues") or []:
        lines.append(f"- [{i.get('severity')}] action {i.get('action_index')}: {i.get('problem')} -> FIX: {i.get('fix')}")
    blocks = [l for l in lint if l["level"] == "BLOCK"]
    if blocks:
        lines.append("Hard policy blocks (these messages cannot be sent as written):")
        lines += [f"- action {b['action_index']}: {b['rule']} '{b['match']}'" for b in blocks]
    return "\n".join(lines)


PLAN_LISTS = ("facts", "conflicts", "missing_information", "risk_flags", "authority_map", "alternatives_rejected",
              "actions", "not_doing")
TOOLS = ("send_message", "escalate_to_human", "schedule_follow_up", "record_case_note")


def sanitize_plan(plan: dict) -> dict:
    """Make a model-produced plan safe to lint, review, execute and report: list fields are lists,
    actions are dicts, and an action with a missing/unknown tool is kept (so it is reported and
    recovered as a failure) rather than crashing the case."""
    plan = dict(plan or {})
    for k in PLAN_LISTS:
        v = plan.get(k)
        if v is None or v == "":
            plan[k] = []
        elif not isinstance(v, list):
            plan[k] = [v]
    plan["actions"] = [a for a in plan["actions"] if isinstance(a, dict)]
    for k in ("facts", "authority_map", "alternatives_rejected"):
        plan[k] = [x if isinstance(x, dict) else {"fact": str(x), "source": "", "status": "inferred", "party": str(x),
                                                    "controls": "", "option": str(x), "why_not": ""} for x in plan[k]]
    for k in ("situation", "decision_summary", "rationale", "closes_when", "follow_up", "direct_answer", "human_handover_notes"):
        if k in plan and not isinstance(plan[k], str):
            plan[k] = json.dumps(plan[k], ensure_ascii=False) if not isinstance(plan[k], (list, tuple)) else "\n".join(map(str, plan[k]))
    if plan.get("decision_type") not in ("act", "request_information", "escalate_to_human", "hold_no_action", "decline"):
        plan["decision_type"] = "escalate_to_human" if plan.get("decision_type") else "hold_no_action"
    return plan


def escalation_plan(plan: dict, reason: str) -> dict:
    """Convert a plan that could not be approved into a safe human handover."""
    drafted = [a for a in plan.get("actions") or [] if a.get("tool") == "send_message"]
    handover = [
        f"Reason for handover: {reason}",
        f"Situation: {plan.get('situation', '')}",
        "Verified facts: " + "; ".join(f"{f.get('fact')} ({f.get('source')})" for f in plan.get("facts") or [] if f.get("status") == "verified"),
    ]
    if plan.get("conflicts"):
        handover.append("Conflicts: " + "; ".join(plan["conflicts"]))
    if plan.get("missing_information"):
        handover.append("Missing: " + "; ".join(plan["missing_information"]))
    if plan.get("risk_flags"):
        handover.append("Risks: " + "; ".join(plan["risk_flags"]))
    if drafted:
        handover.append("Drafted but NOT sent (for your review): " + " | ".join(
            f"to {a.get('to_name') or a.get('to_role')} via {a.get('channel')}: {a.get('body')}" for a in drafted))
    handover.append("Decision needed: confirm the correct next step and recipient, then send or amend the draft.")
    new = dict(plan)
    new["decision_type"] = "escalate_to_human"
    new["decision_summary"] = "Hand the case to the desk supervisor: " + reason
    new["actions"] = [{"tool": "escalate_to_human", "to_name": "Desk supervisor", "priority": "high",
                       "subject": f"Case {plan.get('_case_id', '')} needs human decision", "body": "\n".join(handover),
                       "purpose": "No autonomous action was approved as safe."}]
    new["human_handover_notes"] = "\n".join(handover)
    new["closes_when"] = "A human supervisor reviews this handover and decides the next step; nothing was sent to any party."
    new["follow_up"] = "Supervisor decision needed (see the handover ticket). The drafted messages remain unsent until a human approves them."
    new["not_doing"] = ["Not sending any of the drafted messages: the independent review did not approve autonomous action."] + list(plan.get("not_doing") or [])
    if (plan.get("direct_answer") or "").strip():
        new["direct_answer"] = "(Draft only - NOT sent; awaiting human review.)\n\n" + plan["direct_answer"].strip()
    return new


def execute(plan: dict, tools: DeskTools) -> list:
    executed = []
    for idx, a in enumerate(plan.get("actions") or []):
        tool = a.get("tool")
        fn = {"send_message": tools.send_message, "escalate_to_human": tools.escalate_to_human,
              "schedule_follow_up": tools.schedule_follow_up, "record_case_note": tools.record_case_note}.get(tool)
        rec = {"index": idx, "action": a, "attempts": 0, "status": "pending"}
        if fn is None:
            rec.update(status="failed", error=f"unknown tool {tool}")
        for attempt in range(1, 4 if fn else 1):
            rec["attempts"] = attempt
            try:
                rec["result"] = fn(**a)
                rec["status"] = "done"
                if rec.pop("error", None):
                    rec["recovered_after"] = rec.pop("_errors", [])
                break
            except ToolError as exc:
                rec["error"] = str(exc)
                rec.setdefault("_errors", []).append(str(exc))
                if exc.transient and attempt < 3:
                    time.sleep(0.2 * attempt)
                    continue
                rec["status"] = "failed"
                rec.pop("_errors", None)
                break
            except Exception as exc:  # noqa: BLE001 - a tool bug must not crash the case
                rec.update(status="failed", error=f"{type(exc).__name__}: {exc}")
                rec.pop("_errors", None)
                break
        executed.append(rec)
        if rec["status"] == "failed" and tool != "escalate_to_human" and (a.get("body") or "").strip():
            # Recovery: never silently drop a message - hand it to a human with the exact draft.
            res = tools.escalate_to_human(
                to_name="Desk supervisor", priority="high",
                subject=f"Manual send needed for case {tools.case_id}",
                body=(f"Automated {tool or 'action'} failed ({rec['error']}) after {rec['attempts']} attempt(s). "
                      f"Please deliver this approved message manually or via another verified channel.\n"
                      f"To: {a.get('to_name')} ({a.get('to_role')}) via {a.get('channel')}\n"
                      f"Subject: {a.get('subject', '')}\n{a.get('body')}"))
            executed.append({"index": f"{idx + 1}-recovery", "action": {"tool": "escalate_to_human", "to_name": "Desk supervisor",
                                                                         "priority": "high", "purpose": "recover failed send",
                                                                         "body": res.get("handover", "")},
                             "attempts": 1, "status": "done", "result": res})
    return executed


def final_status(plan: dict, executed: list) -> str:
    sent = [e for e in executed if e["action"].get("tool") == "send_message" and e["status"] == "done"]
    failed = [e for e in executed if e["status"] == "failed"]
    escal = [e for e in executed if e["action"].get("tool") == "escalate_to_human" and e["status"] == "done"]
    parts = []
    if sent:
        parts.append("Awaiting response from " + ", ".join(
            f"{e['action'].get('to_name') or e['action'].get('to_role')} ({e['result']['message_id']})" for e in sent))
    if escal:
        parts.append("Escalated to human (" + ", ".join(e["result"]["ticket_id"] for e in escal) + ")")
    if failed:
        parts.append(f"{len(failed)} action(s) failed and were handed to a human")
    if not parts:
        parts.append("No action taken - holding: " + (plan.get("follow_up") or plan.get("decision_summary", "")))
    return "; ".join(parts) + ". Closes when: " + (plan.get("closes_when") or "n/a")


# --------------------------------------------------------------------- orchestration
def process_case(case: Case, model: Optional[str] = None, review: bool = True, trace: Optional[list] = None) -> dict:
    trace = trace if trace is not None else []
    trace += [{"type": "input", "case_id": case.case_id, "track": case.track, "mode": case.mode,
                    "files": [n for n, _ in case.files], "attachments": [a.rel_path for a in case.attachments],
                    "hidden_events": [e.num for e in case.hidden_events], "hidden_attachments": case.hidden_attachments,
                    "events": len(case.events), "now": case.now, "warnings": case.warnings}]
    t0 = time.time()
    llm = LLM(model=model, trace=trace)
    body = case_body_text(case)
    rounds = []

    allow_numbers = frozenset(record_numbers(body))
    plan = sanitize_plan(plan_case(llm, case, body))
    plan["_case_id"] = case.case_id
    approved = not review
    final_reason = ""
    for r in range(MAX_REVISIONS + 1):
        lint = lint_plan(plan, case.channels, allow_numbers)
        if not review:
            rounds.append({"round": r, "plan_decision": plan.get("decision_type"), "lint": lint, "review": None})
            if any(l["level"] == "BLOCK" for l in lint):
                approved, final_reason = False, "hard policy block in drafted message"
            break
        rv = review_plan(llm, case, body, plan, lint)
        rounds.append({"round": r, "plan_decision": plan.get("decision_type"), "plan_summary": plan.get("decision_summary"),
                       "lint": lint, "review": rv})
        if rv.get("verdict") == "approve":
            approved = True
            break
        if rv.get("verdict") == "escalate_instead":
            approved, final_reason = False, "reviewer judged that no autonomous action is safe: " + rv.get("summary", "")
            break
        if r == MAX_REVISIONS:
            approved, final_reason = False, "plan still had unresolved issues after revisions: " + rv.get("summary", "")
            break
        plan = sanitize_plan(plan_case(llm, case, body, feedback=feedback_text(plan, rv, lint)))
        plan["_case_id"] = case.case_id

    original_plan = plan
    if not approved:
        plan = escalation_plan(plan, final_reason)

    tools = DeskTools(case.answer_id, case.channels, trace, allow_numbers)
    executed = execute(plan, tools)
    return {
        "case_id": case.case_id, "answer_id": case.answer_id, "title": case.title, "track": case.track, "mode": case.mode,
        "plan": plan, "pre_handover_plan": original_plan if not approved else None, "approved": approved,
        "review_rounds": rounds, "executed": executed, "final_status": final_status(plan, executed),
        "warnings": case.warnings, "inputs": trace[0], "usage": llm.usage, "models_used": sorted({t["model"] for t in trace if t.get("type") == "llm_call" and "error" not in t}),
        "elapsed_s": round(time.time() - t0, 1), "trace": trace,
    }
