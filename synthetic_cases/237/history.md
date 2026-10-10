# Case 237 history — Tracker shows the order delivered but a box is missing

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-07 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Inline tracking record, order TG-237 from Harlow Reach Interiors, dispatched by Hest Coyle as DL-237 in three boxes. Order-level status: Delivered, 2026-05-06 16:02 UTC. DL-237-1 (chilled grocery box, chilled route): delivered 11:18 UTC. DL-237-3 (linen set): delivered 16:02 UTC. DL-237-2 (glass vase): last scan loaded to van at East Copperfin depot, 2026-05-06 06:41 UTC; no delivery, counter or locker scan. The order-level status follows the latest parcel delivery scan. Recipient Rask Reeve has an authenticated order-linked portal session for TG-237. The parcel trace team, not the desk, traces parcels and corrects order status.

<a id="event-002"></a>
## 2026-05-07 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Rask Reeve, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My order page says TG-237 was delivered yesterday, but I only have two of the three boxes: the chilled grocery box and the linen set. The missing one is DL-237-2, the glass vase. No card was left and Ashvane Counter has nothing for me. Please trace it.

<a id="event-003"></a>
## 2026-05-07 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Parcel trace team, Plover Arc Logistics

Please trace DL-237-2 of order TG-237 by its own identifier and correct the order-level status, which reads Delivered on the strength of DL-237-1 and DL-237-3 alone. DL-237-2 was last scanned loaded to van at East Copperfin depot on 2026-05-06 at 06:41 UTC, with no delivery scan. The signed-in recipient holds two boxes and names DL-237-2 as missing. I am not treating the parcel as lost and have offered no refund or replacement.

<a id="event-004"></a>
## 2026-05-07 09:55:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Parcel trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace opened on DL-237-2. Found at East Copperfin depot at 09:48 UTC in the end-of-shift return cage for van route 12, with no delivery attempt recorded. Booked out for delivery today, 13:00–17:00 UTC. Order TG-237 status corrected to Partly delivered, 2 of 3 parcels. Located is not delivered.

<a id="event-005"></a>
## 2026-05-08 09:40:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Parcel trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-237-2 delivered 2026-05-07 at 14:52 UTC, POD-237. Order TG-237 status now reads Delivered, 3 of 3 parcels. The scan confirms the parcel count; it is not a check of the vase or any other contents.
