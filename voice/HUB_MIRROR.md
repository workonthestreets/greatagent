# Hub endpoint spec: `POST /webhooks/record_case` (for hub/, Andrey)

Voice (the phone line) uses the team's deskagent to decide each call. After deskagent finishes,
voice mirrors the case into hub so phone cases appear in `/ops` beside every other channel.
**Hub records the case. It must not wake its own agent** — the decision is already made.

Voice side is built and waiting (`voice/hub_mirror.py`); until this endpoint exists, voice logs
`{"ok": false, "error": "HTTP 404 from hub"}` per case and carries on.

## Request

`POST {HUB_URL}/webhooks/record_case`, header `X-Hub-Secret: <HUB_WEBHOOK_SECRET>` (same
`check_secret` dependency as the other webhooks). Voice waits at most 5 s.

```json
{
  "voice_case_id": "88YS",
  "caller_name": "Cash",
  "caller_phone": "07700900123",
  "shipment_ref": "DL-025",
  "request": "I still need the kettle. I choose a like-for-like replacement rather than a refund.",
  "lookup_source_case": "025",
  "decision": {
    "type": "act",
    "summary": "Ask the merchant's replacement team to approve a like-for-like replacement…",
    "approved": true,
    "contacted": ["Returns/Replacements team, Tallowmere Goods", "Cash"],
    "messages": [
      {"to": "Returns/Replacements team, Tallowmere Goods", "channel": "Email", "body": "Hello team, …"},
      {"to": "Cash", "channel": "SMS", "body": "Thanks for calling …"}
    ]
  }
}
```

Field notes:
- `caller_phone` is null unless the caller chose text or call-back updates (it was read back and confirmed).
- `shipment_ref` / `lookup_source_case` are null when the reference didn't match a known shipment.
- `decision.type` is one of `act`, `request_information`, `escalate_to_human`, `hold_no_action`, `decline`.
- `messages` are the messages deskagent actually sent (`send_message`) plus human handovers
  (`escalate_to_human`, `to` is the person/team handed to). Bodies are deskagent's reviewed drafts.

## Response

`200 {"case_id": "C-XXXXXX"}`. Voice stores it as `hub_mirror.case_id` in the case's `_result.json`.
Any non-200 is treated as "not mirrored" and never retried automatically.

## What to write (same tables `new_case` uses)

1. Resolve the caller with the existing `_caller(caller_phone)`; if there's no profile match, fall
   back to `caller_name` (or "Unidentified caller") with role `customer`.
2. `cases`: one row, `id = C-<hex>`, `title` = first 80 chars of `request`, `status = 'open'`
   (or `'escalated'` when `decision.type == 'escalate_to_human'`), `source_name` / `source_role` =
   the caller, `coordinator = 'Iona Quill, Rivet Delivery Desk'`, `shipment_id = shipment_ref`,
   `initial_request = request`.
3. `case_parties`: the caller (their role), the coordinator, and one row per distinct
   `decision.messages[].to` (role `other`). Use `on conflict do nothing`.
4. `case_events`, in order:
   - one `kind = 'call'` event: channel `Phone call`, author = caller, to_party = `Rivet Delivery Desk`,
     body = `request`;
   - one `kind = 'agent_message'` event per `decision.messages[]`: author `Rivet Delivery Desk`,
     author_role `agent`, channel = message `channel`, to_party = message `to`, body = message `body`.
     (This is what `get_latest_update` already reads for the caller.)
5. Optionally a note event with `decision.summary` and `voice_case_id` so staff can trace it back.

**Do not call `driver.wake`.** Hub's agent should not re-decide a case deskagent already handled.

## Idempotency

Voice sends each case once, but a retry could repeat it. Store `voice_case_id` (a column or the
note event) and return the existing `case_id` if it was already recorded.
