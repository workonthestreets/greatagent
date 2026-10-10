#!/usr/bin/env python3
"""Render judge prompts for the proxy evaluation, mirroring eval.py's judge() input.

For each plan file <case_id>.json (the planner's propose_plan object) the script writes
<out>/<case_id>.judge.md containing, in order, the case as the planner saw it, the plan
rendered the way deskagent/report.py renders ANSWER.md, and the hidden reference. The
reference is either the case's _reference.md (stress cases, --reference-dir) or, for cases
with a recorded next action, the hidden index sections plus the hidden later events
(--raw + --manifest), exactly as eval.py's reference_text() builds it.

Proxy declaration: there is no execution stage in a proxy run, so the rendered output says
that every proposed action is to be graded as if executed exactly as written, in order.

  python3 -I proxy_eval_judge_prepare.py --prompts P --plans R --raw raw_cases.jsonl \
      --manifest P/_manifest.json --out J
  python3 -I proxy_eval_judge_prepare.py --prompts P --plans R --raw stress_raw.jsonl \
      --reference-dir stress_cases --out J
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DECISION_LABEL = {
    "act": "ACT — route the request to the party with authority",
    "request_information": "REQUEST INFORMATION — ask the right party for what is missing",
    "escalate_to_human": "ESCALATE TO HUMAN — hand over with full context",
    "hold_no_action": "HOLD — no action now (deliberate)",
    "decline": "DECLINE — request cannot be fulfilled as asked",
}
REVEALING_SECTIONS = {"overview", "next action at escalation", "outcome", "boundaries and remaining work", "boundaries"}
REVEALING_DETAIL_KEYS = ("status", "updated", "completed", "resolved", "closed")
PROXY_NOTE = ("planner proxy run: the proposed actions below are to be graded as executed exactly as "
              "written, in the order given (this run has no reviewer or execution stage)")


def _q(text: str) -> str:
    lines = (text or "").strip().splitlines()
    return "\n".join("> " + ln for ln in lines) if lines else "> (empty)"


def agent_output_text(case_id: str, title: str, plan: dict) -> str:
    dt = plan.get("decision_type")
    out = [f"# Case {case_id} — {title}", "",
           f"**Decision:** {DECISION_LABEL.get(dt, dt)}", "",
           f"**In one line:** {plan.get('decision_summary', '')}", "",
           f"**Final result:** {PROXY_NOTE}", ""]
    if (plan.get("direct_answer") or "").strip():
        out += ["## Direct answer", "", plan["direct_answer"].strip(), ""]
    out += ["## Actions taken", ""]
    actions = plan.get("actions") or []
    if not actions:
        out += ["No outbound action (deliberate). " + (plan.get("follow_up") or ""), ""]
    for i, a in enumerate(actions, 1):
        tool = a.get("tool")
        if tool == "send_message":
            out.append(f"{i}. **send_message** → {a.get('to_name', '')} ({a.get('to_role', '')}) via *{a.get('channel', '')}* — SENT (proxy)")
            if a.get("subject"):
                out.append(f"   - Subject: {a['subject']}")
            out += ["", _q(a.get("body", ""))]
        elif tool == "escalate_to_human":
            out.append(f"{i}. **escalate_to_human** → {a.get('to_name') or 'Desk supervisor'} (priority {a.get('priority', 'normal')}) — SENT (proxy)")
            out += ["", _q(a.get("body", ""))]
        elif tool == "schedule_follow_up":
            out.append(f"{i}. **schedule_follow_up** at {a.get('when', '')} — SCHEDULED (proxy): {a.get('body', '')}")
        else:
            out.append(f"{i}. **{tool}** — RECORDED (proxy): {a.get('body', '')}")
        out.append("")
    out += ["## Deliberately not doing", ""]
    out += [f"- {x}" for x in (plan.get("not_doing") or [])] or ["- (none stated)"]
    out += ["", f"**Closes when:** {plan.get('closes_when', '')}", "", f"**Follow-up:** {plan.get('follow_up', '')}", "",
            "(Reviewer approved autonomous action: not applicable — planner-only proxy run, no reviewer stage)"]
    return "\n".join(out)


def event_text(e: dict) -> str:
    lines = [f"## {e.get('timestamp_raw') or e.get('timestamp')} — event {e.get('event_id')}", ""]
    for k, v in (e.get("meta") or {}).items():
        lines.append(f"- **{k}:** {v}")
    lines += ["", (e.get("body") or "").strip()]
    return "\n".join(lines)


def reference_from_raw(rec: dict, hidden_ids: set[str]) -> str:
    parts = []
    details = rec.get("details") or {}
    det = [f"- **{k}:** {v}" for k, v in details.items() if str(k).strip().lower().startswith(REVEALING_DETAIL_KEYS)]
    for name in rec.get("section_order") or list((rec.get("sections") or {}).keys()):
        if name.lower() in REVEALING_SECTIONS:
            parts.append(f"## {name}\n\n{(rec['sections'].get(name) or '').strip()}")
    if det:
        parts.append("## Case details (hidden keys)\n\n" + "\n".join(det))
    hidden = [e for e in rec.get("events") or [] if str(e.get("event_id")) in hidden_ids]
    if hidden:
        parts.append("Hidden later events (what actually happened next):\n\n" + "\n\n".join(event_text(e) for e in hidden))
    return "\n\n".join(parts) or "(no reference available)"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prompts", required=True, help="directory of <case_id>.prompt.md (the case as the planner saw it)")
    ap.add_argument("--plans", required=True, help="directory of <case_id>.json planner outputs")
    ap.add_argument("--raw", required=True, help="raw_cases.jsonl for titles, sections and events")
    ap.add_argument("--manifest", help="_manifest.json from proxy_eval_prepare (hidden event ids)")
    ap.add_argument("--reference-dir", help="directory of <case_number>/_reference.md rubrics")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = {}
    for line in Path(args.raw).read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            raw[r["case_id"]] = r
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8")) if args.manifest else {}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    written, problems = [], []
    for plan_path in sorted(Path(args.plans).glob("*.json")):
        case_id = plan_path.stem
        prompt_path = Path(args.prompts) / f"{case_id}.prompt.md"
        rec = raw.get(case_id)
        if not prompt_path.exists() or rec is None:
            problems.append(f"{case_id}: missing prompt or raw record")
            continue
        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{case_id}: plan is not valid JSON ({exc})")
            continue
        if args.reference_dir:
            ref_path = Path(args.reference_dir) / str(rec.get("case_number")) / "_reference.md"
            reference = ref_path.read_text(encoding="utf-8") if ref_path.exists() else "(no reference available)"
            if not ref_path.exists():
                problems.append(f"{case_id}: no _reference.md at {ref_path}")
        else:
            hidden = set(str(x) for x in (manifest.get(case_id, {}).get("hidden_events") or []))
            reference = reference_from_raw(rec, hidden)
        text = (f"<case_as_seen_by_agent>\n{prompt_path.read_text(encoding='utf-8').strip()}\n</case_as_seen_by_agent>\n\n"
                f"<agent_output>\n{agent_output_text(case_id, rec.get('title', ''), plan)}\n</agent_output>\n\n"
                f"<hidden_reference>\n{reference.strip()}\n</hidden_reference>\n\nGrade the agent and call submit_grade.")
        (out / f"{case_id}.judge.md").write_text(text, encoding="utf-8")
        written.append(case_id)
    print(json.dumps({"written": len(written), "out": str(out), "problems": problems}))


if __name__ == "__main__":
    main()
