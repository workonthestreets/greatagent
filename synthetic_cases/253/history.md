# Case 253 history — Delivery service charged twice on one invoice

All identities, records and communications are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-05-23 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Business portal
- **From:** Corin Garrow, Oakhollow Press receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

Sent from the authenticated Oakhollow Press business portal session. Inline excerpt, Plover Arc Logistics invoice INV-253 dated 2026-05-21: line 1, DL-253 delivery service, 2026-05-19, GBP 12.00; line 2, DL-253 delivery service, 2026-05-19, GBP 12.00; total GBP 24.00; queries to Business billing, Plover Arc Logistics. Our goods-in log shows a single delivery of DL-253, one office chair, from Harlow Reach depot on 2026-05-19. Our ledger shows both lines unpaid.

<a id="event-002"></a>
## 2026-05-23 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Corin Garrow, Oakhollow Press receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

INV-253 bills our one DL-253 delivery twice at GBP 12.00. Neither line has been paid. Please have Plover Arc Logistics check the pair and credit one if it is a repeat.

<a id="event-003"></a>
## 2026-05-23 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Business billing, Plover Arc Logistics

Please review lines 1 and 2 of INV-253. Each reads DL-253 delivery service, 2026-05-19, GBP 12.00, and Corin Garrow, writing from Oakhollow Press’s authenticated business portal session, reports one delivery that day with neither line paid. If you confirm duplication, please issue a credit and the revised balance. The desk has not judged either line wrong and has given no payment advice.

<a id="event-004"></a>
## 2026-05-23 09:55:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Business billing, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Reviewed: line 2 of INV-253 repeats line 1 for the single DL-253 delivery service on 2026-05-19. Credit note CN-253 for GBP 12.00 is raised against line 2, and the revised INV-253 balance is GBP 12.00, still unpaid. A credit note is not cash received.
