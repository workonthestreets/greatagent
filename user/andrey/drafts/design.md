# High-level design

One backend hub, Supabase as the DB, the agent on Claude Managed Agents. The ElevenLabs voice agent already exists and calls our agent as a tool.

```text
 ElevenLabs voice ──webhook──┐
 Web app (portal + ops) ─────┤──▶  hub (FastAPI, Python)  ──▶  Supabase (Postgres + Auth + Realtime)
                             │        ├─ /webhooks/*   voice tools
                             │        ├─ /api/*        web app
                             │        ├─ /mcp          agent's tools  ◀── Managed Agent session
                             │        └─ session driver: start/continue sessions, mirror events
```

## 1. DB: Supabase

One service gives Postgres, Google login, live updates for dashboards, and hosting.

Tables:

- `users`: id, role, and links to what the user may see (customer_id, driver_id, merchant_id, depot_id)
- `customers`, `shipments`
- `cases`: includes `session_id`, so each case maps to one agent session
- `case_events`: timeline of calls, portal messages, depot notes
- `actions`: what the agent did or proposed; status `pending_approval` / `done` / `rejected`
- `agent_events`: mirror of the session's events
- `agent_runs`: cost and status per session

Seed it from the existing cases so it holds realistic data.

## 2. Accounts and access

Everyone logs in (Google via Supabase Auth, plus a few pre-made demo accounts per role for the demo). What a user sees depends on their role, enforced in the DB with Supabase row-level security, so the web app and the hub can't leak rows by mistake.

Roles follow `delivery-roles-and-actors.md`:

| Role | Sees | Can do |
|---|---|---|
| **admin** (us) | everything: all cases, ops dashboard, agent events, costs, approvals | approve/reject actions, edit data, impersonate a role for the demo |
| **desk coordinator** | all cases and the ops dashboard | approve/reject agent actions, message any party |
| **customer** | own shipments and own cases | open a request, upload evidence, reply in the case thread |
| **driver / collection crew** | own assigned stops for today | report attempt outcome, add notes/photos |
| **depot / pickup point** | shipments at their site | confirm holds, receipts, exceptions |
| **merchant** | cases on their orders | answer approval requests (refund, replacement, exchange) |

Agent replies addressed to a party appear in that party's view. The agent's tools also respect roles: `send_message(to=driver)` goes to that driver's inbox, not to everyone.

## 3. Agent tools (`/mcp` on the hub)

- Read: `read_sql` (read-only DB role, timeout, row limit), `get_case`, `search_docs`
- Write (typed, mirroring today's `DeskTools`): `send_message`, `escalate_to_human`, `schedule_follow_up`, `record_case_note`, `update_case_status`, `submit_decision`
- Every write runs through `deskagent/policy.py`, so today's hard rules still apply (no gate codes, no unapproved refunds, ...)
- Permissions: reads always allowed; risky writes (refunds, customer-facing sends if we want) set to always ask, so they land in `actions` as `pending_approval` for an admin or coordinator

## 4. Agent: Managed Agent

- System prompt ported from `deskagent/prompts.py`; company docs (policies, playbooks) mounted as files
- One case maps to one session. A new case starts a session; new info (call, portal, depot, driver) goes into the same session as a new message
- Planner/reviewer split dropped at first; policy lint plus approvals cover safety. Add a reviewer pass later if budget allows
- Each session gets a budget cap; Sonnet 5.5 while building

## 5. Session driver (inside the hub)

Starts or continues sessions, streams their events into `agent_events`, answers approvals when someone clicks Approve/Reject. The only plumbing we own, roughly 100 lines.

## 6. ElevenLabs voice: our agent as a tool

The voice agent calls the hub through ElevenLabs server tools (webhooks to `/webhooks/*`).

- `ask_agent(case_or_caller, request)`: hands the request to our agent (starts or continues the case's session). An agent run takes tens of seconds, so the tool returns quickly with "logged, case #123" and the agent works in the background. The voice agent tells the caller they'll get an update by SMS/email
- `lookup_shipment(order_id)`, `get_case_status(case_id)`: fast, straight from the DB, for answers during the call
- `get_latest_update(case_id)`: the caller can ask "any news?" and hear the agent's latest decision

Caller identity: match the phone number to `users`, so a caller gets the same access as their account.

## 7. Web app (Next.js or Vite, on Vercel)

One app; after login the user lands on what their role allows.

- `/ops` (admin, coordinator): live case list; per-case timeline (case events plus agent tool calls, updating live); approvals queue; cost per run; link to the Console trace per session; DB table viewer
- `/portal` (customer): my shipments, open a request with attachment, case thread with live agent replies
- `/driver`, `/depot`, `/merchant`: small views listing their items plus a reply/confirm form; reuse the same components

Submitting a request from any view takes the same path as `ask_agent`.

## 8. Evals (cheap)

- **Basic:** 3–5 scripted scenarios on a reset seed DB, checked against the DB itself (an escalation exists, no refund sent, decision is `wait`). Free to grade; run after prompt/tool changes
- **Hard:** ~5 cases from `stress_cases/`, graded by the existing judge in `eval.py`. Run once or twice, not in a loop

## Hosting

Hub on a laptop behind a `cloudflared` tunnel (ElevenLabs and Managed Agents both need a public URL), or Railway/Fly if that's a problem. Web app on Vercel, DB on Supabase.

## Build order

1. Supabase schema, roles and RLS, seed data
2. Hub `/mcp`, then one agent session end to end
3. Session driver and event mirror
4. ElevenLabs webhooks
5. Web app: `/ops` first, then `/portal`, then the role views
6. Basic eval

Steps 4 and 5 can run in parallel once step 3 works.
