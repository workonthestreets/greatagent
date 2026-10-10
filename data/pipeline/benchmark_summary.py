#!/usr/bin/env python3
"""Build the benchmark summary: Roman's live eval runs (evals/*/scores.json, eval.py format) next to the
proxy runs (evals/<bench>/<set>-proxy/{scorer,judge}/scores.json), with breakdowns by complexity level,
queue, action class, twist and human gate, and a per-case table for the dashboard.

  python3 -I benchmark_summary.py --evals evals --bench evals/benchmark-2026-10-10 \
      --gold data/pipeline/gold_labels_delivery.csv --gold data/pipeline/gold_labels_synthetic.csv \
      --stress-labels data/pipeline/labels_stress.csv --commit <sha>

Writes <bench>/summary.json and <bench>/README.md. Proxy numbers are declared as proxies of the planner
stage (no reviewer, no execution); Roman's runs are the live reference.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

JUDGE_KEYS = ("outcome", "safety", "judgement", "message_quality")
LEVEL_NAMES = {1: "simple status", 2: "shipment data correction", 3: "multi-parcel orders", 4: "evidence and downstream decisions",
               5: "conflicting reports", 6: "safety and regulatory holds", 7: "reconciliation across shipments"}


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def judge_summary(rows: list[dict]) -> dict:
    n = len(rows)
    out = {"n": n,
           "pass": sum(r.get("verdict") == "pass" for r in rows),
           "partial": sum(r.get("verdict") == "partial" for r in rows),
           "fail": sum(r.get("verdict") not in ("pass", "partial") for r in rows),
           "mean_score": mean([r.get("score") for r in rows]),
           "critical": sum(1 for r in rows if r.get("safety") == 0 or r.get("critical_failure") or r.get("verdict") == "error")}
    for k in JUDGE_KEYS:
        out["mean_" + k] = mean([r.get(k) for r in rows])
    if any("strict_pass" in r for r in rows):
        out["strict_pass"] = sum(bool(r.get("strict_pass")) for r in rows)
    out["pass_rate"] = round(out["pass"] / n, 3) if n else None
    return out


def scorer_summary(s: dict) -> dict:
    sm = s.get("summary", {})
    return {k: sm.get(k) for k in ("n_cases", "pass", "partial", "fail", "routing_mean", "action_mean", "channel_mean",
                                   "violation_cases", "leak_cases", "decision_types")}


def load_gold(paths: list[str], stress: str | None) -> dict:
    gold = {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf-8")):
            gold[r["case_id"]] = r
    if stress:
        for r in csv.DictReader(open(stress, encoding="utf-8")):
            gold[r["case_id"]] = r
    return gold


def case_key_to_id(case: str) -> str:
    """Roman's rows use the folder number ('001', '101'); map to DEL-/STR- ids."""
    s = str(case)
    if s.isdigit():
        n = int(s)
        return f"DEL-{n:03d}" if n < 100 else (f"STR-{n}" if n < 200 else f"SYN-{n}")
    return s


def breakdown(rows: list[dict], key: str, judge_field="judge_verdict", scorer_field="scorer_verdict") -> dict:
    groups = defaultdict(list)
    for r in rows:
        v = r.get(key)
        if v in (None, "", "N/A"):
            continue
        groups[str(v)].append(r)
    out = {}
    for g, rs in sorted(groups.items(), key=lambda kv: (len(kv[0]), kv[0])):
        d = {"n": len(rs)}
        js = [r for r in rs if r.get(judge_field)]
        if js:
            d["judge_pass"] = sum(r[judge_field] == "pass" for r in js)
            d["judge_pass_rate"] = round(d["judge_pass"] / len(js), 3)
            d["judge_mean_score"] = mean([r.get("judge_score") for r in js])
        ss = [r for r in rs if r.get(scorer_field)]
        if ss:
            d["scorer_pass"] = sum(r[scorer_field] == "pass" for r in ss)
            d["scorer_pass_rate"] = round(d["scorer_pass"] / len(ss), 3)
            d["routing_mean"] = mean([float(r["routing"]) for r in ss if r.get("routing") not in (None, "")])
        out[g] = d
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--evals", default="evals")
    ap.add_argument("--bench", required=True)
    ap.add_argument("--gold", action="append", default=[])
    ap.add_argument("--stress-labels", default=None)
    ap.add_argument("--commit", default="")
    args = ap.parse_args()
    gold = load_gold(args.gold, args.stress_labels)
    bench = Path(args.bench)
    runs, cases = [], []

    # 1. Roman's live runs (eval.py format)
    for d in sorted(Path(args.evals).iterdir()):
        if not d.is_dir() or d.resolve() == bench.resolve():
            continue
        sj = d / "scores.json"
        if sj.exists():
            try:
                rows = json.loads(sj.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if not isinstance(rows, list):
                continue
            name = d.name
            set_name = ("public" if name.startswith("public") else "stress" if name.startswith("stress") else
                        "holdout" if name.startswith("holdout") else "dev" if name.startswith("dev") else "synthetic" if name.startswith("synthetic") else "experiment")
            js = judge_summary(rows)
            runs.append({"id": f"live/{name}", "kind": "live", "set": set_name, "source": str(d),
                         "agent": "deskagent full pipeline (eval.py: plan, lint, review, execute)" + (" — new code" if "new-code" in name else " — original code" if "original-code" in name else ""),
                         "judge": "Claude judge (eval.py JUDGE_SYSTEM)" + (", strict" if "strict" in name else ""),
                         "judge_summary": js})
            for r in rows:
                cid = case_key_to_id(r.get("case", ""))
                g = gold.get(cid, {})
                cases.append({"run": f"live/{name}", "set": set_name, "case_id": cid, "title": r.get("title", ""),
                              "decision": r.get("decision"), "judge_verdict": r.get("verdict"), "judge_score": r.get("score"),
                              **{k: r.get(k) for k in JUDGE_KEYS}, "strict_pass": r.get("strict_pass"),
                              "complexity_level": g.get("complexity_level"), "queue": g.get("queue"), "twist": g.get("twist"),
                              "human_gate": g.get("human_gate"), "action_class": g.get("action_class"),
                              "stress_theme": g.get("stress_theme"), "explanation": (r.get("explanation") or "")[:400]})
        elif (d / "SUMMARY.md").exists() and d.name.startswith("redteam"):
            txt = (d / "SUMMARY.md").read_text(encoding="utf-8")
            rows = []
            for m in re.finditer(r"^\| (rt-\d+) \| (.*?) \| (pass|partial|fail) \| (\d+) \| (\d+)/(\d+) \|", txt, re.M):
                rows.append({"case": m.group(1), "verdict": m.group(3), "score": int(m.group(4)), "title": m.group(2)})
            if rows:
                runs.append({"id": "live/redteam", "kind": "live", "set": "redteam", "source": str(d),
                             "agent": "deskagent full pipeline (eval.py), unchanged code", "judge": "Claude judge (official rubric shape)",
                             "judge_summary": judge_summary(rows)})
                for r in rows:
                    cases.append({"run": "live/redteam", "set": "redteam", "case_id": r["case"], "title": r["title"], "judge_verdict": r["verdict"],
                                  "judge_score": r["score"]})

    # 2. Proxy runs
    for d in sorted(bench.glob("*-proxy")):
        set_name = d.name.replace("-proxy", "")
        run = {"id": f"proxy/{set_name}", "kind": "proxy", "set": set_name, "source": str(d),
               "agent": "PLANNER_SYSTEM (deskagent/prompts.py) run verbatim by Claude Code agents on Opus 5.5; planner stage only, loader-faithful cutoff",
               "judge": "JUDGE_SYSTEM (deskagent/prompts.py) run verbatim by Claude Code agents on Opus 5.5; proposed actions graded as executed"}
        per = {}
        sj = d / "judge" / "scores.json"
        if sj.exists():
            rows = json.loads(sj.read_text(encoding="utf-8"))
            run["judge_summary"] = judge_summary(rows)
            for r in rows:
                cid = r.get("case_id") or case_key_to_id(r.get("case"))
                per[cid] = {"judge_verdict": r.get("verdict"), "judge_score": r.get("score"), **{k: r.get(k) for k in JUDGE_KEYS},
                            "strict_pass": r.get("strict_pass"), "decision": r.get("decision"), "title": r.get("title", ""),
                            "red_flags": r.get("red_flags") or [], "explanation": (r.get("explanation") or "")[:400]}
        ss = d / "scorer" / "scores.json"
        if ss.exists():
            s = json.loads(ss.read_text(encoding="utf-8"))
            run["scorer_summary"] = scorer_summary(s)
            for r in s.get("cases", []):
                cid = r["case_id"]
                per.setdefault(cid, {})
                per[cid].update({"scorer_verdict": r.get("verdict"), "routing": r.get("routing"), "action": r.get("action"),
                                 "channel": r.get("channel"), "violations": r.get("violations"), "decision": per[cid].get("decision") or r.get("decision_type"),
                                 "first_recipient": r.get("first_recipient"), "gold_owner": r.get("gold_owner"), "channel_used": r.get("channel_used"),
                                 "gold_channel": r.get("gold_channel")})
        for cid, row in sorted(per.items()):
            g = gold.get(cid, {})
            cases.append({"run": run["id"], "set": set_name, "case_id": cid, **row,
                          "complexity_level": g.get("complexity_level"), "complexity_name": g.get("complexity_name"), "queue": g.get("queue"),
                          "twist": g.get("twist") or "", "human_gate": g.get("human_gate"), "action_class": g.get("action_class"),
                          "issue_type": g.get("issue_type"), "stress_theme": g.get("stress_theme"), "urgency": g.get("urgency")})
        runs.append(run)

    # 3. Breakdowns per run
    breakdowns = {}
    for run in runs:
        rs = [c for c in cases if c["run"] == run["id"]]
        b = {}
        for key in ("complexity_level", "queue", "action_class", "twist", "human_gate", "stress_theme", "urgency"):
            bd = breakdown(rs, key)
            if bd:
                b[key] = bd
        if b:
            breakdowns[run["id"]] = b

    summary = {"generated_at": datetime.now(timezone.utc).isoformat(), "commit": args.commit, "level_names": LEVEL_NAMES,
               "declaration": ("Live runs come from Roman's eval.py (full pipeline, Claude judge). Proxy runs execute the same planner "
                               "and judge prompts verbatim through Claude Code agents (Opus 5.5) because no API key was available in the data "
                               "session; they cover the planner stage only (no reviewer, no execution) and grade proposed actions as executed. "
                               "The deterministic scorer checks routing (org type + function), action family, strict channels and hard "
                               "violations against the gold labels; it has no model in the loop."),
               "runs": runs, "breakdowns": breakdowns, "cases": cases}
    bench.mkdir(parents=True, exist_ok=True)
    (bench / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")

    # 4. README leaderboard
    L = [f"# Benchmark — Delivery Desk agent — {summary['generated_at'][:10]}", "", summary["declaration"], "",
         f"Repository commit: `{args.commit or 'working tree'}`.", "", "## Leaderboard (judge)", "",
         "| Run | Kind | Set | n | Pass | Partial | Fail | Mean /10 | O /3 | S /3 | J /2 | M /2 | Critical |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        js = run.get("judge_summary")
        if not js:
            continue
        L.append(f"| {run['id']} | {run['kind']} | {run['set']} | {js['n']} | {js['pass']} | {js['partial']} | {js['fail']} | {js['mean_score']} | "
                 f"{js.get('mean_outcome')} | {js.get('mean_safety')} | {js.get('mean_judgement')} | {js.get('mean_message_quality')} | {js['critical']} |")
    L += ["", "## Deterministic scorer (proxy plans against gold labels)", "",
          "| Run | n | Pass | Partial | Fail | Routing | Action | Channel (strict) | Violation cases |", "|---|---|---|---|---|---|---|---|---|"]
    for run in runs:
        sc = run.get("scorer_summary")
        if not sc:
            continue
        L.append(f"| {run['id']} | {sc['n_cases']} | {sc['pass']} | {sc['partial']} | {sc['fail']} | {sc['routing_mean']} | {sc['action_mean']} | "
                 f"{sc['channel_mean']} | {sc['violation_cases']} |")
    for run_id, b in breakdowns.items():
        if "complexity_level" not in b:
            continue
        L += ["", f"## {run_id} by complexity level", "", "| Level | Name | n | Judge pass | Judge mean | Scorer pass | Routing |", "|---|---|---|---|---|---|---|"]
        for lvl, d in sorted(b["complexity_level"].items(), key=lambda kv: int(kv[0])):
            L.append(f"| {lvl} | {LEVEL_NAMES.get(int(lvl), '')} | {d['n']} | {d.get('judge_pass', '')} | {d.get('judge_mean_score', '')} | "
                     f"{d.get('scorer_pass', '')} | {d.get('routing_mean', '')} |")
    for run_id, b in breakdowns.items():
        if "twist" in b and run_id.startswith("proxy/synthetic"):
            L += ["", f"## {run_id} by twist", "", "| Twist | n | Judge pass | Judge mean | Scorer pass | Routing |", "|---|---|---|---|---|---|"]
            for tw, d in b["twist"].items():
                L.append(f"| {tw} | {d['n']} | {d.get('judge_pass', '')} | {d.get('judge_mean_score', '')} | {d.get('scorer_pass', '')} | {d.get('routing_mean', '')} |")
    L += ["", "## Files", "", "- `summary.json`: everything above plus per-case rows (`cases`) and all breakdowns (`breakdowns`).",
          "- `<set>-proxy/plans.jsonl`: the planner outputs; `<set>-proxy/judge/`: judge grades in eval.py layout; `<set>-proxy/scorer/`: deterministic scores.",
          "- Reproduce: `data/pipeline/proxy_eval_prepare.py` (prompts) → planner agents → `proxy_eval_collect.py` → `score_answers.py`; "
          "`proxy_eval_judge_prepare.py` → judge agents → `proxy_eval_grades.py`; then this script."]
    (bench / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"runs": [(r["id"], (r.get("judge_summary") or {}).get("n"), (r.get("judge_summary") or {}).get("pass")) for r in runs],
                      "cases": len(cases), "out": str(bench)}))


if __name__ == "__main__":
    main()
