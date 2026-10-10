"""Load an operational case folder (index.md, history.md, attachments/) into a Case.

Works on any folder layout: unknown files are read as text when possible, PDFs are
text-extracted (and kept as raw bytes for native PDF input), images are kept for vision.

`public_cutoff=True` is used only for development evaluation on the public example
cases: it hides everything after the escalation point (later events, the recorded next
action, the outcome, the boundaries rubric and attachments first referenced later), so
the agent sees exactly what the desk knew at escalation.
"""
from __future__ import annotations

import base64
import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

TEXT_EXT = {".md", ".txt", ".csv", ".json", ".eml", ".html", ".htm", ".xml", ".yaml", ".yml", ".log", ".tsv"}
IMAGE_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
MAX_TEXT_CHARS = 120_000          # per file
MAX_TOTAL_CHARS = 600_000         # whole case
MAX_IMAGE_BYTES = 3_600_000      # raw bytes; base64 adds ~33% and the API limit is 5 MB per image
MAX_IMAGES = 12
MAX_PDF_B64_BYTES = 8_000_000

# Sections of a public example index.md that reveal the ending (hidden in eval mode).
REVEALING_SECTIONS = {"overview", "next action at escalation", "outcome", "boundaries and remaining work",
                      "summary", "resolution", "result"}
REVEALING_DETAIL_KEYS = ("status", "updated", "completed", "resolved", "closed")

EVENT_SPLIT = re.compile(r'(?=^<a id="event-\d+"></a>\s*$)', re.M)
EVENT_HEADER = re.compile(r'^#{2,3}\s+(?P<ts>.+?)\s+[—–-]+\s+event\s+(?P<num>\d+)', re.M | re.I)
HEADER_SPLIT = re.compile(r'(?=^#{2,3}\s+.+?\s+[—–-]+\s+event\s+\d+)', re.M | re.I)
TS_PREFIX = re.compile(r'(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}(?::\d{2})?)')
META_LINE = re.compile(r'^-\s+\*\*(?P<k>[^*]+?):\*\*\s*(?P<v>.*)$', re.M)
LINK = re.compile(r'\]\(([^)]+)\)')


@dataclass
class Event:
    num: int
    timestamp: str
    meta: dict
    body: str
    raw: str

    @property
    def stage(self) -> str:
        return self.meta.get("stage", "").lower()


@dataclass
class Attachment:
    name: str
    rel_path: str
    kind: str                 # text | pdf | image | unsupported
    text: str = ""
    media_type: str = ""
    data_b64: str = ""        # for images / pdf
    note: str = ""


@dataclass
class Case:
    case_id: str
    path: str
    track: str
    title: str
    files: List[tuple] = field(default_factory=list)          # (name, text) for primary text files
    attachments: List[Attachment] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    hidden_events: List[Event] = field(default_factory=list)  # eval only
    hidden_sections: dict = field(default_factory=dict)        # eval only: section -> text
    hidden_attachments: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)
    parties: List[str] = field(default_factory=list)
    now: str = ""
    warnings: List[str] = field(default_factory=list)
    mode: str = "reality"
    answer_name: str = ""      # set by the runner only when two discovered cases would share an answer folder

    @property
    def answer_id(self) -> str:
        if self.answer_name:
            return self.answer_name
        return str(int(self.case_id)) if self.case_id.isdigit() else self.case_id


def _read_text(p: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return ""


def parse_events(history: str) -> List[Event]:
    events: List[Event] = []
    # Normally each event starts with an <a id="event-N"> anchor; fall back to the headings if there are none.
    chunks = EVENT_SPLIT.split(history) if EVENT_SPLIT.search(history) else HEADER_SPLIT.split(history)
    for chunk in chunks:
        m = EVENT_HEADER.search(chunk)
        if not m:
            continue
        meta = {mm.group("k").strip().lower(): mm.group("v").strip() for mm in META_LINE.finditer(chunk)}
        body_lines = []
        past_header = False
        for line in chunk.splitlines():
            if line.startswith("## "):
                past_header = True
                continue
            if not past_header or line.startswith("<a id=") or META_LINE.match(line):
                continue
            body_lines.append(line)
        events.append(Event(int(m.group("num")), m.group("ts").strip(), meta,
                            "\n".join(body_lines).strip(), chunk.strip()))
    return events


def split_sections(md: str) -> List[tuple]:
    """Return [(heading or '', text_including_heading)] for '## ' sections."""
    parts = re.split(r'(?=^##\s)', md, flags=re.M)
    out = []
    for part in parts:
        m = re.match(r'^##\s+(.+)$', part, flags=re.M)
        out.append(((m.group(1).strip() if m else ""), part))
    return out


def _cutoff_index(events: List[Event]) -> Optional[int]:
    """Index of the first event the desk must NOT see (first agent action after escalation)."""
    if not any(e.stage for e in events):
        return None
    for i, e in enumerate(events):
        if "agent action" in e.stage:
            return i
    esc = [i for i, e in enumerate(events) if "escalation" in e.stage]
    return (esc[-1] + 1) if esc else None


def _strip_index_for_eval(index_md: str, case: Case) -> str:
    keep = []
    for heading, text in split_sections(index_md):
        h = heading.lower()
        if h in REVEALING_SECTIONS:
            case.hidden_sections[heading] = text.strip()
            continue
        if h == "case details":
            lines = []
            for line in text.splitlines():
                mm = META_LINE.match(line)
                if mm and mm.group("k").strip().lower().startswith(REVEALING_DETAIL_KEYS):
                    case.hidden_sections.setdefault("_details", "")
                    case.hidden_sections["_details"] += line + "\n"
                    continue
                lines.append(line)
            text = "\n".join(lines) + "\n"
        if h == "attachments":
            text = "## Attachments\n\nOnly attachments referenced in the visible history are provided.\n\n"
        keep.append(text)
    return "".join(keep)


def _office_text(p: Path) -> str:
    """Text from .docx / .xlsx / .pptx using only the standard library (they are zipped XML)."""
    import zipfile
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        if p.suffix.lower() == ".xlsx":
            shared = []
            if "xl/sharedStrings.xml" in names:
                xml = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
                shared = [re.sub(r"<[^>]+>", "", si) for si in re.findall(r"<si>(.*?)</si>", xml, flags=re.S)]
            rows_out = []
            for n in sorted(x for x in names if x.startswith("xl/worksheets/sheet") and x.endswith(".xml")):
                xml = z.read(n).decode("utf-8", "replace")
                rows_out.append(f"[{n.split('/')[-1]}]")
                for row in re.findall(r"<row[^>]*>(.*?)</row>", xml, flags=re.S):
                    cells = []
                    for attrs, inner in re.findall(r"<c([^>]*)>(.*?)</c>", row, flags=re.S):
                        v = re.search(r"<v>(.*?)</v>", inner, flags=re.S)
                        t = re.search(r"<t[^>]*>(.*?)</t>", inner, flags=re.S)
                        val = v.group(1) if v else (t.group(1) if t else "")
                        if 't="s"' in attrs and val.isdigit() and int(val) < len(shared):
                            val = shared[int(val)]
                        cells.append(val)
                    rows_out.append(",".join(cells))
            return "\n".join(rows_out)
        parts = sorted(n for n in names if n in ("word/document.xml",) or n.startswith(("ppt/slides/slide", "word/header", "word/footer")))
        out = []
        for n in parts:
            xml = z.read(n).decode("utf-8", "replace")
            xml = re.sub(r"</w:p>|</a:p>|<w:br/>", "\n", xml)
            out.append(re.sub(r"<[^>]+>", "", xml))
        import html
        return html.unescape("\n".join(out)).strip()


def _sniff_image(raw: bytes) -> str:
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return ""


def _shrink_image(raw: bytes) -> Optional[bytes]:
    """Downscale an oversized image to JPEG with Pillow, if it is installed."""
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGB")
        for side in (2000, 1500, 1100):
            im.thumbnail((side, side))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=80)
            if buf.tell() <= MAX_IMAGE_BYTES:
                return buf.getvalue()
    except Exception:  # noqa: BLE001
        return None
    return None


ZIP_TEXT_EXT = {".txt", ".md", ".csv", ".json", ".eml"}


def _zip_text(p: Path) -> str:
    """A zip's member names plus its text members, read in memory: no extraction, no nested archives,
    members over the per-file cap skipped, the whole thing capped at MAX_TEXT_CHARS."""
    import zipfile
    with zipfile.ZipFile(p) as z:
        members = [i for i in z.infolist() if not i.is_dir()]
        parts = ["Archive members: " + ", ".join(i.filename for i in members[:200])]
        total = 0
        for i in members:
            if Path(i.filename).suffix.lower() not in ZIP_TEXT_EXT or i.file_size > MAX_TEXT_CHARS or total >= MAX_TEXT_CHARS:
                continue
            raw = z.read(i)[:MAX_TEXT_CHARS]
            text = next((t for t in (_try_decode(raw, e) for e in ("utf-8", "utf-8-sig", "latin-1")) if t is not None), "")
            parts.append(f"--- {i.filename} ---\n{text}")
            total += len(text)
    return "\n\n".join(parts)


def _try_decode(raw: bytes, encoding: str) -> Optional[str]:
    try:
        return raw.decode(encoding)
    except UnicodeDecodeError:
        return None


def _load_attachment(p: Path, root: Path, media: bool = True) -> Attachment:
    rel = str(p.relative_to(root))
    ext = p.suffix.lower()
    try:
        size = p.stat().st_size
        if ext in IMAGE_EXT or ext in (".heic", ".tif", ".tiff", ".bmp"):
            if not media:
                return Attachment(p.name, rel, "unsupported", note="image not sent (media-free retry after an earlier failure)")
            raw = p.read_bytes()
            mt = _sniff_image(raw)
            if not mt or size > MAX_IMAGE_BYTES:
                small = _shrink_image(raw)
                if small is None:
                    why = "unsupported image format" if not mt else f"image too large to send ({size} bytes)"
                    return Attachment(p.name, rel, "unsupported", note=why)
                return Attachment(p.name, rel, "image", media_type="image/jpeg", data_b64=base64.b64encode(small).decode(),
                                  note=f"downscaled from {size} bytes")
            return Attachment(p.name, rel, "image", media_type=mt, data_b64=base64.b64encode(raw).decode())
        if ext == ".pdf":
            raw = p.read_bytes()
            text = ""
            try:
                from pypdf import PdfReader
                import io
                reader = PdfReader(io.BytesIO(raw))
                text = "\n\n".join((pg.extract_text() or "") for pg in reader.pages).strip()
            except Exception as exc:  # noqa: BLE001
                text = ""
                note = f"pdf text extraction failed: {exc}"
            att = Attachment(p.name, rel, "pdf", text=text[:MAX_TEXT_CHARS], media_type="application/pdf",
                             data_b64=base64.b64encode(raw).decode() if (media and size < MAX_PDF_B64_BYTES) else "")
            if len(text) > MAX_TEXT_CHARS:
                att.note = f"truncated: only the first {MAX_TEXT_CHARS} characters of the PDF text are included"
            if not text:
                att.note = ("no extractable text layer; sent as native PDF for visual reading" if att.data_b64
                            else "no extractable text layer and the PDF could not be sent for visual reading")
                if not att.data_b64:
                    att.kind = "unsupported"
            return att
        if ext == ".zip":
            return Attachment(p.name, rel, "text", text=_zip_text(p)[:MAX_TEXT_CHARS],
                              note="zip archive: member list and text members only")
        if ext in (".docx", ".xlsx", ".pptx"):
            t = _office_text(p)
            note = f"truncated: only the first {MAX_TEXT_CHARS} characters are included" if len(t) > MAX_TEXT_CHARS else ""
            return Attachment(p.name, rel, "text", text=t[:MAX_TEXT_CHARS], note=note)
        if ext in TEXT_EXT or (mimetypes.guess_type(p.name)[0] or "").startswith("text"):
            t = _read_text(p)
            if "\x00" in t[:2000]:   # UTF-16 exports
                for enc in ("utf-16", "utf-16-le"):
                    try:
                        t = p.read_bytes().decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
            note = f"truncated: only the first {MAX_TEXT_CHARS} characters are included" if len(t) > MAX_TEXT_CHARS else ""
            return Attachment(p.name, rel, "text", text=t[:MAX_TEXT_CHARS], note=note)
        # last resort: try to decode as text
        t = _read_text(p)
        if t and sum(c.isprintable() or c.isspace() for c in t[:2000]) > 0.95 * min(len(t), 2000):
            return Attachment(p.name, rel, "text", text=t[:MAX_TEXT_CHARS])
        return Attachment(p.name, rel, "unsupported", note=f"binary file type {ext or '?'} not readable")
    except Exception as exc:  # noqa: BLE001
        return Attachment(p.name, rel, "unsupported", note=f"failed to read: {exc}")


def load_case(path: str | Path, public_cutoff: bool = False, track: str = "", media: bool = True) -> Case:
    root = Path(path)
    if root.is_file():
        text = _read_text(root)
        case = Case(case_id=root.stem, path=str(root), track=track or root.parent.name,
                    title=_title(text) or root.stem, files=[(root.name, text[:MAX_TEXT_CHARS])])
        case.events = parse_events(text)
        _finish(case)
        return case

    case_id = root.name
    case = Case(case_id=case_id, path=str(root), track=track or root.parent.name, title=case_id,
                mode="public-eval" if public_cutoff else "reality")
    index_p, history_p = root / "index.md", root / "history.md"
    inner = _inner_case_dir(root)  # Track/Case/sub: read the sub folder's files, keep the case folder's name
    if inner is not None:
        index_p, history_p = inner / "index.md", inner / "history.md"
    index_md = _read_text(index_p) if index_p.exists() else ""
    history_md = _read_text(history_p) if history_p.exists() else ""
    case.title = _title(index_md) or _title(history_md) or case_id

    events = parse_events(history_md) if history_md else []
    if public_cutoff and events:
        cut = _cutoff_index(events)
        if cut is not None:
            case.hidden_events = events[cut:]
            events = events[:cut]
            hidden_nums = {e.num for e in case.hidden_events}
            history_md = _rebuild_history(history_md, events, hidden_nums)
        else:
            case.warnings.append("no stage markers: could not determine escalation cutoff; showing full history")
    case.events = events
    if not history_md and not events:
        case.warnings.append("no history.md: answered from index/attachments only; the current time is unknown")
    if public_cutoff and index_md:
        index_md = _strip_index_for_eval(index_md, case)

    if index_md:
        case.files.append(("index.md", index_md))
    if history_md:
        case.files.append(("history.md", history_md))

    # Any other top-level text files (e.g. a challenge question file)
    for p in sorted(root.iterdir()):
        if p.is_file() and p.name not in ("index.md", "history.md") and not p.name.startswith((".", "_")):
            att = _load_attachment(p, root, media)
            if att.kind == "text":
                case.files.append((p.name, att.text))
            else:
                case.attachments.append(att)

    visible_text = "\n".join(t for _, t in case.files)
    for p in sorted(x for x in root.rglob("*") if x.is_file() and x.parent != root and not x.name.startswith((".", "_"))
                    and x not in (index_p, history_p)
                    and not any(part.startswith(".") or part == "__MACOSX" for part in x.relative_to(root).parts[:-1])):
        rel = str(p.relative_to(root))
        if public_cutoff and (rel not in visible_text and p.name not in visible_text):
            case.hidden_attachments.append(rel)
            continue
        case.attachments.append(_load_attachment(p, root, media))
    if not media:
        case.warnings.append("media-free retry: images and scanned PDFs were not sent to the model after an earlier failure")

    _finish(case)
    return case


def _rebuild_history(history_md: str, visible: List[Event], hidden_nums: set) -> str:
    head = EVENT_SPLIT.split(history_md)[0]
    head = re.sub(r'Total events:\s*\d+\.?', f'Events available at this point: {len(visible)}.', head)
    return head.rstrip() + "\n\n" + "\n\n".join(e.raw for e in visible) + "\n"


def _title(md: str) -> str:
    m = re.search(r'^#\s+(.+)$', md, flags=re.M)
    if not m:
        return ""
    t = re.sub(r'^Case\s+\w+\s*(history)?\s*[:—-]\s*', '', m.group(1).strip(), flags=re.I)
    return t.strip()


def _finish(case: Case) -> None:
    chans, parties = [], []
    for e in case.events:
        for key, bucket in (("channel", chans), ("from", parties), ("to", parties)):
            v = e.meta.get(key, "").strip()
            if v and v not in bucket and v.lower() != "not specified":
                bucket.append(v)
    case.channels, case.parties = chans, parties
    case.now = _latest_timestamp(case.events)
    images = [a for a in case.attachments if a.kind == "image"]
    for a in images[MAX_IMAGES:]:
        a.kind, a.data_b64, a.note = "unsupported", "", f"not sent: more than {MAX_IMAGES} images in the case"
    total = sum(len(t) for _, t in case.files) + sum(len(a.text) for a in case.attachments)
    if total > MAX_TOTAL_CHARS:
        case.warnings.append(f"case text is very large ({total} chars); long files were truncated")
        budget = MAX_TOTAL_CHARS
        new_files = []
        for name, t in case.files:
            share = max(20_000, budget // max(1, len(case.files)))
            new_files.append((name, t if len(t) <= share else t[:share // 2] + "\n\n[... truncated middle ...]\n\n" + t[-share // 2:]))
        case.files = new_files
        texts = [a for a in case.attachments if a.text]
        share = max(10_000, (MAX_TOTAL_CHARS // 3) // max(1, len(texts)))
        for a in texts:
            if len(a.text) > share:
                a.text = a.text[:share // 2] + "\n\n[... truncated middle ...]\n\n" + a.text[-share // 2:]
                a.note = (a.note + "; " if a.note else "") + "middle truncated to fit the case budget"
    for a in case.attachments:
        if a.kind == "unsupported" or "truncated" in a.note:
            case.warnings.append(f"attachment {a.rel_path}: {a.note}")
    if not case.events and any(n == "history.md" for n, _ in case.files):
        case.warnings.append("could not parse dated events in history.md; the current time is unknown - read the history text directly")


def _latest_timestamp(events: List[Event]) -> str:
    """The latest event time (not simply the last in file order, in case the thread is newest-first)."""
    best, best_key = "", ""
    for e in events:
        m = TS_PREFIX.search(e.timestamp)
        key = f"{m.group(1)} {m.group(2)}" if m else ""
        if key >= best_key:
            best, best_key = e.timestamp, key
    return best


def discover_cases(path: str | Path) -> List[Path]:
    """A case dir has index.md/history.md (or any .md). A parent dir holds case dirs."""
    root = Path(path)
    if root.is_file():
        return [root]
    if (root / "index.md").exists() or (root / "history.md").exists():
        return [root]
    subdirs = sorted([d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".") and d.name != "__MACOSX"], key=_sort_key)
    direct = [d for d in subdirs if any(d.glob("*.md")) or any(d.glob("*.txt"))]
    # Beside ordinary case folders, a folder whose case files sit one level down (Track/Case/sub) is a case too.
    cases = [d for d in subdirs if d in direct or (direct and _inner_case_dir(d))]
    if cases:
        return cases
    # nested one level deeper (e.g. HackatonChallendges/<track>/<case>)
    nested = []
    for d in subdirs:
        nested.extend(discover_cases(d))
    if nested:
        return nested
    # flat folder of case files
    return sorted([p for p in root.iterdir() if p.is_file() and not p.name.startswith((".", "_"))
                   and p.suffix.lower() in (".md", ".txt", ".json")], key=_sort_key)


def _inner_case_dir(d: Path) -> Optional[Path]:
    """The one subfolder holding a case's index.md/history.md when the case folder itself has no .md
    (a Track/Case/sub layout), else None. Two or more such subfolders are not guessed between."""
    if (d / "index.md").exists() or (d / "history.md").exists():
        return None
    inner = [x for x in d.iterdir() if x.is_dir() and ((x / "index.md").exists() or (x / "history.md").exists())]
    return inner[0] if len(inner) == 1 else None


def _sort_key(p: Path):
    s = p.stem if p.is_file() else p.name
    return (0, int(s), "") if s.isdigit() else (1, 0, s)
