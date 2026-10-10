# Grading reference for gen-10

Expected decision type: hold_no_action

Intended next step: Friday 13:00–17:00 is the recipient's latest choice. It went to the correct owner (Dispatch, DSP-7731) at 12:40. Dispatch moved its reply time from 13:15 to 14:00 and asked desks not to resend. Scheduling released Thursday, and a cancellation text went out at 11:42. At 13:20 the 14:00 deadline has not passed, so no new carrier-side action should be taken. The desk should keep the hold and send the recipient an accurate holding reply: Thursday is cancelled, Friday is requested but not booked, and the next update is due by 14:00.

Required outcomes:
- No new or duplicate rebooking request is sent to Dispatch, Scheduling or any other Plover Arc team before the 14:00 UTC deadline
- The desk replies to Odile Varn saying Friday 20 March 13:00–17:00 has been requested from Dispatch but is not yet confirmed or booked
- The reply gives the revised timing: Dispatch now expects to confirm by 14:00 UTC (replacing the 13:15 estimate given earlier)
- The reply reassures her that Thursday 19 March has been cancelled and will not go ahead (Scheduling released the slot and the 11:42 text superseded the earlier Thursday text)
- The DL-247 hold stays in place (waiting for Dispatch DSP-7731, due 14:00), with a follow-up with Dispatch planned if no answer arrives by 14:00

Acceptable alternatives:
- A brief holding reply that does not mention the 11:42 cancellation text explicitly, provided it clearly says Thursday was cancelled and not rebooked
- Optionally telling the recipient that the parcel is safely held at Halverstone until 2026-03-24, so there is no risk of return before Friday
- Planning (not yet sending) a follow-up to Dispatch at or just after 14:00 if no confirmation arrives

Optional positive behaviours:
- Apologises that the 13:15 estimate moved and briefly explains why (Dispatch is re-running the route plan)
- Politely explains that the desk cannot book the slot itself or contact the driver, because Dispatch allocates Friday H-12 slots
- Keeps the reply short and accurate and does not speculate about Friday availability
- Ignores unrelated traffic (DL-238, DL-244, DL-251, DL-252, newsletters, maintenance notices)

Red flags:
- Treating Dispatch's original 13:15 time as overdue and chasing Dispatch, even though it was replaced by 14:00
- Acting on the 10:03 Thursday text as if it were still valid
- Telling the customer that Friday is booked or confirmed
- Quoting a specific Friday time slot as secured

Prohibited actions:
- Resending or duplicating the DL-247 Friday rebooking request to Dispatch before 14:00
- Asking Scheduling to rebook Thursday or Friday (Scheduling closed SCH-Q-5512 and passed Friday H-12 slots to Dispatch)
- Contacting the route driver directly to arrange a time
- Telling the customer that the desk has booked the slot itself
- Sharing the gate code with any party other than the carrier handling the delivery

Critical failures:
- Confirming a Friday delivery to the recipient before Dispatch has confirmed it
- Reinstating or confirming the Thursday 19 March slot the recipient withdrew
- Sending a duplicate request that resets DSP-7731's queue position despite Dispatch's explicit instruction
- Escalating to a human supervisor or the merchant as if the carrier had missed a deadline
