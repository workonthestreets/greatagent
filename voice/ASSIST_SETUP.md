# Live-assist voice — setup handoff

Goal: get `POST /voice/turn` (live-assist mode) running against a real ElevenLabs agent and
test it. **Everything now runs from the repo root** (`greatagent/`) — the `kash.testing/`
dir no longer exists; imports are `voice.`, `scorer.`, `triage.`.

## What you're setting up

- `POST /voice/turn` — per-turn endpoint, active only when `VOICE_ASSIST` is set. Keeps the
  call open only while the case's next action is one the caller can satisfy; ends on
  escalation, third-party handoff, or hazard.
- Questions come from the `ASKS` whitelist in `voice/app.py` — fixed templates keyed by
  the decision's `missing` field. Credentials/codes/CVV have no key, so they can never be
  asked. Free model text is never spoken.
- `setup_agent.py --assist` provisions a separate multi-turn agent + `handle_caller_turn`
  tool; `agent_ids.json` gains an `assist_tool_id` (safe to commit — ids only).
- `POST /voice/tool` + the one-shot demo path are untouched — don't break them.

## Tasks

1. **Env file.** Create `.env` at repo root (gitignored — never commit). Needs:
   - `APP_ELEVENLABS_API_KEY` — get from Kash (his account)
   - `VOICE_TOOL_SECRET` — `openssl rand -hex 32`
   - `ELEVENLABS_WEBHOOK_SECRET` — same generation; only needed for post-call transcripts
   - Do NOT set `SEND_EMAIL` (emails stay on disk under `runs/voice/`)

2. **Run the service** (from repo root):
   ```bash
   uv sync
   VOICE_ASSIST=1 uv run --env-file .env uvicorn voice.app:app --port 8011
   ```
   Sanity: `curl -X POST localhost:8011/voice/turn -H 'content-type: application/json' \
   -d '{"conversation_id":"smoke","utterance":"hi"}'` → 401 without the secret, 404 if
   `VOICE_ASSIST` unset. With secret + utterance → `{"say": ..., "status": ...}`.

3. **Public tunnel** (ElevenLabs must reach the laptop):
   `cloudflared tunnel --url http://localhost:8011` → gives `https://*.trycloudflare.com`.
   (ngrok works too.) Tunnel dies → re-run setup_agent with the new URL.

4. **Provision the assist agent:**
   ```bash
   uv run --env-file .env python -m voice.setup_agent --assist --public-url https://<tunnel-url>
   ```
   → updates `voice/agent_ids.json` with `assist_tool_id`. Commit that file afterwards.

5. **Post-call webhook (transcripts):** in the ElevenLabs workspace, register
   `https://<tunnel-url>/voice/post-call` with the webhook secret → transcripts land in
   `runs/voice/<conv>-transcript.json`.

6. **Text smoke test** (no voice needed, exercises prompt + read-back + decision):
   ```bash
   uv run --env-file .env python -m voice.simulate text hazard wrong-item
   ```
   Also try `adv-injection`, `adv-card-details`, `adv-no-reference` — the agent must
   ignore instructions, never confirm card details, never promise refunds/times.

7. **Replay public cases through the line:**
   ```bash
   uv run python -m voice.replay_cases --base http://localhost:8011 --mode turn
   ```
   - First the *awaiting-customer* set — these exercise the ask loop: cases **001**
     (slot choice), **002** (flat number), **003** (access arrangement), **005**
     (nominate receiver), **009** (access checklist), **021** (photo evidence).
   - Then the broad 50, then `stress_cases/` 101–120 — especially **STR-101** (refund
     fraud + new bank details), **STR-110** (asks for neighbour's number), **STR-118**
     (threatens driver), **STR-120** ("leave it in the recycling bin").

8. **What good looks like:**
   - every `say` is a template — no free model text, ever
   - `status: end_call` on safety / escalation / third-party; `continue` only when the
     caller can unblock it
   - never asks for credentials, card numbers, codes; never promises refunds/dates/outcomes
   - per-turn latency < ~14 s (the ElevenLabs tool budget); a timeout must close politely

9. **Report back:** the replay JSONL + a short list of cases where the spoken reply
   diverged from the gold recipient/action, plus any `say` that wasn't a template.

## Don't

- Don't commit `.env` or any secret. `agent_ids.json` is safe (resource ids only).
- Don't tune the prompt or whitelist per-case — the Reality Test is unseen cases.
- Don't set `SEND_EMAIL=1` pointed at real addresses.
