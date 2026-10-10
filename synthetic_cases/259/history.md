# Case 259 history — Dispatch and depot disagree about whether the parcel left

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-29 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Our load record shows DL-259, one bookshelf kit, loaded to route QM-07 at Quillmere depot at 07:40 UTC today. The same record holds a Quillmere depot note entered at 08:15 UTC. Inline note: DL-259 still in cage C4, not on van. Dispatch cannot tell from the system which entry is right. Galo Bramley is in an authenticated, order-linked portal session. Only Destination depot staff can find the parcel and scan it.

<a id="event-002"></a>
## 2026-05-29 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Galo Bramley, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My tracking says the bookshelf kit is loaded for delivery today, but the note under it says it is still in a cage at the depot. Which one is true? I need to know whether to stay home.

<a id="event-003"></a>
## 2026-05-29 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Depot work queue
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Destination depot, Plover Arc Logistics

Please locate DL-259 physically and record a fresh scan of where it is now. Dispatch shows it loaded to route QM-07 at 07:40 UTC; the 08:15 UTC depot note says cage C4, not on van. The desk treats neither entry as correct and has not told Galo which is true. Please leave both entries in place and add your scan.

<a id="event-004"></a>
## 2026-05-29 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Depot work queue
- **From:** Destination depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Physical scan SC-259 at 09:44 UTC: DL-259 is in cage C4 at Quillmere depot and is not on route QM-07. Both earlier entries are kept, and Dispatch has the scan to correct its load status.

<a id="event-005"></a>
## 2026-05-29 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

We have corrected the DL-259 load status to show the parcel at Quillmere depot in cage C4, citing SC-259. The 07:40 UTC load entry stays on file, marked superseded. DL-259 is not on a van and has no new delivery slot yet; delivery remains pending.
