# Case 429 — Case 429

**Decision:** ACT — route the request to the party with authority

**In one line:** Ask Redgum to hold consignment RRF-QLD-3302715 at Archerfield and take it off the 20 Mar disposal run, with written confirmation. Ask Bellini to decide on 24 Mar delivery or a refund, and to settle its return request with its insurer, before the desk answers the customer.

**Final result:** Awaiting response from Redgum Road Freight claims team (MSG-429-01), Tomasz Bellini (MSG-429-02). Proof that closes this step: operator_confirmation

## What the system received

- Case `429` (track: hard_cases); files: index.md, history.md
- Attachments: none
- 7 dated events; latest at 2026-03-18 09:58:41 AEST +10:00 (decision made as of then)

## Actions taken

1. **send_message** → Redgum Road Freight claims team (Carrier claims / depot) via *Email* — DONE MSG-429-01
   - Subject: HOLD REQUEST – RRF-QLD-3302715 – please exclude from disposal run Fri 20 Mar

> Dear Redgum Road Freight claims team,
>
> We write on behalf of the merchant, Bellini Barista Supply, about consignment RRF-QLD-3302715 (order BBS-20917), which is now at your Archerfield depot.
>
> Please hold this consignment as it is, where it is, and take it off the depot disposal run on Friday 2026-03-20 and any later run. The goods are under an open insurance claim, and the cargo survey your inspection note refers to (Pike Marine Surveys, ref PMS-26-0418) is still in progress. Until further written notice, please do not dispose of, release, return, repair or move the goods off site.
>
> Please note this is a request to hold only. We are not asking for collection or return, and we are not discussing liability or settlement.
>
> Please confirm in writing by 17:00 AEST today, Wednesday 2026-03-18, that the hold is in place and the consignment is off the 20 Mar run. If someone else at the depot needs to action this, please pass it to the Archerfield depot manager and let us know who that is.
>
> Regards,
> Priyanka Ostrowski
> Southbank Post-Delivery Desk

2. **send_message** → Tomasz Bellini (Bellini Barista Supply) via *Email* — DONE MSG-429-02
   - Subject: BBS-20917 / RRF-QLD-3302715 – decision needed today: 24 Mar replacement or refund; return on hold per your insurer's notice

> Hi Tomasz,
>
> Three points on order BBS-20917 (consignment RRF-QLD-3302715).
>
> 1. Customer's request – your decision needed today. Dariusz Wolak has asked for a firm answer today. His cafe opens on 28 March and he needs time for the plumber and electrician. He asks for a new machine delivered by 24 March; if that isn't possible, he wants a full refund (order value AUD 4,860.00 incl. freight). Your email of 16 March said ready in about 9 days, which would be around 25 March. Can you get a replacement delivered by 24 March, or else offer a refund? Please also confirm the delivery date you can commit to, if any. He has also asked who will pay for his losses, including baristas he has already hired. We have made no promise to him on any of this, and we will not reply on dates, refunds or losses until we have your decision. He has said he will complain to Fair Trading and online, and take legal action if the machine is disposed of.
>
> 2. Return of the damaged unit – not arranged. Your insurer's notice (Harbourline claim HBM-AU-77310, 17 Mar, which you forwarded to us) says the goods must stay in their present condition and location. It also says any return, repair, sale or disposal without their written release may prejudice cover. Because of that, we have not booked the return you asked for on 16 March. If you want it to go ahead, please get Harbourline's written release first and send it to us.
>
> 3. Disposal run. Redgum had the unit on its Archerfield disposal run for Friday 20 March. Today we asked Redgum to hold it where it is and take it off that run, and asked them to confirm in writing by 17:00 AEST today. This is a request only; Redgum has not confirmed yet.
>
> Please reply by 14:00 AEST today, Wednesday 18 March, so we can answer Mr Wolak today.
>
> Regards,
> Priyanka Ostrowski
> Southbank Post-Delivery Desk

3. **record_case_note** — DONE NOTE-429-03: 18 Mar 10:20 AEST: Asked Redgum to hold the goods and take them off the 20 Mar disposal run; confirmation due 17:00 today. Bellini's return request (event 003) is on hold because of Harbourline notice HBM-AU-77310 (event 006). Asked Bellini to decide on 24 Mar delivery or a refund, and on the losses claim; reply due 14:00 today. Customer has not been answered yet: reply to him today once Bellini decides, or at the latest with the Redgum hold status. Nothing to be promised on dates, refund or losses.

4. **schedule_follow_up** at 2026-03-18 14:00 AEST (04:00 UTC) — DONE FUP-429-04: Check for Bellini's reply on 24 Mar replacement or refund and on Harbourline's release. If it has arrived, send the customer Bellini's decision through his email thread, with no added promises. If not, phone or chase Tomasz Bellini, and send the customer a factual update that day: we have asked Redgum to hold the machine (a request, not yet confirmed) and Bellini's decision is pending.

5. **schedule_follow_up** at 2026-03-18 17:00 AEST (07:00 UTC) — DONE FUP-429-05: Check Redgum's written confirmation that RRF-QLD-3302715 is held and off the 20 Mar disposal run. If there is none, phone the Archerfield depot manager / Redgum claims on Thu 19 Mar morning. If still unconfirmed by midday Thu 19 Mar, escalate to the supervisor and notify Bellini.

## What was escalated

Nothing was escalated to a human.

## What failed

Nothing failed.

## Wait test (before any outbound message)

- New since the desk's last promise: The desk has made no promise to the customer yet. New since his last email: insurer hold instruction (event 006) and inspection note (event 005). The disposal run is still pending.
- Pending promise from the owning party: none
- Inbound is a chase only: no
- Verdict: proceed

## Deliberately not done

- Not booking the return Bellini asked for: the insurer says a return without its written release may prejudice cover. Bellini must get that release first.
- Not promising the customer 24 March, a refund or payment for his losses: these are Bellini's decisions, and the insurer forbids settlement talks.
- Not telling the customer the machine is safe from disposal until Redgum confirms the hold in writing.
- Not sharing the insurer's claim correspondence with the customer, and not discussing liability with Redgum.
- Not asking anyone to open, move or inspect the unit.
- Not escalating to the supervisor yet: Bellini, as the insured, can settle the conflict with its insurer, and the customer's threat is not a new fact. Will escalate if the Redgum hold or Bellini's decision is not in by the follow-up times.

## Proof that closes this step

operator_confirmation

## Follow-up

14:00 AEST today: check Bellini's decision and reply to the customer the same day, giving Bellini's decision or a factual status update. 17:00 AEST today: check Redgum's written confirmation of the hold. If there is none, phone the depot on Thu 19 Mar morning. If still unconfirmed by Thu 19 Mar midday, escalate to the supervisor before the 20 Mar disposal run.

_generated by delivery-desk-agent · models: claude-opus-5-5_
