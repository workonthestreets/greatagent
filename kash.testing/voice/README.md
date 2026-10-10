# Voice line (ElevenLabs Agents → delivery agent)

A caller reports a delivery problem. The ElevenLabs agent collects the details and calls
`POST /voice/tool` mid-call. We run the same `agent.decide` as every other case and reply
with a fixed spoken template, so the call can't promise money, a time or an outcome. The
decision and the transcript are logged in `runs/voice/`.

## Run

```bash
cd kash.testing
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
