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
about 40 s; its decision lands in `_result.json`, `answer/<id>/ANSWER.md`, and the outbox
(Mailpit with `SEND_EMAIL=1`). `POST /voice/update {conversation_id}` speaks a template summary.
Before the merge with main, point `DESKAGENT_PATH` at a checkout of main
(`git worktree add --detach ../greatagent-main origin/main`). `VOICE_AGENT=triage` restores
the older inline path.


**Shipment lookup.** When the caller's reference matches a known shipment (`voice/lookup.py`,
case folders under `VOICE_SHIPMENT_DATA`, default the public Delivery cases), the case deskagent
sees starts with the desk's own record up to the escalation — Case details and the events staged
Context/Escalation, never later events or labels — and the call is appended as the latest event.
In production this would query the shipment database (e.g. the data branch's SQLite) instead.

## Hub mode (`VOICE_AGENT=hub`)

Phone cases go to the team's hub (`hub/` on main) so they show in its `/ops` view. Voice still
does read-back, the 999 line, second-problem-as-new-case and the shipment lookup, then sends hub
one request (caller, reference, preferred contact, issue, and pre-escalation shipment context)
via `POST {HUB_URL}/webhooks/ask_agent` with `X-Hub-Secret`. The caller hears our template with
hub's case id. If hub isn't configured or doesn't answer within 3 s, the local deskagent path
decides instead (recorded in the case's `_hub.json`).

Env: `VOICE_AGENT=hub`, `HUB_URL` (where hub runs), `HUB_WEBHOOK_SECRET` (same value as hub's).

**The one non-template reply:** `/voice/update` in hub mode speaks hub's latest agent message
("The latest update on your case is: …"). It is model-written, so it is checked for promises,
amounts and credential words first; anything flagged becomes a fixed line instead.

## Mirroring to hub (option B, active when `HUB_URL` + `HUB_WEBHOOK_SECRET` are set)

deskagent decides; after it finishes, `voice/hub_mirror.py` posts the call and the decision to
hub's `POST /webhooks/record_case` so the case appears in hub's `/ops` (hub records only, its agent
is not woken). Spec for the hub side: `voice/HUB_MIRROR.md`. Failures (including 404 while the
endpoint doesn't exist) land in `_result.json` as `hub_mirror: {ok: false, error}` and never affect
the call or the decision. `VOICE_AGENT=hub` (hub decides instead) still exists but is off by default.

## ElevenLabs agent tests (the phone's guardrails)

`uv run --env-file <env> python -m voice.agent_tests [--repeat 3]` runs six ElevenLabs "next reply"
tests against the demo agent: ignores an injected refund instruction, refuses card details, promises
no delivery time, gives no advice on a leaking parcel, reads the reference back ("letter O" vs zero),
and reads the phone number back before logging. Tests are created once (ids in
`voice/agent_tests.json`) and judged by ElevenLabs' evaluator on the agent's next reply only. A tool
the reply calls runs for real: the hazard test logs a real case and starts deskagent, so don't run it
during a live recording. Exits non-zero on any failure, so run it after every prompt
change. Last run: 18/18 (6 tests × 3).
