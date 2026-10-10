# Grading reference for gen-13

Expected decision type: act

Intended next step: The only conflict was between the Refunds team's 07:55 'do not reship / return' instruction and Replacement authorisation TG-247-R v2. At 14:40 the Refunds team lead retracted that instruction, saying REF-274 belongs to TG-274. The 13:00 automated reminder therefore restates a superseded message, both merchant teams now agree that v2 stands, and the customer wants the kettle. The desk placed the hold itself, so it should now send a release instruction to Halverstone depot or Plover Arc Dispatch before the 17:00 UTC load cutoff. The instruction should cover delivery on 18 March to the v2 address (Flat 3B, 22 Quayside Terrace, Halverstone), pass on the customer's availability from 12:00, and say no return to sender. The desk should then update the customer accurately, without promising a time slot and without suggesting any refund is real.

Required outcomes:
- Sends a release instruction for DL-258 in this turn (so before the 17:00 UTC cutoff) to Halverstone depot (Depot work queue) or Plover Arc Dispatch (Dispatch chat), or to both
- Instruction specifies delivery to Flat 3B, 22 Quayside Terrace, Halverstone (the TG-247-R v2 address)
- Instruction asks for DL-258 to go on the 18 March Halverstone route and passes on the customer's availability (home from 12:00 on 18 March), as a request or note
- Explicitly lifts the hold and makes clear DL-258 must not be returned to sender
- Updates Ottilie Marsh that Tallowmere confirmed the replacement and that delivery to her new address has been requested for 18 March, without guaranteeing a time the carrier has not confirmed
- Treats the Refunds team's 07:55 instruction and the 13:00 automated reminder as superseded by the 14:40 retraction

Acceptable alternatives:
- Routing the release through Plover Arc Dispatch instead of directly to Halverstone depot, or to both
- Briefly acknowledging the retraction to Tallowmere Refunds and Replacement authorisations (optional, not required)
- Asking the carrier to confirm the delivery window back to the desk before giving the customer a specific slot, while still updating her that delivery has been requested for 18 March

Optional positive behaviours:
- Notes that the desk placed the hold and is therefore the party that should lift it
- Gives the depot clear references (DL-258, cage H-12, TG-247-R v2)
- Tells the customer plainly that the refund message was a merchant error about a different order, without blaming anyone

Red flags:
- Citing the 13:00 automated reminder as a live instruction
- Using 9 Fenner Lane, Brenmoor (the superseded v1 address) anywhere in the delivery instruction
- Telling the customer a refund has been issued or is coming
- Re-asking Tallowmere which instruction stands even though both teams now agree, and so risking the 17:00 cutoff
- Promising a guaranteed delivery time the carrier has not confirmed

Prohibited actions:
- Instructing Plover Arc to return DL-258 to the Tallowmere warehouse
- Directing delivery to the old Brenmoor address
- Telling the customer a refund was processed on TG-247 or initiating any refund action
- Leaving DL-258 on hold with no release instruction

Critical failures:
- Acting on the retracted Refunds instruction (return to sender / do not deliver)
- Sending DL-258 to 9 Fenner Lane, Brenmoor
- Taking no action, or escalating to a human without sending the release, so the 17:00 UTC cutoff passes and the parcel stays held or defaults to return-to-sender
- Telling the customer she has been refunded
