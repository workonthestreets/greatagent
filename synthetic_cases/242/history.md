# Case 242 history — Delivered item confirmed broken; customer wants a replacement

All identities, records and communications are fictional. Total events: 6.

<a id="event-001"></a>
## 2026-05-12 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Damage intake, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Inline inspection record INS-242 for DL-242, order TG-242: one Ferncastle Supplies chilled grocery box, line value GBP 6.00, delivered from Harlow Reach depot on 2026-05-11. Recipient photos reviewed: outer box split along the base, two glass jars broken inside. Result: damage accepted for replacement assessment. Options open to the recipient: a refund of GBP 6.00, or a like-for-like replacement. Damage intake does not approve replacements or create orders; Replacement authorisations does. Erys Weld is in an authenticated order-linked portal session for TG-242.

<a id="event-002"></a>
## 2026-05-12 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Erys Weld, recipient
- **To:** Iona Quill, Rivet Delivery Desk

I have read the inspection result on TG-242. I would rather have the same chilled grocery box again than the GBP 6.00 refund. Please arrange a like-for-like replacement to the delivery address on the order.

<a id="event-003"></a>
## 2026-05-12 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Replacement authorisations, Tallowmere Goods

Please approve a like-for-like replacement for order TG-242 (DL-242, one chilled grocery box) on the basis of Damage intake’s accepted inspection record INS-242. The recipient, Erys Weld, chose replacement instead of the GBP 6.00 refund in an authenticated TG-242 portal session, for delivery to the address on the order. The approval decision is yours; I have not promised the recipient a replacement, a refund or a dispatch date.

<a id="event-004"></a>
## 2026-05-12 09:35:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Replacement authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Like-for-like replacement for TG-242 approved under APR-242 against INS-242, at no charge to the recipient; the GBP 6.00 refund will not also be issued. Passed to Order control to create the replacement order.

<a id="event-005"></a>
## 2026-05-12 09:50:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Replacement order RPL-242 created under APR-242 for delivery to the TG-242 address. One chilled grocery box reserved in chilled stock. Not yet picked or dispatched; no shipment reference has been issued.

<a id="event-006"></a>
## 2026-05-12 10:05:00 UTC — event 006

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Erys Weld, recipient

Replacement authorisations has approved a like-for-like replacement under APR-242, and Order control has created replacement order RPL-242 with one chilled grocery box reserved. It has not been dispatched and has no tracking reference yet. Approval and reserved stock are not dispatch.
