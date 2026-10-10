# Case 403 — reasoning

## What the system received

- Case folder: `403` (track: hard_cases, mode: reality)
- Files read: index.md, history.md
- Attachments read: none

## Situation

Marguerite Tran's kiln (Brightstall order BS-2209-4417, CAD 2,860.00) arrived damaged on 2026-10-06, with DAMAGED noted on the delivery record. Claim HM-CA-228904 is open with Harbourline Mutual, and the decision is promised by 14 October 2026. Two things have happened since the desk last wrote to her on 7 Oct, and she doesn't know about either. On 9 Oct the adjuster reviewed her photos and the delivery record and said nothing more is needed. The seller also has a replacement unit and says it will ship it the same day the claim is approved. She is now chasing, threatening a chargeback and a one-star review, and asking for payment today or a direct refund.

## Facts

| Fact | Source | Status |
|---|---|---|
| Kiln delivered 2026-10-06 15:10 PDT with DAMAGED noted on the delivery record (POD tablet); crushed crate corner and cracked lid | event 001, event 002 | claimed |
| Claim HM-CA-228904 registered; documents complete for first review; coverage decision promised by 14 October 2026 (Thanksgiving 12 Oct not counted); no phone status before then | event 003 | verified |
| Desk last wrote to Marguerite on 2026-10-07: decision due by 14 Oct, desk will write when it arrives, nothing needed from her | event 005 | verified |
| Fernhill Kilns has one more unit in stock and will ship it the same day the claim is approved; it will not ship before approval | event 006 | claimed |
| Adjuster A. Brandt reviewed the photos and the POD; no further documents needed; file queued for a coverage decision in the normal order | event 007 | verified |
| Marguerite says she has heard nothing. She threatens a chargeback and a one-star review after Monday and asks for payment today or a direct refund | event 008 | verified |
| Marguerite has a client firing schedule about two weeks after 7 Oct | event 004 | claimed |

## Case parameters

- requester_type: consumer
- issue_type: damage_or_condition
- shipment_stage: delivered
- owner_org_type: business_counterparty
- verification_state: asserted_only
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

- Harbourline's coverage decision on HM-CA-228904, due by 14 October 2026
- Whether Brightstall wants to take any step on the buyer's direct-refund request or the chargeback she has mentioned (Brightstall's decision)

## Risk flags

- money: refund or payout demanded; only Harbourline (claim) or Brightstall/the seller can commit an amount; the desk cannot
- chargeback and review threats are pressure, not new facts, and get no reply
- the seller's internal reasoning (carrying the loss twice) is not shared with the buyer
- the customer's client deadline is her own, not an irreversible shipment cutoff

## Who controls what

- **Harbourline Mutual (adjuster A. Brandt)** — Coverage decision and payout on claim HM-CA-228904, promised by 14 Oct 2026
- **Brightstall seller support (Joss Reyes) / Fernhill Kilns** — Any marketplace refund or chargeback response; shipping the replacement (offered the same day the claim is approved)
- **Marguerite Tran** — Her own choices once options exist
- **Larkspur Resolution Desk** — Coordination only; no authority to refund, pre-pay or speed up the insurer's decision

## Decision and rationale

**ACT — route the request to the party with authority** — Send Marguerite a factual update: the adjuster reviewed her file on 9 Oct, the decision is still due by 14 Oct, and the replacement depends on approval. Pass her direct-refund request and chargeback mention to Brightstall seller support for their decision. Keep the 14 Oct check.

Two real updates have arrived since the desk's last message, and they answer her worries directly: whether anyone is looking at the claim, and her earlier question about a new kiln. So holding is wrong. The insurer still owns the decision and its date is still ahead, so the desk doesn't chase Harbourline or promise any outcome. Refunds are Brightstall's decision, not the desk's, so her request goes to Brightstall as a request with no option promised to her.

## Independent review (before anything was sent)

### Round 0 — planner decision: hold_no_action
Automated policy lint: no findings.
Reviewer verdict: **revise** — The plan respects authority and doesn't over-claim. But it wrongly treats the case as having nothing new: the adjuster's 9 Oct review and the seller's offer to ship a replacement on approval are both new to Marguerite. The coordinator should send her a factual update instead of holding.
Failed checks: right_next_step
- [major] action -1: The wait check is wrong. Two things have happened since the desk last wrote to Marguerite on 7 Oct (event 005), and she knows neither. (1) On 9 Oct the adjuster reviewed her photos and the POD, said no more documents are needed, and queued the file for a decision (event 007). That answers her worry that she doesn't 'even know if anyone is looking at this.' (2) The seller has a replacement unit in stock and will ship it the same day the claim is approved (event 006). That answers her 7 Oct question about a new kiln and matters for her client deadline. Her email is a chase, but it is not true that nothing is new, so hold_no_action is not the right step. → fix: Change decision_type to a reply to Marguerite by email. Tell her the insurer reviewed her photos and the POD on 9 Oct and needs nothing more. Tell her the decision is still due by 14 Oct and the desk will write as soon as it arrives. Tell her the seller has a replacement unit and has said it will ship the same day the claim is approved, conditional on approval. Do not give any decision outcome, payout, refund or delivery date. Do not share the seller's internal reasoning about carrying the loss twice. Say plainly that the desk cannot issue a refund or speed up the insurer's decision, and do not respond to the threats. Keep the internal note and the 14 Oct follow-up.
- [minor] action 0: Marguerite's demand that someone refund her directly is a marketplace or seller decision. The plan only notes that the desk has no authority. It does not consider passing the request to Brightstall seller support, which owns refunds. → fix: Optionally, send Joss Reyes a short FYI that the buyer has asked for a direct refund and mentioned a chargeback, and leave any decision to Brightstall. Do not present a refund as an option to Marguerite.

### Round 1 — planner decision: act
Automated policy lint: no findings.
Reviewer verdict: **approve** — Two real facts have arrived since the desk's 7 Oct promise: the adjuster's 9 Oct review and the seller's offer to ship a replacement once the claim is approved. The buyer doesn't know either, so updating her passes the wait test. The plan promises no refund, payout or date. It routes her direct-refund request to Brightstall, which owns refunds, and keeps the seller's internal reasoning private. It doesn't respond to her threats and schedules a check for Harbourline's 14 Oct decision deadline.
- [minor] action -1: case_parameters set human_gate to 'hard' and queue to 'billing_review', but the plan sends messages on its own and never routes to a human. The outbound actions commit no money, so this doesn't change the outcome, but the metadata is inconsistent. → fix: Lower human_gate to match the coordination-only actions, or add a note that the refund decision sits with Brightstall, not a desk supervisor.
- [minor] action 0: The message says the seller 'told us' about the replacement. In fact Fernhill's message reached the desk as a forward from Brightstall seller support. → fix: Optionally say 'the seller, Fernhill Kilns, has told Brightstall…'. This is a wording precision point and doesn't block approval.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-403-01", "channel": "Email", "note": "queued on channel"}
- 1: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-403-02", "channel": "Email", "note": "queued on channel"}
- 2: `record_case_note` → done after 1 attempt(s) — {"status": "recorded", "note_id": "NOTE-403-03"}
- 3: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-403-04", "when": "2026-10-14 17:00 PDT -07:00"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 4; tokens in/out: 19103/10689
- Elapsed: 99.9 s; full trace: `trace.json`
