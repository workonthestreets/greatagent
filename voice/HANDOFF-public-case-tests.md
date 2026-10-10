# Handoff — voice line tested against the public Delivery cases

Written 2026-10-10 by the Devin session. Repo root layout (`voice/`, `scorer/`, `triage/`).
Branch `feat/case-scorer`, PR #2. Nothing below is committed yet.

## State in 30 seconds

- 12 public Delivery cases replayed through `/voice/tool` with real Claude: **9/12 routed as the
  organisers recorded, 3 safe-but-vague** ("asking our delivery team" where merchant/customer was
  recorded). No reply promised money, a date or an outcome. Decide time 2.6–6.7 s (budget 14 s).
- 8 scripted ElevenLabs calls (5 from public cases, 3 adversarial): the agent refused prompt
  injection twice, refused card/PIN, refused a refund pushed 3×, gave no food-safety advice,
  read back and waited for "yes" every time.
- **Bug found and fixed:** `spoken()` on `/voice/tool` spoke the model's `missing` text verbatim
  (case 005: "we need the brother's full name, so the delivery can be authorised…"). Both paths now
  use the `ASKS` whitelist; new `receiver` question; tightened `_ASK_RULES`; new test.
  `uv run pytest -q tests/test_voice.py` → 7 passed, `uv run ruff check voice/ tests/` clean.

## Uncommitted changes (`git status`)

| File | Change | Owner |
| --- | --- | --- |
| `voice/app.py` | customer branch of `spoken()` → `ASKS[ask_key(d)]`; `receiver` ask; tightened `_ASK_RULES`; import order fix | Devin |
| `tests/test_voice.py` | `test_tool_asks_only_from_whitelist` | Devin |
| `voice/README.md` | two clauses: `/voice/tool` asks from the whitelist too | Devin |
| `voice/replay_cases.py` (new) | replays public cases through `/voice/tool` or `/voice/turn`, 4 workers, JSONL out | Devin |
| `voice/simulate.py` | 9 scenarios (`pc0xx-*`, `adv-*`), 2-attempt retry, `timeout=240` | Devin (+ `--assist` flag from Claude session) |
| `voice/setup_agent.py` | `call(..., timeout=30)` kwarg only | Devin — rest of the diff is the Claude session's assist-agent work |
| `voice/agent_ids.json` | `assist_tool_id`, `assist_agent_id` | Claude session |

Suggested commit split: Devin's files as `voice: whitelist /voice/tool asks; public-case replay + sim scenarios`;
the assist-agent edits as their own commit.

## Running processes (left up)

- `uvicorn voice.app:app --port 8010` with `SEND_EMAIL=1` → demo server, log `runs/voice-8010.log`
- `uvicorn voice.app:app --port 8011` with `VOICE_ASSIST=1 VOICE_LOG_DIR=runs/voice-replay` → replay server
- `cloudflared tunnel --url http://localhost:8010` → `https://jacob-celtic-press-producer.trycloudflare.com`
  (the ElevenLabs one-shot agent's tool points here)
- `mailpit` (http://localhost:8025)

Restart recipe (from repo root, env is `/Users/kash/Code/sandbox/dwelly-prep/.env`):
`SEND_EMAIL=1 uv run --env-file <env> uvicorn voice.app:app --port 8010`

## Artifacts

- `runs/voice-replay-tool.jsonl` — last 12 rows are this run (`expected` vs `replies[-1].say`);
  per-case decisions in `runs/voice-replay/replay-tool-<n>-*.json`
- `runs/voice-replay-tool-fix.jsonl` — case 005 after the fix
- `runs/voice-sim-public.log` — all 8 ElevenLabs transcripts
- `runs/voice-replay-turn.jsonl` — 37 rows from an earlier `/voice/turn` pass (pre-flatten, not judged)

Re-run: `uv run --env-file <env> python -m voice.replay_cases --base http://localhost:8011 --mode tool --ids 002 005 ... --out runs/x.jsonl`
Sims: `uv run --env-file <env> python -m voice.simulate pc050-refund-demand adv-injection [--assist]`

## Open threads

1. **Sims never reach our webhook** (ElevenLabs fakes the tool reply) — confirmed again: 0 sim POSTs
   on 8010. Server and prompt are tested separately; only a real call tests them together.
   Still needs: one real spoken call (call 1 from `voice/DEMO_SCRIPT.md`) before recording.
2. **Double tool call.** With an empty fake reply the agent called `report_delivery_issue` twice in
   most sims. On the real server a second call in the same conversation is treated as a *contact
   correction* and would speak "Thanks, I've updated that…" instead of the decision. Likely a sim
   artifact; watch for it on the real call. If it happens, make the second call idempotent when
   `update_by`/`contact` are unchanged (return the stored decision's `say`).
3. **Vague party.** `triage.decide` returns `party=other_business, org=""` for cases 002/021/031 →
   "our delivery team". Consider mapping `need=info_held_by_party` + a `team` naming returns/damage
   to merchant, or having the voice reply name the `team` when `org` is blank.
4. **Case 029 (chilled food at 9.2 °C)** fires the 999 safety template. Correct per the recorded
   action (escalate, no consumption advice) but the wording is heavy for food; optional softer
   template keyed on a food/temperature flag.
5. `adv-injection` needed the 240 s API timeout; the 30 s default in `call()` is too short for
   long simulations.
6. The 8010 access log showed one `401` from an ElevenLabs IP earlier today — unexplained; the
   stored secret matched for the later 200. Check if the real call fails auth.
