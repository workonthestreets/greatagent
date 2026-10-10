# Case 233 history — Tracker shows the order delivered but a box is missing

All identities, records and communications are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-05-03 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Inline tracking record, order TG-233 from Harlow Reach Interiors, dispatched by Wren Sterne as DL-233 in three parcels. Order-level status: Delivered, 2026-05-02 16:08 UTC. DL-233-2 (cushion set): delivered 15:51 UTC. DL-233-3 (picture frames): delivered 16:08 UTC. DL-233-1 (desk lamp): last scan sorted at Harlow Reach depot, 2026-05-02 05:47 UTC; no out-for-delivery, delivery, counter or locker scan. The order-level status took the latest parcel delivery scan. Recipient Ebbe Dorne has an authenticated order-linked portal session for TG-233. The parcel trace team, not the desk, traces parcels and corrects tracking status.

<a id="event-002"></a>
## 2026-05-03 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Ebbe Dorne, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My tracker says order TG-233 is delivered, but only two boxes came yesterday: the cushion set and the picture frames. The missing box is DL-233-1, the desk lamp. It is not at Copperfin Counter either. Please find it.

<a id="event-003"></a>
## 2026-05-03 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Parcel trace team, Plover Arc Logistics

Please trace DL-233-1 of order TG-233 by its own identifier and correct the order-level status. Tracking shows the order as Delivered, but only DL-233-2 and DL-233-3 have delivery scans; DL-233-1 was last scanned sorted at Harlow Reach depot on 2026-05-02 at 05:47 UTC. The signed-in recipient holds two boxes and names DL-233-1 as missing. I have not told the recipient the parcel is lost and have offered no refund or replacement.

<a id="event-004"></a>
## 2026-05-04 09:40:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Parcel trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace on DL-233-1 complete. It was found at Harlow Reach depot on 2026-05-03 at 10:52 UTC on a held-items shelf with no route scan, and order TG-233 was corrected at 10:58 UTC to Partly delivered, 2 of 3 parcels. DL-233-1 was delivered to the recipient’s address at 15:36 UTC, POD-233; the order now reads Delivered, 3 of 3 parcels. The delivery scan records the parcel count, not the condition of the lamp.
