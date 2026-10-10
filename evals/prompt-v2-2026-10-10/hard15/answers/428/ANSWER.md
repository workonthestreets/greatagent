# Case 428 — Case 428

**Decision:** REQUEST INFORMATION — ask the right party for what is missing

**In one line:** Ask the customer to get a dock booking sponsored as a tenant through Vastbeheer Hoogstraat NV for a Mon-Fri 06:00-09:00 slot before the 2026-01-20 hold ends. At the same time, ask Scheldt Line which morning dates it can attend and whether it can register its vehicle and COI with the building portal.

**Final result:** Awaiting response from Marit Desmedt (MSG-428-01), Scheldt Line customer care (MSG-428-02). Proof that closes this step: customer_confirmation

## What the system received

- Case `428` (track: hard_cases); files: index.md, history.md
- Attachments: none
- 8 dated events; latest at 2026-01-15 16:41:07 CET +01:00 (decision made as of then)

## Actions taken

1. **send_message** → Marit Desmedt (Customer / consignee) via *Email* — DONE MSG-428-01
   - Subject: Table AB-55102 (tracking SLP-BE-8830417): what is needed for delivery

> Dear Ms Desmedt,
>
> Thank you for your patience. We have now found out why both deliveries failed. Your table was not refused by you. The loading dock at Hoogstraat Tower is managed by Vastbeheer Hoogstraat NV. Their dock booking system turned down the carrier's requests on 12 and 14 January because a tenant had not sponsored the booking. The table (190 kg, crated) cannot be taken through the front lobby or the passenger lift, so it has to come in through the dock.
>
> What we need from you:
> 1. Please ask your building management or front desk (Vastbeheer Hoogstraat NV) to approve, as a tenant, a dock booking for Scheldt Line Parcel, tracking SLP-BE-8830417. The building only allows deliveries Monday to Friday between 06:00 and 09:00.
> 2. Please send us the date and time they confirm, any booking reference they give you, and the name of the person at the building who approved it.
>
> The carrier is holding your table at its depot until 20 January 2026, so please send this as soon as you can. The building's system shows a handling fee of EUR 85.00 per slot, and the carrier charges EUR 62.50 for a third attempt. Who pays these has not been decided yet, so please do not pay anything until we come back to you on it.
>
> We cannot give you a firm delivery date until the building has confirmed a slot and the carrier has accepted it. We will confirm a date as soon as both are in place. We have also noted your refund request. Refunds are decided by Atelier Brum Furniture, and we will raise it with them if delivery cannot be arranged in time.
>
> Kind regards,
> Joost Verhaar
> Kadewerk Delivery Desk

2. **send_message** → Scheldt Line customer care (Carrier customer care / dispatch, depot ANR-2) via *Email* — DONE MSG-428-02
   - Subject: SLP-BE-8830417: dates you can attend and building portal registration before the 2026-01-20 hold ends

> Hello,
>
> Regarding SLP-BE-8830417 (one pallet, 190 kg, held at ANR-2 until 2026-01-20): your dock log shows Hoogstraat Tower's portal (Vastbeheer Hoogstraat NV) rejected the requests with NO_TENANT_SPONSOR. It also showed plate 1-LKW-482 as unregistered and no COI on file. The consignee is being asked to get a tenant-sponsored dock booking in the building's Mon-Fri 06:00-09:00 window.
>
> Please tell us by end of day 2026-01-16 CET:
> 1. Which morning dates between 06:00 and 09:00 you can attend with a tail-lift vehicle before 2026-01-20.
> 2. Whether you will register the vehicle plate and submit a COI to the building's dock portal, so that a sponsored slot is not rejected for those reasons.
> 3. Whether the hold at ANR-2 can be extended if the building's first available slot is after 2026-01-20.
>
> This is a request for options, not a booking and not agreement to the EUR 62.50 third-attempt fee. Who pays will be confirmed separately.
>
> Kind regards,
> Joost Verhaar
> Kadewerk Delivery Desk

3. **schedule_follow_up** at 2026-01-16 12:00 CET +01:00 — DONE FUP-428-03: Check whether Marit Desmedt has sent a building-confirmed dock slot and whether Scheldt Line has replied with dates and registration status. If either is silent, send a reminder. If no slot by Monday 2026-01-19 morning, raise with Atelier Brum Furniture (merchant_authorisation) whether the hold should be extended, the order cancelled or refunded, and who pays the fees.

## What was escalated

Nothing was escalated to a human.

## What failed

Nothing failed.

## Wait test (before any outbound message)

- New since the desk's last promise: The desk made no earlier promise to the customer (event 005 was a fact-finding call). Since then, the dock log (event 006) shows the tenant-sponsor requirement, and customer care (event 007) gave the fee, the window requirement and the hold deadline of 2026-01-20.
- Pending promise from the owning party: none
- Inbound is a chase only: no
- Verdict: proceed

## Deliberately not done

- Not giving a firm delivery date: neither the building nor the carrier has confirmed a slot.
- Not promising or starting a refund: that is the merchant's decision and delivery is still possible within the hold.
- Not agreeing to, waiving or assigning the EUR 62.50 or EUR 85.00 charges: nobody has decided who pays.
- Not contacting Vastbeheer Hoogstraat NV directly: the building needs a tenant to sponsor the booking, and that has to come from the customer.
- Not asking anyone to carry the 190 kg crate through the lobby or lift.
- Not blaming the customer, the driver or the building.

## Proof that closes this step

customer_confirmation

## Follow-up

On 2026-01-16 12:00 CET, check for the customer's building-confirmed slot and the carrier's dates and registration reply. Once both are in, ask Scheldt Line to book the third attempt with a booking reference, and raise who pays the fees with the merchant. If there is no slot by 2026-01-19 morning, take the hold extension, refund or cancellation decision to Atelier Brum Furniture before the hold ends on 2026-01-20.

_generated by delivery-desk-agent · models: claude-opus-5-5_
