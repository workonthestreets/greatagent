# Case 292 history — Missing pallet buried in a long multi-shipment thread

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-05-02 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Freight portal
- **From:** Freight dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Thread export, Harlow Reach Interiors goods-in, run of 2026-05-01 from Quillmere depot. One load list covered three shipments: DL-292, kitchen scales for order TG-292, four pallets labelled DL-292/1 to DL-292/4; DL-917, wall shelving, three pallets labelled DL-917/1 to DL-917/3; DL-934, light fittings, two pallets labelled DL-934/1 and DL-934/2. 13:55 UTC, Freight dispatch: load list closed at nine pallets; vehicle departed. 14:20 UTC, Quillmere depot: DL-917/3 found in bay 6 after departure; added to the 16:00 UTC run. 15:05 UTC, driver note: seven pallets handed over at goods-in; tail-lift used; count signed by Orra Dorne. 15:40 UTC, Harlow Reach Interiors goods-in: please send accounts an invoice copy for DL-934. 16:05 UTC, Harlow Reach Interiors goods-in: the driver left a card for a small parcel held at Ashvane Counter; not urgent. 16:50 UTC, driver note: DL-917/3 handed over on the second run; signed. 17:10 UTC, Freight dispatch: Harlow Reach shortage cleared by the second run; query closed. Inline signed count excerpt, POD-292, 15:05 UTC: DL-292/1, DL-292/2, DL-292/4, DL-917/1, DL-917/2, DL-934/1, DL-934/2; seven pallets. Second-run count, POD-917, 16:50 UTC: DL-917/3. No scan for DL-292/3 is recorded after the load list. Coordinator Arlo Ives is signed in to the authenticated Harlow Reach Interiors business portal session. Physical pallet traces are run by the Freight trace team.

<a id="event-002"></a>
## 2026-05-02 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Arlo Ives, Harlow Reach Interiors receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

Picking up yesterday’s thread, which has got muddled. DL-917 is complete on our side now that the second run brought DL-917/3, and DL-934 is complete too; accounts still want that invoice copy, but that is separate. The query was closed on the second-run delivery, but that pallet was DL-917/3, not ours from DL-292. Our signed count for DL-292 is three of four: we have DL-292/1, DL-292/2 and DL-292/4. Pallet DL-292/3, kitchen scales for order TG-292, never arrived. The driver also mentioned moving next week’s slot; leave that for now. Please get DL-292/3 traced. It is the only pallet we are missing.

<a id="event-003"></a>
## 2026-05-02 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Freight trace team, Plover Arc Logistics

Please trace pallet DL-292/3, one pallet of kitchen scales on shipment DL-292 for order TG-292. It is on the 2026-05-01 load list from Quillmere depot but absent from signed count POD-292 at Harlow Reach Interiors, which lists DL-292/1, DL-292/2 and DL-292/4, and no scan for it is recorded after the load list. Yesterday’s query was closed on the second-run delivery of DL-917/3, a pallet on a different shipment, and DL-917 and DL-934 are complete on the consignee’s count. Please do not close this trace on those scans. I am drawing no conclusion about where the pallet is or why it was missed.

<a id="event-004"></a>
## 2026-05-02 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Freight trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Trace FT-292 opened for pallet DL-292/3 on shipment DL-292. The pallet was located at Quillmere depot, bay 2, at 09:44 UTC; label DL-292/3 and order TG-292 match. It has no departure scan since the 2026-05-01 load list. It is booked on the first Harlow Reach Interiors run on 2026-05-03, 07:00–09:00 UTC. It has not been delivered.

<a id="event-005"></a>
## 2026-05-03 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Freight trace team, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-292/3 was handed over at Harlow Reach Interiors goods-in at 08:20 UTC today; signed count POD-292-B lists one pallet. DL-292 now stands at four of four signed pallets, and trace FT-292 is closed with the count reconciled. The signed count confirms pallets received, not the condition of the kitchen scales inside.
