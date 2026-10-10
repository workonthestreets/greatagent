"""Shipment lookup for the voice line: find what the desk already knows about a caller's parcel.

The desk's records here are case folders in the organisers' format (`index.md` + `history.md`),
indexed once by every reference in their Case details. A real deployment would query the
shipment database instead; the interface stays `find_shipment(ref)` + `known_context(folder)`.

Only what was known before the desk had to act is ever returned: Case details (minus status and
completion lines) and the events staged Context or Escalation. Later events, labels and the
attachments only those later events link to are never read out of the folder.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DATA = Path(os.getenv("VOICE_SHIPMENT_DATA", "data/public-cases/Delivery & Logistics"))
_REF = re.compile(r"\b[A-Z]{2,4}-?\d{2,}[A-Z0-9-]*\b")
_EVENT = re.compile(r'(?=^<a id="event-\d+"></a>\s*$)', re.MULTILINE)
_STAGE = re.compile(r"^- \*\*Stage:\*\*\s*(.+)$", re.MULTILINE)
_LATER_DETAIL = re.compile(r"^- \*\*(Status|Updated|Completed|Resolved|Closed):\*\*.*$\n?", re.MULTILINE)
_ATTACHMENT = re.compile(r"\]\((attachments/[^)]+)\)")
KNOWN_STAGES = ("context", "escalation")


def norm(ref: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", ref.upper())


def _section(md: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", md, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


_PRIMARY = re.compile(r"\*\*Primary (?:shipment|task reference):\*\*\s*(\S+)")


def _known_events(history: str) -> list[str]:
    """Events staged Context or Escalation, stopping at the first later or unstaged event."""
    events = []
    for block in _EVENT.split(history)[1:]:
        stage = _STAGE.search(block)
        if not stage or stage.group(1).strip().lower() not in KNOWN_STAGES:
            break
        events.append(block.strip())
    return events


@lru_cache(maxsize=1)
def _index(root: str) -> dict[str, Path | None]:
    """Normalised reference -> case folder, or None when a reference points at two cases (no guessing).

    A case's own Primary shipment / task reference beats a reference merely mentioned in its Case
    details or its pre-escalation events.
    """
    primary: dict[str, set[Path]] = {}
    other: dict[str, set[Path]] = {}
    for idx in sorted(Path(root).glob("*/index.md")):
        folder = idx.parent
        details = _section(idx.read_text(errors="replace"), "Case details")
        m = _PRIMARY.search(details)
        if m:
            primary.setdefault(norm(m.group(1)), set()).add(folder)
        history = folder.joinpath("history.md").read_text(errors="replace") if (folder / "history.md").exists() else ""
        for ref in _REF.findall(details + "\n" + "\n".join(_known_events(history))):
            other.setdefault(norm(ref), set()).add(folder)
    resolved: dict[str, Path | None] = {}
    for ref, folders in other.items():
        resolved[ref] = next(iter(folders)) if len(folders) == 1 else None
    for ref, folders in primary.items():
        resolved[ref] = next(iter(folders)) if len(folders) == 1 else None
    return resolved


def find_shipment(ref: str, root: Path | None = None) -> Path | None:
    return _index(str(root or DATA)).get(norm(ref)) if ref.strip() else None


@dataclass
class KnownContext:
    source_case: str
    primary: str
    details: str
    initial_request: str
    events: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)


def known_context(folder: Path) -> KnownContext:
    """The case as the desk saw it at the moment of escalation, never after."""
    index = folder.joinpath("index.md").read_text(errors="replace")
    details = _LATER_DETAIL.sub("", _section(index, "Case details"))
    m = _PRIMARY.search(details)
    history = folder.joinpath("history.md").read_text(errors="replace") if (folder / "history.md").exists() else ""
    events = _known_events(history)  # the first later or unstaged event stops it: never guess
    linked = sorted({a for e in events for a in _ATTACHMENT.findall(e) if (folder / a).is_file()})
    return KnownContext(folder.name, m.group(1) if m else "", details, _section(index, "Initial request"),
                        events, linked)
