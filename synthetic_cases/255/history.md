# Case 255 history — Warehouse has the return but no refund review exists

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-25 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Warehouse work queue
- **From:** Warehouse receiving, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Inline receipt WH-255: return RT-255 for order TG-255, one coffee grinder, booked in at 14:10 UTC on 2026-05-23, routed from Ashvane Counter through Quillmere depot. Return value on RT-255: GBP 48.00. No refund review is open against it. Receiving records arrivals only; refund decisions sit with the Refunds team. Yalo Ashby’s portal session is authenticated and linked to TG-255.

<a id="event-002"></a>
## 2026-05-25 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Yalo Ashby, customer
- **To:** Iona Quill, Rivet Delivery Desk

The warehouse has had my coffee grinder since 2026-05-23, yet my order shows no refund review for the GBP 48.00. Please get the review started.

<a id="event-003"></a>
## 2026-05-25 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Refunds team, Tallowmere Goods

Please register a refund review for RT-255 / TG-255 against warehouse receipt WH-255, which books in one coffee grinder at 14:10 UTC on 2026-05-23; the recorded return value is GBP 48.00. Yalo Ashby asks for the review from an authenticated order-linked session. Please reply with the review case reference. The desk is not approving, pricing or dating any refund.

<a id="event-004"></a>
## 2026-05-25 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Refunds team, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Refund review RF-255 is registered at 09:44 UTC for RT-255, linked to WH-255, with a claimed value of GBP 48.00. The reference now shows in Yalo’s order thread. Next update by 2026-05-28, 16:00 UTC. No decision on eligibility or payment has been taken.

<a id="event-005"></a>
## 2026-05-25 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Yalo Ashby, customer
- **To:** Iona Quill, Rivet Delivery Desk

I can see RF-255 on my order and will watch for the update by 2026-05-28. I understand the refund itself is not approved yet.
