# Case 251 history — Returned order still wanted at a confirmed address

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-21 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Warehouse work queue
- **From:** Warehouse returns, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

DL-251 for order TG-251 came back through Quillmere depot as return-to-sender RT-251 after its Ashvane Counter collection window lapsed. The desk lamp passed our check and went into sellable stock at 16:20 UTC on 2026-05-20. Order record: Dima Thane’s portal session is authenticated and linked to TG-251, and the stored destination, 6 Tansy Row, Quillmere, has not been edited since the first dispatch. A second dispatch needs approval from Reshipment authorisations; the reshipment charge for this order type is GBP 4.50. No refund is raised on TG-251.

<a id="event-002"></a>
## 2026-05-21 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Dima Thane, recipient
- **To:** Iona Quill, Rivet Delivery Desk

I still want the desk lamp, so please have it sent again. The address on my account, 6 Tansy Row, Quillmere, is correct and unchanged since I ordered. I accept the GBP 4.50 reshipment charge.

<a id="event-003"></a>
## 2026-05-21 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Reshipment authorisations, Tallowmere Goods

Please approve reshipment of TG-251 to its verified, unchanged destination, 6 Tansy Row, Quillmere. Warehouse returns holds the desk lamp in sellable stock under RT-251, and no refund is raised. Dima confirmed that address from an authenticated order-linked session and accepts the GBP 4.50 reshipment charge. The desk has taken no payment, sent no payment link and given no dispatch date.

<a id="event-004"></a>
## 2026-05-21 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Reshipment authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Approved under RS-251: TG-251 reships to 6 Tansy Row, Quillmere, and the GBP 4.50 charge is added to the order. Warehouse dispatch is instructed to raise the new shipment. Approval alone is not dispatch.

<a id="event-005"></a>
## 2026-05-21 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

New shipment DL-251-R is raised under RS-251 for the desk lamp to the stored destination. The label is printed and the parcel waits in the outbound bay for the next Plover Arc Logistics collection; it has not been handed over. A new reference is not dispatch or receipt.
