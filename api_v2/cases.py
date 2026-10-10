"""Case files -> a browsable list: title, preview and the events (tickets) in order."""
from __future__ import annotations

import re
from pathlib import Path


def parse_events(text: str) -> list:
    out = []
    for block in re.split(r'<a id="event-\d+"></a>', text)[1:]:
        field = lambda k: (re.search(rf"- \*\*{k}:\*\* (.*)", block) or [None, ""])[1].strip()
        head = re.search(r"## (.+?) — event (\d+)", block)
        body = [ln for ln in block.splitlines() if ln.strip() and not ln.startswith("## ") and not re.match(r"- \*\*(Channel|From|To|Stage):\*\*", ln)]
        out.append({"id": f"event-{head.group(2)}" if head else f"event-{len(out) + 1:03d}", "timestamp": head.group(1) if head else "",
                    "stage": field("Stage"), "channel": field("Channel"), "from": field("From"), "to": field("To"), "body": "\n".join(body).strip()})
    return out


def summarise(path: Path) -> dict:
    text = path.read_text()
    events = parse_events(text)
    ref = (re.search(r"\b[A-Z]{2,4}-\d+\b", text) or [None])[0]
    customer = next((e["from"] for e in events if re.search(r"recipient|customer|contact|consignee|shipper", e["from"], re.I)), events[0]["from"] if events else "")
    last = events[-1]["body"].replace("\n", " ") if events else ""
    return {"id": path.stem, "title": " · ".join(x for x in (ref, customer) if x) or path.stem,
            "preview": last[:110] + ("…" if len(last) > 110 else ""), "events": events}


def list_cases(folder: Path) -> list:
    return [summarise(p) for p in sorted(folder.glob("*.md"))] if folder.exists() else []
