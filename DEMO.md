# Demo

The 60-second video (`demo/demo.mp4`) shows the **live desk**: a customer phones the ElevenLabs voice agent, our agent works the case, a coordinator approves the drafted messages in `/ops`, and the caller hears the approved update. All data is fictional, and messages land in the parties' portals in our demo app. Nothing reaches a real carrier or customer.

The live desk can run two engines (`DESK_ENGINE`):

| Engine | What runs | Status |
|---|---|---|
| `pipeline` | The evaluated `deskagent` pipeline: Claude planner → policy lint → independent Claude reviewer. This is the same code the Reality Test runs (`run.py`). | Tested end to end locally: `tests/test_pipeline_driver.py`, plus real runs in `demo/recorded/`. |
| `managed` | A Claude Managed Agents session per case, calling the hub's MCP tools (`hub/driver.py`). | Built by Andrey; first live run pending. |

Either way, outbound messages wait in the **Approvals** queue (`AGENT_APPROVAL_TOOLS=send_message`) until a coordinator clicks Approve.

## Setup (once)

Follow `hub/README.md` (Supabase project, `.env`, migrate, seed), then:

```bash
# .env additions for the demo
DESK_ENGINE=pipeline                 # or managed
DEMO_CUSTOMER_PHONE=+44...           # the phone you call from; maps the caller to the demo customer
HUB_PUBLIC_URL=https://<id>.ngrok-free.app

.venv/bin/uvicorn hub.app:app --port 8000      # terminal 1
ngrok http 8000                                # terminal 2 (cloudflared works too)
cd web && npm run dev                          # terminal 3, http://localhost:3000
```

ElevenLabs server tools: `ask_agent`, `get_latest_update`, `get_case_status` and `lookup_shipment`, each a POST to `HUB_PUBLIC_URL/webhooks/<name>` with the header `X-Hub-Secret`. Pass `caller_phone` from `system__caller_id`. If the call comes from the web widget with no phone number, pass `case_id: "D103"`. The hub will then treat the caller as unidentified, and the agent will answer only through the verified portal.

## Before each take

```bash
.venv/bin/python -m db.seed_demo --wake D101   # resets D103 + D101 with times relative to now; works D101 (fraud) in advance
```

D103's change cutoff is about 45 minutes after seeding (printed by the script), so record within that window.

## The take (≤ 60 s)

| Time | Screen | Say |
|---|---|---|
| 0–6 s | `/ops` case list | "Delivery desks run on calls and messages. Our agent decides the next safe step, and hands over when it can't safely act." |
| 6–20 s | Phone call | Caller: "Hi, it's Vessa Lorne. Has my delivery DL-103 been moved? I can't be home this afternoon." Voice: "I've passed this to the desk under case D103." |
| 20–40 s | `/ops` → D103 → Agent live log, then Approvals | The planner decides, the independent reviewer approves, and two drafts wait for approval: an email to dispatch before the cutoff, and a portal message saying "not confirmed yet". Click **Approve**. |
| 40–50 s | Phone | "Any news?" The voice reads the approved message ("…the change is not confirmed yet…"). |
| 50–60 s | `/ops` → D101 | "When an email asks for a refund to new bank details, it pays nothing, hands it to a human, and still updates the customer. Tools are simulated: 'sent' means delivered to a portal in our demo app." |

A typical run takes 30–70 s (the planner plus reviewer, each calling Claude). Cut the wait in the edit.

## Fallbacks

1. **Voice fails:** log in as `customer@greatagent.demo` and type the same question in the portal. It takes the same path through `/api/cases/D103/messages`.
2. **Supabase or web app fails:** show the recorded real runs in `demo/recorded/D103` and `demo/recorded/D101`. Each has `ANSWER.md`, `REASONING.md`, `trace.json`, the input the agent saw (`index.md`, `history.md`) and a DB export (`live_desk_db.json`). These are recorded output from 10 Oct 2026 on local Postgres, not a live execution.
3. **Last resort, no hub:** run `python3 run.py stress_cases --only 101,103 --out demo/run && python3 viewer.py demo/run` (CLI engine, same pipeline), then open `demo/run/index.html`.

## Compress the recording

```bash
ffmpeg -i take.mov -vf "scale='min(1920,iw)':-2" -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -c:a aac -b:a 96k demo/demo.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 demo/demo.mp4     # must be <= 60
```

## Local check without Supabase

```bash
docker run -d --name greatagent-pg -e POSTGRES_PASSWORD=postgres -p 54329:5432 postgres:16
export DATABASE_URL=postgresql://postgres:postgres@localhost:54329/postgres
.venv/bin/python -m db.migrate --local && .venv/bin/python -m db.seed --reset --local
.venv/bin/python tests/test_pipeline_driver.py          # scripted Claude, no API cost
```
