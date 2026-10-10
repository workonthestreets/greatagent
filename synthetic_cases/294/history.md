# Case 294 history — Return reached the carrier depot but not the merchant

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-04 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Depot work queue
- **From:** East Copperfin depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

RT-294: return of one medication parcel for Tallowmere Goods order TG-294, sent by Cael Coyle. Accepted at Copperfin Counter at 11:20 UTC on 2026-05-01; arrived East Copperfin depot at 18:05 UTC the same day; departed East Copperfin depot for the Tallowmere Goods returns warehouse at 06:40 UTC on 2026-05-02. No merchant receiving scan is recorded. The departure scan shows the parcel left this depot; it does not show that the merchant holds it. Traces from depot departure to merchant receipt are run by the Returns trace team. Cael Coyle is signed in to the customer portal session linked to TG-294.

<a id="event-002"></a>
## 2026-05-04 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Cael Coyle, customer
- **To:** Iona Quill, Rivet Delivery Desk

Tracking on RT-294 hasn’t changed since it left East Copperfin depot on 2026-05-02. When will Tallowmere Goods actually have my return? The medication was unopened when I handed it in at Copperfin Counter. My return to Quillmere Fabrication went the same week and Zeph Ulm there confirmed it the next day, so I don’t see why this one is stuck. The counter receipt says 11:18, not 11:20, if that matters. And my refund hasn’t come through either, so please chase that too.

<a id="event-003"></a>
## 2026-05-04 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Returns trace team, Plover Arc Logistics

Please trace return RT-294 (order TG-294, one parcel) from its departure scan at East Copperfin depot at 06:40 UTC on 2026-05-02 through to receipt at the Tallowmere Goods returns warehouse. The departure scan is not enough to close this: please confirm physical acceptance by the merchant warehouse, with its receiving reference and time. I am not asking about the refund or the condition of the contents, and I have given the customer no date.

<a id="event-004"></a>
## 2026-05-04 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Returns trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace RTT-294 opened. Linehaul records show RT-294 on the 2026-05-02 East Copperfin trailer to the Tallowmere Goods returns warehouse, unloaded at the warehouse dock at 15:30 UTC that day. Dock unloading is not merchant receipt. We have asked Warehouse receiving, Tallowmere Goods, to check its unreceipted returns cage and confirm acceptance to the desk.

<a id="event-005"></a>
## 2026-05-04 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Warehouse receiving, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

RT-294 was found in the unreceipted returns cage and physically received at 09:58 UTC today under WH-294: one parcel. This records arrival only. It is not an inspection or acceptance of condition, and it is not a refund; the Refunds team acts only after inspection.
