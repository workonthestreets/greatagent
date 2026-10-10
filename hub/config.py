"""Hub settings, read once from the environment (.env is loaded by deskagent's loader)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from deskagent.llm import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "hub" / ".agent_state.json"   # agent/environment/vault IDs from setup_agent

load_dotenv(ROOT / ".env")


def _bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    database_url: str = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:54329/postgres")
    supabase_url: str = os.environ.get("SUPABASE_URL", "").rstrip("/")
    supabase_anon_key: str = os.environ.get("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    hub_public_url: str = os.environ.get("HUB_PUBLIC_URL", "").rstrip("/")
    mcp_token: str = os.environ.get("HUB_MCP_TOKEN", "")
    webhook_secret: str = os.environ.get("HUB_WEBHOOK_SECRET", "")
    workspace_id: str = os.environ.get("ANTHROPIC_WORKSPACE_ID", "default")
    agent_model: str = os.environ.get("AGENT_MODEL", "claude-sonnet-5-5")
    session_budget_cents: int = int(os.environ.get("AGENT_SESSION_BUDGET_CENTS", "150"))
    # Tools that pause for a human Approve/Reject in /ops (comma-separated MCP tool names).
    approval_tools: tuple = tuple(t.strip() for t in os.environ.get("AGENT_APPROVAL_TOOLS", "send_message").split(",") if t.strip())
    # Evals and unattended runs: approve paused calls automatically (policy BLOCKs still apply).
    auto_approve: bool = _bool("AGENT_AUTO_APPROVE")
    # Local testing without Supabase Auth: trust an X-Dev-User email header on /api.
    dev_auth: bool = _bool("HUB_DEV_AUTH")
    # Which agent works the cases: "managed" (Managed Agents session, hub/driver.py) or "pipeline" (the evaluated
    # deskagent planner -> lint -> reviewer, hub/pipeline_driver.py).
    engine: str = os.environ.get("DESK_ENGINE", "managed").strip().lower()

    @property
    def mcp_url(self) -> str:
        return f"{self.hub_public_url}/mcp"

    def trace_url(self, session_id: str) -> str:
        return f"https://platform.claude.com/workspaces/{self.workspace_id}/sessions/{session_id}"


settings = Settings()


def agent_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_agent_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
