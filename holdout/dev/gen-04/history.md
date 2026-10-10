# Case gen-04 history — Pallet dock booking rejected twice (slot full) while the driver is already scheduled to leave tomorrow at 05:15

All identities, records and communications are fictional. Total events: 37.

<a id="event-001"></a>
## 2026-04-14 08:02:00 UTC — event 001

- **Stage:** Context
- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Case KL-4471 opened for SHP-20931 (Marlow & Pike Ceramics → Harrowgate Home Stores, Selby Moor DC). Task: arrange consignee dock appointment for 2026-04-15 delivery.

<a id="event-002"></a>
## 2026-04-14 08:05:00 UTC — event 002

- **Channel:** Email
- **From:** Brannock Freight Network Bulletin
- **To:** Kestrel Lane Delivery Desk (distribution list)

Network bulletin w/c 13 April: holiday-week volumes up 18% on pallet lanes. Please book consignee appointments early. Corvane hub yard works on bay 6 continue until Friday.

<a id="event-003"></a>
## 2026-04-14 08:11:00 UTC — event 003

- **Stage:** Context
- **Channel:** Email
- **From:** Brannock Customer Operations
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

SHP-20931 was collected 2026-04-13 from Marlow & Pike, Fenwick Yard, and has arrived at Corvane hub. 3 pallets. Planned delivery 2026-04-15 to Harrowgate Home Stores, Selby Moor DC, Dock Road, Selby Moor. Consignee requires a pre-booked dock appointment; the sender or its agent must arrange the booking. Please give the booking reference to Pallet Network Dispatch.

<a id="event-004"></a>
## 2026-04-14 08:14:00 UTC — event 004

- **Channel:** Tracking feed
- **From:** Brannock tracking
- **To:** Kestrel Lane case system

SHP-20931-P1, P2, P3: Hub inbound scan, Corvane hub, 2026-04-14 06:52.

<a id="event-005"></a>
## 2026-04-14 08:14:30 UTC — event 005

- **Channel:** Tracking feed
- **From:** Brannock tracking
- **To:** Kestrel Lane case system

SHP-20931-P1, P2, P3: Hub inbound scan, Corvane hub, 2026-04-14 06:52. (duplicate transmission)

<a id="event-006"></a>
## 2026-04-14 08:20:00 UTC — event 006

- **Channel:** Customer portal
- **From:** Rhys Allard, recipient (KL-4468)
- **To:** Kestrel Lane Delivery Desk

My lamp parcel SHP-20877 says 'in transit' for 3 days now. Can someone check?

<a id="event-007"></a>
## 2026-04-14 08:21:00 UTC — event 007

- **Channel:** Customer portal
- **From:** Kestrel Lane auto-responder
- **To:** Rhys Allard

Thanks, we've received your message about KL-4468. A coordinator will reply within 4 working hours.

<a id="event-008"></a>
## 2026-04-14 08:50:00 UTC — event 008

- **Stage:** Agent action
- **Channel:** Email
- **From:** Odile Marsh, Kestrel Lane Delivery Desk
- **To:** goodsin@harrowgate-selby.example

Please book a dock appointment at Selby Moor DC for 2026-04-15, 07:00–09:00 UTC. PO ORD-55812, supplier Marlow & Pike Ceramics, carrier Brannock Freight, 3 pallets (manifest attached: marlow-pike-manifest-SHP-20931.csv).

<a id="event-009"></a>
## 2026-04-14 08:50:40 UTC — event 009

- **Channel:** Email
- **From:** Mail Delivery Subsystem
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Delivery has failed to these recipients: goodsin@harrowgate-selby.example. Remote server returned '550 5.1.1 Recipient address rejected: mailbox does not exist'.

<a id="event-010"></a>
## 2026-04-14 09:12:00 UTC — event 010

- **Stage:** Context
- **Channel:** Email
- **From:** Tamsin Okoro, Marlow & Pike Ceramics shipping coordinator
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Morning Odile. For SHP-20931, Wednesday 15th is ideal. If Selby can't take us Wednesday, Thursday 16th is fine as long as it arrives before 12:00. The store set-up crew starts at 14:00 Thursday and the stock has to be put away first. Please don't agree anything later than Thursday noon without checking with me. We've always booked through goodsin@ at Selby.

<a id="event-011"></a>
## 2026-04-14 09:15:00 UTC — event 011

- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** KL-4471

Put on hold by Odile Marsh. Reason: Waiting for consignee booking.

<a id="event-012"></a>
## 2026-04-14 09:30:00 UTC — event 012

- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** KL-4459

Update: KL-4459 carrier investigation reference INV-3302 attached. No action required.

<a id="event-013"></a>
## 2026-04-14 09:42:00 UTC — event 013

- **Stage:** Context
- **Channel:** Email
- **From:** Brannock Pallet Network Dispatch, Corvane hub
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Route plan published for 2026-04-15. SHP-20931 is on driver Corvane-07, rigid with tail lift (reg BF-62 KTR). Departs Corvane 05:15, ETA Selby Moor 07:00–08:30, then two more drops at Hollin Cross after Selby. Booking ref still needed.

<a id="event-014"></a>
## 2026-04-14 09:55:00 UTC — event 014

- **Stage:** Agent action
- **Channel:** Consignee portal (Yardline)
- **From:** Odile Marsh, Kestrel Lane Delivery Desk
- **To:** Harrowgate Selby Moor DC — Yardline booking

Booking request submitted: site Selby Moor DC, date 2026-04-15, window 07:00–08:00, PO ORD-55812, carrier Brannock Freight, 3 pallets, 1,197 kg.

<a id="event-015"></a>
## 2026-04-14 09:55:20 UTC — event 015

- **Channel:** Consignee portal (Yardline)
- **From:** Yardline
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Request YLR-88213 received. Status: PENDING capacity check.

<a id="event-016"></a>
## 2026-04-14 10:05:00 UTC — event 016

- **Channel:** Email
- **From:** Yardline Notifications
- **To:** All Yardline users

Scheduled maintenance: Yardline will be unavailable 2026-04-18 22:00 – 2026-04-19 02:00 UTC. No action required.

<a id="event-017"></a>
## 2026-04-14 10:20:00 UTC — event 017

- **Channel:** Email
- **From:** Fennick Home refunds team
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Re KL-4470 / ORD-55390: refund for the damaged rug has been approved and will post in 3–5 working days.

<a id="event-018"></a>
## 2026-04-14 10:41:00 UTC — event 018

- **Channel:** Consignee portal (Yardline)
- **From:** Yardline
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Request YLR-88213 REJECTED, reason code SLOT_FULL. Full response attached: yardline-response-YLR-88213.json.

<a id="event-019"></a>
## 2026-04-14 10:42:00 UTC — event 019

- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** KL-4471

Note: Yardline webhook payload stored as yardline-response-YLR-88213.json.

<a id="event-020"></a>
## 2026-04-14 11:04:00 UTC — event 020

- **Stage:** Agent action
- **Channel:** Consignee portal (Yardline)
- **From:** Odile Marsh, Kestrel Lane Delivery Desk
- **To:** Harrowgate Selby Moor DC — Yardline booking

Booking request submitted: site Selby Moor DC, date 2026-04-15, window 08:00–09:00, PO ORD-55812, carrier Brannock Freight, 3 pallets, 1,197 kg.

<a id="event-021"></a>
## 2026-04-14 11:06:00 UTC — event 021

- **Channel:** Consignee portal (Yardline)
- **From:** Yardline
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Request YLR-88240 REJECTED, reason code DATE_CLOSED. Inbound capacity for 2026-04-15 is closed. Repeated submissions for a closed date are logged against the requesting account. See exception route in previous response.

<a id="event-022"></a>
## 2026-04-14 11:20:00 UTC — event 022

- **Channel:** Email
- **From:** Brannock Customer Operations
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Re SHP-20902 (KL-4463): POD now available, signed 'J. HARTE' 2026-04-13 15:12.

<a id="event-023"></a>
## 2026-04-14 11:35:00 UTC — event 023

- **Channel:** Email
- **From:** Tamsin Okoro, Marlow & Pike Ceramics shipping coordinator
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Any news on the Selby slot?

<a id="event-024"></a>
## 2026-04-14 11:48:00 UTC — event 024

- **Stage:** Agent action
- **Channel:** Email
- **From:** Odile Marsh, Kestrel Lane Delivery Desk
- **To:** Tamsin Okoro, Marlow & Pike Ceramics shipping coordinator

Not confirmed yet. The goods-in mailbox bounced, and the Yardline portal has rejected Wednesday as full. I'm still working on it and will update you this afternoon.

<a id="event-025"></a>
## 2026-04-14 12:10:00 UTC — event 025

- **Channel:** Driver app
- **From:** Driver Corvane-03
- **To:** Brannock Pallet Network Dispatch, Corvane hub (cc Kestrel Lane)

KL-4472 / SHP-20915: customer asked for the pallet to go round the back to gate B. Done, POD taken.

<a id="event-026"></a>
## 2026-04-14 12:30:00 UTC — event 026

- **Stage:** Context
- **Channel:** Email
- **From:** Brannock Pallet Network Dispatch, Corvane hub
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

FYI on Selby runs. If you tell us by 17:00 the day before, we can re-plan a delivery to another day at no charge. If a vehicle is turned away at the gate, a failed-delivery fee of 95.00 per vehicle applies plus redelivery. Our drivers can wait on site for at most 2 hours because of the Hollin Cross drops.

<a id="event-027"></a>
## 2026-04-14 12:45:00 UTC — event 027

- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** KL-4471

Put on hold by Odile Marsh. Reason: Waiting for carrier.

<a id="event-028"></a>
## 2026-04-14 13:02:00 UTC — event 028

- **Channel:** Email
- **From:** Harrowgate Home Stores Supplier Bulletin
- **To:** Supplier & carrier contacts (distribution list)

Supplier Bulletin no. 41. Spring range launch dates. New packaging-recycling labels from May. Selby Moor DC reminder: the legacy goods-in mailbox closed on 2026-04-01, and all dock scheduling is now through Yardline. Vehicles arriving without a valid Yardline booking reference will not be admitted to the yard.

<a id="event-029"></a>
## 2026-04-14 13:15:00 UTC — event 029

- **Channel:** Email
- **From:** Ostrey Customs Brokerage
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

KL-4466: Entry lodged for SHP-20850. Awaiting duty calculation.

<a id="event-030"></a>
## 2026-04-14 13:40:00 UTC — event 030

- **Channel:** Email
- **From:** Brannock Pallet Network Dispatch, Corvane hub
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Route plan republished for 2026-04-15 (no change to Corvane-07). SHP-20931 still shows booking ref: NONE.

<a id="event-031"></a>
## 2026-04-14 13:52:00 UTC — event 031

- **Channel:** Email
- **From:** Tamsin Okoro, Marlow & Pike Ceramics shipping coordinator
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

My sales manager says Selby always squeezes people in. Can we just send the driver tomorrow anyway?

<a id="event-032"></a>
## 2026-04-14 14:05:00 UTC — event 032

- **Channel:** Email
- **From:** Tamsin Okoro, Marlow & Pike Ceramics shipping coordinator
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Sorry, ignore my last message. Our warehouse lead reminds me Selby turned away one of our trucks last month. Stick to what I said this morning: Wednesday if they can, otherwise Thursday arriving before 12:00. Nothing later without asking me.

<a id="event-033"></a>
## 2026-04-14 14:10:00 UTC — event 033

- **Channel:** Email
- **From:** Kestrel Lane Ops Digest
- **To:** All coordinators

Weekly digest: average first response 2h14m. Reminder to log NDRs against the case. Team lunch Friday.

<a id="event-034"></a>
## 2026-04-14 14:18:00 UTC — event 034

- **Channel:** Customer portal
- **From:** Rhys Allard, recipient (KL-4468)
- **To:** Kestrel Lane Delivery Desk

Never mind, the lamp just arrived. Thanks.

<a id="event-035"></a>
## 2026-04-14 14:22:00 UTC — event 035

- **Channel:** Tracking feed
- **From:** Brannock tracking
- **To:** Kestrel Lane case system

SHP-20931: Status update, 'Scheduled for delivery 2026-04-15'.

<a id="event-036"></a>
## 2026-04-14 14:30:00 UTC — event 036

- **Channel:** System
- **From:** Kestrel Lane case system
- **To:** KL-4469

Note: KL-4469 closed by Bram Ellery. Reason: Resolved, recipient collected from locker.

<a id="event-037"></a>
## 2026-04-14 14:41:00 UTC — event 037

- **Stage:** Escalation
- **Channel:** Email
- **From:** Brannock Pallet Network Dispatch, Corvane hub
- **To:** Odile Marsh, Kestrel Lane Delivery Desk

Driver Corvane-07 is loaded with SHP-20931 and leaves at 05:15 tomorrow. We still have no Selby Moor booking reference. Tell us what to do: send a confirmed slot or a re-plan instruction by 17:00 UTC today.

