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
from collections.abc import Callable
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
    """Comparable form of a reference, as speech-to-text hears it: no spaces or hyphens, and the
    letters O and I folded into 0 and 1 ("DL-039-O" and a misheard "DL0390" are the same)."""
    return re.sub(r"[^A-Z0-9]", "", ref.upper()).translate(str.maketrans("OI", "01"))


_CORE = re.compile(r"^([A-Z]{2,4})(\d{3})")


def core(ref_norm: str) -> str:
    """The leading letters + three digits of a normalised reference (DL0390 -> DL039), or ''."""
    m = _CORE.match(ref_norm)
    return m.group(1) + m.group(2) if m else ""


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
    cores: dict[str, set[Path]] = {}
    for ref, folders in (other | primary).items():
        if core(ref):
            cores.setdefault("core:" + core(ref), set()).update(folders)
    for key, folders in cores.items():  # fallback when the exact form was misheard; never guesses
        resolved[key] = next(iter(folders)) if len(folders) == 1 else None
    return resolved


def find_shipment(ref: str, root: Path | None = None) -> Path | None:
    """The case folder for a spoken reference: exact match first, then a unique letters+digits core.
    A reference or core that points at two cases matches nothing."""
    if not ref.strip():
        return None
    index, n = _index(str(root or DATA)), norm(ref)
    if n in index:
        return index[n]
    return index.get("core:" + core(n)) if core(n) else None


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


_EVENT_DATE = re.compile(r"^## (\d{4})-(\d{2})-(\d{2})\b", re.MULTILINE)
_FROM = re.compile(r"^- \*\*From:\*\*\s*(.+)$", re.MULTILINE)
_TO = re.compile(r"^- \*\*To:\*\*\s*(.+)$", re.MULTILINE)
_ORG = re.compile(r"^(?:[A-Z][A-Za-z&'-]*)(?: [A-Z][A-Za-z&'-]*){0,4}$")  # "Plover Arc Logistics"
_MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December")
_UNSAYABLE = re.compile(r"@|\d{6,}|[£$€]|\b\d+(\.\d+)?\s?(GBP|EUR|USD|pounds?|euros?|dollars?)\b", re.IGNORECASE)
NOT_FOUND = ("I can't find that reference in our records. Could you read it again, or I can log it so "
             "the desk can check.")


def _org(party: str) -> str:
    """The organisation in a "Team, Organisation" party line, or '' for a person, a role or our own desk."""
    org = party.rsplit(",", 1)[-1].strip() if "," in party else ""
    return org if _ORG.match(org) and "desk" not in org.lower() else ""


def _first_sentence(body: str) -> str:
    text = " ".join(line.strip() for line in body.splitlines() if line.strip() and not line.startswith(("-", "#", "<")))
    return re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0].strip()


def spoken_summary(ctx: KnownContext, safe: Callable[[str], bool]) -> str:
    """What the caller may hear about their parcel: references, the businesses involved and the latest
    update from one of them, all from the record as it stood before the desk acted. No outcome, no next
    action, no amounts; the update's first sentence is dropped unless `safe` passes it."""
    refs = list(dict.fromkeys([ctx.primary] + _REF.findall("\n".join([ctx.details, *ctx.events]))))
    refs = [r for r in refs if r][:4]
    said = f"I can see {refs[0]}" + (f", with {' and '.join(refs[1:])}" if len(refs) > 1 else "") + "."
    orgs = list(dict.fromkeys(o for e in ctx.events for m in (_FROM, _TO) for o in [_org(x) for x in m.findall(e)] if o))
    if orgs:
        said += (f" The business on it is {orgs[0]}." if len(orgs) == 1
                 else f" The businesses on it are {' and '.join(orgs[:3])}.")
    for event in reversed(ctx.events):  # the latest update a business sent; a caller's own message is no news
        sender = _FROM.search(event)
        org = _org(sender.group(1)) if sender else ""
        if not org:
            continue
        d = _EVENT_DATE.search(event)
        when = f" on {int(d.group(3))} {_MONTHS[int(d.group(2)) - 1]}" if d else ""
        said += f" The latest update was from {org}{when}"
        body = event.split(sender.group(0), 1)[1]
        body = _TO.sub("", body)
        first = _first_sentence(body)
        factual = not first.endswith("?") and not re.match(r"(please|kindly|can you|could you)\b", first, re.IGNORECASE)
        if first and factual and len(first) <= 200 and not _UNSAYABLE.search(first) and safe(first):
            said += f": {first}"
        else:
            said += "."
        break
    return said


# ------------------------------------------------------------------ hub database (read-only, first choice)
_NORM_SQL = "translate(upper(regexp_replace(coalesce({col}, ''), '[^A-Za-z0-9]', '', 'g')), 'OI', '01')"
_CALLER_ROLES = ("customer", "recipient", "sender", "caller", "reporting customer", "intended recipient")


def _plain(value: object, safe: Callable[[str], bool], limit: int = 120) -> str:
    """A database value fit to say aloud, or '' (too long, an amount, contact details or a failed check)."""
    text = " ".join(str(value or "").split())
    return text if text and len(text) <= limit and not _UNSAYABLE.search(text) and safe(text) else ""


def db_lookup(ref: str, safe: Callable[[str], bool]) -> dict | None:
    """The shipment from the hub database when DATABASE_URL is set, else None.

    Read-only session, 3 s connect and statement timeouts. Any error, no row, or a reference that
    matches two shipments gives None, so the caller falls back to the case files.
    """
    url = os.getenv("DATABASE_URL", "")
    n = norm(ref)
    if not url or not n:
        return None
    import psycopg  # only needed on this path; hub deployments install it

    with psycopg.connect(url, connect_timeout=3, autocommit=True, prepare_threshold=None) as conn:
        conn.execute("set default_transaction_read_only = on")
        conn.execute("set statement_timeout = 3000")
        ships = conn.execute(f"select id, description, status, eta, depot, case_id from shipments "
                             f"where {_NORM_SQL.format(col='id')} = %s limit 2", (n,)).fetchall()
        case = None
        if not ships:
            case = conn.execute(f"select id, status, shipment_id from cases where {_NORM_SQL.format(col='shipment_id')} = %s "
                                "order by updated_at desc limit 1", (n,)).fetchone()
            if case and case[2]:
                ships = conn.execute("select id, description, status, eta, depot, case_id from shipments where id = %s",
                                     (case[2],)).fetchall()
        if len(ships) != 1 and not case:
            return None
        ship = ships[0] if len(ships) == 1 else None
        if case is None:
            case_id = ship[5]
            case = conn.execute("select id, status, shipment_id from cases where id = %s", (case_id,)).fetchone() if case_id \
                else conn.execute(f"select id, status, shipment_id from cases where {_NORM_SQL.format(col='shipment_id')} = %s "
                                  "order by updated_at desc limit 1", (n,)).fetchone()
        event = conn.execute("select ts, author, author_role from case_events where case_id = %s and kind in ('call', 'message') "
                             "and visibility = 'all' order by ts desc limit 1", (case[0],)).fetchone() if case else None
    shipment_id = ship[0] if ship else case[2]
    said = f"I can see shipment {shipment_id}"
    if ship:
        desc, status, depot, eta = (_plain(ship[1], safe), _plain(str(ship[2] or "").replace("_", " "), safe, 40),
                                    _plain(ship[4], safe, 60), _plain(ship[3], safe, 40))
        said += (f", {desc}" if desc else "") + (f", currently {status}" if status else "")
        said += (f" at {depot}" if depot and status else "") + (f", expected {eta}" if eta else "")
    said += "."
    if event and event[0]:
        role = str(event[2] or "").strip().lower()
        who = "the customer" if role in _CALLER_ROLES else _plain(event[1], safe, 60)
        if who:
            ts = event[0]
            said += f" The latest update on the case was from {who} on {ts.day} {_MONTHS[ts.month - 1]}."
    return {"found": True, "shipment": shipment_id, "say": said}
