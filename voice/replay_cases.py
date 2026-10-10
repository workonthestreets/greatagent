"""Replay the organisers' public Delivery cases through the voice line as if the recipient had phoned.

    uv run python -m voice.replay_cases --base http://localhost:8011 --mode tool [--ids 002 024 ...]

For each case whose escalation message comes from a recipient/customer, the escalation text is the
caller's `issue`, the From name is the caller, and the Primary shipment is the reference. `tool`
posts one CallReport to /voice/tool; `turn` runs live-assist: first the issue with no reference,
then the reference as a second turn. Each line of the JSONL output holds the case's recorded
"Next action at escalation" next to what the voice line said, so a reader can judge the routing.
Needs VOICE_TOOL_SECRET in the env and a running voice service (VOICE_ASSIST set for `turn`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scorer.cases import load_cases

ROOT = Path(__file__).resolve().parents[1] / "data" / "public-cases"
CALLER = re.compile(r"recipient|customer", re.IGNORECASE)
SHIPMENT = re.compile(r"\*\*Primary (?:shipment|task reference):\*\*\s*(\S+)")


def post(base: str, path: str, body: dict, secret: str) -> dict:
    req = urllib.request.Request(f"{base}{path}", method="POST", data=json.dumps(body).encode(),
                                 headers={"content-type": "application/json", "X-Tool-Secret": secret})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def caller_cases(ids: list[str] | None, root: Path = ROOT) -> list[tuple]:
    out = []
    for case in load_cases(root, ["delivery"], ids):
        esc = next((e for e in case.events if e.fields.get("Stage", "").lower() == "escalation"), None)
        if esc is None and not any("Stage" in e.fields for e in case.events):  # unstaged (stress) cases:
            esc = next((e for e in reversed(case.events) if CALLER.search(e.fields.get("From", ""))), None)
        if not esc or not CALLER.search(esc.fields.get("From", "")):
            continue
        name = esc.fields["From"].split(",")[0].strip()
        m = SHIPMENT.search(case.sections.get("Case details", ""))
        out.append((case, name, m.group(1) if m else "", esc.body))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8011")
    ap.add_argument("--mode", choices=["tool", "turn"], default="tool")
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--root", type=Path, default=ROOT, help="folder holding 'Delivery & Logistics/<NNN>/'")
    ap.add_argument("--workers", type=int, default=4)  # the service's decide pool is 4 wide
    a = ap.parse_args(argv)
    secret = os.environ["VOICE_TOOL_SECRET"]
    out = Path(a.out or f"runs/voice-replay-{a.mode}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time())

    def run(item: tuple) -> dict:
        case, name, ref, issue = item
        conv = f"replay-{a.mode}-{case.number}-{stamp}"
        t0 = time.time()
        try:
            if a.mode == "tool":
                replies = [post(a.base, "/voice/tool", {"conversation_id": conv, "caller_name": name, "order_ref": ref,
                                                         "issue": issue, "update_by": "text", "contact": "07700 900123"}, secret)]
            else:
                replies = [post(a.base, "/voice/turn", {"conversation_id": conv, "utterance": issue, "caller_name": name,
                                                         "update_by": "text", "contact": "07700 900123"}, secret)]
                if replies[-1].get("status") == "continue":
                    replies.append(post(a.base, "/voice/turn", {"conversation_id": conv, "order_ref": ref,
                                                                 "utterance": f"The reference is {ref}"}, secret))
        except OSError as e:  # keep the batch going; the row records what failed
            replies = [{"error": repr(e)}]
        title = (case.folder / "index.md").read_text().splitlines()[0].split(":", 1)[-1].strip()
        return {"case": case.case_id, "title": title, "ref": ref, "expected": case.label[:400], "issue": issue[:400],
                "replies": replies, "seconds": round(time.time() - t0, 1), "conversation_id": conv}

    with out.open("a") as fh, ThreadPoolExecutor(a.workers) as pool:
        for row in pool.map(run, caller_cases(a.ids, a.root)):
            fh.write(json.dumps(row) + "\n")
            fh.flush()
            last = row["replies"][-1]
            print(f"{row['case'][-3:]} [{row['seconds']:>5}s] {last.get('status') or last.get('error')} | {last.get('say', '')[:110]}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
