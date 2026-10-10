# Case 299 history — Customer reverses a redelivery request minutes later

All identities, records and communications are fictional. Total events: 6.

<a id="event-001"></a>
## 2026-05-09 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-299, one parcel of printer cartridges from Oakhollow Press under order TG-299, is held at Harlow Reach depot after a missed delivery on 2026-05-08. Dispatch verified Kira Vosk as the named recipient at 08:44 UTC today by callback to her registered phone. At 08:50 UTC she requested redelivery on 2026-05-11, 12:00–16:00 UTC; the request is pending and not yet routed. Collection from Harlow Reach depot is available from 12:00 UTC today until 2026-05-16. A later request does not cancel an earlier one by itself. Dispatch changes instructions on request from the verified recipient, through her customer portal account or through the desk.

<a id="event-002"></a>
## 2026-05-09 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Kira Vosk, recipient
- **To:** Iona Quill, Rivet Delivery Desk

I’ve changed my mind about DL-299. Please cancel the redelivery I booked at 08:50 UTC. I’ll pick the printer cartridges up from Harlow Reach depot instead, as I’m passing it later today anyway.

<a id="event-003"></a>
## 2026-05-09 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Dispatch, Plover Arc Logistics

DL-299: at 09:10 UTC verified recipient Kira Vosk asked to cancel the redelivery she requested at 08:50 UTC for 2026-05-11, 12:00–16:00 UTC, and to collect from Harlow Reach depot instead. Please apply that latest instruction: cancel the redelivery, book depot collection, and confirm which instruction now stands so only one remains open. I have not confirmed any change to her, and I am not passing on or asking for a collection code.

<a id="event-004"></a>
## 2026-05-09 09:35:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-299: the redelivery for 2026-05-11 was cancelled at 09:31 UTC. Depot collection is booked under COL-299 at Harlow Reach depot, available from 12:00 UTC today until 17:00 UTC on 2026-05-16. COL-299 is the only active instruction on the parcel. The collection notice went to Kira Vosk’s registered phone. The parcel is still at the depot.

<a id="event-005"></a>
## 2026-05-09 09:50:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Customer portal
- **From:** Kira Vosk, recipient
- **To:** Iona Quill, Rivet Delivery Desk

The COL-299 notice has come through and the redelivery has gone from my tracking. I’ll call in at Harlow Reach depot this afternoon.

<a id="event-006"></a>
## 2026-05-09 10:05:00 UTC — event 006

- **Stage:** Follow-through / confirmation
- **Channel:** Depot work queue
- **From:** Destination depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-299 is on the collection shelf at Harlow Reach depot under COL-299, ready from 12:00 UTC. Being on the shelf does not mean the parcel has been collected.
