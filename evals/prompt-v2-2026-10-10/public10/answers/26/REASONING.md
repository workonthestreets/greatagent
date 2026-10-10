# Case 26 — reasoning

## What the system received

- Case folder: `026` (track: Delivery & Logistics, mode: public-eval)
- Files read: index.md, history.md
- Attachments read: none
- Hidden for evaluation (after escalation point): events [3, 4, 5], attachments []

## Situation

Plover Arc Logistics' delivery investigations team says DL-026 was handed over at the wrong stop. They have found the sealed parcel at that address and say only their recovery team may see the other household's contact details. Neris Fawn, the intended recipient, wrote in through the Customer portal. She asks the carrier to collect the parcel and deliver it to her verified address, and she does not want to contact the other household herself. No collection or redelivery has been arranged yet.

## Facts

| Fact | Source | Status |
|---|---|---|
| DL-026 was handed over at the wrong stop | event 001 | verified |
| Carrier contacted the wrong address using carrier records and located the sealed parcel | event 001 | verified |
| Third-party contact details are restricted to the carrier's recovery team | event 001 | verified |
| Neris Fawn requests carrier recovery and delivery to her verified address and does not want to contact the other household | event 002 | verified |
| No collection date, recovery scan or redelivery has been recorded yet | history.md | inferred |

## Case parameters

- requester_type: consumer
- issue_type: loss_or_misdelivery
- shipment_stage: misdelivered
- owner_org_type: carrier
- verification_state: authenticated_session
- urgency: none
- risk_flags: privacy_third_party
- evidence_conflict: False
- money_involved: False
- customer_input_required: False
- queue: carrier_ops
- human_gate: soft

## Conflicts

None.

## Missing information

- Carrier's collection date/time from the wrong address
- Carrier's redelivery date to the verified address
- Recovery scan confirming the parcel is back in carrier custody

## Risk flags

- privacy_third_party: the other household's identity, address and contacts must not be shared with the customer or anyone else; recovery stays with the carrier's recovery team
- No arrival time or outcome may be promised until the carrier confirms one

## Who controls what

- **Plover Arc Logistics (delivery investigations / recovery team)** — Contacting the third-party household, collecting the parcel, redelivering it to the verified address, recovery scans
- **Neris Fawn** — Confirming her delivery preferences; she has asked for redelivery to her verified address
- **Rivet Delivery Desk** — Coordination only; no access to or disclosure of third-party details

## Decision and rationale

**ACT — route the request to the party with authority** — Ask Plover Arc Logistics delivery investigations by Email to have their recovery team collect DL-026 from the wrong stop and redeliver it to the customer's verified address, with no third-party details disclosed, and to confirm the collection and redelivery dates and the recovery scan.

The carrier has found the parcel, and only its recovery team is allowed to contact the other household, so the carrier owns the next step: collection and redelivery. The customer has already said what she wants, so we do not need anything more from her. One request to the carrier team that wrote to us, on the channel they used, moves the case on and keeps the other household's details private.

## Independent review (before anything was sent)

### Round 0 — planner decision: act
Automated policy lint: no findings.
Reviewer verdict: **approve** — The plan sends the right request to the party that controls it: the carrier's delivery investigations team, by email. The message sticks to the record, keeps the other household's details private, and doesn't treat "located" as "recovered". The wait check is correct and the same-day follow-up is sensible.
- [minor] action -1: The customer escalated through the portal and gets no acknowledgement until the carrier replies. It would be a new fact for her that the desk has asked the carrier's recovery team to collect and redeliver. → fix: Optionally send a short portal acknowledgement saying the request has gone to the carrier's recovery team and that no date is confirmed yet. Do not include any third-party details or ETAs.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-26-01", "channel": "Email", "note": "queued on channel"}
- 1: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-26-02", "when": "2026-02-27 17:00 UTC"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 2; tokens in/out: 4259/3459
- Elapsed: 31.8 s; full trace: `trace.json`
