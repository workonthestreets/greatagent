# Case gen-19 history — Merchant asks whether a collection is booked after two carrier booking API calls returned HTTP 503

All identities, records and communications are fictional. Total events: 40.

<a id="event-001"></a>
## 2026-04-14 08:02:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Brindlewick Freight Newsletter
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Brindlewick Spring Network Update: new Harrowgate cross-dock opening in May, revised fuel surcharge table attached, and a reminder that Booking API v2 is retired on 30 June. No action required.

<a id="event-002"></a>
## 2026-04-14 08:15:00 UTC — event 002

- **Stage:** Context
- **Channel:** Business portal
- **From:** Tamsin Hool, Fennick & Daw Ceramics
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Please book a Brindlewick collection for SHP-40917 (order ORD-55130) for tomorrow, 15 April. Collection address: Unit 7, Calloway Yard, Pressingham PR4 9LT. Ready from 10:00 UTC, the warehouse closes at 16:00 UTC. 6 cartons, manifest attached (manifest-SHP-40917.csv). Destination: Pellin Home Store, Holloway Mere. It has to arrive by 16 April.

<a id="event-003"></a>
## 2026-04-14 08:15:30 UTC — event 003

- **Channel:** Business portal
- **From:** Kestrel Lane Portal (automated)
- **To:** Tamsin Hool, Fennick & Daw Ceramics

Thanks, we've received your request for SHP-40917. Reference KL-REQ-30411. Portal status: Booking requested.

<a id="event-004"></a>
## 2026-04-14 08:30:00 UTC — event 004

- **Channel:** Customer portal
- **From:** Luca Prentiss, recipient
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Hi, my parcel KL-77102 shows 'arriving today'. Can you tell me if it's morning or afternoon? I need to pop out for an hour.

<a id="event-005"></a>
## 2026-04-14 08:41:00 UTC — event 005

- **Channel:** System
- **From:** Kestrel TMS
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Note on KL-77102: Carrier ETA window 13:00–15:00 UTC (Brindlewick route PR-12).

<a id="event-006"></a>
## 2026-04-14 08:55:00 UTC — event 006

- **Stage:** Context
- **Channel:** Email
- **From:** Tamsin Hool, Fennick & Daw Ceramics
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

One thing I forgot: dock door A is closed all this week for resurfacing. The driver needs to use dock door B, which is on the Calloway Lane side (the second gate past the weighbridge). Our account profile still says door A, please ignore that this week. Bram Ostler is on the dock tomorrow, 07700 900 412.

<a id="event-007"></a>
## 2026-04-14 09:05:00 UTC — event 007

- **Channel:** System
- **From:** Brindlewick Tracking (webhook)
- **To:** Kestrel TMS

KL-77088: Out for delivery, Harrowgate depot, route HG-04.

<a id="event-008"></a>
## 2026-04-14 09:20:00 UTC — event 008

- **Stage:** Agent action (earlier desk actions only)
- **Channel:** Customer portal
- **From:** Odile Marrow, Kestrel Lane Delivery Desk
- **To:** Luca Prentiss, recipient

Hi Luca, Brindlewick's current window for KL-77102 is 13:00–15:00 UTC. If that changes we'll let you know.

<a id="event-009"></a>
## 2026-04-14 09:48:00 UTC — event 009

- **Stage:** Context
- **Channel:** Status page notification
- **From:** Brindlewick Integration Status
- **To:** Kestrel Lane Delivery Desk (subscriber)

INVESTIGATING – Booking API v3: elevated error rates on POST /v3/collections. Tracking and label APIs are not affected. Next update within 60 minutes.

<a id="event-010"></a>
## 2026-04-14 10:02:11 UTC — event 010

- **Stage:** Agent action (earlier desk actions only)
- **Channel:** System
- **From:** Kestrel TMS integration
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Booking call for SHP-40917 sent by Odile Marrow: POST /v3/collections, attempt 1. Response: HTTP 503 Service Unavailable. Correlation ID bwf-7c21e0a4. Full request/response logged to brindlewick-api-response-SHP-40917.json.

<a id="event-011"></a>
## 2026-04-14 10:02:12 UTC — event 011

- **Channel:** System
- **From:** Kestrel TMS
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Update on SHP-40917: Booking status set to 'Submitted'. Portal status synced to merchant: 'Booking requested'.

<a id="event-012"></a>
## 2026-04-14 10:10:00 UTC — event 012

- **Channel:** System
- **From:** Brindlewick Tracking (webhook)
- **To:** Kestrel TMS

KL-77088: Out for delivery, Harrowgate depot, route HG-04. (duplicate event)

<a id="event-013"></a>
## 2026-04-14 10:30:00 UTC — event 013

- **Channel:** Business portal
- **From:** Nell Aske, Orrin Vale Outfitters
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Customer on ORD-55098 wants to return a jacket. Can you get a Brindlewick return label to them? Their email is in the order.

<a id="event-014"></a>
## 2026-04-14 10:31:00 UTC — event 014

- **Channel:** System
- **From:** Kestrel TMS
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

SHP-40917 put on hold by Odile Marrow. Reason: Waiting for carrier.

<a id="event-015"></a>
## 2026-04-14 10:45:00 UTC — event 015

- **Stage:** Agent action (earlier desk actions only)
- **Channel:** Email
- **From:** Odile Marrow, Kestrel Lane Delivery Desk
- **To:** Integration Support, Brindlewick Freight

Our POST /v3/collections for SHP-40917 returned 503 at 10:02 UTC (correlation bwf-7c21e0a4). Can you confirm whether the request was processed and a collection created? We need a collection on 15 April.

<a id="event-016"></a>
## 2026-04-14 10:46:00 UTC — event 016

- **Channel:** Email
- **From:** Integration Support, Brindlewick Freight (automated)
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Ticket INT-8812 created. We aim to respond within 4 business hours. During active incidents please check the status page for updates.

<a id="event-017"></a>
## 2026-04-14 11:00:00 UTC — event 017

- **Channel:** Status page notification
- **From:** Brindlewick Integration Status
- **To:** Kestrel Lane Delivery Desk (subscriber)

INVESTIGATING – Booking API v3: errors continue. Engineers engaged.

<a id="event-018"></a>
## 2026-04-14 11:15:04 UTC — event 018

- **Channel:** System
- **From:** Kestrel TMS integration
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Automatic retry for SHP-40917: POST /v3/collections, attempt 2. Response: HTTP 503 Service Unavailable. Correlation ID bwf-91d3f6b2. Logged to brindlewick-api-response-SHP-40917.json.

<a id="event-019"></a>
## 2026-04-14 11:15:05 UTC — event 019

- **Channel:** System
- **From:** Kestrel TMS integration
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Update on SHP-40917: retry policy used up (2/2). Manual action required. Booking status still shows 'Submitted'.

<a id="event-020"></a>
## 2026-04-14 11:20:00 UTC — event 020

- **Stage:** Context
- **Channel:** Status page notification
- **From:** Brindlewick Integration Status
- **To:** Kestrel Lane Delivery Desk (subscriber)

IDENTIFIED – Booking API v3: queue failure in the booking engine. Some requests that returned 503 may have been accepted before the error and are being reconciled. Do NOT resubmit failed collection bookings through the API until we mark this resolved, because doing so may create duplicate collections. For collections needed on 15 April, email Collections Planning at collections.planning@brindlewick.example and include the correlation IDs of all failed attempts so planners can check for and merge duplicates. The cutoff for next-day collection requests is extended from 14:00 to 15:00 UTC today.

<a id="event-021"></a>
## 2026-04-14 11:30:00 UTC — event 021

- **Channel:** Customer portal
- **From:** Luca Prentiss, recipient
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Thanks, that works for me.

<a id="event-022"></a>
## 2026-04-14 11:40:00 UTC — event 022

- **Channel:** Email
- **From:** Harrowgate Depot, Brindlewick Freight
- **To:** All account desks

Notice: Harrowgate depot gate 3 is closed on 18 April for maintenance. Trunk arrivals will be redirected to gate 1. No impact on collections.

<a id="event-023"></a>
## 2026-04-14 11:52:00 UTC — event 023

- **Channel:** Internal chat
- **From:** Jory Fenwick, Kestrel Lane Delivery Desk
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Can you swap lunch with me today? 12:30 instead of 13:00?

<a id="event-024"></a>
## 2026-04-14 11:55:00 UTC — event 024

- **Channel:** Internal chat
- **From:** Odile Marrow, Kestrel Lane Delivery Desk
- **To:** Jory Fenwick, Kestrel Lane Delivery Desk

Sure, go at 12:30.

<a id="event-025"></a>
## 2026-04-14 12:05:00 UTC — event 025

- **Channel:** Email
- **From:** Billing, Brindlewick Freight
- **To:** Kestrel Lane Delivery Desk accounts

Your March statement BW-INV-22871 is now available in the account portal. Payment due 30 April.

<a id="event-026"></a>
## 2026-04-14 12:10:00 UTC — event 026

- **Channel:** Business portal
- **From:** Nell Aske, Orrin Vale Outfitters
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Any news on the ORD-55098 return label?

<a id="event-027"></a>
## 2026-04-14 12:20:00 UTC — event 027

- **Stage:** Agent action (earlier desk actions only)
- **Channel:** Business portal
- **From:** Odile Marrow, Kestrel Lane Delivery Desk
- **To:** Nell Aske, Orrin Vale Outfitters

The return label for ORD-55098 was generated through Brindlewick's label service (unaffected by today's booking incident) and emailed to your customer at 12:18 UTC. Return ref RTN-6620.

<a id="event-028"></a>
## 2026-04-14 12:33:00 UTC — event 028

- **Channel:** Phone (call note)
- **From:** Bram Ostler, Fennick & Daw warehouse lead
- **To:** Kestrel Lane Delivery Desk

Call note (logged by front desk): Bram asked whether the 'Booking requested' status on the portal means the driver is definitely coming tomorrow. He's building the dock rota. Told him the coordinator would follow up.

<a id="event-029"></a>
## 2026-04-14 12:40:00 UTC — event 029

- **Channel:** System
- **From:** Kestrel TMS
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Note: Brindlewick ticket INT-8812 status changed to 'Assigned – incident linked'. No resolution text.

<a id="event-030"></a>
## 2026-04-14 12:48:00 UTC — event 030

- **Channel:** Status page notification
- **From:** Brindlewick Integration Status
- **To:** Kestrel Lane Delivery Desk (subscriber)

MONITORING (partial) – Booking API v3: a fix is deployed to part of the fleet, but intermittent 503s continue and reconciliation of affected requests is still running. The guidance from 11:20 still applies: do not resubmit failed bookings through the API. Use Collections Planning email for 15 April collections.

<a id="event-031"></a>
## 2026-04-14 12:55:00 UTC — event 031

- **Channel:** System
- **From:** Brindlewick Tracking (webhook)
- **To:** Kestrel TMS

KL-77088: Delivered 12:51 UTC, signed 'R. Tull'. POD available.

<a id="event-032"></a>
## 2026-04-14 13:00:00 UTC — event 032

- **Channel:** Email
- **From:** Kestrel Lane Ops Bulletin
- **To:** All desk staff

Reminder: the quarterly carrier scorecard review is on Thursday. Please log any carrier incidents in the shared tracker.

<a id="event-033"></a>
## 2026-04-14 13:02:00 UTC — event 033

- **Channel:** System
- **From:** Brindlewick Tracking (webhook)
- **To:** Kestrel TMS

KL-77102: Out for delivery, route PR-12, ETA 13:40 UTC.

<a id="event-034"></a>
## 2026-04-14 13:05:00 UTC — event 034

- **Channel:** Internal chat
- **From:** Jory Fenwick, Kestrel Lane Delivery Desk
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

The integration queue has SHP-40917 flagged red. Want me to hit 'Resubmit' in the TMS? Status page says they've deployed a fix, so it'll probably go through now.

<a id="event-035"></a>
## 2026-04-14 13:08:00 UTC — event 035

- **Channel:** Email
- **From:** Pellin Home Store goods-in
- **To:** Kestrel Lane Delivery Desk

Automated: Goods-in slots for 16 April are now published. Deliveries are accepted 07:00–13:00 local. Bookings are not required for under 10 cartons.

<a id="event-036"></a>
## 2026-04-14 13:10:00 UTC — event 036

- **Channel:** Customer portal
- **From:** Aric Dunmore, recipient
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Is KL-77140 coming this week? Tracking hasn't moved since Friday.

<a id="event-037"></a>
## 2026-04-14 13:11:00 UTC — event 037

- **Channel:** System
- **From:** Kestrel TMS
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

KL-77140 put on hold by Jory Fenwick. Reason: Awaiting depot trace.

<a id="event-038"></a>
## 2026-04-14 13:12:00 UTC — event 038

- **Stage:** Context
- **Channel:** Email
- **From:** Collections Planning, Brindlewick Freight (bulletin)
- **To:** All account desks

Manual collection requests during the API incident: send to collections.planning@brindlewick.example before 15:00 UTC. Please include: shipper ref, collection address and access point, collection date, ready and close times, number of pieces, weight of each piece and total weight, any piece over 30 kg (flag it for two-person collection; we cannot assign a single-person van otherwise), and the correlation IDs of any failed API attempts. We'll reply with a COL- reference once the booking is accepted. A request is not booked until you have a COL- reference.

<a id="event-039"></a>
## 2026-04-14 13:15:00 UTC — event 039

- **Channel:** Email
- **From:** Brindlewick Freight Newsletter
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Webinar invitation: 'Getting the most from Booking API v3', 29 April, 14:00 UTC.

<a id="event-040"></a>
## 2026-04-14 13:18:00 UTC — event 040

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Tamsin Hool, Fennick & Daw Ceramics
- **To:** Odile Marrow, Kestrel Lane Delivery Desk

Hi Odile, is the Brindlewick collection for SHP-40917 booked for tomorrow? The portal has said 'Booking requested' since this morning and Bram is planning dock staff around a 10:00 pickup. I need a straight yes or no and the booking reference. If it isn't booked, please get it booked today. We cannot miss Pellin's 16 April delivery.

