# Design implementation status

Tracks `design.md` against what's in the repo. Run guide: `hub/README.md`. Human setup: `todo-human.md`.

Last updated: 2026-10-10.

## Summary

All parts of the design are written and pushed. Everything that doesn't need external accounts was tested locally against Postgres in Docker. **No end-to-end agent run has happened yet**: the agent needs the hub at a public URL plus real keys (Anthropic, Supabase), so no Claude credits have been spent on it.

| Part | Status | Where |
|---|---|---|
| 1. DB (Supabase) | Built, tested locally | `db/` |
| 2. Accounts and access | Built, RLS tested locally; Google login not tested | `db/migrations/001_schema.sql`, `web/src/Login.tsx` |
| 3. Agent tools (`/mcp`) | Built, tested through a real MCP client | `hub/mcp_tools.py` |
| 4. Managed Agent | Setup script written, not run | `hub/setup_agent.py`, `hub/prompts.py` |
| 5. Session driver | Written, not run against the API | `hub/driver.py` |
| 6. ElevenLabs voice tools | Built, tested locally; not yet wired into ElevenLabs | `hub/webhooks.py` |
| 7. Web app | Builds and type-checks; not run against Supabase | `web/` |
| 8. Evals | Basic eval written, not run; hard eval not started | `hub/eval_basic.py` |

## Details

### 1. DB
- Tables: `profiles`, `admin_emails`, `cases`, `case_parties`, `shipments`, `case_events`, `actions`, `agent_events`, `agent_runs`. Realtime enabled on the live tables.
- `db/migrate.py` applies the schema (can be re-run safely); `--local` adds stand-ins for Supabase's auth schema so it runs on plain Postgres.
- `db/seed.py` loads the 50 public Delivery cases cut at the escalation point (50 cases, 100 events, 41 shipments, 142 case parties) plus demo accounts.
- Tested locally: applies twice cleanly, seed loads.

### 2. Accounts and access
- Roles: admin, coordinator, customer, driver, depot, merchant (carriers, brokers and specialist teams are grouped under merchant).
- Row-level security: staff see everything; other roles see only cases they are a party to, and never staff-only notes, agent actions or agent events.
- New Google sign-ups become customers; emails in `ADMIN_EMAILS` become admins.
- Demo accounts `<role>@greatagent.demo`, each linked to the party that appears most often for that role. All share `DEMO_PASSWORD`.
- Tested locally: admin sees 50 cases; customer, driver and depot 1 each; merchant 5; no account sees nothing.
- Not tested: Google login (needs the OAuth client from `todo-human.md` step 3).

### 3. Agent tools
- `get_case`, `read_sql`, `search_docs`, `send_message`, `escalate_to_human`, `schedule_follow_up`, `record_case_note`, `update_case_status`, `submit_decision`.
- `read_sql`: one SELECT, read-only transaction, separate DB role with no access to profiles or auth, 5s timeout, 200 rows max.
- Every write is checked with `deskagent/policy.py`; BLOCK rules (links, card numbers) reject the call.
- `/mcp` requires a bearer token; the agent gets it from an Anthropic vault.
- Tested: all 9 tools through an MCP client. A payment link was blocked; reading profiles, DELETE and a data-modifying CTE were refused.
- `search_docs` only covers `hub/docs/` (currently the roles-and-actors doc). Add company docs there.

### 4. Managed Agent
- Prompt: live-desk intro plus the operating manual from `deskagent/prompts.py`.
- Model Sonnet 5.5, session budget $1.50, web/bash/file tools off (only our MCP tools).
- `send_message` waits for Approve/Reject in `/ops` (`AGENT_APPROVAL_TOOLS`).
- Planner/reviewer split from the CLI pipeline is not used here; policy checks plus approvals cover safety for now.
- Not run yet: needs `HUB_PUBLIC_URL`, `HUB_MCP_TOKEN` and an Anthropic key.

### 5. Session driver
- One session per case; new info (portal, voice, staff) is sent to the same session.
- Mirrors every session event into `agent_events`; paused tool calls become `pending_approval` actions; records run status and cost.
- Not run against the real API yet. Most likely to need fixes on first run: event field names, approval round-trip, cost lookup.

### 6. ElevenLabs voice
- `/webhooks/ask_agent`, `lookup_shipment`, `get_case_status`, `get_latest_update`, all requiring `X-Hub-Secret`.
- `ask_agent` returns at once with a case number; the agent works in the background.
- Callers are matched to accounts by phone; `get_latest_update` only reads out messages addressed to that caller.
- Tested locally: secret check, lookups, caller privacy. Not yet registered as tools in ElevenLabs (`todo-human.md` step 6).

### 7. Web app
- Vite + React + Supabase JS. Login with Google, email/password, or one-click demo accounts.
- Admin/coordinator: stats, approvals queue, live case list, case detail with timeline, actions, agent live log, cost and trace link, re-run button, message box.
- Customer/driver/depot/merchant: own shipments and cases, case thread, reply box; customers can open new requests.
- Built and type-checked; never run against Supabase. No deploy yet (Vercel optional).

### 8. Evals
- `hub/eval_basic.py`: 3 scenarios checked against the DB (photo evidence on case 021, fake pre-approved refund with bank details on 001, volunteered gate code on 002). Auto-approves paused calls; each session capped by the budget.
- Hard eval: not started. Plan: ~5 cases from `stress_cases/` graded by the judge in `eval.py`, run once or twice.

## Next steps

1. Human: `todo-human.md` steps 1, 2, 4, 5 (Anthropic, Supabase, cloudflared, secrets).
2. Migrate and seed Supabase; start hub and tunnel; run `hub.setup_agent`.
3. One agent run on one case from `/ops`; fix whatever the driver gets wrong.
4. `hub.eval_basic` (about $1–5 total).
5. Google login and web app against Supabase; ElevenLabs tools.
6. Hard eval; deploy web app if we demo from a public URL.

## Known gaps

- Demo password is shared and printed by the seed script; change it before anything is public.
- Party roles come from a keyword heuristic on case records, so some carriers show up as "merchant".
- Shipment status and ETA are placeholders (`in_progress`, no ETA); the public cases don't carry them.
- Attachments are listed on the case but not shown to the agent or in the web app.
- The local Docker container `greatagent-pg` is still running (`docker rm -f greatagent-pg` to remove).
