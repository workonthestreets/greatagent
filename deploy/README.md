# Hosting the voice line on Railway

The phone line (`voice/`, which hands each call to `deskagent` unchanged) runs as one Railway
service with a fixed `https://` address, so ElevenLabs reaches it without a laptop tunnel.
A second service runs Mailpit as the demo inbox.

## Live now: no need to build this again

- Voice line: `https://voice-production-ef21.up.railway.app`. `GET /health` returns
  `{"ok":true,"agent":"deskagent"}`.
- Railway project `greatagent-voice` has 2 services: `voice` (volume at `/data`) and `mailpit`
  (demo inbox, behind a password). Ask Kash for access.
- The "Delivery desk - DEMO" agent's tools (`report_delivery_issue`, `get_case_update`) and the
  workspace post-call webhook all point at the voice line. A test call returned `200` on
  `/voice/tool` and `/voice/update`. The laptop tunnel is no longer used.
- It was deployed with the Railway CLI (`railway up` from a checkout), not GitHub-connect, so
  **merging to `main` does not redeploy it**. Redeploy with `railway up` from an up-to-date `main`.

The steps below are how it was set up, for a rebuild or a second environment.

## 1. Voice service

1. Railway → **New Project** → **Deploy from GitHub repo** → `workonthestreets/greatagent`, branch `main`.
2. Service → **Settings** → **Config-as-code** → path `/deploy/railway.json`. This sets the
   Dockerfile (`deploy/Dockerfile`), the `/health` check and restart on failure.
3. Service → right-click → **Attach volume** → mount path `/data`. Cases, call logs and sent
   emails land there and survive a redeploy.
4. Service → **Variables**, set these by name (values come from your own accounts):

   | Name | What |
   | --- | --- |
   | `APP_ANTHROPIC_API_KEY` | your Anthropic key; deskagent uses it |
   | `VOICE_TOOL_SECRET` | a long random string; ElevenLabs sends it on every tool call |
   | `ELEVENLABS_WEBHOOK_SECRET` | from ElevenLabs → post-call webhook settings |
   | `VOICE_AGENT` | `deskagent` |
   | `VOICE_DESK_MODEL` | `claude-sonnet-5-5` |
   | `VOICE_DESK_MAX_PER_HOUR` | `20` |
   | `SEND_EMAIL` | `1` (needs the Mailpit service below) |
   | `SMTP_HOST` | `mailpit.railway.internal` |
   | `SMTP_PORT` | `1025` |

   `VOICE_SHIPMENT_DATA`, `VOICE_CASES_DIR`, `VOICE_LOG_DIR` and `OUTBOX_SENT_DIR` are already
   set in the image; set them only to override. `ELEVENLABS_API_KEY` is not needed on Railway:
   only `setup_agent` uses it, from your laptop (step 3).
   If the logs show `Permission denied` under `/data`, add `RAILWAY_RUN_UID=0` (Railway
   volumes are owned by root; the image runs as a non-root user).
5. Service → **Settings** → **Networking** → **Generate Domain**.
6. Check it: `curl https://<domain>/health` → `{"ok": true, "agent": "deskagent"}`.

## 2. Mailpit service (demo inbox)

1. In the same project → **New** → **Docker Image** → `axllent/mailpit`.
2. Name the service exactly `mailpit`, so the voice service reaches it at
   `mailpit.railway.internal:1025` over Railway's private network. Don't expose port 1025 publicly.
3. Variables: `MP_UI_AUTH` = `<user>:<password>`. The inbox is public, so it needs a password.
4. Settings → Networking → **Generate Domain** on port `8025`. Open it, log in, and emails
   from the agent appear there.

## 3. Point ElevenLabs at Railway

From the repo root on your laptop, with the same `VOICE_TOOL_SECRET` as Railway and your
ElevenLabs key in the env file:

```bash
uv run --env-file <env> python -m voice.setup_agent --public-url https://<domain>
```

This re-points the demo agent's `report_delivery_issue` tool at `https://<domain>/voice/tool`.
Then, in ElevenLabs → workspace settings → post-call webhook, set the URL to
`https://<domain>/voice/post-call`.

## Roll back to the laptop tunnel

```bash
uv run --env-file <env> uvicorn voice.app:app --port 8010
cloudflared tunnel --url http://localhost:8010
uv run --env-file <env> python -m voice.setup_agent --public-url https://<tunnel-url>
```

Then set the post-call webhook back to `https://<tunnel-url>/voice/post-call`. The Railway
service can stay up; ElevenLabs only calls whichever URL `setup_agent` set last.

## Run it locally in Docker

```bash
docker compose -f deploy/docker-compose.yml up --build   # voice on :8010, inbox on :8025
```

Keys and secrets come from `.env` at the repo root (never committed), with the names above.

## Live desk on Railway: hub + web

Two more services in the same project build from `main` with their own Dockerfiles:

| Service | Config-as-code | Dockerfile | Serves |
| --- | --- | --- | --- |
| `hub` | `deploy/railway.hub.json` | `deploy/Dockerfile.hub` | `hub.app:app` (`/api`, `/webhooks`, `/mcp`); healthcheck `/api/health` hits the database |
| `web` | `deploy/railway.web.json` | `deploy/Dockerfile.web` | the Vite build of `web/`, served as a single-page app |

Hub variables: everything in `.env.example` under "Live desk" (`SUPABASE_*`, `DATABASE_URL`, `ADMIN_EMAILS`,
`DEMO_PASSWORD`, `HUB_MCP_TOKEN`, `HUB_WEBHOOK_SECRET`, `ANTHROPIC_API_KEY`, `ANTHROPIC_WORKSPACE_ID`) plus
`HUB_PUBLIC_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}` and `DESK_ENGINE=pipeline`.
Web variables (read at build time): `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_DEMO_PASSWORD` and
`VITE_HUB_URL=https://${{hub.RAILWAY_PUBLIC_DOMAIN}}`.

Schema and seed data still come from a laptop against the same Supabase database
(`python -m db.migrate`, `python -m db.seed --reset`, `python -m db.seed_demo`). ElevenLabs webhook tools point at
`https://<hub domain>/webhooks/...` (see `DEMO.md`).
