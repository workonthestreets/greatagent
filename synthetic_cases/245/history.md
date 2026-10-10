# Case 245 history — Delivery service charged twice on one invoice

All identities, records and communications are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-05-15 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Freight portal
- **From:** Freight dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Inline delivery record DL-245: one pallet of wool blankets from Quillmere depot to Ferncastle Supplies, delivered in a single drop on 2026-05-12. One pallet delivery service was booked and performed. Ulla Marrow is verified by Plover Arc Logistics account checks as Ferncastle Supplies’ registered contact for DL-245 invoices. Invoice queries and credits sit with Business billing, not Freight dispatch.

<a id="event-002"></a>
## 2026-05-15 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Ulla Marrow, Ferncastle Supplies receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

Invoice INV-245 bills the DL-245 delivery service twice. Inline excerpt, INV-245 dated 2026-05-14: line 1, DL-245 pallet delivery service, 2026-05-12, GBP 30.00; line 2, DL-245 pallet delivery service, 2026-05-12, GBP 30.00; total GBP 60.00. We took one delivery that day. We have paid neither line. Please have the invoice checked and corrected.

<a id="event-003"></a>
## 2026-05-15 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Business billing, Plover Arc Logistics

Please review invoice INV-245 for Ferncastle Supplies, where lines 1 and 2 are identical: each is DL-245 pallet delivery service on 2026-05-12 at GBP 30.00. Freight dispatch’s record shows one delivery service performed on DL-245. Verified invoice contact Ulla Marrow reports that neither line has been paid. If your review confirms a duplicate, please issue a credit for the duplicated line. I have not told the customer that either line is wrong or that a credit is agreed.

<a id="event-004"></a>
## 2026-05-15 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Business billing, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

INV-245 reviewed. Line 2 duplicates line 1: same shipment, service, date and booking. Credit note CN-245 issued for GBP 30.00 against line 2. Revised INV-245 balance: GBP 30.00, unpaid. A credit note is not cash received; no payment or refund has moved.
