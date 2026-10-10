"""Get a structured answer from Claude.

Two routes, picked by LLM_BACKEND:
  api (default when APP_ANTHROPIC_API_KEY is set): Messages API, schema enforced as a forced tool call.
  cli: the local `claude` binary on your Claude Code login (no API key; text only, no images).

`ask_json` takes a JSON Schema dict and returns a dict; `ask` wraps it for pydantic models.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time

from pydantic import BaseModel


class LLMUnavailable(RuntimeError):
    """Every try failed; callers fall back to a safe default (escalate) and record it."""


LLMError = LLMUnavailable  # older name used by the scorer


def backend() -> str:
    return os.getenv("LLM_BACKEND") or ("api" if os.getenv("APP_ANTHROPIC_API_KEY") else "cli")


def ask_json(system: str, user: str, schema: dict, model: str | None = None, attempts: int = 3) -> dict:
    route = _via_api if backend() == "api" else _via_cli
    last: Exception | None = None
    for n in range(attempts):
        try:
            return route(system, user, schema, model)
        except LLMUnavailable as e:  # throttling, timeouts, malformed JSON
            last = e
            time.sleep(4 * (n + 1))
    raise LLMUnavailable(f"gave up after {attempts} attempts: {last}")


def ask[T: BaseModel](prompt: str, schema: type[T], system: str, attempts: int = 3) -> T:
    data = ask_json(system, prompt, schema.model_json_schema(), attempts=attempts)
    try:
        return schema.model_validate(data)
    except ValueError as e:
        raise LLMUnavailable(f"answer failed validation: {e}") from e


def _via_api(system: str, user: str, schema: dict, model: str | None) -> dict:
    import anthropic

    key = os.getenv("APP_ANTHROPIC_API_KEY")
    if not key:
        raise LLMUnavailable("APP_ANTHROPIC_API_KEY missing")
    tool = {"name": "answer", "description": "Return the answer.", "input_schema": schema}
    try:
        msg = anthropic.Anthropic(api_key=key).messages.create(
            model=model or os.getenv("API_MODEL", "claude-sonnet-5-5"), max_tokens=2048,
            system=system, tools=[tool], tool_choice={"type": "tool", "name": "answer"},
            messages=[{"role": "user", "content": user}])
    except anthropic.APIError as e:
        raise LLMUnavailable(str(e)) from e
    block = next((b for b in msg.content if b.type == "tool_use"), None)
    if block is None:
        raise LLMUnavailable("model did not call the answer tool")
    return dict(block.input)


def _via_cli(system: str, user: str, schema: dict, model: str | None) -> dict:
    instructions = (f"{system}\n\nAnswer with one JSON object and nothing else. It must validate "
                    f"against this JSON Schema:\n{json.dumps(schema)}")
    with tempfile.TemporaryDirectory() as empty:  # outside any repo, so no project config loads
        try:
            done = subprocess.run(
                ["claude", "-p", "--output-format", "json", "--tools", "",
                 "--model", model or os.getenv("CLI_MODEL", "sonnet"), "--system-prompt", instructions],
                input=user, capture_output=True, text=True, timeout=180, cwd=empty, check=False)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise LLMUnavailable(f"claude CLI: {e}") from e
    out = done.stdout
    try:  # a shell profile may print terminal escape codes before the JSON envelope
        envelope = json.loads(out[out.index("{"):out.rindex("}") + 1])
    except (ValueError, json.JSONDecodeError) as e:
        raise LLMUnavailable(f"claude CLI exit {done.returncode}: {done.stderr[-200:]}") from e
    if envelope.get("is_error"):
        raise LLMUnavailable(f"claude CLI: {str(envelope.get('result'))[:200]}")
    found = re.search(r"\{.*\}", str(envelope.get("result", "")), re.DOTALL)
    if not found:
        raise LLMUnavailable("no JSON object in the reply")
    try:
        return json.loads(found.group(0))
    except json.JSONDecodeError as e:
        raise LLMUnavailable(f"bad JSON in reply: {e}") from e
