"""Thin Claude client: model fallback, retries, prompt caching and a full call trace."""
from __future__ import annotations

import json
import os
import threading
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, Dict, List, Optional

DEFAULT_MODELS = ["claude-opus-5-5", "claude-sonnet-5-5", "claude-opus-4-1", "claude-sonnet-4-5"]


def load_dotenv(path: str | Path = ".env") -> None:
    """Minimal .env loader (KEY=VALUE lines); never overrides already-set variables."""
    for candidate in (Path(path), Path(__file__).resolve().parent.parent / ".env"):
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip().removeprefix("export ").strip(), v.strip().strip('"').strip("'")
                if k and v:
                    os.environ.setdefault(k, v)
            return


def model_list(primary: Optional[str]) -> List[str]:
    env = os.environ.get("DESK_MODELS", "")
    models = [m.strip() for m in env.split(",") if m.strip()] or list(DEFAULT_MODELS)
    if primary:
        models = [primary] + [m for m in models if m != primary]
    return models


class _ModelState:
    """Remembers which model works so parallel workers stop retrying dead ones."""
    lock = threading.Lock()
    dead: set = set()


class LLM:
    def __init__(self, model: Optional[str] = None, trace: Optional[list] = None, max_tokens: int = 16000):
        import anthropic  # imported lazily so --help works without the SDK
        self._anthropic = anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set (put it in .env or the environment)")
        self.client = anthropic.Anthropic(max_retries=4, timeout=240)
        self.models = model_list(model)
        self.trace = trace if trace is not None else []
        self.max_tokens = max_tokens
        self.usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "calls": 0}

    # ------------------------------------------------------------------ core call
    def create(self, purpose: str, system: str, messages: list, tools: list, tool_choice: dict,
               max_tokens: Optional[int] = None, temperature: Optional[float] = None):
        last_exc = None
        for model in self.models:
            if model in _ModelState.dead:
                continue
            t0 = time.time()
            try:
                kwargs = dict(model=model, max_tokens=max_tokens or self.max_tokens,
                              system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                              messages=messages, tools=tools, tool_choice=tool_choice)
                if temperature is not None:
                    kwargs["temperature"] = temperature
                resp = self.client.messages.create(**kwargs)
            except (self._anthropic.NotFoundError, self._anthropic.PermissionDeniedError) as exc:
                with _ModelState.lock:
                    _ModelState.dead.add(model)
                self._log(purpose, model, messages, None, time.time() - t0, error=f"model unavailable: {exc}")
                last_exc = exc
                continue
            except self._anthropic.BadRequestError as exc:
                msg = str(exc)
                self._log(purpose, model, messages, None, time.time() - t0, error=msg[:500])
                if "not_found" in msg or "model:" in msg.lower() or "unknown model" in msg.lower():
                    with _ModelState.lock:
                        _ModelState.dead.add(model)
                    last_exc = exc
                    continue
                raise
            except Exception as exc:  # noqa: BLE001 - network/overload after SDK retries: try next model
                self._log(purpose, model, messages, None, time.time() - t0, error=f"{type(exc).__name__}: {str(exc)[:300]}")
                last_exc = exc
                continue
            self._log(purpose, model, messages, resp, time.time() - t0)
            u = resp.usage
            self.usage["input_tokens"] += getattr(u, "input_tokens", 0) or 0
            self.usage["output_tokens"] += getattr(u, "output_tokens", 0) or 0
            self.usage["cache_read_input_tokens"] += getattr(u, "cache_read_input_tokens", 0) or 0
            self.usage["calls"] += 1
            return resp
        raise RuntimeError(f"all models failed for {purpose}: {last_exc}")

    def _log(self, purpose, model, messages, resp, dt, error=None):
        entry = {"type": "llm_call", "purpose": purpose, "model": model, "latency_s": round(dt, 2),
                 "request_messages": _redact(messages)}
        if error:
            entry["error"] = error
        if resp is not None:
            entry["stop_reason"] = resp.stop_reason
            entry["usage"] = {k: getattr(resp.usage, k, None) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens")}
            entry["response"] = [_block_to_dict(b) for b in resp.content]
        self.trace.append(entry)

    # ------------------------------------------------------- structured tool loop
    def run_tool_loop(self, purpose: str, system: str, user_content: list, final_tool: dict,
                      aux_tools: Optional[Dict[str, tuple]] = None, max_turns: int = 6,
                      max_tokens: Optional[int] = None) -> dict:
        """Let the model call auxiliary tools (name -> (schema, fn)) until it calls final_tool.

        Uses tool_choice=auto throughout: the current Claude 5.5 models reject forced tool
        choice (and think adaptively), so we instruct, nudge if needed, and validate the
        required fields ourselves. Thinking blocks are passed back untouched."""
        aux_tools = aux_tools or {}
        tools = [schema for schema, _ in aux_tools.values()] + [final_tool]
        required = final_tool["input_schema"].get("required", [])
        messages = [{"role": "user", "content": list(user_content) + [
            {"type": "text", "text": f"Respond by calling the `{final_tool['name']}` tool (exactly once)."}]}]
        for _turn in range(max_turns):
            resp = self.create(purpose, system, messages, tools, {"type": "auto"}, max_tokens=max_tokens)
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            final = next((b for b in tool_uses if b.name == final_tool["name"]), None)
            messages.append({"role": "assistant", "content": resp.content})
            if final is not None:
                data = dict(final.input) if isinstance(final.input, dict) else {}
                missing = [k for k in required if k not in data]
                if not missing:
                    return data
                results = [{"type": "tool_result", "tool_use_id": final.id, "is_error": True,
                            "content": f"Missing required fields: {missing}. Call {final_tool['name']} again with all fields."}]
                results += [{"type": "tool_result", "tool_use_id": b.id, "is_error": True, "content": "not executed"}
                            for b in tool_uses if b is not final]
                messages.append({"role": "user", "content": results})
                continue
            if resp.stop_reason == "max_tokens" and not tool_uses:
                messages.append({"role": "user", "content": f"Your output was cut off. Call {final_tool['name']} now, more concisely."})
                continue
            results = []
            for b in tool_uses:
                schema_fn = aux_tools.get(b.name)
                try:
                    out = schema_fn[1](**b.input) if schema_fn else {"error": f"unknown tool {b.name}"}
                except Exception as exc:  # noqa: BLE001
                    out = {"error": str(exc)}
                self.trace.append({"type": "tool_call", "phase": purpose, "tool": b.name, "input": b.input, "output": out})
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)})
            if not results:
                results = [{"type": "text", "text": f"Now call the `{final_tool['name']}` tool with your answer."}]
            messages.append({"role": "user", "content": results})
        raise RuntimeError(f"{purpose}: model never produced a valid {final_tool['name']} call")


# ---------------------------------------------------------------------- helpers
def calculate(expression: str, label: str = "") -> dict:
    """Safe decimal arithmetic: numbers, + - * / ( ) only."""
    import ast
    import operator as op
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.USub: op.neg, ast.UAdd: op.pos}

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return Decimal(str(n.value))
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.operand))
        raise ValueError("only numbers and + - * / ( ) are allowed")

    try:
        clean = expression.replace(",", "").replace("£", "").replace("GBP", "").replace("$", "")
        val = ev(ast.parse(clean, mode="eval"))
        return {"expression": expression, "label": label, "result": str(val.normalize() if val == val.to_integral() else val.quantize(Decimal("0.0001")).normalize())}
    except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError) as exc:
        return {"expression": expression, "error": str(exc)}


def _block_to_dict(b) -> dict:
    if isinstance(b, dict):
        return b
    t = getattr(b, "type", "?")
    if t == "text":
        return {"type": "text", "text": b.text}
    if t == "tool_use":
        return {"type": "tool_use", "name": b.name, "input": b.input}
    if t == "thinking":
        return {"type": "thinking", "thinking": (getattr(b, "thinking", "") or "")[:20000]}
    return {"type": t}


def _redact(messages: list) -> list:
    """Keep the trace readable: drop base64 payloads, keep text."""
    out = []
    for m in messages:
        content = m.get("content")
        if isinstance(content, str):
            out.append({"role": m["role"], "content": content})
            continue
        parts = []
        for c in content or []:
            if isinstance(c, dict) and c.get("type") in ("image", "document"):
                parts.append({"type": c["type"], "note": "binary attachment omitted from trace"})
            else:
                parts.append(_block_to_dict(c))
        out.append({"role": m["role"], "content": parts})
    return out
