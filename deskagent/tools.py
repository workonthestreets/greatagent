"""Simulated operational tool layer (the desk's 'APIs').

In a real deployment these would call the messaging gateway, ticketing system and
scheduler. Here they validate inputs, apply the hard policy blocks, return realistic
IDs and record everything to the case trace. Failures can be injected to exercise
recovery paths:
  * DESK_SIM_FAIL_RATE=0.3        -> random transient failures (seeded per case)
  * DESK_SIM_FAIL_CHANNELS=Email  -> channel outage (comma-separated channel names)
"""
from __future__ import annotations

import hashlib
import os
import random
from datetime import datetime, timezone
from typing import List

from .policy import lint_text


class ToolError(Exception):
    def __init__(self, message: str, transient: bool):
        super().__init__(message)
        self.transient = transient


class DeskTools:
    def __init__(self, case_id: str, known_channels: List[str], trace: list):
        self.case_id = case_id
        self.known_channels = known_channels
        self.trace = trace
        self.fail_rate = float(os.environ.get("DESK_SIM_FAIL_RATE", "0") or 0)
        self.down_channels = {c.strip().lower() for c in os.environ.get("DESK_SIM_FAIL_CHANNELS", "").split(",") if c.strip()}
        seed = int(hashlib.sha256(case_id.encode()).hexdigest()[:8], 16)
        self.rng = random.Random(seed)
        self.outbox: list = []
        self.tickets: list = []
        self.followups: list = []
        self.notes: list = []
        self._n = 0

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}-{self.case_id}-{self._n:02d}"

    def _maybe_fail(self, channel: str = ""):
        if channel and channel.lower() in self.down_channels:
            raise ToolError(f"channel '{channel}' is unavailable (gateway outage)", transient=False)
        if self.fail_rate and self.rng.random() < self.fail_rate:
            raise ToolError("messaging gateway timeout (HTTP 504)", transient=True)

    def _log(self, tool, args, result=None, error=None):
        self.trace.append({"type": "tool_call", "phase": "execute", "tool": tool, "input": args,
                           "output": result, "error": error, "at": datetime.now(timezone.utc).isoformat()})

    # ---------------------------------------------------------------- tools
    def send_message(self, to_name: str = "", to_role: str = "", channel: str = "", subject: str = "",
                     body: str = "", **_) -> dict:
        args = {"to_name": to_name, "to_role": to_role, "channel": channel, "subject": subject, "body": body}
        try:
            if not body.strip():
                raise ToolError("empty message body", transient=False)
            if not (to_name or to_role):
                raise ToolError("no recipient", transient=False)
            if not channel:
                raise ToolError("no channel", transient=False)
            blocks = [f for f in lint_text(subject + "\n" + body) if f["level"] == "BLOCK"]
            if blocks:
                raise ToolError("policy block: " + ", ".join(f"{b['rule']}('{b['match']}')" for b in blocks), transient=False)
            self._maybe_fail(channel)
            res = {"status": "sent", "message_id": self._id("MSG"), "channel": channel,
                   "note": "queued on channel" + ("" if channel.lower() in {c.lower() for c in self.known_channels}
                                                  else " (channel not previously used in this case)")}
            self.outbox.append({**args, **res})
            self._log("send_message", args, res)
            return res
        except ToolError as exc:
            self._log("send_message", args, error=str(exc))
            raise

    def escalate_to_human(self, to_name: str = "", body: str = "", priority: str = "normal", subject: str = "", **_) -> dict:
        args = {"queue": to_name or "Desk supervisor", "priority": priority or "normal", "subject": subject, "handover": body}
        res = {"status": "queued_for_human", "ticket_id": self._id("ESC"), "queue": args["queue"], "priority": args["priority"],
               "handover": body}
        self.tickets.append({**args, **res})
        self._log("escalate_to_human", args, res)
        return res

    def schedule_follow_up(self, when: str = "", body: str = "", **_) -> dict:
        args = {"when": when, "check": body}
        res = {"status": "scheduled", "follow_up_id": self._id("FUP"), "when": when or "next working check"}
        self.followups.append({**args, **res})
        self._log("schedule_follow_up", args, res)
        return res

    def record_case_note(self, body: str = "", **_) -> dict:
        res = {"status": "recorded", "note_id": self._id("NOTE")}
        self.notes.append({"note": body, **res})
        self._log("record_case_note", {"note": body}, res)
        return res
