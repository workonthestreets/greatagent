"""System prompt = preprocess/delivery_desk_system_prompt.md, read at run time (single source of truth)."""
from __future__ import annotations

import json
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parent.parent / "preprocess" / "delivery_desk_system_prompt.md"

# The prompt tells the model to ignore these; leave them out of what it sees.
IGNORED_FIELDS = ("case", "spec", "events_seen", "usage", "_raw")


def system_prompt() -> str:
    return PROMPT_PATH.read_text()


def model_view(pre: dict) -> dict:
    return {k: v for k, v in pre.items() if k not in IGNORED_FIELDS}


def user_message(case_text: str, pre: dict, case_id: str = "case") -> str:
    return (
        f'<case id="{case_id}">\n{case_text.strip()}\n</case>\n\n'
        f"<preprocessing>\n{json.dumps(model_view(pre), indent=1, ensure_ascii=False)}\n</preprocessing>\n\n"
        "Write the response for this case as the JSON object described in section 10."
    )
