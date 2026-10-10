# Case 50 — reasoning

## What the system received

- Case folder: `050` (track: Delivery & Logistics, mode: public-eval)
- Files read: index.md, history.md
- Attachments read: none
- Hidden for evaluation (after escalation point): events [3, 4], attachments []

## Situation

Nella Voss's guaranteed-delivery parcel DL-050 was due by 2026-03-23 08:00 UTC but was handed over at 08:40 UTC, 40 minutes late. The carrier's route record gives the cause as a carrier sorting delay. She has asked the desk to submit a request for the GBP 7.50 guarantee surcharge. Under the booking terms the surcharge may be credited only after Plover Arc Logistics billing has reviewed it, so the next step is a billing-review request to the carrier.

## Facts

| Fact | Source | Status |
|---|---|---|
| DL-050 was guaranteed for delivery by 2026-03-23 08:00 UTC with a GBP 7.50 surcharge | event 001 | verified |
| If a carrier-caused delay is confirmed, the surcharge may be credited after billing review | event 001 | verified |
| Route record: carrier sorting delay; actual recipient handover 2026-03-23 08:40 UTC | event 001 | verified |
| No exclusion is recorded | event 001 | verified |
| Handover was 40 minutes after the guaranteed time | calculation from event 001 | inferred |
| Customer asks the desk to submit a request for the GBP 7.50 surcharge | event 002 | verified |
| The guarantee covers only the surcharge, subject to billing approval | index: Context | verified |

## Case parameters

- requester_type: consumer
- issue_type: money_and_billing
- shipment_stage: delivered
- owner_org_type: carrier
- verification_state: authenticated_session
- urgency: none
- risk_flags: money
- evidence_conflict: False
- money_involved: True
- customer_input_required: False
- queue: billing_review
- human_gate: hard

## Conflicts

None.

## Missing information

- Billing review outcome and any credit reference from Plover Arc Logistics billing
- Billing team's turnaround date for the review

## Risk flags

- money: the credit is limited to the recorded GBP 7.50 surcharge; no other compensation may be claimed or promised
- Hard human gate: the draft asks for a credit of an amount, so it waits for human approval before it is sent
- No payment links and no card or bank details may be requested

## Who controls what

- **Plover Arc Logistics billing (via Service guarantees)** — Whether to credit the GBP 7.50 surcharge after billing review
- **Nella Voss, customer** — Making the claim; receives the outcome
- **Rivet Delivery Desk** — Submitting the request only; has no pre-authorisation to credit any amount

## Decision and rationale

**ACT — route the request to the party with authority** — Ask Plover Arc Logistics billing, by email, to review a credit of the GBP 7.50 guarantee surcharge on DL-050. The draft is held for human approval because it asks for a credit of an amount.

The carrier's own record confirms a carrier-caused delay (40 minutes past the guarantee) and records no exclusion. The booking terms send any credit through billing review. So carrier billing is the owner of this decision, and the request is for the recorded surcharge only.

## Independent review (before anything was sent)

### Round 0 — planner decision: act
Automated policy lint:
- [WARN] action 0: promise_language 'guarantee'
- [WARN] action 0: promise_language 'guaranteed'
- [WARN] action 0: promise_language 'Guaranteed'
Reviewer verdict: **approve** — The plan is correct. It sends the request for the GBP 7.50 surcharge only to Plover Arc billing, the party that decides it, using the verified email channel. Every fact and calculation comes from event 001, and the 40-minute delay is right. The plan doesn't promise a credit, holds the draft for human approval, and the follow-up is sensible. The two minor points need no change before sending.
- [minor] action -1: Nella Voss asked the desk to submit the request, but the plan doesn't tell her when it has been sent. The only customer update is planned for after billing confirms the outcome, so she won't know her request is in progress. → fix: Optional: once the human approves and the email is sent, send a short portal note telling her the request has gone to carrier billing for review. Don't give any outcome or timing.
- [minor] action 0: The policy lint flagged the words 'guarantee' and 'guaranteed'. These are false positives: the words name the service and its booked deadline and don't promise any outcome. → fix: No change needed.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-50-01", "channel": "Email", "note": "queued on channel"}
- 1: `record_case_note` → done after 1 attempt(s) — {"status": "recorded", "note_id": "NOTE-50-02"}
- 2: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-50-03", "when": "2026-03-23 17:00 UTC"}

## What failed

Nothing failed during execution.

## Calculations

- Delay in minutes past the 08:00 UTC guarantee: `(8*60+40) - (8*60)` = 4E+1

## Run metadata

- Models: claude-opus-5-5; LLM calls: 3; tokens in/out: 6436/3883
- Elapsed: 36.4 s; full trace: `trace.json`
