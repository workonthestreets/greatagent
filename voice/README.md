# Voice line (ElevenLabs Agents → delivery agent)

A caller reports a delivery problem. The ElevenLabs agent collects the details and calls
`POST /voice/tool` mid-call. We run the same `triage.decide` as every other case and reply
with a fixed spoken template (a customer question comes from the same ASKS whitelist), so the
call can't promise money, a time or an outcome. The
decision and the transcript are logged in `runs/voice/`.

## Run

```bash
VOICE_TOOL_SECRET=<long random> ELEVENLABS_WEBHOOK_SECRET=<from dashboard> \
  uv run uvicorn voice.app:app --port 8000
cloudflared tunnel --url http://localhost:8000     # public https URL for ElevenLabs
```

Set `SEND_EMAIL=1` with Mailpit running (`mailpit`; inbox at http://localhost:8025) to show
the agent's email arriving. Without it, emails are only written to disk.

## ElevenLabs setup (dashboard, then pull into the repo)

1. Create an agent: "Delivery desk". System prompt: collect the caller's name, order or
   tracking reference and what went wrong; call `report_delivery_issue` once; read its `say`
   field back word for word; never promise refunds, dates or outcomes yourself.
2. Add a **Webhook tool** `report_delivery_issue`: POST `<tunnel>/voice/tool`, response
   timeout 20 s, pre-tool speech "auto". Body params:
   - `conversation_id`: type **Dynamic variable** → `system__conversation_id`
   - `caller_name`, `order_ref`, `issue`: type LLM prompt, each with a one-line description
   - Header `X-Tool-Secret`: type **Secret** → the value of `VOICE_TOOL_SECRET`
3. Workspace settings → post-call webhook (transcription) → `<tunnel>/voice/post-call`;
   copy its secret into `ELEVENLABS_WEBHOOK_SECRET`.
4. Test with the dashboard's "Test AI agent" button (no phone number needed).
5. Keep the config in git: `elevenlabs agents pull` into `voice/`.

If the decision takes longer than 14 s, the caller hears "logged for the delivery team"
and the decision still finishes and is logged.

## Live assist mode (`POST /voice/turn`)

Opt-in multi-turn mode: the service runs with `VOICE_ASSIST` set, and the agent is provisioned
with `uv run --env-file <env> python -m voice.setup_agent --public-url <tunnel> --assist`, which
registers a `handle_caller_turn` webhook tool and a prompt that calls it after **every** caller
message, speaks the returned `say` verbatim, and wraps up when `status` is `end_call`.

Per call the service keeps `runs/voice/<conv>-state.json` — caller name, order reference, update
contact and every utterance so far. Each turn re-runs `triage.decide` on the whole call history
(each utterance is an event), so a late reference or correction changes the next answer.

The reply is always a fixed template:

- escalation → the usual escalation wording, `status: "end_call"`, `reason: "escalated"`
- decision asks the customer → one question from a whitelist (`ASKS` in `voice/app.py`:
  reference, confirm details, contact, delivery slot, access notes, photo, or a generic
  "tell me more"), `status: "continue"`
- any other party → "I'm asking \<who\> to look into this…", `status: "end_call"`,
  `reason: "handed_to_third_party"`
- decision over the 14 s budget → the safe "logged for the delivery team" close, `end_call`

The whitelist is the safety property: the question is picked by matching keywords in the
decision's `missing` field against fixed keys — unmatched text falls back to the generic ask and
is never spoken. Credentials have no key (no PIN, CVV or password template exists), so the voice
agent cannot be made to ask for one. `/voice/tool` now asks from the same whitelist; the
60-second demo flow is unchanged.

## Who decides: deskagent (default) or triage

`VOICE_AGENT=deskagent` (default): `/voice/tool` writes the call as a case folder under
`runs/voice/cases/<conversation>/` and replies at once with a template ("logged as case 5417…").
The team's deskagent then runs `load_case` + `process_case` (reviewer on) in the background,
about 40 s; its decision lands in `result.json`, `answer/<id>/ANSWER.md`, and the outbox
(Mailpit with `SEND_EMAIL=1`). `POST /voice/update {conversation_id}` speaks a template summary.
Before the merge with main, point `DESKAGENT_PATH` at a checkout of main
(`git worktree add --detach ../greatagent-main origin/main`). `VOICE_AGENT=triage` restores
the older inline path.

