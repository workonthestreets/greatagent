# Case 409 — Case 409

**Decision:** REQUEST INFORMATION — ask the right party for what is missing

**In one line:** Do not book Option A on estimates. Marta's own figures put the crate at 110 cm or more against a 107 cm limit. Ask Marta for the measured crated dimensions and a weighed gross weight on Tuesday morning, plus her instruction on Option B (CAD 1,940), so the booking and insurance can go ahead before the Option B cutoff on Wed 14 Oct 12:00 MDT.

**Final result:** Awaiting response from Marta Hollis (MSG-409-01). Proof that closes this step: document_from_party

## What the system received

- Case `409` (track: hard_cases); files: index.md, history.md
- Attachments: none
- 7 dated events; latest at 2026-10-12 13:15:44 MDT UTC-06:00 (decision made as of then)

## Actions taken

1. **send_message** → Marta Hollis (Hollis & Daughter Instruments (shipper)) via *Email* — DONE MSG-409-01
   - Subject: CD-5521 harpsichord YYC-YZF: crated measurements and booking choice needed Tue 13 Oct

> Hi Marta,
>
> We can't book the flight yet. Both the airline and the insurer need measured figures for the finished crate.
>
> Option A (turboprop, Thu 15 Oct, CAD 880) only accepts pieces up to 107 cm high and 180 kg. Your figures are 98 cm for the instrument plus 12 cm cradle runners, which is already 110 cm before the foam top and lid. The crate weight of about 175 kg from a bathroom scale is also close to the limit. If a piece is over the limit, the airline refuses it at acceptance and keeps the CAD 120 acceptance fee. That would put the 18 Oct recital at risk. So we are not booking Option A on the current estimates.
>
> When you are back at the shop on Tuesday 13 Oct, please send us:
> 1. The measured outside length, width and height of the crate in cm, including runners, foam and lid.
> 2. The gross weight of the crate from a proper scale, if you can.
> 3. Your instruction on which option to book. Option B is the charter freighter on Fri 16 Oct, CAD 1,940, which takes up to 1.6 m high and 400 kg. Please also tell us who is paying for the freight.
>
> Timings: if the measured crate does fit Option A, we would need your reply before Tue 13 Oct 12:00 MDT, when the airline stops holding that space. Option B has to be confirmed by Wed 14 Oct 12:00 MDT. Please reply by Tue 13 Oct 11:00 MDT if you can.
>
> Cordova Mutual will put the CAD 22,000 cover in place once we send them the same measured figures. The premium is CAD 198 for either option.
>
> This is a request for information. Nothing is booked yet, and nothing will be until you confirm.
>
> Dev Okafor, Bowline Cargo Desk

2. **record_case_note** — DONE NOTE-409-02: CD-5521: Option A not booked. Stated figures give a crated height of at least 110 cm (98 + 12 runners) against the 107 cm limit, and the weight is a bathroom-scale 175 kg against the 180 kg limit. Asked Marta for measured crated L x W x H, gross weight and an instruction on Option B (CAD 1,940; CAD 1,060 more than A), plus who pays. Deadlines: A Tue 13 Oct 12:00 MDT, B Wed 14 Oct 12:00 MDT. Insurance (CAD 198) waits for the measured figures. Committing a fare needs payer approval (hard gate).

3. **schedule_follow_up** at 2026-10-13T15:00:00Z — DONE FUP-409-03: Tue 13 Oct 09:00 MDT: check for Marta's measurements and instruction. If none, contact her through the recorded channel as soon as she is back at the shop. Option A lapses at 12:00 MDT. If there is still no reply by Tue afternoon, escalate to the supervisor ahead of the Option B cutoff on Wed 14 Oct 12:00 MDT.

## What was escalated

Nothing was escalated to a human.

## What failed

Nothing failed.

## Wait test (before any outbound message)

- New since the desk's last promise: The desk has made no earlier promise to Marta. The carrier's reminder (event 007) brings no new fact. The booking decision is due today.
- Pending promise from the owning party: none from the requester; carrier Option A allocation held to Tue 13 Oct 12:00 MDT, Option B to Wed 14 Oct 12:00 MDT
- Inbound is a chase only: yes
- Verdict: proceed

## Deliberately not done

- Not booking Option A on estimates: stated figures already exceed the height limit, and a refusal loses CAD 120 and risks the deadline
- Not committing Option B (CAD 1,940) without the payer's instruction
- Not replying to the carrier with a commitment or asking for an extension it has not offered
- Not sending estimated dimensions to Cordova Mutual or the carrier
- Not promising Rowan an arrival date or that insurance is in place
- Not suggesting the crate travel on its side or be rebuilt; that is the shipper's decision

## Proof that closes this step

document_from_party

## Follow-up

Tue 13 Oct 09:00 MDT: check for Marta's measured crate figures and booking instruction. If they confirm a fit under 107 cm and 180 kg before 12:00, Option A can be considered with the payer's approval. Otherwise prepare Option B for human approval before Wed 14 Oct 12:00 MDT. Then send the figures to Athabasca and Cordova Mutual. If Marta is silent by Tuesday afternoon, escalate to the supervisor before the Option B cutoff.

_generated by delivery-desk-agent · models: claude-opus-5-5_
