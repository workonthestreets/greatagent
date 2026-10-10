# Case 403 — Case 403

**Decision:** ACT — route the request to the party with authority

**In one line:** Send Marguerite a factual update: the adjuster reviewed her file on 9 Oct, the decision is still due by 14 Oct, and the replacement depends on approval. Pass her direct-refund request and chargeback mention to Brightstall seller support for their decision. Keep the 14 Oct check.

**Final result:** Awaiting response from Marguerite Tran (MSG-403-01), Joss Reyes (MSG-403-02). Proof that closes this step: document_from_party

## What the system received

- Case `403` (track: hard_cases); files: index.md, history.md
- Attachments: none
- 8 dated events; latest at 2026-10-10 08:35:56 PDT -07:00 (decision made as of then)

## Actions taken

1. **send_message** → Marguerite Tran (Buyer, order BS-2209-4417) via *Email* — DONE MSG-403-01
   - Subject: Update on your kiln claim HM-CA-228904 (order BS-2209-4417)

> Hi Marguerite,
>
> Thank you for your message. Here is where things stand.
>
> 1. The insurer is looking at your claim. On 9 October the Harbourline Mutual adjuster reviewed your photos and the signed delivery record. They have said no further documents are needed, and your claim HM-CA-228904 is queued for a coverage decision. Harbourline has said that decision will be issued by 14 October 2026.
>
> 2. A replacement is possible. The seller, Fernhill Kilns, has another unit of this model in stock. They have told us they will ship it the same day the claim is approved. This depends on the claim being approved, so I can't confirm a shipping or delivery date yet.
>
> To be straightforward with you: this desk can't issue a refund itself, and we can't make the insurer decide sooner than the date it has given. I have passed your request for a direct refund to Brightstall seller support, who handle refunds on marketplace orders. That is a request, not a confirmation.
>
> You don't need to do anything right now. I will write to you as soon as Harbourline's decision arrives.
>
> Dani Okafor
> Larkspur Resolution Desk

2. **send_message** → Joss Reyes (Brightstall seller support) via *Email* — DONE MSG-403-02
   - Subject: BS-2209-4417 / claim HM-CA-228904: buyer asks for a direct refund

> Hi Joss,
>
> An update on order BS-2209-4417 (claim HM-CA-228904). The Harbourline adjuster reviewed the photos and the POD on 9 October and needs no further documents. The coverage decision is still due by 14 October 2026.
>
> In her email of 10 October 08:35 PDT, the buyer, Marguerite Tran, asked to be refunded directly before the insurer decides. She also said she may file a card chargeback after Monday 12 October. Refunds on this order are Brightstall's decision, not ours. Please let us know whether Brightstall will take any step before 14 October, or whether the plan stays as Fernhill proposed: ship the replacement the same day the claim is approved. We have told the buyer that her request has gone to you and that no refund has been promised.
>
> Thanks,
> Dani Okafor
> Larkspur Resolution Desk

3. **record_case_note** — DONE NOTE-403-03: 2026-10-10 08:41 PDT: Marguerite chased (event 008) with chargeback and review threats and asked for payment today or a direct refund. Sent her an update: adjuster review on 9 Oct (event 007); decision still due by 14 Oct (event 003); replacement ships the same day the claim is approved, if approved (event 006). Told her the desk can't refund or speed up the decision. Did not share the seller's reasoning. Sent her refund request and chargeback mention to Joss Reyes (Brightstall) for their decision. No outcome or dates promised.

4. **schedule_follow_up** at 2026-10-14 17:00 PDT -07:00 — DONE FUP-403-04: Check for Harbourline's coverage decision on HM-CA-228904 (due by 14 Oct) and for any reply from Joss Reyes. If the decision has arrived: tell Marguerite, and if approved, ask Joss Reyes to have Fernhill ship the replacement and send a shipment reference. If it has not arrived: email claims-intake@harbourline.example / adjuster A. Brandt asking for the decision that was due 14 Oct, and update Marguerite.

## What was escalated

Nothing was escalated to a human.

## What failed

Nothing failed.

## Wait test (before any outbound message)

- New since the desk's last promise: Yes. Since the desk's 7 Oct message (event 005): on 9 Oct the adjuster reviewed the photos and the POD, needs no more documents, and queued the file for a decision (event 007). The seller has a replacement in stock and will ship it the same day the claim is approved (event 006). Marguerite knows neither. Her threats and Monday deadline (event 008) are not new facts.
- Pending promise from the owning party: Harbourline Mutual coverage decision by 14 October 2026 (PDT -07:00), still in the future
- Inbound is a chase only: no
- Verdict: proceed

## Deliberately not done

- Not promising a payout, refund, approval, shipping date or delivery date; no owner has confirmed any of them
- Not presenting a refund as an option to Marguerite; that is Brightstall's decision
- Not sharing Fernhill's internal reasoning about carrying the loss twice
- Not chasing Harbourline before its promised date of 14 Oct
- Not responding to the chargeback or review threats
- Not asking the seller to ship before approval; the seller has said it will wait

## Proof that closes this step

document_from_party

## Follow-up

On 2026-10-14 at 17:00 PDT, check for Harbourline's decision on HM-CA-228904 and for any reply from Brightstall. If the decision has arrived, tell Marguerite and, if approved, ask Brightstall/Fernhill to ship the replacement with a shipment reference. If no decision has arrived, chase adjuster A. Brandt by email and update Marguerite.

_generated by delivery-desk-agent · models: claude-opus-5-5_
