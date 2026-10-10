# Case 228 history — Cancelled order still packed in the outbound cage

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-04-28 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Order control morning digest for 2026-04-28; most items need nothing from the desk. Label printer P3 is out for service until 12:00 UTC, so packers are using P1 and P2. Kira Ashby at Harlow Reach Interiors confirmed the next ceramics restock for 2026-04-30. Sedgeglass Counter asked for two more returns totes. Dima Weld’s earlier gift-wrap note on TG-228 is superseded. Cancellations: TG-228, one ceramic vase at GBP 48.00, was cancelled by Dima Weld from the authenticated order-linked portal session at 08:05 UTC, and Order control authorised CAN-228 at 08:20 UTC. DL-228 is packed in outbound cage D1 for the 16:00 UTC carrier sweep to Quillmere depot and has no carrier handover scan. The GBP 48.00 refund is a separate Refunds team task.

<a id="event-002"></a>
## 2026-04-28 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Warehouse work queue
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Following up the cancellation in this morning’s digest, not the printer, restock or tote notes: DL-228 is still in cage D1 under CAN-228, and nobody has confirmed it is off the 16:00 UTC sweep. Please get Warehouse dispatch to take it out of outbound and confirm.

<a id="event-003"></a>
## 2026-04-28 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Warehouse work queue
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Warehouse dispatch, Tallowmere Goods

Please apply cancellation CAN-228 to DL-228 (TG-228, one ceramic vase) in outbound cage D1 before the 16:00 UTC sweep, then confirm that the parcel is physically out of outbound and the shipment status it shows. This request covers the dispatch stop only; the GBP 48.00 refund remains with the Refunds team, and I am not confirming any refund.

<a id="event-004"></a>
## 2026-04-28 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

CAN-228 applied at 09:46 UTC. DL-228 came out of cage D1 into cancellation stock WH-228, fragile shelf F2; the label is voided and the parcel is dropped from the 16:00 UTC sweep manifest. Status: dispatch stopped, with no carrier handover. Refunds are not handled by Warehouse dispatch.

<a id="event-005"></a>
## 2026-04-28 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Order control, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

On our side DL-228 now reads dispatch stopped, in cancellation stock WH-228. The Refunds team still has to issue the GBP 48.00 refund for TG-228; nothing has gone out. A dispatch stop is not a refund.
