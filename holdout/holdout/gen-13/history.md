# Case gen-13 history — Merchant refund and replacement teams conflict over a held reshipment, then the refund instruction is retracted

All identities, records and communications are fictional. Total events: 40.

<a id="event-001"></a>
## 2026-03-16 09:02:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-231 (Tallowmere Goods, order TG-247) was found with crushed outer packaging and broken contents (glass kettle) at Brenmoor depot sort on 2026-03-15. The item was recorded as damaged beyond delivery and disposed of under damage policy. Damage report DR-231 is attached to the shipment record. Nothing will be delivered on DL-231.

<a id="event-002"></a>
## 2026-03-16 09:30:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Ottilie Marsh, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My original kettle order arrived broken and I was told a replacement would be sent. I've moved, so it needs to come to my new flat in Halverstone. Can you tell me where it is and when I'll get it? New address from 15 March: Flat 3B, 22 Quayside Terrace, Halverstone. The order still has my old address, 9 Fenner Lane, Brenmoor. I'm not after a refund, I just want the kettle.

<a id="event-003"></a>
## 2026-03-16 09:41:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Replacement authorisations, Tallowmere Goods

Order TG-247 / DL-231: Plover Arc recorded the contents as damaged in transit and disposed of them (damage report DR-231). The customer, Ottilie Marsh, is asking for a replacement and does not want a refund. Please review whether a replacement can be authorised.

<a id="event-004"></a>
## 2026-03-16 09:42:00 UTC — event 004

- **Channel:** Email
- **From:** Tallowmere Goods auto-acknowledgement
- **To:** Iona Quill, Rivet Delivery Desk

Thank you for contacting Tallowmere Goods. Your message has been received by Replacement authorisations and logged as case C-88214. We aim to reply within one business day.

<a id="event-005"></a>
## 2026-03-16 10:05:00 UTC — event 005

- **Channel:** Email
- **From:** Greywick Homewares newsletter
- **To:** Iona Quill, Rivet Delivery Desk

Spring partner bulletin: Greywick's new tableware range ships from 1 April. Packaging specs for fragile items are updated in the partner handbook, section 4.

<a id="event-006"></a>
## 2026-03-16 10:22:00 UTC — event 006

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

FYI: DL-226 (Brineleaf chilled box) is on today's Brenmoor afternoon route. The recipient's preferred window is held. No action needed from the desk.

<a id="event-007"></a>
## 2026-03-16 11:20:00 UTC — event 007

- **Channel:** Email
- **From:** Replacement authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Replacement TG-247-R (v1) is authorised: 1 × Corrie glass kettle, no charge. Ship to the address on the order, 9 Fenner Lane, Brenmoor. Warehouse dispatch has been notified.

<a id="event-008"></a>
## 2026-03-16 11:48:00 UTC — event 008

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Replacement authorisations, Tallowmere Goods

Re TG-247-R: the customer moved on 15 March and asked for delivery to Flat 3B, 22 Quayside Terrace, Halverstone, not 9 Fenner Lane, Brenmoor. Please update the authorisation address before Warehouse dispatch ships it.

<a id="event-009"></a>
## 2026-03-16 12:30:00 UTC — event 009

- **Channel:** Business portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Note added to DL-219 by Collections control: 'Collection rebooked to 2026-03-17 AM, shipper confirmed.'

<a id="event-010"></a>
## 2026-03-16 13:15:00 UTC — event 010

- **Channel:** Email
- **From:** Replacement authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

TG-247-R is updated to v2, which supersedes v1. Delivery address: Flat 3B, 22 Quayside Terrace, Halverstone. Contents unchanged. Warehouse dispatch has the v2 instruction. — Dana Rook, Replacement authorisations

<a id="event-011"></a>
## 2026-03-16 14:02:00 UTC — event 011

- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Replacement TG-247-R v2 is packed. Carrier label DL-258 is printed to Flat 3B, 22 Quayside Terrace, Halverstone. Plover Arc collection is booked for 16:00 today.

<a id="event-012"></a>
## 2026-03-16 14:40:00 UTC — event 012

- **Channel:** Email
- **From:** Brineleaf customer care
- **To:** Iona Quill, Rivet Delivery Desk

Thanks for the help with DL-226 earlier. Please close our ticket BL-551.

<a id="event-013"></a>
## 2026-03-16 16:10:00 UTC — event 013

- **Channel:** Business portal
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-258: collected from Tallowmere warehouse at 16:07 UTC. Destination: Halverstone depot.

<a id="event-014"></a>
## 2026-03-16 16:11:00 UTC — event 014

- **Channel:** Business portal
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-258: collected from Tallowmere warehouse at 16:07 UTC. Destination: Halverstone depot. (duplicate scan event)

<a id="event-015"></a>
## 2026-03-16 16:30:00 UTC — event 015

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Ottilie Marsh, recipient

Tallowmere has authorised a replacement kettle to your new address, Flat 3B, 22 Quayside Terrace, Halverstone. It was collected today as DL-258. I'll update you when it reaches the Halverstone depot.

<a id="event-016"></a>
## 2026-03-16 19:45:00 UTC — event 016

- **Channel:** Email
- **From:** Plover Arc Logistics newsletter
- **To:** Iona Quill, Rivet Delivery Desk

Network update: Brenmoor depot sort hours are extended on weekdays until 22:00 from 23 March.

<a id="event-017"></a>
## 2026-03-17 07:55:00 UTC — event 017

- **Channel:** Email
- **From:** Refunds team, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Re: TG-247. The customer has been refunded in full under refund REF-274. Do not reship. Please arrange for the carrier to return DL-258 to the Tallowmere warehouse unopened. — Refunds team

<a id="event-018"></a>
## 2026-03-17 08:10:00 UTC — event 018

- **Stage:** Agent action
- **Channel:** Dispatch chat
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Dispatch, Plover Arc Logistics

Please hold DL-258 at Halverstone depot when it arrives. Do not deliver it and do not return it to sender. Two Tallowmere teams have given conflicting instructions, and I'll send a release or return instruction once the merchant confirms which one stands.

<a id="event-019"></a>
## 2026-03-17 08:12:00 UTC — event 019

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Replacement authorisations, Tallowmere Goods; Refunds team, Tallowmere Goods

TG-247: we have conflicting instructions. Replacement authorisations authorised replacement TG-247-R v2 (shipped as DL-258 to Halverstone). Refunds team says the order was refunded under REF-274 and DL-258 should be returned. The customer told us she wants the replacement, not a refund. Please confirm which instruction stands. DL-258 is on hold at the carrier until then.

<a id="event-020"></a>
## 2026-03-17 08:30:00 UTC — event 020

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Ottilie Marsh, recipient

Your replacement DL-258 is in transit to Halverstone. I'm checking a query with Tallowmere about the order before it goes out for delivery, and I'll update you today.

<a id="event-021"></a>
## 2026-03-17 08:45:00 UTC — event 021

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Hold instruction for DL-258 has been passed to Halverstone depot. Neither delivery nor RTS will happen until the desk instructs.

<a id="event-022"></a>
## 2026-03-17 08:46:00 UTC — event 022

- **Channel:** Business portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-258 put on hold by Dispatch, Plover Arc Logistics. Reason: Waiting for merchant.

<a id="event-023"></a>
## 2026-03-17 09:05:00 UTC — event 023

- **Channel:** Business portal
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-258: arrived at Halverstone depot 09:01 UTC. Status: On hold.

<a id="event-024"></a>
## 2026-03-17 09:20:00 UTC — event 024

- **Channel:** Email
- **From:** Replacement authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

TG-247-R v2 stands. We have no record of a refund on TG-247 and the customer asked for a replacement. Please proceed with delivery. We can't speak for the Refunds team's message, so we've asked them to check. — Dana Rook

<a id="event-025"></a>
## 2026-03-17 09:34:00 UTC — event 025

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-244 (Greywick Homewares): recipient not home, card left. Second attempt is scheduled automatically for 2026-03-18. For information only.

<a id="event-026"></a>
## 2026-03-17 10:02:00 UTC — event 026

- **Channel:** Email
- **From:** Refunds team, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Received. We are checking REF-274 against our ledger and will come back to you. Please keep the parcel held for now.

<a id="event-027"></a>
## 2026-03-17 10:15:00 UTC — event 027

- **Channel:** Business portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Update on DL-219: collected 09:58 UTC by Plover Arc. Status: In transit.

<a id="event-028"></a>
## 2026-03-17 10:40:00 UTC — event 028

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-258 is held in cage H-12. Note: to load it for tomorrow's (2026-03-18) Halverstone route, we need a release instruction by 17:00 UTC today. Merchant holds without instruction default to return-to-sender at 18:00 UTC on 2026-03-18.

<a id="event-029"></a>
## 2026-03-17 11:05:00 UTC — event 029

- **Channel:** Email
- **From:** Tallowmere Goods auto-acknowledgement
- **To:** Iona Quill, Rivet Delivery Desk

Your message has been received by Refunds team and logged as case C-88239.

<a id="event-030"></a>
## 2026-03-17 11:30:00 UTC — event 030

- **Channel:** Customer portal
- **From:** Ottilie Marsh, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Thanks. Just to repeat, I haven't asked for or received any refund. I only want the kettle. I'm home on 18 March from 12:00 onwards.

<a id="event-031"></a>
## 2026-03-17 11:52:00 UTC — event 031

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-237 (Tallowmere) address query resolved by Tracking support. Closing the thread on our side.

<a id="event-032"></a>
## 2026-03-17 12:20:00 UTC — event 032

- **Channel:** Email
- **From:** Greywick Homewares, Customer service
- **To:** Iona Quill, Rivet Delivery Desk

Customer on DL-244 is asking whether the second attempt could be morning. Ticket GW-310. Not urgent.

<a id="event-033"></a>
## 2026-03-17 13:00:00 UTC — event 033

- **Channel:** Email
- **From:** Tallowmere case system (automated reminder)
- **To:** Iona Quill, Rivet Delivery Desk

Reminder of an open instruction on TG-247 from Refunds team (sent 2026-03-17 07:55): 'Do not reship. Please arrange for the carrier to return DL-258 to the Tallowmere warehouse unopened.' This is an automated reminder of an unacknowledged instruction.

<a id="event-034"></a>
## 2026-03-17 13:20:00 UTC — event 034

- **Channel:** Business portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-258 hold extended by Halverstone depot. Reason: Waiting for merchant.

<a id="event-035"></a>
## 2026-03-17 13:45:00 UTC — event 035

- **Channel:** Email
- **From:** Collections control, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Monthly statement INV-233 for desk-arranged collections is now available in the Business portal.

<a id="event-036"></a>
## 2026-03-17 14:40:00 UTC — event 036

- **Channel:** Email
- **From:** Refunds team, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk; Replacement authorisations, Tallowmere Goods

Correction: our 07:55 email today about TG-247 was sent in error. Refund REF-274 belongs to order TG-274 (a different customer). No refund has been issued on TG-247. Please disregard our instruction to stop or return DL-258. Replacement TG-247-R v2 should proceed as authorised. Apologies for the confusion. — Hal Venn, Refunds team lead

<a id="event-037"></a>
## 2026-03-17 14:41:00 UTC — event 037

- **Channel:** Email
- **From:** Tallowmere case system (automated)
- **To:** Iona Quill, Rivet Delivery Desk

Case C-88239 updated by Refunds team. Status: Resolved.

<a id="event-038"></a>
## 2026-03-17 14:50:00 UTC — event 038

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Reminder to all desks: route-load instructions for 2026-03-18 should go to the relevant depot work queue or to Dispatch by 17:00 UTC.

<a id="event-039"></a>
## 2026-03-17 14:58:00 UTC — event 039

- **Channel:** Email
- **From:** Brineleaf newsletter
- **To:** Iona Quill, Rivet Delivery Desk

New seasonal box lineup: preorders open 20 March.

<a id="event-040"></a>
## 2026-03-17 15:10:00 UTC — event 040

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Ottilie Marsh, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Any news? It's been sitting in Halverstone since this morning according to tracking. Can I please have it tomorrow? I'm home at Flat 3B, 22 Quayside Terrace from 12:00 on 18 March. And just to be clear, I don't want a refund.

