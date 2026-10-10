# Case 297 history — Return reached the carrier depot but not the merchant

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-07 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** North Sedgeglass depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

RT-297: return of one chilled grocery box for Tallowmere Goods order TG-297, sent by Kira Varro. Accepted at Ashvane Counter at 10:30 UTC on 2026-05-05; arrived North Sedgeglass depot at 17:45 UTC the same day; departed for the Tallowmere Goods returns warehouse at 06:15 UTC on 2026-05-06. No merchant receiving scan is recorded, and departure from this depot is not receipt by the merchant. Kira Varro is signed in to the customer portal session linked to TG-297. The Returns trace team traces returns from depot departure to merchant receipt.

<a id="event-002"></a>
## 2026-05-07 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Kira Varro, customer
- **To:** Iona Quill, Rivet Delivery Desk

Tracking for RT-297 stops at the departure from North Sedgeglass depot on 2026-05-06. I need to know when Tallowmere Goods actually has the chilled grocery box back. Please find out where it is.

<a id="event-003"></a>
## 2026-05-07 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Returns trace team, Plover Arc Logistics

Please trace return RT-297 (order TG-297, one chilled grocery box) from its departure scan at North Sedgeglass depot at 06:15 UTC on 2026-05-06 to receipt at the Tallowmere Goods returns warehouse. Please confirm physical acceptance by the merchant warehouse with its receiving reference; a departure or in-transit scan will not close this. I am not asking about the refund or the box’s condition, and I have given the customer no date or handling advice.

<a id="event-004"></a>
## 2026-05-07 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Returns trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace RTT-297 opened. Trailer records place RT-297 at the chilled intake of the Tallowmere Goods returns warehouse from 14:20 UTC on 2026-05-06. No receiving scan is logged there. Arrival at the intake is not merchant receipt. We have asked Warehouse receiving, Tallowmere Goods, to check the chilled intake and confirm acceptance.

<a id="event-005"></a>
## 2026-05-07 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Warehouse receiving, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

RT-297 was physically received at the chilled intake at 09:57 UTC today under WH-297: one chilled grocery box. This confirms arrival only. Condition has not been assessed, and no refund decision has been made; the Refunds team acts only after inspection.
