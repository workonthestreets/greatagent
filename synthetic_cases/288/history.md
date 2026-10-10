# Case 288 history — Return reached the carrier depot but not the merchant

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-04-28 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Depot work queue
- **From:** Quillmere depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Return RT-288, order TG-288: one camera tripod going back to Tarn Loom Works. Dropped at Copperfin Counter on 2026-04-24. Scanned in at Quillmere depot on 2026-04-25 at 06:42 UTC; line-haul departure scan towards the merchant at 18:10 UTC the same day. No merchant receiving scan is on the record. Customer Pavo Vosk was verified by the operator against TG-288 when the return label was issued. Merchant receipt means physical acceptance recorded by the merchant's warehouse; a departure or in-transit scan is not receipt. Traces beyond the depot are run by the Returns trace team.

<a id="event-002"></a>
## 2026-04-28 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Pavo Vosk, customer
- **To:** Iona Quill, Rivet Delivery Desk

I dropped my tripod return at Copperfin Counter last Friday. Tracking says it left Quillmere depot on Saturday evening, and the person at the counter told me that means it's as good as delivered. Tarn Loom Works' chat says refunds take up to 14 days after they receive it. The leg clamp kept slipping, which is why it's going back, and I lost a different parcel last month, so I'm wary. I just want to know when Tarn Loom Works actually has it.

<a id="event-003"></a>
## 2026-04-28 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Returns trace team, Plover Arc Logistics

Please trace return RT-288, order TG-288, one camera tripod, from Quillmere depot to merchant receipt at Tarn Loom Works. The record shows a depot scan at 06:42 UTC and a line-haul departure scan at 18:10 UTC on 2026-04-25, and no merchant receiving scan since. Please report back only when the merchant's warehouse has physically accepted the parcel, giving the time and the receiving record; a departure or in-transit scan does not answer this. The desk is not asking about the item's condition or the refund.

<a id="event-004"></a>
## 2026-04-28 09:45:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Returns trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace opened on RT-288. The line-haul manifest shows the parcel offloaded at the Tarn Loom Works returns dock on 2026-04-26 at 07:55 UTC, but the dock did not scan it. That is a carrier handover, not merchant acceptance. We have asked Tarn Loom Works warehouse receiving to check physically and to reply to the desk with their receiving record.

<a id="event-005"></a>
## 2026-04-28 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Joss Holt, Tarn Loom Works warehouse receiving
- **To:** Iona Quill, Rivet Delivery Desk

Return RT-288 was found in our returns bay and accepted onto receiving record WH-2885 at 09:58 UTC today. It came in on the 2026-04-26 inbound but was not scanned at the dock. Inspection and any refund are handled separately by our returns team. Receipt is not an accepted condition or a refund.
