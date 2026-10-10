# Human to-do: accounts, keys, local setup

Everything below goes into `greatagent/.env` (gitignored). Variable names match `.env.example`.
Items marked **(blocking)** are needed before the first end-to-end agent run; the rest can come later.

## 1. Anthropic (blocking)

- [ ] `ANTHROPIC_API_KEY`: you probably have it already. Make sure the key's workspace has Managed Agents (beta) access: Console → Managed Agents should open without a waitlist.
- [ ] `ANTHROPIC_WORKSPACE_ID`: the workspace ID from the Console URL (`platform.claude.com/workspaces/<this>/...`), or `default` if it's the Default workspace. Used only to build "open trace" links in the dashboard.
- [ ] Optional: set a monthly spend limit in Console → Settings → Limits, since credits are tight.
- [ ] Optional: install the CLI to inspect sessions from the terminal: `brew install anthropics/tap/ant`, then `ant auth login`.

## 2. Supabase (blocking)

- [ ] Create a project at supabase.com (free tier is fine). Pick a region near London. Save the DB password it asks for.
- [ ] From Project Settings → API:
  - `SUPABASE_URL` (https://<ref>.supabase.co)
  - `SUPABASE_ANON_KEY` (public, used by the web app)
  - `SUPABASE_SERVICE_ROLE_KEY` (secret, hub only, never in the web app)
- [ ] From Project Settings → Database → Connection string → **Session pooler** (URI): `DATABASE_URL` (postgres://postgres.<ref>:<password>@...pooler.supabase.com:5432/postgres)
- [ ] Nothing else by hand: the migration script creates tables, roles, RLS policies, the read-only role for the agent, and the demo accounts.

## 3. Google login (needed for the web app login, not for the agent)

- [ ] Google Cloud Console → APIs & Services → OAuth consent screen: External, app name "greatagent", add your team's emails as test users.
- [ ] Credentials → Create OAuth client ID → Web application. Authorized redirect URI: `https://<ref>.supabase.co/auth/v1/callback`.
- [ ] Supabase → Authentication → Providers → Google: paste the client ID and secret, enable.
- [ ] Supabase → Authentication → URL Configuration: Site URL `http://localhost:3000`; add the Vercel URL later.
- [ ] Tell me which Google emails should be **admin** (`ADMIN_EMAILS=a@x.com,b@y.com`). Everyone else who logs in with Google becomes a customer until an admin changes their role. Demo accounts (driver, depot, merchant, coordinator, customer) are created with email + password by the seed script.

## 4. Public URL for the hub (blocking for agent and voice)

Managed Agents and ElevenLabs both call the hub from the internet.

- [ ] `brew install cloudflared`
- [ ] Quick option: `cloudflared tunnel --url http://localhost:8000` prints a random `https://*.trycloudflare.com` URL. Put it in `HUB_PUBLIC_URL`. It changes on every restart; rerun `python -m hub.setup_agent` after a change (it updates the agent's MCP URL).
- [ ] Stable option (if you have a domain on Cloudflare): `cloudflared tunnel login`, create a named tunnel, point e.g. `hub.yourdomain.com` at `localhost:8000`.
- [ ] Alternative: deploy the hub to Railway or Fly instead of the laptop (account needed; I can add a Dockerfile).

## 5. Shared secrets (I'll generate these unless you want your own)

- [ ] `HUB_MCP_TOKEN`: bearer token the agent uses to call `/mcp` (stored in an Anthropic vault, never in prompts).
- [ ] `HUB_WEBHOOK_SECRET`: header value ElevenLabs sends to `/webhooks/*`.
- Generate with `openssl rand -hex 32`.

## 6. ElevenLabs (when the hub is up)

- [ ] In your existing ElevenLabs agent → Tools → add **webhook (server) tools** pointing at `HUB_PUBLIC_URL`:
  - `ask_agent`: POST `/webhooks/ask_agent`, body `{caller_phone, case_id?, request}`
  - `lookup_shipment`: POST `/webhooks/lookup_shipment`, body `{order_id}`
  - `get_case_status`: POST `/webhooks/get_case_status`, body `{case_id}`
  - `get_latest_update`: POST `/webhooks/get_latest_update`, body `{case_id}`
  - Each one: header `X-Hub-Secret: <HUB_WEBHOOK_SECRET>`
- [ ] Alternatively give me `ELEVENLABS_API_KEY` + `ELEVENLABS_AGENT_ID` and I'll register the tools by script.
- [ ] Make sure the caller's phone number reaches the tool (system variable `system__caller_id` for phone calls), so callers map to accounts.

## 7. Vercel (optional, only for a public web app)

- [ ] Account, then `npm i -g vercel` and `vercel login`. Otherwise the web app runs locally on `localhost:3000`.
- [ ] After deploying, add the Vercel URL to Supabase redirect URLs (step 3).

## 8. Local tooling

- [ ] Already there: Python 3.14, Node 24, uv, Docker.
- [ ] `brew install cloudflared` (step 4).
- [ ] Optional: `brew install supabase/tap/supabase` (not required; migrations run from Python).

## Order of operations

1. Steps 1, 2, 5 → I can run the migration, seed, and one agent session against Supabase.
2. Step 4 → the agent can actually call our tools.
3. Steps 3 and 6 → login and voice.
4. Step 7 → only if we demo from a public URL.
