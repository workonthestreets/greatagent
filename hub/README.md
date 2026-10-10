# Live desk: hub + Managed Agent + Supabase + web app

Design: `user/andrey/drafts/design.md`. Accounts and keys to create first: `user/andrey/drafts/todo-human.md`.

```text
ElevenLabs ──/webhooks──┐
Web app ─────/api───────┤──▶ hub (FastAPI) ──▶ Supabase Postgres (RLS per role)
Managed Agent ──/mcp────┘        └─ driver: one agent session per case, events mirrored to agent_events
```

| Path | What |
|---|---|
| `db/migrations/001_schema.sql` | tables, roles, row-level security, agent read-only role, realtime |
| `db/seed.py` | loads the 50 public cases (cut at escalation) and demo accounts per role |
| `hub/mcp_tools.py` | the agent's tools: `get_case`, `read_sql`, `search_docs`, `send_message`, `escalate_to_human`, `schedule_follow_up`, `record_case_note`, `update_case_status`, `submit_decision` |
| `hub/driver.py` | starts/continues sessions, approvals, cost tracking |
| `hub/api.py`, `hub/webhooks.py` | web app API and ElevenLabs tools |
| `hub/setup_agent.py` | creates/updates the agent, environment and vault |
| `hub/eval_basic.py` | 3 end-to-end scenarios graded by DB checks |
| `web/` | Vite + React app: `/ops` for admin/coordinator, own-items view for customer/driver/depot/merchant |

## First run

```bash
uv venv .venv && uv pip install --python .venv/bin/python -r hub/requirements.txt
cp .env.example .env        # fill in per todo-human.md

.venv/bin/python -m db.migrate               # schema on Supabase
.venv/bin/python -m db.seed --reset          # cases + demo accounts

.venv/bin/uvicorn hub.app:app --port 8000    # terminal 1
cloudflared tunnel --url http://localhost:8000   # terminal 2 -> put the URL in HUB_PUBLIC_URL
.venv/bin/python -m hub.setup_agent          # rerun whenever HUB_PUBLIC_URL changes (restart the hub too)

cd web && cp .env.example .env && npm install && npm run dev   # http://localhost:3000
```

Demo logins: `admin@greatagent.demo`, `coordinator@…`, `customer@…`, `driver@…`, `depot@…`, `merchant@…` with `DEMO_PASSWORD` (one-click buttons on the login page).

## Try it

- In `/ops`, open a case and click **Ask agent to re-assess**. Watch the agent's live log; `send_message` calls wait in **Approvals**.
- Log in as the customer and write on their case: the agent wakes in the same session with the new message.
- `.venv/bin/python -m hub.eval_basic` runs the 3 scenarios (auto-approves; each session is capped by `AGENT_SESSION_BUDGET_CENTS`).

## Local testing without Supabase

```bash
docker run -d --name greatagent-pg -e POSTGRES_PASSWORD=postgres -p 54329:5432 postgres:16
DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres .venv/bin/python -m db.migrate --local
DATABASE_URL=... .venv/bin/python -m db.seed --reset --local
DATABASE_URL=... HUB_DEV_AUTH=1 HUB_MCP_TOKEN=x HUB_WEBHOOK_SECRET=y .venv/bin/uvicorn hub.app:app --port 8000
```

With `HUB_DEV_AUTH=1`, `/api` accepts `X-Dev-User: <email>` instead of a Supabase token.

## Engines

`DESK_ENGINE` picks what works a case when it is woken (by `/api`, `/webhooks` or a re-assess click):

- `managed` (default): one Managed Agents session per case, using the `/mcp` tools (`hub/driver.py`). Needs `hub.setup_agent` and a public `HUB_PUBLIC_URL`.
- `pipeline`: the evaluated `deskagent` pipeline (planner → policy lint → independent reviewer, the same code `run.py` uses for the Reality Test), in `hub/pipeline_driver.py`.
  - It renders the case from the database in the CLI's case format and plans it.
  - It then carries out the approved plan through the same desk tools in `hub/mcp_tools.py`.
  - Sends wait in Approvals like the managed engine, and the agent live log shows the planner, reviewer and tool steps.
  - Every run keeps its input plus `ANSWER.md` / `REASONING.md` / `trace.json` under `runs/live/<run>/`.
  - No public URL is needed for the agent itself, only for ElevenLabs.

Demo cases with times relative to now: `python -m db.seed_demo [--wake D101]` (see `DEMO.md`). Pipeline engine test against local Postgres: `python tests/test_pipeline_driver.py`.
