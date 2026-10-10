# Case 296 history — Return reached the carrier depot but not the merchant

All identities, records and communications are fictional. Total events: 6.

<a id="event-001"></a>
## 2026-05-06 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Depot work queue
- **From:** North Sedgeglass depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

RT-296: return of one wool blanket for Tallowmere Goods order TG-296. Dropped at Ashvane Counter at 14:10 UTC on 2026-05-02; arrived North Sedgeglass depot at 19:30 UTC the same day; departed for the Tallowmere Goods returns warehouse at 05:50 UTC on 2026-05-03. No merchant receiving scan is recorded. The departure scan shows the parcel left this depot, not that the merchant holds it. Tracking support verified Kira Bramley as the sender of RT-296 at 08:45 UTC today against her counter drop-off receipt. The Returns trace team runs traces from depot departure to merchant receipt.

<a id="event-002"></a>
## 2026-05-06 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Kira Bramley, customer
- **To:** Iona Quill, Rivet Delivery Desk

My return RT-296 left North Sedgeglass depot on 2026-05-03 and tracking hasn’t moved since. Tallowmere Goods say they can’t see it yet. Can someone find out when the merchant actually has the blanket in its warehouse?

<a id="event-003"></a>
## 2026-05-06 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Returns trace team, Plover Arc Logistics

Please trace return RT-296 (order TG-296, one parcel) from its departure scan at North Sedgeglass depot at 05:50 UTC on 2026-05-03 to receipt at the Tallowmere Goods returns warehouse. A departure or dock scan will not close this: please confirm physical acceptance by the merchant warehouse, with its receiving reference and time. The sender, Kira Bramley, was verified by Tracking support. I am not asking about the refund or the blanket’s condition, and I have given her no date.

<a id="event-004"></a>
## 2026-05-06 09:35:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Returns trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace RTT-296 opened. Linehaul shows RT-296 on the 2026-05-03 trailer to the Tallowmere Goods returns warehouse, with a dock handover scan at 13:05 UTC that day. A dock handover is not merchant receipt. We have asked Warehouse receiving, Tallowmere Goods, to locate the parcel and confirm acceptance.

<a id="event-005"></a>
## 2026-05-06 09:50:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Warehouse receiving, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

RT-296 was found among unbooked returns from the 2026-05-03 trailer and physically received at 09:46 UTC today under WH-296: one parcel. This records arrival only. The blanket has not been inspected, and the Refunds team acts only after inspection.

<a id="event-006"></a>
## 2026-05-06 10:05:00 UTC — event 006

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Returns trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace RTT-296 closed on merchant receipt WH-296 at 09:46 UTC. The closure confirms physical receipt only; it does not cover accepted condition or a refund.
