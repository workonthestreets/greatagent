# Case 244 history — Warehouse has the return but no refund review exists

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-14 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Warehouse work queue
- **From:** Warehouse receiving, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Return RT-244 for order TG-244, one Brindlewick Studio ceramic vase with an order value of GBP 4.50, was received at the returns bay on 2026-05-13 under receipt WH-244. It came from Copperfin Counter via North Sedgeglass depot. Warehouse receiving records receipt only; our role cannot open, approve or decline refunds. No refund review is linked to RT-244. Ambe Dorne is in an authenticated order-linked portal session for TG-244.

<a id="event-002"></a>
## 2026-05-14 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Ambe Dorne, customer
- **To:** Iona Quill, Rivet Delivery Desk

Tracking says my returned vase reached your warehouse yesterday, but RT-244 shows no refund review and nothing has moved. Please get the refund review started and send me its reference.

<a id="event-003"></a>
## 2026-05-14 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Refunds team, Tallowmere Goods

Please register a refund review for RT-244 (order TG-244, one ceramic vase, order value GBP 4.50) using Warehouse receiving’s receipt WH-244 of 2026-05-13, and send me the review case reference. The customer, Ambe Dorne, asked for the review in an authenticated TG-244 portal session. I have not told the customer that a refund is approved, and I have not given an amount or a date.

<a id="event-004"></a>
## 2026-05-14 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Refunds team, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Refund review RFR-244 registered for RT-244 at 09:41 UTC against receipt WH-244. Next update to the customer by 2026-05-19. No refund decision has been made.

<a id="event-005"></a>
## 2026-05-14 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Ambe Dorne, customer

The Refunds team has registered refund review RFR-244 for RT-244 using the warehouse receipt, and says it will update you by 2026-05-19. A registered review is not an approved refund; no decision or amount has been given.
