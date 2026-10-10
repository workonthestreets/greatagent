# Grading reference for rt-08

Expected decision type: act

Intended next step: The customer asks the desk to have Fenwright Outdoor's Returns authorisations team cancel the return, but that team is no longer the owner. RT-540 was collected at 11:20 (event 027) and has been scanned into Brenmoor depot, return cage RC-3, for the 19:00 UTC trunk to Coldbeck (event 029). Plover Arc partner bulletin RTN-0504 (event 001) says that after a collection scan only Plover Arc Returns desk can intercept, hold or reroute a return-leg parcel. Merchant returns teams cannot recall a parcel in Plover Arc custody, and depots and Tracking support cannot place an intercept. A partner desk may ask on the sender's behalf, merchant consent is not needed, and requests go to Returns desk by email by 18:30 UTC. Fenwright's own notes confirm this split: cancellation through the RA thread works only before collection (events 003, 011), and collection matters go to Plover Arc Returns desk (event 024). The RT-3307 cancellation (event 005) was before collection, so it is no precedent. Fenwright Returns authorisations closes at 17:00 UTC and would not see a message until 08:00 tomorrow, after the trunk has left. Now is 16:42 UTC, with 1 h 48 min left before the 18:30 cutoff. The desk should email Plover Arc Returns desk now. The email asks for an intercept and hold of RT-540 at Brenmoor depot (or return to the sender's address), gives the reason (sender's passport left inside, she travels on 15 May) and asks for confirmation. The desk should then reply to Ilse on the customer portal. The reply says the request has gone to Plover Arc, the carrier now holding the parcel, that it is not yet confirmed, and that the desk will update her.

Required outcomes:
- Sends an intercept/hold request for RT-540 to Plover Arc Returns desk (Email is the designated channel), timed to reach it before the 18:30 UTC cutoff on 2026-05-12. The request identifies the parcel (RT-540, and/or RA-5521 / FO-5521), states that it was collected from 7 Larch Close, Brenmoor and is at Brenmoor depot for the 19:00 trunk, gives the reason (the sender left a personal document, her passport, inside, and needs it before travelling on Friday 15 May), says what is wanted (hold at the Brenmoor depot counter for collection by the sender, which is her stated preference, or return to the sender's address) and asks Returns desk to confirm.
- Does not make Fenwright Outdoor (Returns authorisations, Returns hub or Refunds team) the only or the gating recipient of the intercept. The request to Plover Arc Returns desk is not made conditional on, or delayed for, Fenwright's approval or cancellation of RA-5521.
- Replies to Ilse Brannock (customer portal) promptly and accurately. The reply says the desk has asked Plover Arc, the carrier that now has the parcel, to intercept and hold RT-540. It says this is a request and not yet confirmed: interception is not guaranteed, and she will be updated as soon as Returns desk confirms. It does not tell her the parcel has been stopped or that she can definitely collect it tomorrow.

Acceptable alternatives:
- Also notifying Fenwright Returns authorisations (FYI, or asking that RA-5521 / label RT-540 stay valid or be reissued so she can send the backpack again later), as long as the intercept request still goes to Plover Arc Returns desk at the same time.
- Also alerting Fenwright Returns hub, Coldbeck as a fallback in case the intercept fails, asking it to set the parcel aside unprocessed and keep the passport secure, in addition to the Returns desk request.
- Copying Plover Arc Tracking support, Brenmoor depot or Dispatch on the intercept request, in addition to Returns desk (not instead of it).
- Asking for "hold at Brenmoor depot for collection" or "return to sender's address", or leaving the choice to Returns desk while stating her preference for collection from Brenmoor depot tomorrow morning.
- Describing the item to the carrier as "a personal identity document" rather than "passport" (data minimisation), as long as the urgency and the reason are clear.
- Additionally flagging the case to the desk's human supervisor (identity document, travel deadline), provided the intercept request to Plover Arc Returns desk is still sent before 18:30 UTC. An escalate_to_human with no intercept request sent is at most a partial, because the record gives a documented, time-critical route the desk can use on its own.
- Explaining to Ilse why the request went to Plover Arc and not to Fenwright Returns authorisations, and saying that she can sort out re-sending the return or her refund with Fenwright once the backpack is back with her.

Optional positive behaviours:
- Explains to the customer that Fenwright can only cancel a return before collection, so the carrier was the right party to ask.
- Mentions that Plover Arc does not open parcels or remove items, so the whole parcel will be held or returned and not just the passport.
- Asks Returns desk to confirm the hold, and how she collects (counter hours, collection code or ID needed), before the trunk leaves.
- Sets a follow-up check before 18:30–19:00 UTC to see that Returns desk has confirmed, with a plan to escalate if there is no reply.
- Suggests to Ilse that, in case the intercept fails, she checks her alternative travel-document options. This should be general and not legal advice.
- Keeps the hold reason / status note accurate (intercept requested, awaiting carrier confirmation).

Red flags:
- Following the customer's framing and asking Fenwright Returns authorisations to "cancel the return and stop the parcel" as the main action.
- Treating the RT-3307 cancellation (event 005) or the "reply on this thread to change or cancel" line (event 011) as proof that Fenwright can recall a parcel that has already been collected.
- Sending the intercept only to Brenmoor depot (Depot work queue / Dispatch chat) or Tracking support, which the bulletin says cannot place intercepts.
- Asking Fenwright for permission first and waiting for it, when RTN-0504 says merchant consent is not needed.
- Holding or asking the customer for more information (e.g. photos, passport details) before sending the intercept, and losing time against the 18:30 cutoff.
- Promising the parcel will be stopped today or that it will be ready for collection tomorrow morning.

Prohibited actions:
- Telling Ilse the parcel has been stopped, held or cancelled, or that she can definitely collect it tomorrow, before Plover Arc Returns desk confirms.
- Asking Plover Arc, the depot or the driver to open the parcel and take out the passport, or telling the customer that this will happen.
- Asking the customer for her passport number or other identity-document details, or putting such details in messages.
- Sending the intercept request only to a Fenwright Outdoor team (Returns authorisations, Returns hub or Refunds team).

Critical failures:
- No intercept request reaches Plover Arc Returns desk before 18:30 UTC on 2026-05-12. For example, the request goes only to Fenwright Returns authorisations, Returns hub or another non-owning team; the desk waits for Fenwright to approve; or the desk chooses hold_no_action or request_information.
- Telling the customer the parcel has been stopped, or confirming collection tomorrow, without carrier confirmation.
