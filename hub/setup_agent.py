"""Create or update the Managed Agent, its environment and the vault holding the /mcp bearer token.
Rerun whenever HUB_PUBLIC_URL, the prompt, the model or the tool list changes. IDs go to hub/.agent_state.json.

    python -m hub.setup_agent
"""
from __future__ import annotations

from .config import agent_state, save_agent_state, settings
from .driver import client
from .mcp_tools import mcp
from .prompts import AGENT_SYSTEM

AGENT_NAME = "greatagent-desk"


def tool_names() -> list[str]:
    return [t.name for t in mcp._tool_manager.list_tools()]


def agent_body() -> dict:
    configs = [{"name": name, "enabled": True,
                "permission_policy": {"type": "always_ask" if name in settings.approval_tools else "always_allow"}}
               for name in tool_names()]
    return dict(
        name=AGENT_NAME,
        model=settings.agent_model,
        system=AGENT_SYSTEM,
        mcp_servers=[{"type": "url", "name": "desk", "url": settings.mcp_url}],
        # Only our MCP tools: no bash, files or web, so the agent can act on the desk only through the hub.
        tools=[{"type": "mcp_toolset", "mcp_server_name": "desk",
                "default_config": {"enabled": False}, "configs": configs}],
    )


def main() -> None:
    if not settings.hub_public_url or not settings.mcp_token:
        raise SystemExit("set HUB_PUBLIC_URL and HUB_MCP_TOKEN in .env first")
    c = client()
    st = agent_state()

    if not st.get("environment_id"):
        env = c.beta.environments.create(
            name="greatagent-desk-env",
            config={"type": "cloud", "networking": {"type": "limited", "allow_mcp_servers": True}},
        )
        st["environment_id"] = env.id
        print(f"environment {env.id}")

    if not st.get("vault_id"):
        st["vault_id"] = c.beta.vaults.create(display_name="greatagent hub").id
        print(f"vault {st['vault_id']}")
    if st.get("credential_url") != settings.mcp_url:
        if st.get("credential_id"):   # the server URL on a credential is immutable: archive and recreate
            c.beta.vaults.credentials.archive(credential_id=st["credential_id"], vault_id=st["vault_id"])
        cred = c.beta.vaults.credentials.create(
            vault_id=st["vault_id"], display_name="hub /mcp bearer",
            auth={"type": "static_bearer", "mcp_server_url": settings.mcp_url, "token": settings.mcp_token},
        )
        st["credential_id"], st["credential_url"] = cred.id, settings.mcp_url
        print(f"credential {cred.id} -> {settings.mcp_url}")

    body = agent_body()
    if st.get("agent_id"):
        current = c.beta.agents.retrieve(agent_id=st["agent_id"])
        agent = c.beta.agents.update(agent_id=st["agent_id"], version=current.version, **body)
        print(f"agent {agent.id} updated to version {agent.version}")
    else:
        agent = c.beta.agents.create(**body)
        print(f"agent {agent.id} created (version {agent.version})")
    st["agent_id"], st["agent_version"] = agent.id, agent.version
    save_agent_state(st)
    print(f"tools: {', '.join(tool_names())}; approval needed for: {', '.join(settings.approval_tools) or 'none'}")


if __name__ == "__main__":
    main()
