"""Read a Dwelly case folder and cut it at the decision point.

A case is `<Track>/<NNN>/index.md` + `history.md` + optional `attachments/`. The ending
(Overview, Outcome, Next action, ...) is hidden from the agent and kept as the label.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

TRACKS = {
    "Banking & Financial Services": "banking",
    "Delivery & Logistics": "delivery",
    "Insurance Claims Processing": "insurance",
    "Property Management": "property",
}
VISIBLE_SECTIONS = {"Case details", "Initial request"}  # everything else in index.md leaks the ending
HIDDEN_DETAILS = re.compile(r"^- \*\*(Status|Updated|Completed):\*\*.*$\n?", re.MULTILINE)  # say it resolved


@dataclass
class Event:
    head: str
    fields: dict[str, str]
    body: str

    @property
    def channel(self) -> str:
        return self.fields.get("Channel", "")


@dataclass
class Case:
    track: str
    number: str
    folder: Path
    sections: dict[str, str]
    events: list[Event]

    @property
    def case_id(self) -> str:
        return f"{self.track}-{self.number}"

    @property
    def label(self) -> str:
        return self.sections.get("Next action at escalation", "").strip()


@dataclass(frozen=True)
class AgentInput:
    """Everything the agent may see. Nothing here hints at the ending or where the cut fell."""
    case_id: str
    track: str
    text: str


@dataclass
class Snapshot:
    """The scorer's view: the agent's input plus the hidden answer. Never pass this to an agent."""
    agent_input: AgentInput
    events_kept: int
    events_total: int
    expected: str = field(repr=False)


def _sections(md: str) -> dict[str, str]:
    out: dict[str, str] = {}
    cur = None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = ""
        elif cur:
            out[cur] += line + "\n"
    return out


def _events(md: str) -> list[Event]:
    evs = []
    for block in re.split(r'<a id="event-\d+"></a>', md)[1:]:
        fields = dict(re.findall(r"^- \*\*([^*]+):\*\* (.*)$", block, re.MULTILINE))
        head = re.search(r"^## (.*)$", block, re.MULTILINE)
        body = re.sub(r"^- \*\*[^*]+:\*\* .*$|^## .*$", "", block, flags=re.MULTILINE).strip()
        evs.append(Event(head.group(1) if head else "", fields, body))
    return evs


def load_case(folder: Path) -> Case:
    track = TRACKS.get(folder.parent.name, folder.parent.name.lower())
    return Case(track, folder.name, folder, _sections((folder / "index.md").read_text()),
                _events((folder / "history.md").read_text()))


def case_folders(root: Path, tracks: list[str], ids: list[str] | None) -> list[Path]:
    folders = []
    for track_dir, track in TRACKS.items():
        if track not in tracks or not (root / track_dir).is_dir():
            continue
        folders += [f for f in sorted((root / track_dir).iterdir())
                    if f.is_dir() and (ids is None or f.name in ids)]
    return folders


def load_cases(root: Path, tracks: list[str], ids: list[str] | None) -> list[Case]:
    return [load_case(f) for f in case_folders(root, tracks, ids)]


# --- decision points -------------------------------------------------------------------

Picker = Callable[[str, list[tuple[int, Event]]], int]  # (label, broker events) -> event index


def decision_point(case: Case, pick: Picker | None = None) -> tuple[int, str] | None:
    """(events to keep, expected answer), or None when the case has no usable decision point."""
    evs, label = case.events, case.label
    if case.track == "delivery":  # marked: Stage = Context/Escalation comes before the agent acts
        n = next((i for i, e in enumerate(evs)
                  if e.fields.get("Stage", "").lower() not in ("context", "escalation")), len(evs))
        return (n, label) if label else None
    if case.track == "banking":  # the first internal note is the agent's own action
        n = next((i for i, e in enumerate(evs) if "internal note" in e.channel.lower()), None)
        return (n, label) if n and label else None
    if case.track == "insurance":
        # Unmarked and it moves (case 045 acts at event 5). The label says what the broker does,
        # so pick the broker message that carries it out and cut before it. snapshot() drops the
        # broker's planning notes, which state the answer.
        m = re.search(r"\*\*Broker:\*\* (.*)", case.sections.get("Case details", ""))
        broker = m.group(1).strip() if m else ""
        outgoing = [(i, e) for i, e in enumerate(evs)
                    if i > 0 and broker and broker in e.fields.get("From", "") and e.channel != "Note"]
        if not outgoing or not label:
            return None
        n = pick(label, outgoing) if pick else outgoing[0][0]
        if n not in [i for i, _ in outgoing]:
            n = outgoing[0][0]
        return n, label
    # property: no label section. Cut after the first system Update handing off to a human;
    # the answer is the next human event. Crude: it lands early in long cases.
    for i, e in enumerate(evs):
        if e.channel == "Update" and "please" in e.body.lower():
            nxt = next((x for x in evs[i + 1:] if x.channel != "Update"), None)
            if not nxt:
                return i + 1, "No further human action; only system updates follow."
            f = nxt.fields
            return i + 1, f"{f.get('Channel')} from {f.get('From')} to {f.get('To')}: {nxt.body[:600]}"
    return None


# --- what the agent sees ---------------------------------------------------------------

def attachment_text(folder: Path, body: str) -> str:
    out = []
    for rel in re.findall(r"\]\((attachments/[^)]+)\)", body):
        p = folder / rel
        if not p.is_file():
            continue
        suffix = p.suffix.lower()
        if suffix in (".txt", ".csv", ".md"):
            out.append(f"[attachment {p.name}]\n{p.read_text(errors='replace')[:3000]}")
        elif suffix == ".pdf" and shutil.which("pdftotext"):
            try:
                txt = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True,
                                     timeout=30, check=False).stdout
            except subprocess.TimeoutExpired:
                txt = "(pdftotext timed out)"
            out.append(f"[attachment {p.name}]\n{txt[:3000]}")
        else:
            out.append(f"[attachment {p.name}: not read (image or no pdftotext)]")
    return "\n".join(out)


def snapshot(case: Case, pick: Picker | None = None) -> Snapshot | None:
    cut = decision_point(case, pick)
    if not cut:
        return None
    n, expected = cut
    parts = [f"## {k}\n{HIDDEN_DETAILS.sub('', v).strip()}"
             for k, v in case.sections.items() if k in VISIBLE_SECTIONS]
    for e in case.events[:n]:
        if case.track == "insurance" and e.channel == "Note":
            continue
        meta = " | ".join(f"{k}: {v}" for k, v in e.fields.items() if k != "Stage")
        parts.append(f"### {e.head}\n{meta}\n{e.body}\n{attachment_text(case.folder, e.body)}")
    return Snapshot(AgentInput(case.case_id, case.track, "\n\n".join(parts)), n, len(case.events), expected)
