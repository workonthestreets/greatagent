# Case 291 history — Customer reverses a redelivery request minutes later

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-01 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-291, one parcel holding a wool blanket from Quillmere Fabrication under order TG-291, has been at Quillmere depot since a missed delivery on 2026-04-30. Dispatch verified Vane Yarrow as the named recipient at 08:46 UTC today by callback to her registered phone. At 08:50 UTC we recorded her request for redelivery on 2026-05-02, 08:00–12:00 UTC. It is pending and not yet routed. Depot collection at Quillmere depot is also available, from 13:00 UTC today until the hold ends on 2026-05-08. A later request does not cancel an earlier one automatically. Dispatch books or cancels on instruction from the verified recipient, through her customer portal account or through the desk.

<a id="event-002"></a>
## 2026-05-01 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Vane Yarrow, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Change of plan, sorry. Please cancel the redelivery I asked for at 08:50 UTC on DL-291. I’ll collect the wool blanket from Quillmere depot myself instead, and I don’t want a driver coming out tomorrow as well.

<a id="event-003"></a>
## 2026-05-01 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Dispatch, Plover Arc Logistics

DL-291: at 09:10 UTC verified recipient Vane Yarrow asked to cancel the redelivery she requested at 08:50 UTC for 2026-05-02, 08:00–12:00 UTC, and to collect from Quillmere depot instead. Please apply that latest instruction: cancel the redelivery, book depot collection, and confirm which instruction now stands so that only one is open. I have not told her the change is made. Please send any collection code to her directly, not to the desk.

<a id="event-004"></a>
## 2026-05-01 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-291: the redelivery request for 2026-05-02 was cancelled at 09:41 UTC. Depot collection is booked under COL-291 at Quillmere depot, available from 13:00 UTC today until 17:00 UTC on 2026-05-08. COL-291 is now the only active instruction on the parcel. The collection notice and code went to Vane Yarrow’s registered phone. The parcel is still at the depot; no collection has taken place.

<a id="event-005"></a>
## 2026-05-01 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Vane Yarrow, recipient
- **To:** Iona Quill, Rivet Delivery Desk

The COL-291 collection notice has arrived, and tomorrow’s redelivery no longer shows on my tracking. I’ll go to Quillmere depot this afternoon. Until then the blanket stays at the depot; I haven’t collected it.
