# Case 300 history — Missing pallet buried in a long multi-shipment thread

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-10 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Freight portal
- **From:** Freight dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Thread export, Ferncastle Supplies goods-in, run of 2026-05-09 from Quillmere depot. Three shipments on one load list: DL-300, floor lights for order TG-300, five pallets labelled DL-300/1 to DL-300/5; DL-981, desk chairs, two pallets labelled DL-981/1 and DL-981/2; DL-994, cable reels, three pallets labelled DL-994/1 to DL-994/3. 06:50 UTC, Freight dispatch: load list closed at ten pallets. 09:40 UTC, driver note: nine pallets presented at goods-in; DL-981/2 refused by the consignee for torn wrap; eight pallets signed by Arlo Ulm. 10:15 UTC, Ferncastle Supplies goods-in: can next week’s delivery arrive before 08:00 UTC? 12:30 UTC, Quillmere depot: one pallet returned from the Ferncastle run, scanned in at bay 4. 12:45 UTC, Freight dispatch: missing Ferncastle pallet back at Quillmere depot; query closed. 13:10 UTC, Ferncastle Supplies goods-in: a small parcel for us is waiting at Ashvane Counter; separate matter. Inline signed count excerpt, POD-300, 09:40 UTC: DL-300/1, DL-300/2, DL-300/3, DL-300/5, DL-981/1, DL-994/1, DL-994/2, DL-994/3; eight pallets signed; DL-981/2 noted as refused. The 12:30 UTC return scan is for DL-981/2. No scan for DL-300/4 is recorded after the load list. Coordinator Joss Ives is signed in to the authenticated Ferncastle Supplies business portal session. Physical pallet traces are run by the Freight trace team.

<a id="event-002"></a>
## 2026-05-10 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Joss Ives, Ferncastle Supplies receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

Yesterday’s thread has crossed two different problems. The pallet that went back to Quillmere depot is DL-981/2, which we refused for torn wrap; we’re sorting that with the sender, so it isn’t the missing one. DL-981/1 and all three DL-994 pallets are signed for. The early-delivery question and the Ashvane Counter parcel can wait. What we never received is pallet DL-300/4, floor lights for order TG-300: our signed count for DL-300 is four of five. Please trace DL-300/4 only, and please don’t let it be closed on the DL-981/2 return scan again.

<a id="event-003"></a>
## 2026-05-10 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Freight trace team, Plover Arc Logistics

Please trace pallet DL-300/4, floor lights on shipment DL-300 for order TG-300. It is on the 2026-05-09 load list from Quillmere depot but was not presented at Ferncastle Supplies and is absent from signed count POD-300, which lists DL-300/1, DL-300/2, DL-300/3 and DL-300/5. The 12:30 UTC return scan that closed yesterday’s query is for DL-981/2, a pallet the consignee refused on a different shipment; DL-981/1 and DL-994 are signed for. Please do not close this trace on those scans. I am drawing no conclusion about where DL-300/4 is or why it was missed.

<a id="event-004"></a>
## 2026-05-10 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Freight trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace FT-300 opened for pallet DL-300/4 on shipment DL-300. The pallet was located at Quillmere depot, overflow bay 9, at 09:46 UTC; label DL-300/4 and order TG-300 match. It has no loading scan for 2026-05-09. It is booked on the Ferncastle Supplies run on 2026-05-11, 07:00–09:00 UTC. DL-981/2 is a separate pallet and is not part of this trace. DL-300/4 has not been delivered.

<a id="event-005"></a>
## 2026-05-11 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Freight trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-300/4 was handed over at Ferncastle Supplies goods-in at 08:05 UTC today and signed for by Arlo Ulm on POD-300-B. DL-300 now stands at five of five signed pallets, and trace FT-300 is closed with the count reconciled. The signed count covers pallets received, not the condition of the floor lights.
