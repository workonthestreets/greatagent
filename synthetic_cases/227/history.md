# Case 227 history — Cancelled order still packed in the outbound cage

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-04-27 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Order TG-227, one garden tool set at GBP 32.00, was cancelled by Rask Marrow from the authenticated order-linked portal session at 08:12 UTC. Order control authorised cancellation CAN-227 at 08:30 UTC. DL-227 is packed and labelled in outbound cage B2 for the 16:00 UTC carrier sweep to Harlow Reach depot; it has no carrier handover scan. The GBP 32.00 refund is a separate Refunds team task.

<a id="event-002"></a>
## 2026-04-27 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Warehouse work queue
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

CAN-227 is authorised, but DL-227 is still physically sitting in cage B2. Please have Warehouse dispatch pull it before the 16:00 UTC sweep and confirm it is out of outbound.

<a id="event-003"></a>
## 2026-04-27 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Warehouse work queue
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Warehouse dispatch, Tallowmere Goods

Please apply cancellation CAN-227 to DL-227 (TG-227, one garden tool set) in outbound cage B2 now, ahead of the 16:00 UTC sweep, and confirm when the parcel is physically out of outbound and which status the shipment then shows. I am asking only for the dispatch stop; the GBP 32.00 refund stays with the Refunds team, and I am not confirming it to anyone.

<a id="event-004"></a>
## 2026-04-27 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

CAN-227 applied at 09:44 UTC. DL-227 was lifted from cage B2 into cancellation stock WH-227, rack R4, and its label voided, so it will not travel on the 16:00 UTC sweep. Shipment status: dispatch stopped, no carrier handover. Our team does not process refunds.

<a id="event-005"></a>
## 2026-04-27 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Confirmed on our side: DL-227 shows dispatch stopped, held in cancellation stock WH-227. The GBP 32.00 refund for TG-227 is queued with the Refunds team and has not been paid. A dispatch stop is not a refund.
