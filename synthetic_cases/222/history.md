# Case 222 history — Cancelled order still packed in the outbound cage

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-04-22 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Cancellation for order TG-222 is authorised. Please work from cancellation note CAN-222; its key lines are excerpted inline here rather than attached. Inline cancellation note CAN-222: order TG-222, one coffee grinder, GBP 48.00; customer Fenna Holt asked to cancel by phone, and Order support verified her by callback to the order number at 08:25 UTC; cancellation authorised by Order control at 08:40 UTC; shipment DL-222 packed in outbound cage C4, consigned to Ashvane Counter; no carrier handover scan; refund of GBP 48.00 to the original payment method to be raised by the Refunds team. The next carrier sweep of the outbound cages leaves for North Sedgeglass depot at 16:00 UTC today.

<a id="event-002"></a>
## 2026-04-22 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Warehouse work queue
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Please get Warehouse dispatch to take DL-222 out of outbound before the 16:00 UTC sweep, using the cancellation reference and cage shown in this morning’s note excerpt. The cancellation is authorised; the physical stop is not yet confirmed. The GBP 48.00 refund stays with the Refunds team.

<a id="event-003"></a>
## 2026-04-22 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Warehouse work queue
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Warehouse dispatch, Tallowmere Goods

Please apply cancellation CAN-222 to DL-222 (order TG-222, one coffee grinder) in outbound cage C4 before the 16:00 UTC sweep. Once the parcel is physically out of outbound, please confirm that and the shipment status it now shows. This is a dispatch stop only; I am not asking you to action the GBP 48.00 refund, which the Refunds team raises, and I am not confirming any refund to the customer.

<a id="event-004"></a>
## 2026-04-22 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

CAN-222 applied at 09:43 UTC. DL-222 was lifted out of cage C4 and booked into cancellation stock location WH-222, bay K1; its label is voided and it is off the 16:00 UTC sweep manifest. Shipment status: dispatch stopped. No carrier handover happened, and refunds are outside our team.

<a id="event-005"></a>
## 2026-04-22 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Our order view now shows DL-222 as dispatch stopped in cancellation stock WH-222. The Refunds team holds the GBP 48.00 refund for TG-222 as an open task, and nothing has been paid. A dispatch stop is not a refund.
