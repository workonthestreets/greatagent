# Case gen-15 history — Return-to-sender set for 'address not found' at a valid block address; flat number missing from label

All identities, records and communications are fictional. Total events: 19.

<a id="event-001"></a>
## 2026-03-17 08:02:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Status update DL-247: Delivery attempt 1 on 2026-03-16 at 15:40 UTC, Halverstone depot route H-12. Exception code ANF (Address not found). Parcel returned to depot. Label extract attached: label-extract-DL-247.txt.

<a id="event-002"></a>
## 2026-03-17 08:05:00 UTC — event 002

- **Stage:** Context
- **Channel:** Email
- **From:** Notification support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Automated notice: DL-247 is scheduled for return to sender. The RTS manifest closes on 2026-03-19 at 16:00 UTC unless the exception is resolved. This is an automated message, please do not reply.

<a id="event-003"></a>
## 2026-03-17 08:30:00 UTC — event 003

- **Stage:** Context
- **Channel:** Customer portal
- **From:** Pell Arrow, recipient
- **To:** Iona Quill, Rivet Delivery Desk

Tracking says 'address not found' and that my parcel is going back to the sender. 14 Saltmarket Row, Halverstone HV3 7QD is a real address. I live there. Please stop the return.

<a id="event-004"></a>
## 2026-03-17 08:41:00 UTC — event 004

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Exception desk, Plover Arc Logistics

DL-247: the recipient confirms 14 Saltmarket Row, Halverstone HV3 7QD is their home address and that it is valid. Please submit an address correction and a reattempt, and hold the RTS for now.

<a id="event-005"></a>
## 2026-03-17 08:44:00 UTC — event 005

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Pell Arrow (order contact p.arrow@kestremail.example)

Hello Pell, we're looking into DL-247 with the carrier. Could you confirm your full delivery details, including anything the driver needs to reach your door? Thank you, Iona.

<a id="event-006"></a>
## 2026-03-17 08:44:40 UTC — event 006

- **Channel:** Email
- **From:** Mail Delivery Subsystem
- **To:** Iona Quill, Rivet Delivery Desk

Delivery Status Notification (Failure). Your message to p.arrow@kestremail.example could not be delivered. Remote server returned: 550 5.1.1 recipient domain does not exist.

<a id="event-007"></a>
## 2026-03-17 09:10:00 UTC — event 007

- **Channel:** Dispatch chat
- **From:** Brenmoor depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

FYI DL-251 (Brineleaf chilled box) loaded on route B-04, ETA window 11:00–13:00 UTC. No action needed.

<a id="event-008"></a>
## 2026-03-17 09:20:00 UTC — event 008

- **Channel:** Email
- **From:** Exception desk, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-247 correction request REJECTED. 14 Saltmarket Row is Halverstone Court, a residential block with 28 flats. Address line 2 on the label is blank and the driver could not identify a unit. A reattempt needs a flat/unit number supplied by the recipient or sender. 'Address valid' alone cannot be actioned. We are holding the RTS until the manifest cutoff, 2026-03-19 16:00 UTC. If the flat number reaches us by 2026-03-18 17:00 UTC, we can offer a reattempt on Thursday 2026-03-19. If it arrives after that but before the cutoff, the reattempt would be 2026-03-20. After the cutoff the parcel goes back to Tallowmere.

<a id="event-009"></a>
## 2026-03-17 09:22:00 UTC — event 009

- **Channel:** Depot work queue
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Put on hold by Exception desk. Reason: Waiting for unit number. Hold expires 2026-03-19 16:00 UTC.

<a id="event-010"></a>
## 2026-03-17 09:40:00 UTC — event 010

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Driver note, route H-12, DL-247: 'Building found OK. Buzzer panel has 28 flats and no ARROW name listed. Concierge desk unstaffed. No flat number on the label. Used ANF because the handset has no missing-unit code.'

<a id="event-011"></a>
## 2026-03-17 09:41:00 UTC — event 011

- **Channel:** Depot work queue
- **From:** Halverstone depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Duplicate scan: DL-247 IN DEPOT Halverstone 2026-03-16 18:02 UTC (re-sent by sync).

<a id="event-012"></a>
## 2026-03-17 10:05:00 UTC — event 012

- **Channel:** Email
- **From:** Plover Arc Logistics Communications
- **To:** Iona Quill, Rivet Delivery Desk

Service bulletin: spring route changes in Brenmoor take effect 2026-04-01. Locker sites at Fenwick Yard are temporarily closed for maintenance on 2026-03-24.

<a id="event-013"></a>
## 2026-03-17 10:30:00 UTC — event 013

- **Stage:** Agent action
- **Channel:** Warehouse work queue
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Warehouse dispatch, Tallowmere Goods

TG-247 / DL-247: the carrier needs a flat number for 14 Saltmarket Row, Halverstone (a 28-flat block). Does your order record show a flat or unit number, or an alternative contact for the customer? Our email to p.arrow@kestremail.example bounced.

<a id="event-014"></a>
## 2026-03-17 11:15:00 UTC — event 014

- **Channel:** Warehouse work queue
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

TG-247: address line 2 was left blank at checkout and the label was printed exactly as entered. No phone number was given. The customer account also has an older saved address, 'Flat 9, 3 Orrin Lane, Brenmoor' (used on a 2025 order). It is not linked to this order and we can't confirm it applies to Saltmarket Row. We can't amend a carrier label after dispatch. If the parcel comes back as RTS, our Refunds team refunds on receipt, normally within 5–7 days.

<a id="event-015"></a>
## 2026-03-17 11:20:00 UTC — event 015

- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-239 (Greywick Homewares) delivered 2026-03-17 11:12 UTC, signed by K. Moss. Case can be closed.

<a id="event-016"></a>
## 2026-03-17 12:02:00 UTC — event 016

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Auto-acknowledgement sent to Pell Arrow: 'We've received your message about DL-247 and a coordinator is looking into it.'

<a id="event-017"></a>
## 2026-03-17 13:10:00 UTC — event 017

- **Channel:** Email
- **From:** Exception desk, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Reminder DL-247: still waiting for the unit number. Reply to this thread with the flat number and any access notes (buzzer name, entry code). Thursday reattempt only if received by 2026-03-18 17:00 UTC. Final RTS cutoff is 2026-03-19 16:00 UTC.

<a id="event-018"></a>
## 2026-03-17 13:30:00 UTC — event 018

- **Channel:** Dispatch chat
- **From:** Brenmoor depot, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-251 delivered 12:21 UTC, chilled chain intact.

<a id="event-019"></a>
## 2026-03-17 14:35:00 UTC — event 019

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Pell Arrow, recipient
- **To:** Iona Quill, Rivet Delivery Desk

I haven't heard anything back, and I didn't get any email from you. Just tell the driver to deliver it Thursday. I'm home all day. The address is right, so I don't understand why this is so hard. Please don't let it go back to the shop.

