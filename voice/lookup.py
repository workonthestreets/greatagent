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


@lru_cache(maxsize=1)
def _index(root: str) -> dict[str, Path]:
    """Normalised reference -> case folder. The Primary shipment wins over other refs."""
    primary: dict[str, Path] = {}
    other: dict[str, Path] = {}
    for idx in sorted(Path(root).glob("*/index.md")):
        details = _section(idx.read_text(errors="replace"), "Case details")
        m = re.search(r"\*\*Primary shipment:\*\*\s*(\S+)", details)
        if m:
            primary.setdefault(norm(m.group(1)), idx.parent)
        for ref in _REF.findall(details):
            other.setdefault(norm(ref), idx.parent)
    return other | primary


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
    m = re.search(r"\*\*Primary shipment:\*\*\s*(\S+)", details)
    history = folder.joinpath("history.md").read_text(errors="replace") if (folder / "history.md").exists() else ""
    events = []
    for block in _EVENT.split(history)[1:]:
        stage = _STAGE.search(block)
        if not stage or stage.group(1).strip().lower() not in KNOWN_STAGES:
            break  # the first event after escalation, or an unstaged history: stop, never guess
        events.append(block.strip())
    linked = sorted({a for e in events for a in _ATTACHMENT.findall(e) if (folder / a).is_file()})
    return KnownContext(folder.name, m.group(1) if m else "", details, _section(index, "Initial request"),
                        events, linked)
