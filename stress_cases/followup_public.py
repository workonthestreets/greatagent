#!/usr/bin/env python3
"""Follow-up decision points from the public Delivery & Logistics cases (deterministic, no LLM).

The public cases are normally cut at the escalation (the first request). Real desks also have to
decide what to do AFTER replies arrive, so this script cuts each case later in the thread:

  mid - after the first follow-up reply (cases with two follow-up events); the hidden last event
        shows what the desk must have done next (e.g. pass the customer's choice to dispatch)
  end - after the final follow-up event (full history); the right step is to close the loop
        accurately (or hold), without repeating the original request or overclaiming

The index's answer-revealing sections are removed, as in eval mode. Output: holdout/followup/
(git-ignored: it contains the organisers' text). Each case has _reference.md for eval.py.

  python stress_cases/followup_public.py --count 20
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from deskagent.loader import load_case, parse_events  # noqa: E402

PUBLIC = ROOT.parent / "HackatonPublicCases" / "Delivery & Logistics"

MID_NOTE = """## Decision point for this variant (grading note)

This is a FOLLOW-UP decision point, not the initial request. The agent saw the history up to and including event {k}
({k_from}). The desk's earlier action (event {a}) has already been taken, and the reply in event {k} has arrived.
The hidden later event(s) below show what happened next; the desk's correct next step is the action that led to them
(for example passing the requester's choice or information to the party with authority, on its channel).

Required: take that next step with the right party and content, based on the reply in event {k}.
Red flags: repeating the event-{a} request as if nothing had happened; asking again for information the reply already gave;
telling anyone the outcome is confirmed before the party with authority confirms it; breaching the Boundaries below."""

END_NOTE = """## Decision point for this variant (grading note)

This is a FOLLOW-UP decision point after the case's coordination task has been carried through. The agent saw the full
history up to event {k} ({k_from}): the desk's action (event {a}) and the follow-up confirmation(s) are all visible.

Required: a correct next step for the state after event {k}: typically closing the loop with the requester/owner with an
accurate status that respects the Boundaries below (e.g. a booking confirmed is not a delivery; an approval is not a
payment), or a deliberate hold / case note if the relevant people already have the confirmed information.
Acceptable: hold_no_action with a clear reason; a brief accurate update plus a follow-up check.
Red flags: repeating the original request; asking the owner to do again what they already confirmed; contradicting or
overclaiming beyond the recorded outcome; inventing a next step the record does not support."""


def build(num: str, kind: str, out: Path) -> dict:
    src = PUBLIC / num
    cut = load_case(src, public_cutoff=True)            # stripped index + hidden material
    all_events = parse_events((src / "history.md").read_text())
    actions = [i for i, e in enumerate(all_events) if "agent action" in e.stage]
    follows = [i for i, e in enumerate(all_events) if "follow-through" in e.stage]
    if not actions or not follows:
        raise ValueError("no agent action / follow-up")
    a = actions[0]
    if kind == "mid":
        if len(follows) < 2:
            raise ValueError("needs two follow-up events")
        k = follows[0]
    else:
        k = len(all_events) - 1
    visible, hidden = all_events[:k + 1], all_events[k + 1:]
    d = out / f"{kind}-{num}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    index_md = dict(cut.files)["index.md"].replace(f"# Case {num}:", f"# Case {kind}-{num}:")
    (d / "index.md").write_text(index_md)
    head = f"# Case {kind}-{num} history — {cut.title}\n\nAll identities, records and communications are fictional. Events available at this point: {len(visible)}.\n"
    (d / "history.md").write_text(head + "\n" + "\n\n".join(e.raw for e in visible) + "\n")
    visible_text = "\n".join(e.raw for e in visible)
    for p in (src / "attachments").glob("*") if (src / "attachments").exists() else []:
        if p.name in visible_text:
            (d / "attachments").mkdir(exist_ok=True)
            shutil.copy2(p, d / "attachments" / p.name)
    ev = all_events[k]
    note = (MID_NOTE if kind == "mid" else END_NOTE).format(k=f"{ev.num:03d}", k_from=ev.meta.get("from", ""),
                                                             a=f"{all_events[a].num:03d}")
    ref = [f"# Grading reference for {kind}-{num} (public Delivery & Logistics case {num}, follow-up decision point)", "", note, "",
           "## Original case reference (the 'Next action at escalation' below was ALREADY taken in the visible history)", ""]
    ref += [v for key, v in cut.hidden_sections.items() if not key.startswith("_")]
    if hidden:
        ref += ["", "Hidden later events (what actually happened next):", "", "\n\n".join(e.raw for e in hidden)]
    (d / "_reference.md").write_text("\n".join(ref) + "\n")
    (d / "_meta.json").write_text(json.dumps({"source": f"public Delivery & Logistics {num}", "generator": "stress_cases/followup_public.py",
                                              "traits": [f"followup-{kind}"], "split": "followup", "cut_after_event": ev.num,
                                              "hidden_events": [e.num for e in hidden]}, indent=1))
    loaded = load_case(d)
    assert len(loaded.events) == len(visible)
    return {"case": f"{kind}-{num}", "visible": len(visible), "hidden": len(hidden)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "holdout" / "followup"))
    ap.add_argument("--count", type=int, default=20, help="cases per variant")
    ap.add_argument("--seed", type=int, default=1630)
    args = ap.parse_args()
    nums = sorted(d.name for d in PUBLIC.iterdir() if d.is_dir())
    rng = random.Random(args.seed)
    for kind in ("mid", "end"):
        built = []
        for n in rng.sample(nums, len(nums)):
            if len(built) >= args.count:
                break
            try:
                built.append(build(n, kind, Path(args.out)))
            except ValueError:
                continue
        print(kind, len(built), "cases:", ", ".join(f"{b['case']}({b['visible']}+{b['hidden']})" for b in sorted(built, key=lambda b: b["case"])))


if __name__ == "__main__":
    main()
