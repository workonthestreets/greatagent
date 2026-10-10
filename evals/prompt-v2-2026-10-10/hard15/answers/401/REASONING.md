# Case 401 — reasoning

## What the system received

- Case folder: `401` (track: hard_cases, mode: reality)
- Files read: index.md, history.md
- Attachments read: none

## Situation

Mr Nowak's 2 pallets (AWB 999-4812 0377) are in Aerovanta's bonded shed B at GDN on customs hold. Duty has been paid. The veterinary inspector is at the shed today between 13:30 and 15:00 CEST. The broker expects his written protocol by about 16:30, and if it is clean the release takes about 30 minutes more. On 8 Oct the desk promised Mr Nowak the inspection outcome and the delivery plan by 17:00 CEST today. He is now chasing angrily. He wants an exact truck time before 14:00, threatens his lawyer and online reviews, and asks for his freight money back.

## Facts

| Fact | Source | Status |
|---|---|---|
| Cargo landed 06 Oct 22:10, 2 pcs / 412 kg, bonded shed B, status CUSTOMS HOLD; release needs customs plus veterinary inspectorate sign-off | event 002 | verified |
| No storage charge before 12 Oct | event 002 | verified |
| Entry lodged, duty PLN 1,312.40 paid from deposit; broker cannot give a release time until the inspector's protocol | event 004 | verified |
| Desk promised the customer the inspection outcome and delivery plan by Fri 9 Oct 17:00 CEST | event 005 | verified |
| Inspector at shed B 13:30-15:00 CEST today; protocol usually by 16:30; if clean, ~30 min to release stamp, then Aerovanta can load; broker will forward on arrival | event 006 | verified |
| Customer demands exact delivery hour before 14:00 today or a freight refund; threatens lawyer, airline director, Google reviews | event 007 | claimed |
| Customer states transport already paid | event 007 | claimed |

## Case parameters

- requester_type: consumer
- issue_type: customs_and_import
- shipment_stage: customs_hold
- owner_org_type: business_counterparty
- verification_state: asserted_only
- urgency: none
- risk_flags: money
- evidence_conflict: False
- money_involved: True
- customer_input_required: False
- queue: awaiting_counterparty
- human_gate: none

## Conflicts

None.

## Missing information

- Veterinary inspection result and written protocol (expected by about 16:30 CEST)
- Release stamp time and Aerovanta loading/delivery slot to Straszyn (only possible after a clean protocol)
- Who issued the freight invoice and what the refund terms are, needed only if the refund demand is pursued

## Risk flags

- Legal threat and threat of public reviews: pressure, not a new fact; it does not change the wait test
- Self-set 14:00 deadline is not a real cutoff
- Refund demand: the desk must not promise any refund or compensation it has not been given
- Must not invent a delivery hour before the inspector's protocol exists
- Storage charges may start from 12 Oct if release slips (event 002)

## Who controls what

- **Veterinary inspectorate** — Inspection result and written protocol
- **Baltic Clear Customs (Ewa Sawicka)** — Customs entry, release stamp, forwarding the protocol
- **Aerovanta Cargo GDN import handling** — Release from shed B, loading, storage charges
- **Freight invoicing party (not identified in record)** — Any freight refund; no pre-authorisation recorded
- **Zbigniew Nowak** — Whether to keep or cancel his order

## Decision and rationale

**HOLD — no action now (deliberate)** — Hold: the inspection is under way inside its window and the desk's 17:00 CEST promise still stands, so send nothing now, record the chase, and check for the protocol at 16:30 CEST so the promised update goes out by 17:00.

Event 007 is a chase with threats and no new fact. The inspection is happening inside its confirmed window, and the owners' times (protocol about 16:30, desk update 17:00) are still ahead. No delivery hour exists until the protocol and release exist. A message now could only repeat 'working on it' or invent a time, and the customer has explicitly rejected the first. The refund demand is not something the desk controls or can promise. It can be raised with the invoicing party later if he formally pursues it after the 17:00 update.

## Independent review (before anything was sent)

### Round 0 — planner decision: hold_no_action
Automated policy lint: no findings.
Reviewer verdict: **approve** — The hold is correct. The customer's message adds no new fact, only pressure, a deadline he set himself and a refund demand. The inspector is on site inside the confirmed 13:30–15:00 window, the protocol is expected by about 16:30, and the desk's 17:00 CEST promise has not come due yet. The plan sends nothing outbound, invents no delivery time and promises no refund. The follow-up at 16:30 CEST (14:30 UTC) is converted correctly and is timed to meet the 17:00 promise.

## Execution log

- 0: `record_case_note` → done after 1 attempt(s) — {"status": "recorded", "note_id": "NOTE-401-01"}
- 1: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-401-02", "when": "2026-10-09 14:30 UTC (16:30 CEST)"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 2; tokens in/out: 7485/4369
- Elapsed: 41.4 s; full trace: `trace.json`
