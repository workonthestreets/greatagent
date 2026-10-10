# Case 21 — reasoning

## What the system received

- Case folder: `021` (track: Delivery & Logistics, mode: reality)
- Files read: index.md, history.md
- Attachments read: none
- Loader warnings: could not parse dated events in history.md; the current time is unknown - read the history text directly

## Situation

Iona Fen's parcel VEL-021-26 from Marigold Books has had no scan since 2026-10-12 18:20 BST at Cress depot. Vellora opened trace TR-021 at 08:00 BST on 14 Oct. Its status is open, with no finding yet and the next review at 12:00 BST on 15 Oct. Ms Fen thinks the open investigation means the parcel is confirmed lost. She wants that confirmed and her GBP 39 refunded today. Marigold has made no refund decision and given no payment authorisation.

## Facts

| Fact | Source | Status |
|---|---|---|
| VEL-021-26 for Iona Fen from Marigold Books has no recent delivery scan | event E01 | verified |
| Under RM21, opening a carrier investigation is not a finding of loss. Merchant care decides refunds from the actual carrier result or a documented discretionary decision. Escalation staff cannot promise payment | event E02 | verified |
| Trace TR-021 was opened 2026-10-14T08:00+01:00. Status open, finding null, next review 2026-10-15T12:00+01:00 | event E03 | verified |
| Customer says the investigation means loss is confirmed and asks for a GBP 39 refund | event E04 | claimed |
| No refund decision or payment authorisation exists on the merchant account | event E05 | verified |
| Last physical scan was 2026-10-12T18:20+01:00 at Cress depot | event E05 | verified |
| Customer asks for loss to be confirmed and money sent today | event E06 | claimed |

## Case parameters

- requester_type: consumer
- issue_type: loss_or_misdelivery
- shipment_stage: at_depot
- owner_org_type: carrier
- verification_state: asserted_only
- urgency: none
- risk_flags: money
- evidence_conflict: False
- money_involved: True
- customer_input_required: False
- queue: carrier_trace
- human_gate: none

## Conflicts

- Customer says loss is confirmed (E04/E06). The record shows TR-021 is open with no finding (E03), and RM21 says opening an investigation is not a loss finding (E02). The record settles this; nothing needs brokering.

## Missing information

- Carrier investigation finding for TR-021 (due for review 2026-10-15 12:00 BST)
- Marigold Books merchant care refund decision, which depends on that finding or a documented discretionary decision

## Risk flags

- money: customer is asking for a GBP 39 refund with no authorisation; promising payment or confirming loss is not allowed
- Customer's deadline of 'today' is self-set, not an operational cutoff
- Customer verification: email assertion only

## Who controls what

- **Vellora trace team (trace@vellora.example)** — Investigation TR-021 and any loss finding; next review 2026-10-15 12:00 BST
- **Marigold Books merchant care (care@marigold.example)** — Refund decision, based on the carrier result or a documented discretionary decision
- **Vellora escalation desk** — Customer communication only; cannot confirm loss or promise payment (RM21)

## Decision and rationale

**DECLINE — request cannot be fulfilled as asked** — Decline to confirm loss or promise a refund today. Tell Ms Fen that TR-021 is open with no finding, that the next carrier review is at 12:00 BST on 15 Oct, and that Marigold Books merchant care decides any refund after that. Set a follow-up for the review time.

Under RM21, opening an investigation is not a loss finding, and escalation staff cannot promise payment. The finding is null and the merchant has given no authorisation. The carrier's review time is still ahead, so chasing now adds nothing. The customer has not been answered yet, so she should get an accurate explanation and a concrete next step.

## Independent review (before anything was sent)

### Round 0 — planner decision: decline
Automated policy lint: no findings.
Reviewer verdict: **approve** — The plan is sound and can go ahead; the three issues are minor fixes. The desk has not yet replied to the customer, so a first reply is the right next step. The reply correctly declines to confirm loss or promise a refund, as RM21 requires: the trace has no finding yet and Marigold has not authorised any refund. It gives the carrier's real review time (12:00 BST on 15 October), names Marigold Books as the party that decides refunds, and sets a follow-up for the review time.
- [minor] action 0: The message is signed 'Rivet Delivery Desk', but the case record names the desk as the Vellora escalation desk. → fix: Sign the message with the desk name used in the record, for example 'Vellora escalation desk'.
- [minor] action 0: The action_class is 'ask_customer', but the message asks the customer for nothing. It explains and declines her request. → fix: Change the action_class to an inform or decline class.
- [minor] action 0: The message says merchant care decides refunds 'based on the investigation result'. Under RM21, merchant care can also make a documented discretionary decision. → fix: Optionally say the decision is based on the investigation result 'or its own review'. Do not imply that a discretionary refund is likely.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-21-01", "channel": "Email", "note": "queued on channel (channel not previously used in this case)"}
- 1: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-21-02", "when": "2026-10-15T12:00:00+01:00"}
- 2: `record_case_note` → done after 1 attempt(s) — {"status": "recorded", "note_id": "NOTE-21-03"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 2; tokens in/out: 5511/4585
- Elapsed: 41.8 s; full trace: `trace.json`
