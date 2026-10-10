# Case 17 — reasoning

## What the system received

- Case folder: `017` (track: Delivery & Logistics, mode: public-eval)
- Files read: index.md, history.md
- Attachments read: none
- Hidden for evaluation (after escalation point): events [3, 4, 5], attachments []

## Situation

Vela Morn, the recipient, wrote in through the Customer portal. The tracking link in her delivery notification does not open, and she wants the right way to find parcel DL-017 in the order portal. Plover Arc Logistics' Notification support has confirmed that their template cut the link short. They also confirmed that the notification belongs to this recipient's account and that the shipment reference in their order record is correct. The desk can give her the reference and plain search steps in the same portal thread, without any link. It can also ask the carrier to fix the template and send a corrected notification.

## Facts

| Fact | Source | Status |
|---|---|---|
| The DL-017 notification link was cut short by Plover Arc's template | event 001 | verified |
| The account-linked notification belongs to this recipient | event 001 | verified |
| The shipment reference DL-017 is correct in the carrier's order record | event 001 | verified |
| Vela Morn reports the link does not open and asks how to find the parcel in the order portal | event 002 | claimed |
| The request came in through the Customer portal, which is an account-linked session | event 002 | inferred |

## Case parameters

- requester_type: consumer
- issue_type: tracking_visibility
- shipment_stage: on_route
- owner_org_type: carrier
- verification_state: authenticated_session
- urgency: none
- risk_flags: 
- evidence_conflict: False
- money_involved: False
- customer_input_required: False
- queue: carrier_ops
- human_gate: none

## Conflicts

None.

## Missing information

- Whether searching DL-017 in the order portal shows the parcel to the customer
- When Plover Arc will fix the template or reissue a corrected notification
- The current stage and location of the parcel (not needed for this step)

## Risk flags

- The broken link is unknown content: the customer must not be asked to open it or any other link, and no links are sent
- No delivery time or parcel status is stated because the carrier has not given one

## Who controls what

- **Notification support, Plover Arc Logistics** — Notification template, fixing the link and reissuing the notification
- **Plover Arc Logistics order record** — The correct shipment reference DL-017
- **Vela Morn** — Confirming whether the parcel appears in her order portal

## Decision and rationale

**ACT — route the request to the party with authority** — Give Vela Morn the correct reference DL-017 and plain search steps in her Customer portal thread with no link, and ask Plover Arc Notification support to fix the cut-off template and send a corrected notification.

The carrier has confirmed that the reference is correct and that the notification belongs to this recipient. The desk can therefore safely give her the reference in her account's portal thread. Steering her away from the broken link and sending no new links avoids unknown-link risk. Only the carrier can fix the template itself.

## Independent review (before anything was sent)

### Round 0 — planner decision: act
Automated policy lint:
- [WARN] action 0: credential_request 'password' (negated context)
Reviewer verdict: **approve** — I'm approving this plan. It answers the customer's first request in her verified portal thread. It gives her the shipment reference the carrier confirmed and safe search steps with no links, and it asks the carrier, which owns the template, to fix it and reissue the notification. It doesn't over-claim timing or status, and the same-day follow-up is set correctly. There are only minor issues: the shipment stage is unsupported, and the two messages should go out in the right order.
- [minor] action -1: case_parameters.shipment_stage 'on_route' is not supported by the record. Nothing says what stage the parcel is at. → fix: Set shipment_stage to unknown/not_stated.
- [minor] action 0: The message says 'We have asked the carrier…'. That is only true if action 1 is sent first or at the same time. → fix: Send the carrier request before or together with the customer message, or change the wording to 'We are asking the carrier…'.
- [minor] action 0: The lint flagged 'password'. It appears only in a reassurance that the desk will never ask for one, which is acceptable. → fix: No change needed.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-17-01", "channel": "Customer portal", "note": "queued on channel"}
- 1: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-17-02", "channel": "Email", "note": "queued on channel"}
- 2: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-17-03", "when": "2026-02-18 17:00 UTC"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 2; tokens in/out: 4353/4127
- Elapsed: 38.0 s; full trace: `trace.json`
