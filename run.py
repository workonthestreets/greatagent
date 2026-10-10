#!/usr/bin/env python3
"""Run the desk agent on one case folder or a folder of cases and write ANSWERS/.

  python run.py path/to/cases --out ANSWERS              # Reality Test (all input visible)
  python run.py "Delivery & Logistics" --public-cutoff   # dev: hide events after escalation
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import re
import threading

from deskagent.llm import FatalAPIError, load_dotenv
from deskagent.loader import discover_cases, load_case

STOP = threading.Event()   # set on a fatal API error (no credit / bad key): remaining cases are skipped, not failed
MEDIA_ERRORS = ("image", "document", "pdf", "media", "too large", "413", "request_too_large", "base64")
from deskagent.pipeline import process_case
from deskagent.report import write_case, write_failure


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def code_fingerprint() -> str:
    """sha256 over the agent's source, so results can be tied to the frozen code even
    when the run happens outside a git checkout."""
    import hashlib
    root = Path(__file__).parent
    h = hashlib.sha256()
    for p in sorted([root / "run.py"] + list((root / "deskagent").glob("*.py"))):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def default_answer_id(path: Path) -> str:
    name = path.stem if path.is_file() else path.name
    return str(int(name)) if name.isdigit() else name


def answer_names(cases: list) -> dict:
    """Answer folder per case. Normally ANSWERS/<case number>; only if two discovered cases would
    share a folder (e.g. the same number in two track folders) are those prefixed with their track."""
    ids = [default_answer_id(c) for c in cases]
    dup = {i for i in ids if ids.count(i) > 1}
    out = {}
    for c, i in zip(cases, ids):
        if i in dup:
            track = re.sub(r"[^a-z0-9]+", "-", c.parent.name.lower()).strip("-") or "case"
            out[c] = f"{track}-{i}"
        else:
            out[c] = i
    return out


def run_one(path: Path, out: Path, args, answer_name: str = "") -> dict:
    t0 = time.time()
    case = None
    trace: list = []
    media = True
    if STOP.is_set():
        return {"case": path.name, "ok": False, "skipped": True, "error": "skipped: Anthropic API unavailable (see earlier error)",
                "elapsed_s": 0}
    for attempt in (1, 2, 3):
        trace = []
        try:
            case = load_case(path, public_cutoff=args.public_cutoff, media=media)
            if answer_name and answer_name != case.answer_id:
                case.answer_name = answer_name
            res = process_case(case, model=args.model, review=not args.no_review, trace=trace)
            d = write_case(out, res)
            p = res["plan"]
            return {"case": path.name, "answer_dir": str(d), "ok": True, "decision": p.get("decision_type"),
                    "approved": res["approved"], "summary": p.get("decision_summary"), "status": res["final_status"],
                    "elapsed_s": res["elapsed_s"], "attempt": attempt,
                    "failed_actions": sum(1 for e in res["executed"] if e["status"] == "failed")}
        except FatalAPIError as exc:
            first = not STOP.is_set()
            STOP.set()
            if first:
                print(f"\n!!! FATAL: {exc}\n!!! Stopping: remaining cases are skipped. Fix the API key/credit, then re-run with --resume.\n",
                      file=sys.stderr, flush=True)
            return {"case": path.name, "ok": False, "skipped": True, "error": f"FatalAPIError: {exc}", "elapsed_s": round(time.time() - t0, 1)}
        except Exception as exc:  # noqa: BLE001
            err = f"{type(exc).__name__}: {exc}"
            trace.append({"type": "error", "attempt": attempt, "error": err, "traceback": traceback.format_exc()})
            print(f"  ! case {path.name} attempt {attempt} failed: {err}", file=sys.stderr, flush=True)
            has_media = case is not None and any(a.kind in ("image", "pdf") and a.data_b64 for a in case.attachments)
            # Degrade instead of failing: retry without images / scanned PDFs if they may be the cause (or on the last try).
            if media and has_media and (any(m in err.lower() for m in MEDIA_ERRORS) or attempt == 2):
                media = False
            elif attempt == 2 and not has_media:
                attempt = 3
            if attempt == 3:
                cid = case.case_id if case else path.stem
                aid = case.answer_id if case else (answer_name or default_answer_id(path))
                d = write_failure(out, cid, aid, case.title if case else path.name, err, trace)
                return {"case": path.name, "answer_dir": str(d), "ok": False, "error": err,
                        "elapsed_s": round(time.time() - t0, 1)}
            time.sleep(3)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases", help="a case folder, or a folder containing case folders")
    ap.add_argument("--out", default="ANSWERS", help="output folder (default ANSWERS)")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("DESK_WORKERS", "6")))
    ap.add_argument("--model", default=os.environ.get("DESK_MODEL"), help="primary Claude model (falls back automatically)")
    ap.add_argument("--no-review", action="store_true", help="skip the independent reviewer (faster, less safe)")
    ap.add_argument("--public-cutoff", action="store_true", help="dev mode: hide events after the escalation point")
    ap.add_argument("--only", default="", help="comma-separated case folder names to run")
    ap.add_argument("--resume", action="store_true", help="skip cases that already have a successful result in --out")
    args = ap.parse_args()

    load_dotenv()
    cases = discover_cases(args.cases)
    if args.only:
        keep = {s.strip().lstrip("0") for s in args.only.split(",")}
        cases = [c for c in cases if (c.stem if c.is_file() else c.name).lstrip("0") in keep]
    if not cases:
        sys.exit(f"No cases found under {args.cases}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = answer_names(cases)
    collided = [f"{c.parent.name}/{c.name} -> {names[c]}" for c in cases if names[c] != default_answer_id(c)]
    if collided:
        print(f"WARNING: {len(collided)} case(s) share a case number with another discovered case; their answer folders are "
              f"prefixed with the track: {', '.join(collided)}", flush=True)
    if args.resume:
        def _done(c: Path) -> bool:
            return (out / names[c] / "result.json").exists()
        skipped = [c.name for c in cases if _done(c)]
        cases = [c for c in cases if not _done(c)]
        if skipped:
            print(f"--resume: skipping {len(skipped)} case(s) already answered: {', '.join(skipped)}")
        if not cases:
            print("Nothing left to run.")
    started = datetime.now(timezone.utc).isoformat()
    print(f"Running {len(cases)} case(s) with {args.workers} workers -> {out}/", flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(run_one, c, out, args, names[c]): c for c in cases}
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            mark = "ok " if r["ok"] else ("SKIP" if r.get("skipped") else "ERR")
            print(f"[{len(results)}/{len(cases)}] {mark} {r['case']}: {r.get('decision', '')} {r.get('summary') or r.get('error', '')}"[:220], flush=True)

    batch = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(), "git_commit": git_commit(),
             "code_sha256": code_fingerprint(), "cases_path": str(args.cases),
             "model_preference": args.model or os.environ.get("DESK_MODELS") or "default", "review": not args.no_review,
             "public_cutoff": args.public_cutoff, "sim_fail_rate": os.environ.get("DESK_SIM_FAIL_RATE", "0"),
             "cases": [r["case"] for r in results]}
    # Merge with earlier batches written to the same --out folder (batched or resumed runs).
    batches, merged = [], {}
    prev_path = out / "run_manifest.json"
    if prev_path.exists():
        try:
            prev = json.loads(prev_path.read_text())
            batches = prev.get("batches") or []
            merged = {r["case"]: r for r in prev.get("results") or []}
        except Exception:  # noqa: BLE001
            pass
    batches.append(batch)
    merged.update({r["case"]: r for r in results if not r.get("skipped")})
    results = sorted(merged.values(), key=lambda r: (0, int(r["case"])) if r["case"].isdigit() else (1, r["case"]))
    manifest = {**batch, "started_utc": batches[0]["started_utc"], "batches": batches, "results": results}
    manifest.pop("cases", None)
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    lines = ["# Run summary", "", f"Commit `{manifest['git_commit']}` · code sha256 `{manifest['code_sha256'][:16]}` · started {started} · {len(results)} cases", "",
             "| Case | Decision | Reviewer-approved | Status |", "|---|---|---|---|"]
    for r in results:
        if r["ok"]:
            lines.append(f"| [{r['case']}]({Path(r['answer_dir']).name}/ANSWER.md) | {r['decision']} | {'yes' if r['approved'] else 'no → human'} | {str(r['status']).replace('|', '/')[:160]} |")
        elif r.get("answer_dir"):
            lines.append(f"| [{r['case']}]({Path(r['answer_dir']).name}/ANSWER.md) | SYSTEM FAILURE | - | {r['error'][:120]} |")
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ok = sum(r["ok"] for r in results)
    print(f"Done: {ok}/{len(results)} cases produced a decision. Summary: {out / 'SUMMARY.md'}")
    if STOP.is_set():
        sys.exit("Stopped early: the Anthropic API is unavailable (credit/key). Fix it and re-run the same command with --resume.")


if __name__ == "__main__":
    main()
