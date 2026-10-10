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
# .env additions for the demo (no comments on value lines: the loader keeps everything after '=')
# engine: pipeline or managed
DESK_ENGINE=pipeline
# set before db.seed; maps the caller to the demo customer
DEMO_CUSTOMER_PHONE=+447700900103
HUB_PUBLIC_URL=https://<id>.ngrok-free.app

.venv/bin/uvicorn hub.app:app --port 8000      # terminal 1
ngrok http 8000                                # terminal 2 (cloudflared works too)
cd web && npm run dev                          # terminal 3, http://localhost:3000
```

### Voice line on Railway (Kashif) → hub mirror

The live voice line (`https://voice-production-ef21.up.railway.app`, see `voice/README.md` and `deploy/README.md`) decides each call with `deskagent` itself, the same planner → lint → reviewer pipeline. The caller hears only fixed templates. After deciding, the voice line posts the finished case to the hub's `POST /webhooks/record_case` (spec: `voice/HUB_MIRROR.md`).

The hub records the call, the reviewed messages and a staff note in `/ops`, and doesn't run its own agent again. It ignores a call it has already recorded (keyed on `voice_case_id`). Phone cases therefore show up already decided, with no approval step; the Approvals step is shown with D103.

To turn the mirror on, set these on the Railway `voice` service:
- `HUB_URL`: the hub's public URL, either the laptop tunnel or the Railway hub once it's deployed
- `HUB_WEBHOOK_SECRET`: the hub's value

### ElevenLabs agent → hub directly (alternative)

Use this if the voice line is down.

Add two **Webhook tools** to the agent. Each one: method POST, response timeout 10 s, header `X-Hub-Secret` of type **Secret**, set to `HUB_WEBHOOK_SECRET`.

| Tool | URL | Body parameters (all type "LLM prompt") |
|---|---|---|
| `ask_agent` | `HUB_PUBLIC_URL/webhooks/ask_agent` | `request`: what the caller wants, in their own words. `case_id`: the tracking or case reference they give, such as DL-103 (blank if none). `caller_phone`: the phone number on their account, as they say it. |
| `get_latest_update` | `HUB_PUBLIC_URL/webhooks/get_latest_update` | `case_id`: the same reference. `caller_phone`: the same number. |

System prompt additions:

> Ask for the caller's name, their tracking reference and the phone number on their account. Call `ask_agent` once with their request and read its `say` field back word for word. When they ask for news, call `get_latest_update` and read `say` word for word. Never promise refunds, dates or outcomes yourself.

How the hub handles these calls:
- **References.** It accepts a tracking reference (`DL-103`) or a case number (`D103`).
- **Caller matching.** It matches the caller by the last 10 digits of the phone number. On a real phone line you can pass `system__caller_id` instead of asking.
- **Unidentified callers** can't be matched to an account. Their request is still logged on the case, but "any news" reads back only messages addressed to that caller, so an unmatched caller hears none of the desk's messages to the customer.
- **While the agent is still working, or a draft is waiting for approval,** "any news" says exactly that.

For the demo, set `DEMO_CUSTOMER_PHONE=+447700900103` before `db.seed`. That's an Ofcom drama number, so it's fictional. The presenter says "07700 900103" when asked.

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

## The two screens

The web app (`web/`) is styled on the Meridian design system (`web/design/meridian/`, licensed for use in this project; fonts Fraunces and Inter from Google Fonts, Lucide icons inline). Each view has one pastel band as its focal point:

- **Desk** (`coordinator@greatagent.demo`): headline, the six desk figures, the approvals band (charcoal draft cards with Approve / Reject, shown only while drafts are pending), the case list, and the case detail with the decision panel. The panel names the decision in words: Acting, Asking for information, Handed to a human, Holding, nothing to send, or Declined, with the "Not doing" and "Next" lines under it.
- **Customer portal** (`customer@greatagent.demo`, shown at phone width next to the desk): headline, the band with the latest desk message (the same text the voice line reads out) and a Reply button, shipments, the case list and the thread.

The login page carries both entry points as two cards on its band ("Sign in as coordinator", "Sign in as customer").

### Swipe approvals, medals, coins and merch (staff)

Drafts waiting for approval are a deck of charcoal cards on the desk: drag the top card right to approve, left to reject (the reason field on the card goes to the agent), or use the round check / x buttons and the arrow keys. Every decision earns coins (15 for an approval, 10 for a rejection with a reason, 5 without) and can unlock a medal: First call, Steady hand, Desk veteran, Gatekeeper, Clean desk, Early bird. The **Rewards** page shows the balance, the medals with progress, the merch shop (coins buy fictional Rivet merch: cap, mug, socks, tote, hoodie, bottle) and past orders; admins also see the team table. Coins and medals are for staff accounts only; nothing is cash.

Setup once per database: `python -m db.migrate` (applies `db/migrations/002_rewards.sql`) and `python -m db.seed_rewards` (120 welcome coins per staff profile, idempotent).

### One portal per role

- **Customer**: the thread with the desk, shipments, new requests.
- **Driver**: stops on the route with "Out for delivery", "Attempted", "Delivered" (each writes the shipment status and a case event, and wakes the agent) and "Report a problem".
- **Depot**: shipments at the site with "Arrived", "Ready for collection", "Collected".
- **Merchant**: cases on the merchant's orders with "Approve replacement", "Approve refund", "Decline" plus a note; the decision lands on the case and the agent takes it from there.

Demo accounts: `driver@`, `depot@`, `merchant@greatagent.demo` (same demo password).

### Preview without Supabase

```bash
cd web && npm run preview:demo      # http://127.0.0.1:3100/?view=login | ops | ops-hold | party | rewards | driver | depot | merchant
web/preview/shoot.sh [out_dir]      # headless-Chrome screenshots at 1440 and 390 px
```

The preview swaps `src/lib.ts` for `preview/mock-lib.ts` (fixture cases D103, D101 and a held D104), so it renders both sides with no backend and no sign-in. Use it to rehearse the take or to check a styling change.

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
