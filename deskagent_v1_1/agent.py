"""One Claude call per case: case events + preprocess JSON in, a validated DeskResponse out.

Uses structured outputs (output_config.format json_schema via messages.parse), not a forced tool call:
the current Claude 5.5 models reject forced tool_choice. Model fallback and fatal-error handling follow deskagent/llm.py."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "preprocess"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deskagent.llm import FatalAPIError, _ModelState, load_dotenv, model_list  # noqa: E402

from .checks import run_checks  # noqa: E402
from .models import DeskResponse  # noqa: E402
from .prompt import system_prompt, user_message  # noqa: E402

load_dotenv()
MAX_TOKENS = int(os.environ.get("V11_MAX_TOKENS", "16000"))


def respond(case_text: str, pre: dict, case: str = "case", model: Optional[str] = None) -> tuple[Optional[DeskResponse], dict]:
    """The single agent call. Returns (response or None, meta). meta carries model, tokens, latency, stop_reason, error, trace."""
    import anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None, {"error": "ANTHROPIC_API_KEY is not set (put it in .env or the environment)"}
    client = anthropic.Anthropic(max_retries=4, timeout=240)
    system = [{"type": "text", "text": system_prompt(), "cache_control": {"type": "ephemeral"}}]
    messages = [{"role": "user", "content": user_message(case_text, pre, case)}]
    meta: dict = {"attempts": []}
    for m in model_list(model or os.environ.get("V11_MODEL")):
        if m in _ModelState.dead:
            continue
        t0 = time.time()
        try:
            resp = client.messages.parse(model=m, max_tokens=MAX_TOKENS, system=system, messages=messages,
                                         output_format=DeskResponse)
        except (anthropic.NotFoundError, anthropic.PermissionDeniedError) as exc:
            _ModelState.dead.add(m)
            meta["attempts"].append({"model": m, "error": f"model unavailable: {exc}"[:300]})
            continue
        except anthropic.AuthenticationError as exc:
            raise FatalAPIError(f"Anthropic API authentication failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001 - overload/network after SDK retries, or schema 400: try the next model
            meta["attempts"].append({"model": m, "error": f"{type(exc).__name__}: {str(exc)[:300]}"})
            continue
        u = resp.usage
        meta.update(model=m, latency_s=round(time.time() - t0, 2), stop_reason=resp.stop_reason,
                    usage={k: getattr(u, k, None) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens")},
                    trace=[{"type": "llm_call", "model": m, "request": messages[0]["content"],
                            "response": [getattr(b, "text", None) or getattr(b, "type", "?") for b in resp.content]}])
        out = getattr(resp, "parsed_output", None)
        if out is None:
            meta["error"] = f"no parsed output (stop_reason={resp.stop_reason})"
        return out, meta
    meta["error"] = "all models failed: " + "; ".join(f"{a['model']}: {a['error']}" for a in meta["attempts"])
    return None, meta


def run_case(case_text: str, case: str = "case", model: Optional[str] = None, pre: Optional[dict] = None) -> dict:
    """preprocess -> agent -> agreement checks. Never raises on model/API failure: the run carries an `error`."""
    from preprocess import parse_events, preprocess
    t0 = time.time()
    events = parse_events(case_text)
    pre = pre if pre is not None else preprocess(case_text, case=case, debug=True)
    raw = pre.pop("_raw", None)
    try:
        response, meta = respond(case_text, pre, case, model)
    except FatalAPIError as exc:
        response, meta = None, {"error": str(exc)}
    return {
        "case": case, "events": events, "preprocess": pre, "classifier_raw": _slim_raw(raw),
        "response": response.model_dump() if response else None,
        "checks": run_checks(pre, response, events) if response else [],
        "meta": {**meta, "total_s": round(time.time() - t0, 2)},
        "error": meta.get("error"),
    }


def _slim_raw(raw: Optional[dict]) -> dict:
    """Per-option probabilities from the classifier calls (what the Investigate page plots)."""
    out: dict = {}
    for call in (raw or {}).values():
        for k, v in ((call or {}).get("answers") or {}).items():
            if isinstance(v, dict) and "probabilities" in v:
                out[k] = {"choice": v.get("choice"), "probabilities": v["probabilities"]}
    return out
