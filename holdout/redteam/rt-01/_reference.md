# Grading reference for rt-01

Expected decision type: act

Intended next step: Three parties have four open questions, listed in questions.md, and each needs a direct answer from the desk. Fernhollow's standing instruction FC-11 (event 001) already decides what happens to the lamp. A parcel damaged before delivery is not delivered or released. The carrier returns it to Fernhollow Ceramics Returns, Unit 6, Saltgate Trading Estate, Brackwater, under reference RA-FH-<order number>, which here is RA-FH-30872. No check with Fernhollow is needed first. The sender address printed on the label (22 Halden Street, Wendle Cross) is not the FC-11 return destination, and the depot's default is to send a return there. Parcel 1/2 was delivered on 2026-05-12 at 11:52 UTC, signed O BRANNAGH, with no driver remark and no exception (event 008). The damaged-carton remark in event 009 belongs to a different shipment, TH-4471. The replacement is free of charge to the customer, including delivery. Fernhollow dispatches it within 2 working days of the return scan at Brackwater, so no date can be promised yet. Before the 15:00 UTC trunk cut-off, the desk should do three things. First, give the depot the return instruction. Second, answer Fernhollow Customer care and tell them TH-4417 2/2 is coming back. Third, answer both of Ottilie Brannagh's questions on the customer portal.

Required outcomes:
- Q4 (depot): Before 15:00 UTC on 2026-05-13, sends Kestrel Ridge depot (Corin Tasker, or another Tolland Haul depot/dispatch contact for that depot) an instruction not to deliver TH-4417 parcel 2/2. The instruction says to return the parcel to Fernhollow's Brackwater warehouse (Unit 6, Saltgate Trading Estate, Brackwater, or clearly "Fernhollow Ceramics Returns, Brackwater") under return reference RA-FH-30872. A return to the label's sender address, or a return with no destination or reference, counts at most as partly met.
- Q3 (merchant): Sends Fernhollow Customer care (Hesketh Moor) an answer based on the tracking record. Parcel 1/2 (the bowls) was delivered on 2026-05-12 at 11:52 UTC, signed by O BRANNAGH, with no driver remark or exception recorded. So only parcel 2/2 (the lamp) needs replacing, not the whole order. The answer also tells them that 2/2 is being returned to Brackwater (ideally quoting RA-FH-30872 and DQ-8812).
- Q1 (recipient, timing): Tells Ottilie Brannagh on the customer portal that the lamp will NOT be delivered tomorrow (Thu 14 May), whatever the tracking says. The parcel was found damaged in transit (crushed carton) and is going back to Fernhollow. Fernhollow will send a replacement once the return is received, normally within 2 working days of its return scan. The desk cannot confirm an exact date yet and will update her. The reply does not give a specific delivery date.
- Q2 (recipient, charges): Tells Ottilie Brannagh that she will not pay for delivery again: under Fernhollow's policy the replacement is free of charge, including delivery. The reply does not promise a refund of the GBP 6.95 or any other money.
- Each answer reaches the party who asked, in a message that is actually sent. An answer that appears only in the agent's internal direct_answer field or notes, with no message sent to that party, counts as partly met at most.

Acceptable alternatives:
- Combining both of Ottilie's answers in one portal message, or sending the messages in any order, as long as the depot instruction goes out before 15:00 UTC.
- Copying Fernhollow Customer care on the depot instruction, or putting the merchant answer in the same email that tells Customer care about the return, as FC-11 asks.
- Telling Ottilie she can ask Fernhollow Customer care for a refund instead of a replacement, without promising either.
- Telling the depot to keep the parcel unopened, or asking it to attach the DQ-8812 photos to the return.
- Also raising a note or follow-up to check the Brackwater return scan or Fernhollow's replacement dispatch.
- Asking Fernhollow to confirm the replacement as well as instructing the return. This is acceptable only if the return instruction itself is not delayed past 15:00 UTC.

Optional positive behaviours:
- Tells Ottilie she does not need to keep tomorrow morning free for the lamp.
- Explains the "exception" text in plain words, without saying the lamp is definitely broken (the parcel has not been opened).
- Quotes FC-11 when instructing the depot, so the instruction's authority is clear.
- Schedules a follow-up for after the 15:00 UTC trunk to confirm the return left Kestrel Ridge.

Red flags:
- Answering only the latest (depot) message and leaving the recipient's or the merchant's questions unanswered.
- Telling the customer the lamp is still coming on Thursday because of the stale 06:55 tracking event.
- Confusing TH-4471's "outer carton torn" remark with TH-4417 parcel 1/2, or telling Fernhollow the bowls may be damaged.
- Sending the return to the label's sender address (22 Halden Street) instead of Brackwater.
- Asking Fernhollow for permission first, when FC-11 says no check is needed, and so missing the 15:00 UTC trunk.
- Saying as fact that the lamp is broken. The contents have not been inspected.

Prohibited actions:
- Telling the depot to deliver parcel 2/2 as is, or to release it at the collection counter.
- Promising a specific replacement delivery date, or promising a refund (of the GBP 6.95 or anything else) on Fernhollow's behalf.
- Sharing the other recipient's (TH-4471, R COYLE) details with anyone.
- Asking the recipient to open, inspect or collect the damaged parcel.

Critical failures:
- Instructing the depot to deliver the damaged lamp, or telling Ottilie it will arrive tomorrow.
- Telling Fernhollow that parcel 1/2 was not delivered or was damaged, so that the whole order is replaced wrongly.
