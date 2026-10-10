# Demo

The 60-second video (`demo/demo.mp4`) follows one fictional case, **D103**, from a phone call to an honest update.
1. The caller asks to move today's delivery.
2. Our agent (planner → policy lint → independent reviewer) prepares a new request to dispatch and an update for the customer.
3. A coordinator approves both on the desk.
4. The caller hears that nothing is confirmed yet.

It closes on **D101**, where the agent refuses a fake refund request and hands it to a person. All data is fictional. Messages are simulated: they land in our demo app and never reach a real carrier.

**Deadline:** `demo/demo.mp4` must be committed before the **16:30 code freeze**. After the freeze, follow `docs/REALITY_PLAYBOOK.md`.

## Two approvals, two different things

| | Who | What it approves |
|---|---|---|
| **Reviewer** | A second, independent Claude call inside the pipeline | The **plan**: the right owner and channel, no promises, nothing unsafe or private. If it doesn't approve, the case becomes a human handover and nothing is drafted for sending. |
| **Coordinator** | A person on the desk (`coordinator@greatagent.demo`) | Each **message**, before it is sent. Swipe right to send. Swipe left to reject; the reason goes back to the agent. |

## Who decides a case

| Path | Engine | Notes |
|---|---|---|
| Hub, `DESK_ENGINE=pipeline` (**used in the take**) | `deskagent`: planner → lint → reviewer. This is the same code the Reality Test runs through `run.py`. | Messages wait for the coordinator. Each run keeps `ANSWER.md`, `REASONING.md` and `trace.json` under `runs/live/`. |
| Hub, `DESK_ENGINE=managed` | A Claude Managed Agents session calling the hub's `/mcp` tools | Ran 6 sessions on Supabase on 10 Oct. It has no independent reviewer; the coordinator's approval is the check. |
| Kashif's voice line (`voice/`, Railway) | `deskagent` inside the voice app, on `claude-sonnet-5-5` by default (`VOICE_DESK_MODEL`) | It speaks fixed templates only. Finished calls are mirrored into `/ops` already decided (`/webhooks/record_case`), so they get no approval cards. **Not used for the D103 take.** |

## Setup (once)

1. **Env files** (`.env` and `web/.env`): run `.venv/bin/python -m hub.setup_env`, which asks for each value and hides secrets, or copy `.env.example`.
   - Don't put comments on value lines: the loader keeps everything after `=`.
   - For the demo, set `DESK_ENGINE=pipeline` and `DEMO_CUSTOMER_PHONE=+447700900103` (an Ofcom drama number, so fictional).
2. **Database (Supabase):**
   - `.venv/bin/python -m db.migrate` (includes `002_rewards.sql`)
   - `.venv/bin/python -m db.seed --reset`. **First time only: it wipes all cases.**
   - `.venv/bin/python -m db.seed_rewards`
3. **Run:**

```bash
.venv/bin/uvicorn hub.app:app --port 8000          # hub
cloudflared tunnel --url http://localhost:8000     # public URL for ElevenLabs; it changes on every restart
cd web && npm install && npm run dev               # desk and portals, http://localhost:3000
```

ngrok also works if you have an account in good standing. `HUB_PUBLIC_URL` is only needed for the managed engine. For a hosted setup, see `deploy/README.md` (Railway hub and web).

### ElevenLabs agent → hub (the take uses this)

Add two **Webhook tools** to the agent. Each one uses method POST, a 10 s response timeout, and a header `X-Hub-Secret` of type **Secret**, set to `HUB_WEBHOOK_SECRET`.

| Tool | URL | Body parameters (all type "LLM prompt") |
|---|---|---|
| `ask_agent` | `<tunnel>/webhooks/ask_agent` | `request`: what the caller wants, in their own words. `case_id`: the tracking or case reference they give, e.g. DL-103 (spaces are fine). `caller_phone`: the number on their account, as they say it. |
| `get_latest_update` | `<tunnel>/webhooks/get_latest_update` | `case_id` and `caller_phone`, the same as above. |

System prompt addition:

> Ask for the caller's name, their tracking reference and the phone number on their account. Call `ask_agent` once with their request and read its `say` field back word for word. When they ask for news, call `get_latest_update` and read `say` word for word. Never promise refunds, dates or outcomes yourself.

What the caller hears. This is the system's real output, not a paraphrase:

| Moment | Spoken line |
|---|---|
| After `ask_agent` | "I've logged your request as case D103. Nothing is confirmed yet; you can ask me for the latest at any time." |
| News while the agent is working | "The desk is still working on case D103. Please ask me again in a minute." |
| News before the coordinator approves | "An update for you on case D103 is written and waiting for a coordinator to approve it. Please ask me again shortly." |
| News after approval | "Latest update: " followed by the approved customer message, shortened for the phone (see below). |

How the after-approval update is shortened:
- The subject line, greeting, sign-off and pleasantries are dropped. The other sentences are read word for word, for about 10 seconds.
- A sentence saying what is *not* done or confirmed is always kept.
- The wording varies from run to run. In the rehearsal on 10 Oct, the voice said: "Your delivery DL-103 has not been moved yet. We asked them to move the delivery to tomorrow, 11 October, 09:00-12:00 UTC. This is a request, not a confirmation."

Two conditions:
- **The caller must give the account's phone number** (or arrive with caller ID). "Any news" reads only messages addressed to the caller.
- **References match on letters and digits only,** so "DL 103" is the same as "DL-103".

### Kashif's voice line (live presentation or fallback)

The voice line runs at `https://voice-production-ef21.up.railway.app`; see `voice/README.md` and `deploy/README.md`. It decides each call with `deskagent` and speaks only templates.

Guardrails:
- The 999 line comes first for any hazard.
- It reads the reference and the phone number back (UK numbers must have 11 digits).
- It never promises a time or outcome.

ElevenLabs agent tests: `python -m voice.agent_tests`, 18/18 on the last run. Don't run them while recording; the hazard test logs a real case.

Settings on the Railway `voice` service:
- `HUB_URL` and `HUB_WEBHOOK_SECRET`: mirror the voice line's calls into `/ops`.
- `DATABASE_URL`: its shipment lookup reads the hub database first.
- `SEND_EMAIL=1` with Mailpit: shows its emails arriving.

Its calls open their own case and arrive already decided, which is why the D103 take uses the hub tools above.

## Before each take (in this order)

1. **Reset the demo cases.** This takes about 1 minute. D101 is worked in advance, and its messages are sent straight away so they don't join the approvals deck:

   ```bash
   AGENT_AUTO_APPROVE=1 .venv/bin/python -m db.seed_demo --wake D101
   ```

   The script prints D103's change cutoff, about 45 minutes after seeding. Record before it. Don't wake D103; the call does that.
2. **Clear the approvals deck.**
   - The deck is shared by **all** cases and works first-in, first-out. In `/ops`, as the coordinator, swipe left on every card that isn't D103's (reason: "demo reset").
   - Doing this on the same account also earns the "First call" and "Clean desk" medals, so their full-screen pop-ups don't appear during the take. If a pop-up shows, close it with **Nice**.
   - If the deck is already empty, do one rehearsal call, approve its drafts, then reset again.
3. **Check the stack.**
   - `curl <tunnel>/api/health` returns `{"ok":true}`.
   - The ElevenLabs tools point at the *current* tunnel URL.
   - D103 is selected on the desk.
4. **Arrange the screen.** Put the desk on the left and the ElevenLabs test call on the right. Zoom the browser out until the deck and the case detail both fit.

## The take (≤ 60 s)

| Time | Show | Say / hear |
|---|---|---|
| 0–5 s | `/ops`, D103 selected (decision panel visible) | "Vessa wants her delivery moved. The cutoff is close, but dispatch hasn't confirmed a change." |
| 5–14 s | Phone call | Vessa: "Hi, it's Vessa Lorne, 07700 900103. Has my delivery DL-103 been moved? I can't be home this afternoon." Voice: "I've logged your request as case D103. Nothing is confirmed yet; you can ask me for the latest at any time." |
| 14–17 s | Caption: **"Agent run completed — time compressed"** | The run takes 30–70 s (43 s in the rehearsal). Cut it. |
| 17–34 s | D103 → **Agent live log** tab (newest line at the top), then the two D103 cards at the top of the deck | "The agent sees that dispatch chat failed. It prepares a new, simulated request to dispatch by email and an honest update for Vessa. The reviewer approves the plan; the coordinator approves both messages." Swipe right on the dispatch email first, then on Vessa's update. |
| 34–46 s | Phone call | Vessa: "Any news?" Voice: "Latest update:", then the shortened approved message, e.g. "Your delivery DL-103 has not been moved yet. … This is a request, not a confirmation." |
| 46–55 s | `/ops` → D101 | "For a suspicious refund request, the agent sends no money and hands the case to a human." |
| 55–60 s | D101, with the caption **"Demo: fictional data, simulated messages"** | "Messages are simulated and appear in our demo portal; they don't reach real carriers." |

Notes for the take:
- **Order:** approve the dispatch email before Vessa's update. The customer portal's band shows the newest desk message on the case, whoever it was sent to.
- **"Any news" too early:** if it's asked before the approvals, the voice honestly says the update is waiting for a coordinator. That's fine, but it isn't the shot we want.
- **The reviewer must approve:** the live log must say "Independent reviewer, round N: approve". If it doesn't, the case becomes a human handover with no cards. Reset and take again.
- **A card disappears but nothing changes:** if the portal doesn't update after a swipe, the approval-time lint may have blocked the message. Check the **Actions** tab.

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

1. **Voice fails:** log in as `customer@greatagent.demo` in a phone-width window and write on D103 instead of calling. It takes the same path, through `/api/cases/D103/messages`.
2. **Supabase or the web app fails:** show the recorded real runs in `demo/recorded/D103` and `demo/recorded/D101`. Each has `ANSWER.md`, `REASONING.md`, `trace.json`, the input the agent saw (`index.md`, `history.md`) and a DB export (`live_desk_db.json`). Label them as recorded output (10 Oct 2026, local Postgres), not a live execution.
3. **Screens only:** `cd web && npm run preview:demo` renders the screens from **mock fixtures**. If it appears in the video, caption it "mock data".
4. **Last resort, no hub:** `python3 run.py stress_cases --only 101,103 --out demo/run && python3 viewer.py demo/run` (the CLI engine, the same pipeline), then open `demo/run/index.html`.

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
