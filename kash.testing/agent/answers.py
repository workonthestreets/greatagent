"""Run the agent over a folder of cases and write the submission layout.

    uv run python -m agent.answers --cases <dir-with-NNN-folders> --out ANSWERS [--deadline 1200]

Each case folder (`index.md` + `history.md` + `attachments/`) becomes `ANSWERS/<n>/ANSWER.md`,
`REASONING.md` and `outbox.eml`, plus one line in `ANSWERS/results.jsonl`. A case that
crashes or runs past the deadline still gets an answer: an escalation saying why. Results are
written as they finish, and a rerun skips cases already in results.jsonl.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from agent.decide import NEVER, decide, escalation
from agent.outbox import deliver
from scorer.cases import AgentInput, attachment_text, load_case

HIDDEN = {"Next action at escalation", "Outcome", "Resolution"}  # labels, if a folder carries them


def case_input(folder: Path) -> AgentInput:
    case = load_case(folder)
    parts = [f"## {k}\n{v.strip()}" for k, v in case.sections.items() if k not in HIDDEN]
    for e in case.events:
        meta = " | ".join(f"{k}: {v}" for k, v in e.fields.items() if k != "Stage")
        parts.append(f"### {e.head}\n{meta}\n{e.body}\n{attachment_text(folder, e.body)}")
    return AgentInput(f"{case.track}-{case.number}", case.track, "\n\n".join(parts))


def answer_md(n: str, d: dict) -> str:
    who = ", ".join(x for x in (d.get("team"), d.get("org")) if x) or d.get("party", "")
    lines = [f"# Case {n}", "", f"**Decision:** {'Escalate to a human' if d.get('escalate') else d.get('action', '').capitalize()}",
             f"**Recipient:** {who} ({d.get('party', '')})", f"**Channel:** {d.get('channel', '')}", "",
             "## Message", "", d.get("message", "") or "(none)"]
    if d.get("question_for_human"):
        lines += ["", "## Question for a human", "", d["question_for_human"]]
    return "\n".join(lines) + "\n"


def reasoning_md(n: str, case: AgentInput, d: dict, mail: dict, seconds: float) -> str:
    received = case.text if len(case.text) < 6000 else case.text[:6000] + "\n…(truncated)"
    return "\n".join([
        f"# Reasoning — case {n}", "",
        "## What the system received", "", "```", received, "```", "",
        "## What it read (facts → decision)", "",
        f"- Need: `{d.get('need', 'n/a')}` — missing: {d.get('missing', 'n/a')}",
        f"- Code checks fired: {', '.join(d.get('flags', [])) or 'none'}",
        f"- Confidence: {d.get('confidence')}", f"- Escalated: {d.get('escalate', False)}", "",
        "## Actions taken", "",
        f"- Email written to `{mail.get('to')}` → `outbox.eml`; sent: {mail.get('sent')}"
        + (f" ({mail['error']})" if mail.get("error") else ""), "",
        "## Rules held", "", *[f"- {r}" for r in d.get("never", NEVER)], "",
        f"Run time: {seconds:.1f}s", ""])


def answer_one(folder: Path, out: Path) -> dict:
    n = str(int(folder.name)) if folder.name.isdigit() else folder.name
    t0 = time.time()
    case = None
    try:
        case = case_input(folder)
        d = decide(case)
    except Exception as e:  # noqa: BLE001 — one bad case must not sink the batch
        d = escalation(f"The system failed on this case ({type(e).__name__}). Please review it by hand "
                       f"and choose the next contact.", ["crashed"])
        case = case or AgentInput(n, "delivery", f"(could not read {folder.name})")
    dest = out / n
    mail = deliver(case.case_id, d, dest)
    dest.joinpath("ANSWER.md").write_text(answer_md(n, d))
    dest.joinpath("REASONING.md").write_text(reasoning_md(n, case, d, mail, time.time() - t0))
    return {"n": n, "case_id": case.case_id, "decision": d, "email": mail}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("ANSWERS"))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--deadline", type=int, default=1200, help="seconds before unfinished cases escalate")
    args = ap.parse_args(argv)
    folders = sorted(f for f in args.cases.iterdir() if f.is_dir() and (f / "history.md").exists())
    args.out.mkdir(parents=True, exist_ok=True)
    results = args.out / "results.jsonl"
    done = {json.loads(line)["n"] for line in results.read_text().splitlines()} if results.exists() else set()
    todo = [f for f in folders if (str(int(f.name)) if f.name.isdigit() else f.name) not in done]
    print(f"{len(folders)} cases, {len(done)} already answered, {len(todo)} to run", file=sys.stderr)
    lock, start = threading.Lock(), time.time()

    def record(row: dict) -> None:
        with lock, results.open("a") as f:
            f.write(json.dumps(row, default=str) + "\n")

    pool = ThreadPoolExecutor(args.workers)
    futures = {pool.submit(answer_one, f, args.out): f for f in todo}
    try:
        for fut in as_completed(futures, timeout=args.deadline):
            record(fut.result())
    except TimeoutError:  # answer whatever is left as an escalation, then stop waiting
        for fut, f in futures.items():
            if not fut.done():
                n = str(int(f.name)) if f.name.isdigit() else f.name
                d = escalation("Not processed before the deadline. Please review this case by hand.",
                               ["deadline"])
                dest = args.out / n
                dest.mkdir(parents=True, exist_ok=True)
                dest.joinpath("ANSWER.md").write_text(answer_md(n, d))
                dest.joinpath("REASONING.md").write_text(f"# Reasoning — case {n}\n\nDeadline reached "
                                                         f"after {time.time() - start:.0f}s; not processed.\n")
                record({"n": n, "case_id": f.name, "decision": d, "email": {}})
        print(f"deadline hit after {time.time() - start:.0f}s → {args.out}", file=sys.stderr)
        os._exit(0)  # worker threads would otherwise keep the process alive and overwrite answers
    pool.shutdown()
    print(f"done in {time.time() - start:.0f}s → {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
