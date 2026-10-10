# Case 249 history — Returned order still wanted at a confirmed address

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-19 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Warehouse work queue
- **From:** Warehouse returns, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

DL-249, order TG-249, one ceramic vase, came back to us via Harlow Reach depot on 2026-05-18 after its collection period at Sedgeglass Counter expired. Receipt WH-249: item intact, back in stock and held against TG-249. Orra Fane is in an authenticated order-linked portal session, and the stored destination on TG-249 is unchanged since the order was placed. Reshipment needs approval from Reshipment authorisations; Warehouse returns cannot approve it. Reshipment to an unchanged destination carries a GBP 4.50 delivery charge, applied only if Reshipment authorisations approves.

<a id="event-002"></a>
## 2026-05-19 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Orra Fane, recipient
- **To:** Iona Quill, Rivet Delivery Desk

I missed the collection at Sedgeglass Counter while I was away, but I still want the vase. The address shown on my TG-249 order is correct and has not changed. Please send it again; I accept the GBP 4.50 delivery charge.

<a id="event-003"></a>
## 2026-05-19 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Reshipment authorisations, Tallowmere Goods

Please approve reshipment of order TG-249, one ceramic vase held under Warehouse returns receipt WH-249, to the stored TG-249 destination. Orra Fane confirmed in an authenticated order-linked portal session that the destination is unchanged, and accepts the GBP 4.50 reshipment delivery charge. No address change is requested. I have not taken payment, sent a payment link or promised a delivery date.

<a id="event-004"></a>
## 2026-05-19 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Reshipment authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Reshipment of TG-249 approved under RSA-249 to the unchanged stored destination. GBP 4.50 delivery charge recorded against TG-249 as accepted by the customer. Passed to Warehouse dispatch.

<a id="event-005"></a>
## 2026-05-19 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

New shipment RSH-249 created for TG-249 under RSA-249; vase picked from stock and labelled. Awaiting carrier collection; not yet handed over to Plover Arc Logistics. A new reference is not dispatch or receipt.
