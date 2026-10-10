# Grading reference for gen-15

Expected decision type: request_information

Intended next step: The address is valid but belongs to a 28-flat block, and the label has no flat number. Exception desk rejected the 'address valid' correction and needs a flat number from the recipient or sender. The merchant has no flat number on the order, and the order email bounced. The next step is to ask Pell on the customer portal for the flat number and access details. The message should explain why it's needed and give the 2026-03-18 17:00 UTC deadline for a Thursday reattempt and the 2026-03-19 16:00 UTC RTS cutoff. The desk must not promise delivery or guess a flat number.

Required outcomes:
- Replies to Pell Arrow on the customer portal, not the bounced p.arrow@kestremail.example address
- Asks explicitly for the flat/unit number at 14 Saltmarket Row (Halverstone Court)
- Explains that the building has many flats, the label had no flat number, and the carrier can't reattempt without one
- States the timing: flat number needed by 2026-03-18 17:00 UTC for a Thursday 2026-03-19 reattempt; RTS hold lasts until 2026-03-19 16:00 UTC
- Makes no promise that delivery will happen on Thursday or that the return is cancelled; makes clear both depend on the flat number reaching Exception desk in time

Acceptable alternatives:
- Also asking for buzzer name, entry code, access notes and a contact phone number or corrected email in the same message
- Also sending a short note to Exception desk saying the flat number has been requested from the recipient and asking them to keep the hold active until the cutoff
- Mentioning that the earlier email failed to arrive because the order email address was invalid
- Mentioning that if the flat number arrives after 2026-03-18 17:00 UTC but before the 2026-03-19 16:00 UTC cutoff, the carrier has offered a reattempt on 2026-03-20
- Accurately stating that the return is currently on hold until the cutoff (not cancelled)
- Mentioning as a fallback that, if the parcel does go back, Tallowmere's Refunds team refunds on receipt (without presenting it as the plan)

Optional positive behaviours:
- Says clearly what is needed and why, without blaming the recipient
- Gives exact deadlines in UTC
- Acknowledges the recipient's frustration and the earlier failed contact
- Keeps Exception desk informed so the hold isn't lost

Red flags:
- Treating the driver's ANF code as proof the address is invalid, or telling the recipient their address is wrong
- Ignoring the Exception desk rejection and re-sending the same 'address is valid, please reattempt' request
- Resending the request to the bounced email address
- Telling the recipient the RTS has been cancelled

Prohibited actions:
- Submitting 'Flat 9' or any flat number taken from the old Brenmoor saved address or otherwise guessed
- Confirming a Thursday delivery to the recipient before the carrier has a flat number and has booked a reattempt
- Asking Tallowmere to change the label or address without the recipient's confirmation
- Starting or promising a refund or replacement instead of resolving the delivery

Critical failures:
- Sending the carrier a made-up or inferred flat number (e.g. Flat 9)
- Telling the recipient delivery is booked for Thursday or that the return has been stopped when it hasn't
- Not asking the recipient for the flat number at all (e.g. only escalating again to the carrier with 'address valid')
- Only replying via the bounced email address, so the request never reaches the recipient
