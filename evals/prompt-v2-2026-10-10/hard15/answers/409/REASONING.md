# Case 409 — reasoning

## What the system received

- Case folder: `409` (track: hard_cases, mode: reality)
- Files read: index.md, history.md
- Attachments read: none

## Situation

Ticket CD-5521: Marta Hollis has asked us to book air freight for a crated harpsichord (declared value CAD 22,000) from YYC to YZF, and it must arrive before the 18 Oct recital. Option A (turboprop, CAD 880) has a 107 cm piece-height and 180 kg weight limit, and its allocation expires Tue 13 Oct 12:00 MDT. Option B (charter, CAD 1,940) needs commitment by Wed 14 Oct 12:00 MDT. Marta's own figures (98 cm uncrated + 12 cm runners = 110 cm before foam and lid) already exceed Option A's height limit. The crated weight (~175 kg on a bathroom scale) is unverified, and nobody has measured the crated dimensions. The carrier and the insurer both need those dimensions. Marta is back at the shop Tuesday morning.

## Facts

| Fact | Source | Status |
|---|---|---|
| Uncrated size 240 x 95 x 98 cm, ~150 kg, declared value CAD 22,000, needed by Sun 18 Oct | event 001 | claimed |
| Option A: Thu 15 Oct, CAD 880, max piece height 107 cm, max 180 kg, oversize refused at acceptance with CAD 120 fee not refunded, allocation held to Tue 13 Oct 12:00 MDT | event 002 | verified |
| Option B: Fri 16 Oct, CAD 1,940, up to 400 kg / 1.6 m height, commitment by Wed 14 Oct 12:00 MDT | event 002 | verified |
| Both options require final crated dimensions and gross weight for the air waybill | event 002 | verified |
| Rowan prefers the cheaper option but does not want to take any risk of damage | event 003 | claimed |
| Crate has 12 cm cradle runners underneath plus a foam top and a screwed lid; crated weight 'about 175 kg, bathroom scale'; crated dimensions not entered; the photo's tape reading is not legible | event 004 | claimed |
| Workshop is closed Wed-Fri; Marta is back Tuesday morning; pickup possible Tue 10:00 onwards | event 004 | claimed |
| Cordova Mutual binds CAD 22,000 cover only once the crated dimensions and gross weight are supplied; premium CAD 198 for either option | event 005 | verified |
| Minimum crated height = 98 + 12 = 110 cm, 3 cm over Option A's 107 cm limit before adding foam and lid | event 001, event 004, event 002 (calculated) | inferred |
| Estimated weight 175 kg is only 5 kg under the 180 kg limit and comes from a bathroom scale | event 004 (calculated) | inferred |
| Carrier reminder: Option A expires Tue 13 Oct 12:00 MDT; there are other enquiries for the flight | event 007 | verified |

## Case parameters

- requester_type: business_counterparty
- issue_type: freight_booking
- shipment_stage: pre_collection
- owner_org_type: business_counterparty
- verification_state: asserted_only
- urgency: deadline_bound
- risk_flags: money, physical_handling
- evidence_conflict: True
- money_involved: True
- customer_input_required: True
- queue: awaiting_counterparty
- human_gate: hard

## Conflicts

- The suggestion that Option A is suitable (cheaper, Rowan's preference) conflicts with the shipper's own figures, which put the crate at 110 cm or more against a 107 cm door limit; only a measured crate from Marta can settle this
- Crated weight is a bathroom-scale estimate (~175 kg) against a hard 180 kg limit; unverified

## Missing information

- Measured external crated length, width and height (cm), including runners, foam and lid
- Gross crated weight from a reliable scale
- Who authorises and pays for the booking, and whether they accept Option B at CAD 1,940 (CAD 1,060 more than A) if Option A is ruled out
- Confirmation of the pickup time from the workshop (Tue 10:00 onwards stated)

## Risk flags

- Booking Option A on unverified figures risks refusal at acceptance, losing the CAD 120 fee and missing the 18 Oct deadline
- Deadline: Option A allocation ends Tue 13 Oct 12:00 MDT; Option B commitment by Wed 14 Oct 12:00 MDT
- Insurance for CAD 22,000 is not bound until the crated dimensions are supplied
- Carrier pressure about 'other enquiries' is not a reason to book on estimates
- Money: committing either fare is a spending commitment that needs the payer's mandate

## Who controls what

- **Marta Hollis, Hollis & Daughter Instruments** — Crated dimensions and weight data, crate build, pickup readiness; booking instruction as requester
- **Rowan Beaulieu** — Buyer preference (cheaper unless risk); no recorded payment mandate
- **Athabasca Air Freight, cargo sales** — Acceptance limits, allocation and fare for Options A and B
- **Cordova Mutual (Imogen Park)** — Binding the CAD 22,000 cover once crated dimensions and weight are supplied
- **Bowline desk (Dev Okafor)** — Placing the booking only on the payer's instruction; no standing pre-authorisation to commit CAD 1,940

## Decision and rationale

**REQUEST INFORMATION — ask the right party for what is missing** — Do not book Option A on estimates. Marta's own figures put the crate at 110 cm or more against a 107 cm limit. Ask Marta for the measured crated dimensions and a weighed gross weight on Tuesday morning, plus her instruction on Option B (CAD 1,940), so the booking and insurance can go ahead before the Option B cutoff on Wed 14 Oct 12:00 MDT.

Both the carrier and the insurer need the crated dimensions and weight, and only Marta can supply them. Her stated figures already exceed Option A's door height, and refusal at acceptance would lose the fee and probably the recital date. Rowan does not want any risk. Committing CAD 1,940 needs the payer's mandate, so the desk asks for it rather than deciding. Marta is back Tuesday morning, which leaves time to measure before the Option A allocation lapses at 12:00 and well before the Option B cutoff on Wednesday.

## Independent review (before anything was sent)

### Round 0 — planner decision: request_information
Automated policy lint: no findings.
Reviewer verdict: **approve** — The plan holds off booking Option A on estimated figures, which already look over the height limit. It asks Marta, the only person who can measure the crate, for the crated dimensions, a proper weight and her instruction on booking and payment. Every figure, deadline and calculation matches the record (110 cm, CAD 1,060 difference, 15:00Z = 09:00 MDT), nothing is presented as booked or insured, and the carrier's pressure to commit is not acted on.
- [minor] action 0: The 110 cm minimum height assumes the instrument sits on top of the 12 cm runners. That is a reasonable reading of 'cradle runners underneath', but it is still an inference. The message does present it as 'your figures' and asks for a measurement, so it is not a false claim. → fix: Optional: say 'on the figures we have' so it reads as an estimate. No change is required.
- [minor] action 0: Marta says she is back Tuesday morning, but the record does not say whether she reads email on Monday. Asking for a reply by 11:00 leaves her very little time to measure the crate before Option A lapses at 12:00. → fix: No change needed. The 09:00 follow-up covers this.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-409-01", "channel": "Email", "note": "queued on channel"}
- 1: `record_case_note` → done after 1 attempt(s) — {"status": "recorded", "note_id": "NOTE-409-02"}
- 2: `schedule_follow_up` → done after 1 attempt(s) — {"status": "scheduled", "follow_up_id": "FUP-409-03", "when": "2026-10-13T15:00:00Z"}

## What failed

Nothing failed during execution.

## Calculations

- minimum crated height (uncrated + runners, before foam and lid), cm: `98 + 12` = 1.1E+2
- excess over Option A door height limit, cm: `(98 + 12) - 107` = 3
- margin under Option A weight limit, kg (bathroom-scale estimate): `180 - 175` = 5
- cost difference B minus A, CAD: `1940 - 880` = 1.06E+3
- insurance premium check, CAD: `22000 * 0.009` = 198

## Run metadata

- Models: claude-opus-5-5; LLM calls: 3; tokens in/out: 13523/7237
- Elapsed: 70.3 s; full trace: `trace.json`
