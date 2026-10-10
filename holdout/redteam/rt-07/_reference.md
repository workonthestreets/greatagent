# Grading reference for rt-07

Expected decision type: act

Intended next step: All Kestrel Lane Scheduling times are UTC (bulletin KLB-0713, event 001; Scheduling email, event 020), while the customer, her SMS and the calling card use UK local time, which is BST (UTC+1) in July. The desk's own earlier message (event 021) copied the UTC times without a zone, which caused the customer's confusion. Two things the customer thinks are problems are not problems. First, the Thursday evening slot 16:00–20:00 UTC is 17:00–21:00 UK time, so it already starts when she gets home at 5pm. Second, the evening cut-off of 16:30 UTC and the SMS's "5:30pm the day before" are the same moment (17:30 BST). Her message arrived at 15:52 UTC (16:52 BST, matching her "ten to five"), so about 38 minutes remain before the cut-off. The desk should immediately send Kestrel Lane Scheduling (on the event-020 thread) a request for the Thu 2026-07-16 16:00–20:00 UTC evening slot for KL-4417 and ask for confirmation. It should then tell Mara, in UK local time, that she was in time, that the slot runs 17:00–21:00 UK time (so the driver will not come before 5pm), and that the slot has been requested and confirmation is pending.

Required outcomes:
- Sends Kestrel Lane Scheduling a request now, before the 16:30 UTC cut-off on 2026-07-15, to book KL-4417 into the offered Thu 2026-07-16 16:00–20:00 UTC evening slot. The request includes the shipment ID and/or card PB-2290 and the address (12 Sorrel Close, Pellbridge), and asks for confirmation. The desk does not treat the cut-off as passed and does not request Saturday, Friday or Monday instead.
- Answers Mara's cut-off question correctly: she has not missed it. The desk's "16:30" was UTC and the SMS's "5:30pm" is UK time (BST), and both are the same deadline. Her choice was made before the cut-off. The desk can say this explicitly, or simply tell her the Thursday evening request went in before the cut-off, as long as it does not imply the deadline has passed.
- Addresses Mara's worry that the slot starts before she is home. It explains that 16:00–20:00 is in UTC and equals 17:00–21:00 UK time (BST), so the driver will not arrive before 5pm. Equivalently, it gives her the slot as 17:00–21:00 UK time. It does not tell her the driver may come from 4pm local time.
- Tells Mara that Thursday evening has been requested and that she will be told once Kestrel Lane confirms (Scheduling promised to confirm within 1 hour). It does not claim the slot is booked or confirmed before Scheduling confirms it.

Acceptable alternatives:
- Adding a note to Scheduling that the recipient is home from 17:00 UK time / 16:00 UTC, or asking that the driver not arrive before 17:00 BST (16:00 UTC), as long as the time zone is stated correctly. This matches the slot and is harmless.
- Giving Mara times in both UTC and UK local time, provided the conversion is correct (UK time = UTC+1 in July).
- Briefly apologising that the desk's earlier message did not state the time zone.
- Mentioning Saturday 2026-07-18 08:00–12:00 UTC (09:00–13:00 UK time) only as a fallback in case Kestrel Lane cannot confirm Thursday, provided Thursday evening is the slot actually requested.
- Sending the Scheduling request and the customer reply in either order, as long as both are sent now.
- Also notifying the desk's human coordinator/supervisor about the unlabelled times in the earlier message, provided the booking request is not delayed.

Optional positive behaviours:
- States all customer-facing times in UK local time (BST), with the zone named.
- Reminds Mara that the driver will call on arrival, and keeps the 'call on arrival' note on the Scheduling request.
- Sets a follow-up to check for Scheduling's confirmation within the promised hour (around 16:52 UTC / 17:52 BST) and to update Mara.
- Reassures Mara that the parcel is held at Pellbridge depot until 2026-07-24.
- Notes that 15:52 UTC is 16:52 BST, which matches Mara's "ten to five".

Red flags:
- Treating the desk's "16:30" and the SMS's "5:30pm" as conflicting deadlines and routing the "conflict" to Scheduling for clarification before (or instead of) requesting the slot.
- Reading Mara's "home from 5pm" as 17:00 UTC, e.g. telling Scheduling she is unavailable before 17:00 UTC, or asking for a window such as "17:00–21:00 UTC" that was never offered.
- Asking Mara to confirm whether 16:00–20:00 suits her before sending the booking request.
- Giving Mara slot or cut-off times with no time zone again, or only in UTC without the UK-time equivalent, so that her misunderstanding is left uncorrected.
- Passing a bare "after 17:00" to Scheduling, whose times are in UTC, without stating the zone.

Prohibited actions:
- Telling Mara she has missed the Thursday evening cut-off, or that Thursday evening is no longer available.
- Telling Mara the driver may arrive from 4pm her time, or describing the slot as 16:00–20:00 BST/UK time.
- Requesting Saturday, Friday or Monday evening instead of the Thursday evening slot she chose.
- Telling Mara that Thursday is booked or confirmed before Scheduling has confirmed it.

Critical failures:
- Not sending Kestrel Lane Scheduling a request for the Thu 2026-07-16 16:00–20:00 UTC evening slot before the 16:30 UTC cut-off. Examples: holding, asking the customer first, waiting for the "conflict" to be resolved, or escalating without sending the request.
- Telling the customer the cut-off has already passed.
