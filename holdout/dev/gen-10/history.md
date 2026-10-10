# Case gen-10 history — Recipient chases a redelivery change while Dispatch's revised reply deadline has not passed

All identities, records and communications are fictional. Total events: 39.

<a id="event-001"></a>
## 2026-03-18 08:02:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-247 (merchant ref TG-231, Tallowmere Goods): failed attempt 2026-03-17 15:42 UTC, reason 'no answer at gate', card left. Parcel inbound-scanned at Halverstone depot 2026-03-17 19:10 UTC. Depot hold expires 2026-03-24 23:59 UTC; after that the parcel goes back to the sender. Redelivery has not been booked yet.

<a id="event-002"></a>
## 2026-03-18 08:05:00 UTC — event 002

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

System update: DL-247 scanned at bay H-3 (shelf check). Status: held at depot.

<a id="event-003"></a>
## 2026-03-18 08:05:30 UTC — event 003

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

System update: DL-247 scanned at bay H-3 (shelf check). Status: held at depot. [duplicate scan]

<a id="event-004"></a>
## 2026-03-18 08:20:00 UTC — event 004

- **Channel:** Email
- **From:** Greywick Homewares customer care
- **To:** Iona Quill, Rivet Delivery Desk

Newsletter: Greywick spring range launches 2026-03-25. Packaging is changing for the large lamp bases. No action needed.

<a id="event-005"></a>
## 2026-03-18 08:34:00 UTC — event 005

- **Channel:** Customer portal
- **From:** Pell Arkwright, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-238: the parcel arrived this morning, thank you. You can close this.

<a id="event-006"></a>
## 2026-03-18 08:41:00 UTC — event 006

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Pell Arkwright, recipient

Thanks for confirming that DL-238 arrived. We've closed the request.

<a id="event-007"></a>
## 2026-03-18 08:55:00 UTC — event 007

- **Channel:** Email
- **From:** Safety lead, Plover Arc Logistics
- **To:** All partner desks

Bulletin: Brenmoor depot yard resurfacing 2026-03-23 to 2026-03-27. Walk-in collections at Brenmoor are paused during that time. Halverstone is not affected.

<a id="event-008"></a>
## 2026-03-18 09:14:00 UTC — event 008

- **Stage:** Context
- **Channel:** Customer portal
- **From:** Odile Varn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My parcel DL-247 wasn't delivered yesterday. Please arrange redelivery on Thursday 19 March, in the morning.

<a id="event-009"></a>
## 2026-03-18 09:30:00 UTC — event 009

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Scheduling, Plover Arc Logistics

Please book a redelivery for DL-247 (held at Halverstone, failed attempt 2026-03-17) on Thursday 2026-03-19, morning window. The recipient has asked for this window. Please confirm the slot or tell us the alternatives.

<a id="event-010"></a>
## 2026-03-18 09:30:40 UTC — event 010

- **Channel:** Email
- **From:** Scheduling, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Auto-acknowledgement: your request has been received (ref SCH-Q-5512). We usually reply within 2 working hours.

<a id="event-011"></a>
## 2026-03-18 09:31:00 UTC — event 011

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Odile Varn, recipient

We've asked Plover Arc Scheduling for a Thursday 19 March morning redelivery. It isn't booked yet. We'll let you know once they confirm.

<a id="event-012"></a>
## 2026-03-18 09:47:00 UTC — event 012

- **Channel:** Business portal
- **From:** Brineleaf dispatch
- **To:** Iona Quill, Rivet Delivery Desk

DL-252 chilled crate: collection confirmed for today at 15:00 UTC from the Brineleaf dock. Just letting you know. No reply needed.

<a id="event-013"></a>
## 2026-03-18 10:02:00 UTC — event 013

- **Channel:** Email
- **From:** Scheduling, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

SCH-Q-5512 / DL-247: we've provisionally pencilled Thursday 2026-03-19, 09:00–12:00 UTC. This isn't final until route sign-off at 12:00 today.

<a id="event-014"></a>
## 2026-03-18 10:03:00 UTC — event 014

- **Channel:** Customer portal
- **From:** Notification support, Plover Arc Logistics
- **To:** Odile Varn, recipient

Automated SMS copy: 'Plover Arc: your parcel DL-247 is planned for Thu 19 Mar, 09:00–12:00. We will confirm on the day.'

<a id="event-015"></a>
## 2026-03-18 10:15:00 UTC — event 015

- **Channel:** Email
- **From:** Tallowmere Goods Warehouse dispatch
- **To:** Iona Quill, Rivet Delivery Desk

Routine: TG-240 to TG-246 handed to Plover Arc this morning. Manifest MN-311 is attached in the portal. No exceptions.

<a id="event-016"></a>
## 2026-03-18 10:30:00 UTC — event 016

- **Channel:** Call transcript
- **From:** Hesper Dunn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Caller asked about locker opening hours for DL-249. The agent gave the Halverstone locker bank hours (06:00–22:00). Call ended.

<a id="event-017"></a>
## 2026-03-18 10:55:00 UTC — event 017

- **Stage:** Context
- **Channel:** Customer portal
- **From:** Odile Varn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Change of plan, sorry. Thursday doesn't work any more because I've been called into work. Please cancel Thursday. Can it come on Friday 20 March in the afternoon instead, 13:00–17:00? The gate code is 4471. I'll be in all afternoon.

<a id="event-018"></a>
## 2026-03-18 11:10:00 UTC — event 018

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Scheduling, Plover Arc Logistics

SCH-Q-5512 / DL-247: the recipient has withdrawn Thursday 19 March. Please release the provisional 09:00–12:00 slot. She now wants Friday 2026-03-20, 13:00–17:00 (gate code 4471). Can you book that, or tell us who owns Friday slots?

<a id="event-019"></a>
## 2026-03-18 11:12:00 UTC — event 019

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Odile Varn, recipient

Got it. We've asked Plover Arc to cancel Thursday and are requesting Friday 20 March, 13:00–17:00, with your gate code. Nothing is confirmed for Friday yet.

<a id="event-020"></a>
## 2026-03-18 11:25:00 UTC — event 020

- **Channel:** Email
- **From:** Scheduling, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

SCH-Q-5512: the Thursday provisional slot for DL-247 has been released and the request is closed. Route H-12 is being rebalanced this week, so Friday H-12 slots are allocated by Dispatch, not Scheduling. Please send the Friday request to Dispatch.

<a id="event-021"></a>
## 2026-03-18 11:26:00 UTC — event 021

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Update: SCH-Q-5512 closed by Scheduling. Reason: Thursday slot released at customer request.

<a id="event-022"></a>
## 2026-03-18 11:42:00 UTC — event 022

- **Channel:** Customer portal
- **From:** Notification support, Plover Arc Logistics
- **To:** Odile Varn, recipient

Automated SMS copy: 'Plover Arc: the planned delivery of DL-247 on Thu 19 Mar has been cancelled. A new date will be confirmed separately.'

<a id="event-023"></a>
## 2026-03-18 11:50:00 UTC — event 023

- **Channel:** Email
- **From:** Plover Arc Logistics partner news
- **To:** Iona Quill, Rivet Delivery Desk

Partner newsletter, March: new Locker routing self-service, Q2 fuel surcharge table, and staff awards. Read online.

<a id="event-024"></a>
## 2026-03-18 12:02:00 UTC — event 024

- **Channel:** Email
- **From:** Customer portal operations
- **To:** All partner desks

Planned maintenance: Customer portal read-only on 2026-03-22, 02:00–03:00 UTC. No action required.

<a id="event-025"></a>
## 2026-03-18 12:10:00 UTC — event 025

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-244: driver confirms delivery to the side door, and the photo has been uploaded. Closing our side.

<a id="event-026"></a>
## 2026-03-18 12:18:00 UTC — event 026

- **Channel:** Customer portal
- **From:** Marta Linn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-251: can I change my delivery address to my office? It's in the same town.

<a id="event-027"></a>
## 2026-03-18 12:25:00 UTC — event 027

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Marta Linn, recipient

For DL-251 we'll need the sender to approve an address change. Please send us the full office address and we'll ask Tallowmere Goods.

<a id="event-028"></a>
## 2026-03-18 12:40:00 UTC — event 028

- **Stage:** Agent action
- **Channel:** Dispatch chat
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Dispatch, Plover Arc Logistics

DL-247 (held at Halverstone, route H-12): please rebook the redelivery for Friday 2026-03-20, 13:00–17:00 UTC. The recipient chose this today and it replaces her earlier Thursday request, which Scheduling released under SCH-Q-5512. Gate code 4471. The failed attempt was 2026-03-17. Please confirm the slot or offer alternatives.

<a id="event-029"></a>
## 2026-03-18 12:52:00 UTC — event 029

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Received, DL-247 Friday PM is in our H-12 queue (ref DSP-7731). We'll confirm by 13:15.

<a id="event-030"></a>
## 2026-03-18 12:54:00 UTC — event 030

- **Stage:** Agent action
- **Channel:** Customer portal
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Odile Varn, recipient

Friday 20 March, 13:00–17:00 has been requested from Plover Arc Dispatch, who handle Friday slots on your route this week. They expect to confirm at about 13:15. It isn't booked yet, and we'll update you.

<a id="event-031"></a>
## 2026-03-18 12:55:00 UTC — event 031

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Put on hold by Iona Quill. Reason: Waiting for carrier (Dispatch DSP-7731), reply due 13:15.

<a id="event-032"></a>
## 2026-03-18 12:58:00 UTC — event 032

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

System update: DL-252 pre-advice received. DL-247 still held at bay H-3.

<a id="event-033"></a>
## 2026-03-18 13:06:00 UTC — event 033

- **Channel:** Dispatch chat
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Update on DSP-7731 / DL-247: the Friday H-12 route plan is being re-run after the rebalancing, so we can't lock afternoon slots until it finishes. New confirmation time is by 14:00 UTC. Please don't resend. A duplicate request puts the item back at the end of the queue.

<a id="event-034"></a>
## 2026-03-18 13:07:00 UTC — event 034

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Hold updated by Iona Quill. Reason: Waiting for carrier (Dispatch DSP-7731), revised reply due 14:00.

<a id="event-035"></a>
## 2026-03-18 13:09:00 UTC — event 035

- **Channel:** Email
- **From:** Collections control, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Reminder: the weekly collections report is due Friday. Unrelated to any open shipment.

<a id="event-036"></a>
## 2026-03-18 13:12:00 UTC — event 036

- **Channel:** Business portal
- **From:** Brineleaf dispatch
- **To:** Iona Quill, Rivet Delivery Desk

DL-252: crate labels printed. See you at 15:00.

<a id="event-037"></a>
## 2026-03-18 13:15:00 UTC — event 037

- **Channel:** Customer portal
- **From:** Marta Linn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-251: office address is Unit 4, Corran Mews, Halverstone. Thanks.

<a id="event-038"></a>
## 2026-03-18 13:16:00 UTC — event 038

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Returns authorisations, Tallowmere Goods

DL-251: the recipient asks to redirect to Unit 4, Corran Mews, Halverstone (same town). Can the sender approve the address change? (This should have gone to your address-change contact. Please forward it if this isn't your team.)

<a id="event-039"></a>
## 2026-03-18 13:20:00 UTC — event 039

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Odile Varn, recipient
- **To:** Iona Quill, Rivet Delivery Desk

It's past 13:15 and I've heard nothing. Is Friday afternoon booked or not? I'm a bit worried because I got a text this morning saying Thursday 09:00–12:00. I can't be in on Thursday, so please make sure it's not Thursday. Can't you just book Friday yourselves or ring the driver? I need to know today so I can sort out work.

