# Case gen-09 history — Short shipment: POD says 12, warehouse counts 11, missing carton turns up at Brenmoor depot

All identities, records and communications are fictional. Total events: 39.

<a id="event-001"></a>
## 2026-03-17 07:30:00 UTC — event 001

- **Stage:** Context
- **Channel:** Business portal
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Advance shipping notice for DL-219 (order TG-241). Consignee: Corran Lantern Co., Unit 4, Fennick Row Trade Park. 12 cartons, labels DL-219-01 to DL-219-12, collected by Plover Arc on 2026-03-16. Manifest attached: manifest-DL-219.csv.

<a id="event-002"></a>
## 2026-03-17 07:41:00 UTC — event 002

- **Channel:** Business portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

Auto-acknowledgement: ASN for DL-219 received and linked to order TG-241.

<a id="event-003"></a>
## 2026-03-17 07:55:00 UTC — event 003

- **Channel:** Dispatch chat
- **From:** Halverstone depot dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

FYI DL-221 driver is running about 40 min late on route HV-09 because of a road closure at Marl Bridge. No action is needed from the desk.

<a id="event-004"></a>
## 2026-03-17 08:10:00 UTC — event 004

- **Channel:** Email
- **From:** Network communications, Plover Arc Logistics
- **To:** Partner desks (bulk)

Spring network bulletin: Brenmoor depot sortation line 3 is being commissioned this week. Halverstone–Brenmoor linehaul cages are being re-labelled. Please report any unexpected Brenmoor scans to Delivery investigations. Other news: new van livery and the holiday schedule.

<a id="event-005"></a>
## 2026-03-17 08:22:00 UTC — event 005

- **Channel:** Customer portal
- **From:** Odo Penfeather, recipient
- **To:** Iona Quill, Rivet Delivery Desk

DL-217: I missed the van yesterday. Could I have redelivery on Thursday afternoon?

<a id="event-006"></a>
## 2026-03-17 08:30:00 UTC — event 006

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Scheduling, Plover Arc Logistics

DL-217: the recipient asks for redelivery on Thursday 2026-03-19 in the afternoon. Please book an available slot and confirm.

<a id="event-007"></a>
## 2026-03-17 09:05:00 UTC — event 007

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-217 put on hold by Scheduling. Reason: waiting for slot capacity.

<a id="event-008"></a>
## 2026-03-17 09:40:00 UTC — event 008

- **Channel:** Email
- **From:** Cold chain team, Brineleaf
- **To:** Iona Quill, Rivet Delivery Desk

Attaching the temperature log for chilled pallet DL-222 for your records. All readings were within range, so no action is required.

<a id="event-009"></a>
## 2026-03-17 10:42:00 UTC — event 009

- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Automated status: DL-219 DELIVERED 10:42 UTC, Unit 4 Fennick Row Trade Park. Signed by J. Marrow. Pieces: 12. POD extract attached: pod-DL-219.txt.

<a id="event-010"></a>
## 2026-03-17 10:50:00 UTC — event 010

- **Channel:** Email
- **From:** Greywick Homewares
- **To:** Partner desks (bulk)

Greywick Homewares spring catalogue for partners is now live. Trade pricing is valid until 30 April.

<a id="event-011"></a>
## 2026-03-17 11:15:00 UTC — event 011

- **Stage:** Context
- **Channel:** Email
- **From:** Hesper Vale, receiving lead, Corran Lantern Co.
- **To:** Iona Quill, Rivet Delivery Desk

DL-219 arrived while I was in a meeting. Our temp clerk Jonah Marrow signed for it. We're breaking it down and counting now and I'll confirm shortly.

<a id="event-012"></a>
## 2026-03-17 11:20:00 UTC — event 012

- **Channel:** Email
- **From:** System
- **To:** Hesper Vale, receiving lead, Corran Lantern Co.

Auto-acknowledgement: your message was received by Rivet Delivery Desk.

<a id="event-013"></a>
## 2026-03-17 11:48:00 UTC — event 013

- **Channel:** Dispatch chat
- **From:** Halverstone depot dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-221 delivered 11:31. Closing the late-running note.

<a id="event-014"></a>
## 2026-03-17 12:30:00 UTC — event 014

- **Stage:** Escalation
- **Channel:** Email
- **From:** Hesper Vale, receiving lead, Corran Lantern Co.
- **To:** Iona Quill, Rivet Delivery Desk

We signed for DL-219 this morning but have only 11 cartons on our dock. Carton DL-219-07 is missing. Our temp clerk signed without counting first. Please find out where it is and get it to us. We need everything for our Fennick Row store opening on Friday 2026-03-20. Photo of the 11 cartons with labels visible is attached. Jonah says he wrote 'STC' on the handset.

<a id="event-015"></a>
## 2026-03-17 12:45:00 UTC — event 015

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Tracking support, Plover Arc Logistics

DL-219: the consignee counts 11 of 12 cartons, and DL-219-07 is missing. POD shows 12 pieces. Please check the piece-level scans for each label against the POD and tell us the last scan for DL-219-07.

<a id="event-016"></a>
## 2026-03-17 12:46:00 UTC — event 016

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Hesper Vale, receiving lead, Corran Lantern Co.

Thanks, Hesper. I've asked Plover Arc to check the piece-level scans for DL-219-07 against the POD. There's no finding yet. I'll update you when they reply.

<a id="event-017"></a>
## 2026-03-17 13:10:00 UTC — event 017

- **Channel:** Email
- **From:** Collections control, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

INV-231 (unrelated account Marrowby Print) payment is overdue. Could you remind the account holder? Reference INV-231.

<a id="event-018"></a>
## 2026-03-17 13:40:00 UTC — event 018

- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-219: the consignment shows all 12 pieces out for delivery and delivered, with POD signed for 12. The driver confirms 12 were handed over. From our side the delivery is complete.

<a id="event-019"></a>
## 2026-03-17 13:55:00 UTC — event 019

- **Channel:** Dispatch chat
- **From:** Teo Brack, route driver HV-14, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-219: I unloaded the cage at Unit 4 and the clerk signed. I keyed 12 because that's what the consignment said. I didn't scan every box at the door because the handset was lagging.

<a id="event-020"></a>
## 2026-03-17 14:20:00 UTC — event 020

- **Channel:** Business portal
- **From:** Warehouse dispatch, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Re DL-219 / TG-241: our pick and pack confirmation shows 12 cartons packed. Carton 07 (lamp bases, 14.2 kg) was weighed at 15:52 on 2026-03-16. Plover collection scan at 16:10 on 2026-03-16 shows 12 pieces. All 12 left our dock.

<a id="event-021"></a>
## 2026-03-17 14:30:00 UTC — event 021

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-219 note by Tracking support: Delivered, no action required.

<a id="event-022"></a>
## 2026-03-17 15:00:00 UTC — event 022

- **Channel:** Broker portal
- **From:** Ossmere Trade Desk
- **To:** Iona Quill, Rivet Delivery Desk

DL-228: the customs entry has been lodged. We're waiting on the commercial invoice copy from the importer. Nothing is needed from the desk today.

<a id="event-023"></a>
## 2026-03-17 15:20:00 UTC — event 023

- **Channel:** Pickup-point portal
- **From:** Locker routing, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-226 has been placed in locker bank Q7 at Sennet Square. Pickup code sent to the recipient.

<a id="event-024"></a>
## 2026-03-17 16:05:00 UTC — event 024

- **Channel:** Email
- **From:** Hesper Vale, receiving lead, Corran Lantern Co.
- **To:** Iona Quill, Rivet Delivery Desk

Any news? We've recounted twice and there are still 11. Carton 07 holds the lamp bases for the window display, and we can't open on Friday without them.

<a id="event-025"></a>
## 2026-03-17 16:20:00 UTC — event 025

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Hesper Vale, receiving lead, Corran Lantern Co.

Plover Arc's first reply says the delivery is complete, but that doesn't match your count. I'm still following it up and haven't concluded anything. I'll come back to you as soon as I have more.

<a id="event-026"></a>
## 2026-03-17 17:00:00 UTC — event 026

- **Channel:** Email
- **From:** Notification support, Plover Arc Logistics
- **To:** Partner desks (bulk)

Resolved: SMS notification delays affecting the north region between 14:10 and 16:30 UTC.

<a id="event-027"></a>
## 2026-03-17 18:30:00 UTC — event 027

- **Channel:** Email
- **From:** Customer care, Greywick Homewares
- **To:** Iona Quill, Rivet Delivery Desk

DL-230: the customer reports a crushed box corner and the contents are fine. Recording this for information only.

<a id="event-028"></a>
## 2026-03-17 19:15:00 UTC — event 028

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-219 update: piece DL-219-07, Brenmoor depot, ARRIVAL – no matching manifest.

<a id="event-029"></a>
## 2026-03-17 19:16:00 UTC — event 029

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-219 update: piece DL-219-07, Brenmoor depot, ARRIVAL – no matching manifest. (duplicate scan)

<a id="event-030"></a>
## 2026-03-17 21:00:00 UTC — event 030

- **Channel:** Email
- **From:** Partner bulletin, Tallowmere Goods
- **To:** Partner desks (bulk)

Tallowmere partner bulletin: Easter dispatch cut-offs and a new returns label format from April.

<a id="event-031"></a>
## 2026-03-18 06:02:00 UTC — event 031

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-219 update: piece DL-219-07 HELD at Brenmoor depot, awaiting instructions. Reason: unmanifested piece.

<a id="event-032"></a>
## 2026-03-18 06:30:00 UTC — event 032

- **Channel:** Depot work queue
- **From:** Brenmoor depot, Plover Arc Logistics
- **To:** Partner desks (auto-list)

Unmatched items list, 18 Mar: DL-219-07 (14.1 kg, shelf B-12, arrived on HAL–BRN linehaul cage 3), DL-208-02 (shelf B-03), DL-233-01 (shelf C-01). Unmatched items not claimed within 5 days are returned to the origin depot or the sender.

<a id="event-033"></a>
## 2026-03-18 07:10:00 UTC — event 033

- **Channel:** Dispatch chat
- **From:** Halverstone depot dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Route HV-09 and HV-14 boundaries change from Monday. Informational only.

<a id="event-034"></a>
## 2026-03-18 07:45:00 UTC — event 034

- **Channel:** Customer portal
- **From:** System
- **To:** Iona Quill, Rivet Delivery Desk

DL-217 hold released by Scheduling. Booked for 2026-03-19, 13:00–17:00 UTC.

<a id="event-035"></a>
## 2026-03-18 08:05:00 UTC — event 035

- **Channel:** Email
- **From:** Replacement authorisations, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

We've been copied on the DL-219 short-delivery report. We don't authorise replacements while the carrier hasn't investigated. Please make sure Plover Arc has a piece-level trace open. Under our carrier terms, short-delivery reports must reach the carrier within 3 business days of POD. If the carrier confirms the carton is lost, we'll review a replacement under TG-241.

<a id="event-036"></a>
## 2026-03-18 08:20:00 UTC — event 036

- **Channel:** Email
- **From:** Tracking support, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Updated full piece-level scan log for DL-219 is attached: scan-log-DL-219.csv. Tracking support can't open traces or change POD records. Piece-level discrepancies have to be raised with Delivery investigations, who coordinate with the depots.

<a id="event-037"></a>
## 2026-03-18 08:40:00 UTC — event 037

- **Channel:** Email
- **From:** Collections control, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

INV-231 paid. Please disregard the earlier reminder.

<a id="event-038"></a>
## 2026-03-18 08:55:00 UTC — event 038

- **Channel:** Email
- **From:** Customer care, Tallowmere Goods
- **To:** Iona Quill, Rivet Delivery Desk

Unrelated: order TG-238 is waiting on a customer address confirmation. We'll handle it directly with the customer.

<a id="event-039"></a>
## 2026-03-18 09:12:00 UTC — event 039

- **Stage:** Escalation
- **Channel:** Email
- **From:** Hesper Vale, receiving lead, Corran Lantern Co.
- **To:** Iona Quill, Rivet Delivery Desk

It's Wednesday now. Plover says they delivered 12, we have 11, and nobody is telling me where carton 07 is. My MD wants to reorder the lamp bases from Tallowmere straight away and knock carton 07 off Tallowmere's invoice for TG-241. What is actually happening? Can carton 07 be here by Friday, and should we go ahead with the deduction?

