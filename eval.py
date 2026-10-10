#!/usr/bin/env python3
"""Development evaluation on the public example cases.

For each case: hide everything after the escalation point, run the full agent, then let
an independent Claude judge compare the decision with the hidden reference (the action a
human coordinator actually took, the outcome, and the case's boundaries / red flags).

  python eval.py "/path/to/HackatonPublicCases/Delivery & Logistics" --out runs/eval1
  python eval.py ... --only 3,23,26 --workers 8
  python eval.py ... --rejudge runs/eval1        # re-grade existing results only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from deskagent.llm import LLM, load_dotenv
from deskagent.loader import discover_cases, load_case
from deskagent.pipeline import case_body_text, process_case
from deskagent.prompts import JUDGE_SYSTEM
from deskagent.report import answer_md, write_case
from deskagent.schemas import SUBMIT_GRADE_TOOL


def reference_text(case) -> str:
    ref = Path(case.path) / "_reference.md"
    if ref.exists():
        return ref.read_text(encoding="utf-8")
    parts = []
    for k, v in case.hidden_sections.items():
        if not k.startswith("_"):
            parts.append(v)
    if case.hidden_events:
        parts.append("Hidden later events (what actually happened next):\n" + "\n\n".join(e.raw for e in case.hidden_events))
    return "\n\n".join(parts) or "(no reference available)"


def agent_output_text(res: dict) -> str:
    """What the official judges read: the case's ANSWER.md, plus the review outcome."""
    return answer_md(res) + f"\n\n(Reviewer approved autonomous action: {res.get('approved')})"


def agent_output_text_v1(res: dict) -> str:
    p = res["plan"]
    lines = [f"Decision type: {p.get('decision_type')}", f"Decision: {p.get('decision_summary')}",
             f"Rationale: {p.get('rationale')}", f"Reviewer approved autonomous action: {res.get('approved')}",
             "Executed actions:"]
    for e in res["executed"]:
        a = e["action"]
        lines.append(f"- {a.get('tool')} -> {a.get('to_name', '')} ({a.get('to_role', '')}) via {a.get('channel', '')} [{e['status']}]\n  {a.get('body', '')}")
    lines.append("Deliberately not doing: " + "; ".join(p.get("not_doing") or []))
    lines.append(f"Proof that closes this step: {p.get('proof_standard')}")
    return "\n".join(lines)


def judge(case, res: dict, model) -> dict:
    llm = LLM(model=model, trace=[])
    text = (f"<case_as_seen_by_agent>\n{case_body_text(case)}\n</case_as_seen_by_agent>\n\n"
            f"<agent_output>\n{agent_output_text(res)}\n</agent_output>\n\n"
            f"<hidden_reference>\n{reference_text(case)}\n</hidden_reference>\n\nGrade the agent and call submit_grade.")
    g = llm.run_tool_loop("judge", JUDGE_SYSTEM, [{"type": "text", "text": text}], SUBMIT_GRADE_TOOL, max_turns=3, max_tokens=8000)
    g["score"] = g.get("outcome", 0) + g.get("safety", 0) + g.get("judgement", 0) + g.get("message_quality", 0)
    req = g.get("required_outcomes") or []
    g["required_met"] = sum(1 for r in req if r.get("met") in ("yes", "via_alternative"))
    g["required_total"] = len(req)
    g["strict_pass"] = bool(g.get("verdict") == "pass" and not g.get("critical_failure") and not g.get("prohibited_actions_taken")
                            and g["required_met"] == g["required_total"])
    return g


def case_meta(path: Path) -> dict:
    m = Path(path) / "_meta.json"
    try:
        return json.loads(m.read_text()) if m.exists() else {}
    except Exception:  # noqa: BLE001
        return {}


def eval_one(path: Path, out: Path, args) -> dict:
    try:
        has_ref = (path / "_reference.md").exists()
        case = load_case(path, public_cutoff=not has_ref)
        rj = out / "answers" / case.answer_id / "result.json"
        if args.rejudge and rj.exists():
            res = json.loads(rj.read_text())
        else:
            res = process_case(case, model=args.model, review=not args.no_review)
            write_case(out / "answers", res)
        g = judge(case, res, args.judge_model or args.model)
        meta = case_meta(path)
        return {"case": path.name, "title": case.title, "decision": res["plan"].get("decision_type"),
                "expected_decision": meta.get("expected_decision") or meta.get("planned_decision", ""),
                "traits": meta.get("traits") or [], "approved": res.get("approved"), "elapsed_s": res.get("elapsed_s"),
                "n_actions": sum(1 for e in res["executed"] if e["action"].get("tool") in ("send_message", "escalate_to_human")), **g}
    except Exception as exc:  # noqa: BLE001
        return {"case": path.name, "error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc(), "score": 0,
                "verdict": "error"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases")
    ap.add_argument("--out", default=f"runs/eval-{datetime.now().strftime('%H%M%S')}")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("DESK_WORKERS", "6")))
    ap.add_argument("--model", default=os.environ.get("DESK_MODEL"))
    ap.add_argument("--judge-model", default=os.environ.get("DESK_JUDGE_MODEL"))
    ap.add_argument("--no-review", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--rejudge", action="store_true", help="reuse result.json files already in --out")
    args = ap.parse_args()
    load_dotenv()

    cases = discover_cases(args.cases)
    if args.only:
        keep = {s.strip().lstrip("0") for s in args.only.split(",")}
        cases = [c for c in cases if c.name.lstrip("0") in keep]
    out = Path(args.out)
    (out / "answers").mkdir(parents=True, exist_ok=True)
    print(f"Evaluating {len(cases)} cases -> {out}", flush=True)
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = [pool.submit(eval_one, c, out, args) for c in cases]
        for f in as_completed(futs):
            r = f.result()
            rows.append(r)
            print(f"[{len(rows)}/{len(cases)}] {r['case']} {r.get('verdict')} score={r.get('score')}/10 "
                  f"{r.get('decision', '')} {('ERR ' + r['error']) if r.get('error') else ''}"[:200], flush=True)
    # merge with rows from earlier batches written to the same --out folder
    prev = out / "scores.json"
    if prev.exists():
        done = {r["case"] for r in rows}
        try:
            rows += [r for r in json.loads(prev.read_text()) if r.get("case") not in done]
        except Exception:  # noqa: BLE001
            pass
    rows.sort(key=lambda r: r["case"])
    n = len(rows)
    tot = sum(r.get("score", 0) for r in rows)
    passes = sum(r.get("verdict") == "pass" for r in rows)
    partial = sum(r.get("verdict") == "partial" for r in rows)
    crit = [r for r in rows if r.get("safety") == 0 or r.get("verdict") == "error"]
    lines = [f"# Eval report — {datetime.now(timezone.utc).isoformat()}", "",
             f"**{passes}/{n} pass · {partial} partial · {n - passes - partial} fail/error · mean score {tot / max(n, 1):.2f}/10**", "",
             f"Mean outcome {sum(r.get('outcome', 0) for r in rows) / max(n, 1):.2f}/3 · safety {sum(r.get('safety', 0) for r in rows) / max(n, 1):.2f}/3 · "
             f"judgement {sum(r.get('judgement', 0) for r in rows) / max(n, 1):.2f}/2 · message {sum(r.get('message_quality', 0) for r in rows) / max(n, 1):.2f}/2", "",
             f"Critical safety failures / errors: {len(crit)} · judge-flagged critical failures: {sum(bool(r.get('critical_failure')) for r in rows)} · "
             f"prohibited actions taken: {sum(len(r.get('prohibited_actions_taken') or []) for r in rows)}", "",
             f"Strict pass (all required outcomes met, nothing prohibited, no critical failure): {sum(bool(r.get('strict_pass')) for r in rows)}/{n} · "
             f"required outcomes met: {sum(r.get('required_met', 0) for r in rows)}/{sum(r.get('required_total', 0) for r in rows)}", ""]
    groups = {}
    for r in rows:
        for t in (r.get("traits") or []) + ([f"expected:{r['expected_decision']}"] if r.get("expected_decision") else []):
            groups.setdefault(t, []).append(r)
    if groups:
        lines += ["| Trait / expected decision | Cases | Pass | Mean score |", "|---|---|---|---|"]
        for t, rs in sorted(groups.items()):
            lines.append(f"| {t} | {len(rs)} | {sum(x.get('verdict') == 'pass' for x in rs)} | {sum(x.get('score', 0) for x in rs) / len(rs):.2f} |")
        lines.append("")
    lines += [
             "| Case | Verdict | Score | O | S | J | M | Req met | Decision (expected) | Red flags / explanation |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        expl = r.get("error") or ("; ".join(r.get("red_flags") or []) + " — " + (r.get("explanation") or ""))
        exp = f" ({r['expected_decision']})" if r.get("expected_decision") else ""
        lines.append(f"| {r['case']} | {r.get('verdict')} | {r.get('score')} | {r.get('outcome', '')} | {r.get('safety', '')} | "
                     f"{r.get('judgement', '')} | {r.get('message_quality', '')} | {r.get('required_met', '')}/{r.get('required_total', '')} | "
                     f"{r.get('decision', '')}{exp} | {expl.replace('|', '/')[:300]} |")
    (out / "eval_report.md").write_text("\n".join(lines) + "\n")
    (out / "scores.json").write_text(json.dumps(rows, indent=1))
    print("\n".join(lines[:6]))
    print(f"Report: {out / 'eval_report.md'}")


if __name__ == "__main__":
    main()
