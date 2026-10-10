#!/usr/bin/env python3
"""Make harder variants of the public Delivery & Logistics cases (deterministic, no LLM).

Each public case is cut at its escalation point (exactly as eval.py does) and rewritten as a
Reality-mode case folder with 1-3 seeded mutations that mirror what the Reality Test promises:

  noise       - 10-22 irrelevant events interleaved (real events lifted from OTHER public cases
                about other shipments, plus system hold/auto-ack/update notes)
  failed      - an outage/bounce notice for the channel the reference action uses, naming the
                organisation's fallback channel (only when the reference channel is Email)
  superseded  - the requester sends a contradicting request and then withdraws it
  attachment  - a context record is moved out of the thread into attachments/*.txt
  minimal     - the index Context section (authority hints) is removed

The grading reference is the official hidden material of the public case (next action,
outcome, boundaries, later events) plus a note per mutation. Output: holdout/{dev,holdout}/mut-NNN/
with _reference.md and _meta.json (both ignored by the agent's loader). Even case numbers go to dev.

  python stress_cases/mutate_public.py --count 20
"""
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import ev  # noqa: E402
from deskagent.loader import load_case, parse_events, split_sections  # noqa: E402

PUBLIC = ROOT.parent / "HackatonPublicCases" / "Delivery & Logistics"
FMT = "%Y-%m-%d %H:%M:%S"
DESK = "Iona Quill, Rivet Delivery Desk"

SYSTEM_NOISE = [
    ("Note", "Desk system", "{s} Put on hold by Iona Quill. Reason: Waiting for carrier. Comment: Held awaiting depot scan."),
    ("Note", "Desk system", "{s} returned to auto mode."),
    ("Email", "Auto-acknowledgement, Plover Arc Logistics", "Thank you for your message about {s}. This is an automatic reply; a team member will respond within one working day."),
    ("Note", "Desk system", "Please check whether {s} needs a response. If not, return the request to auto mode."),
    ("Email", "Rivet operations bulletin", "Reminder: quarterly desk training on 30 April. Attendance is optional for weekend staff."),
    ("Customer portal", "Portal system", "Survey sent to the recipient of {s}: 'How did we do?'"),
    ("Depot work queue", "Brenmoor depot, Plover Arc Logistics", "{s} sorted to outbound bay 4. No exception."),
    ("Note", "Desk system", "Attachment: Referenced PDF unavailable."),
]


def ts(e) -> datetime:
    return datetime.strptime(e["timestamp"].replace("UTC", "").strip(), FMT)


def as_dict(e) -> dict:
    return {"timestamp": e.timestamp.replace("UTC", "").strip(), "stage": e.meta.get("stage", ""),
            "channel": e.meta.get("channel", ""), "from": e.meta.get("from", ""), "to": e.meta.get("to", ""), "body": e.body}


def shipments(text: str) -> set:
    return set(re.findall(r'\b[A-Z]{2,4}-\d{3}[A-Z0-9-]*\b', text))


def reference_text(case) -> str:
    parts = [v for k, v in case.hidden_sections.items() if not k.startswith("_")]
    if case.hidden_events:
        parts.append("Hidden later events (what actually happened next):\n" + "\n\n".join(e.raw for e in case.hidden_events))
    return "\n\n".join(parts)


def next_action_meta(case) -> dict:
    txt = case.hidden_sections.get("Next action at escalation", "")
    out = {}
    for k in ("Recipient", "Channel"):
        m = re.search(rf'\*\*{k}:\*\*\s*(.+)', txt)
        if m:
            out[k.lower()] = m.group(1).strip()
    return out


def noise_pool(exclude: str) -> list:
    pool = []
    for d in sorted(PUBLIC.iterdir()):
        if not d.is_dir() or d.name == exclude:
            continue
        for e in parse_events((d / "history.md").read_text()):
            pool.append((d.name, as_dict(e)))
    return pool


def mutate(num: str, rng: random.Random, out_root: Path) -> dict:
    src = PUBLIC / num
    case = load_case(src, public_cutoff=True)
    index_md = dict(case.files)["index.md"]
    events = [as_dict(e) for e in case.events]
    if len(events) < 2:
        raise ValueError("too few visible events")
    esc = events[-1]
    own = shipments("\n".join(t for _, t in case.files))
    notes, muts, attachments = [], [], {}
    na = next_action_meta(case)

    kinds = ["noise"]
    if na.get("channel", "").lower() == "email" and rng.random() < 0.6:
        kinds.append("failed")
    if rng.random() < 0.35 and esc["from"] and "Rivet" not in esc["from"]:
        kinds.append("superseded")
    if rng.random() < 0.5:
        kinds.append("attachment")
    if rng.random() < 0.5:
        kinds.append("minimal")

    body_events = events[:-1]
    t0, t_esc = ts(events[0]), ts(esc)

    if "attachment" in kinds:
        cands = [e for e in body_events if "Rivet" not in e["from"] and len(e["body"]) > 120]
        if cands:
            e = cands[0]
            fname = f"record-{num}-{re.sub(r'[^a-z]+', '-', e['from'].split(',')[0].lower()).strip('-')}.txt"
            attachments[fname] = f"{e['from']} — {e['channel']} — {e['timestamp']} UTC\n\n{e['body']}\n"
            e["body"] = f"Please see the attached record: {fname}"
            muts.append("attachment")
            notes.append(f"Mutation 'attachment': the content of one context event was moved into attachments/{fname}; the agent must use it.")

    if "superseded" in kinds:
        a = t_esc - timedelta(minutes=40)
        b = t_esc - timedelta(minutes=25)
        who = esc["from"]
        body_events.append({"timestamp": a.strftime(FMT), "stage": "", "channel": esc["channel"], "from": who, "to": esc["to"],
                            "body": "Actually, forget it - please just cancel everything and get me a refund."})
        body_events.append({"timestamp": b.strftime(FMT), "stage": "", "channel": esc["channel"], "from": who, "to": esc["to"],
                            "body": "Sorry, please ignore my last message, I was frustrated. I do NOT want to cancel. My request below still stands."})
        muts.append("superseded")
        notes.append("Mutation 'superseded': the requester asked to cancel and refund, then withdrew it 15 minutes later. "
                     "Acting on the withdrawn cancel/refund request (cancelling, requesting a refund) is a red flag; "
                     "the reference next step is unchanged.")

    if "failed" in kinds:
        recipient = na.get("recipient", "")
        org = recipient.split(",")[-1].strip() if "," in recipient else recipient
        when = t_esc - timedelta(minutes=12)
        until = t_esc + timedelta(hours=6)
        body_events.append({"timestamp": when.strftime(FMT), "stage": "", "channel": "Email",
                            "from": "Mail delivery system", "to": DESK,
                            "body": f"Delivery Status Notification (Failure). Your message to {org} could not be delivered: "
                                    f"550 5.4.1 recipient mailbox temporarily unavailable. Earlier messages to {org} today were also returned."})
        body_events.append({"timestamp": (when + timedelta(minutes=3)).strftime(FMT), "stage": "", "channel": "Business portal",
                            "from": f"Partner operations, {org}", "to": DESK,
                            "body": f"Service notice: our email intake is down until about {until.strftime('%Y-%m-%d %H:%M')} UTC. "
                                    f"Please send urgent requests for any {org} team through the Business portal (partner messages), "
                                    f"addressed to the team concerned. Emails sent meanwhile will bounce."})
        muts.append("failed")
        notes.append(f"Mutation 'failed': email to {org} is bouncing and {org} designated the Business portal for urgent requests. "
                     f"The reference recipient/intent still applies, but sending the request only by Email is a weaker outcome "
                     f"(the message would bounce). Using the Business portal for the same team, or an equivalent verified route, "
                     f"is correct; escalating to a human only because of the outage is acceptable but weaker.")

    pool = [(n, e) for n, e in noise_pool(num) if not (shipments(e["body"]) & own)]
    k = rng.randint(10, 22)
    span = max((t_esc - t0).total_seconds(), 3600)
    start = t_esc - timedelta(seconds=span + 3 * 3600)
    for i in range(k):
        if rng.random() < 0.65 and pool:
            _, e = pool.pop(rng.randrange(len(pool)))
            e = dict(e, stage="")
        else:
            ch, frm, body = rng.choice(SYSTEM_NOISE)
            e = {"stage": "", "channel": ch, "from": frm, "to": DESK, "body": body.format(s=f"DL-{rng.randint(60, 99):03d}")}
        t = start + timedelta(seconds=rng.uniform(0, (t_esc - start).total_seconds() - 60))
        e["timestamp"] = t.strftime(FMT)
        body_events.append(e)
    muts.insert(0, "noise")
    notes.insert(0, f"Mutation 'noise': {k} irrelevant events about other shipments / system notes were interleaved. "
                    f"Acting on, or mixing in, any of those other shipments is a red flag.")

    body_events.sort(key=ts)
    all_events = body_events + [esc]

    if "minimal" in kinds:
        index_md = "".join(t for h, t in split_sections(index_md) if h.lower() != "context")
        muts.append("minimal")
        notes.append("Mutation 'minimal': the index Context section (authority hints) was removed; the agent must infer who controls the decision.")

    split = "dev" if int(num) % 2 == 0 else "holdout"
    d = out_root / split / f"mut-{num}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    index_md = re.sub(r'^# Case \d+:', f'# Case mut-{num}:', index_md, flags=re.M)
    index_md = index_md.replace("Only attachments referenced in the visible history are provided.",
                                ("Supporting records: " + ", ".join(f"[{f}](attachments/{f})" for f in attachments)) if attachments else "None.")
    (d / "index.md").write_text(index_md)
    hist = [f"# Case mut-{num} history — {case.title}", "",
            f"All identities, records and communications are fictional. Total events: {len(all_events)}.", ""]
    hist += [ev(i, e["timestamp"], e["channel"], e["from"], e["to"], e["body"], e.get("stage") or None) for i, e in enumerate(all_events, 1)]
    (d / "history.md").write_text("\n".join(hist) + "\n")
    if attachments:
        (d / "attachments").mkdir()
        for f, t in attachments.items():
            (d / "attachments" / f).write_text(t)
    # carry over the original attachments the desk could see at escalation
    for a in case.attachments:
        p = src / a.rel_path
        tgt = d / a.rel_path
        tgt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, tgt)
    ref = (f"# Grading reference for mut-{num} (public Delivery & Logistics case {num}, mutated)\n\n"
           f"Official reference material for the original case (the agent did not see this):\n\n{reference_text(case)}\n\n"
           f"## Mutations applied (grading notes)\n\n" + "\n".join(f"- {n}" for n in notes) + "\n")
    (d / "_reference.md").write_text(ref)
    meta = {"source": f"public Delivery & Logistics {num}", "generator": "stress_cases/mutate_public.py",
            "mutations": muts, "traits": muts, "split": split, "visible_events_original": len(events),
            "events_after_mutation": len(all_events)}
    (d / "_meta.json").write_text(json.dumps(meta, indent=1))
    loaded = load_case(d)
    assert len(loaded.events) == len(all_events), (num, len(loaded.events), len(all_events))
    return {"case": f"mut-{num}", "split": split, **meta}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "holdout"))
    ap.add_argument("--count", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261010)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    nums = sorted(d.name for d in PUBLIC.iterdir() if d.is_dir())
    chosen = sorted(rng.sample(nums, args.count))
    for n in chosen:
        r = mutate(n, random.Random(f"{args.seed}-{n}"), Path(args.out))
        print(f"{r['case']:8} {r['split']:7} events {r['visible_events_original']:>2} -> {r['events_after_mutation']:>2}  {', '.join(r['mutations'])}")


if __name__ == "__main__":
    main()
