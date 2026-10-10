# Case 280 history — Import held for a missing commercial invoice

All identities, records and communications are fictional. Total events: 5.

<a id="event-001"></a>
## 2026-04-20 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Broker portal
- **From:** Ossmere Trade Desk, appointed customs broker
- **To:** Iona Quill, Rivet Delivery Desk

Broker file OS-280: DL-280, one carton of desk lamps from Oakhollow Press to consignee Ulla Wick, arrived with Harbor Thread International and is held at import. The only document on file is a pro-forma invoice, which cannot support the entry. Our appointment on DL-280 is on record, and this note is posted from our authenticated broker portal session. The shipper record lists Ulla Fane, Oakhollow Press shipping lead, as the authorised contact, with a verified email address. If released, DL-280 goes to East Copperfin depot and on to Copperfin Counter, the consignee’s chosen collection point.

<a id="event-002"></a>
## 2026-04-20 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Broker portal
- **From:** Ossmere Trade Desk, appointed customs broker
- **To:** Iona Quill, Rivet Delivery Desk

For OS-280 we need the shipper’s commercial invoice, not the pro-forma, with these fields: seller and buyer names and addresses; invoice number and date; description of the goods; number of units; unit price, total value and currency; country of manufacture; tariff code; terms of sale; signed declaration by the shipper. Please request it from the authorised shipper contact and leave every value to them; the desk should not complete or correct any field.

<a id="event-003"></a>
## 2026-04-20 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Ulla Fane, Oakhollow Press shipping lead

DL-280 (desk lamps, one carton) is held at import, and the appointed broker, Ossmere Trade Desk, cannot use the pro-forma on file. Please send your commercial invoice by reply with: seller and buyer names and addresses; invoice number and date; description of the goods; number of units; unit price, total value and currency; country of manufacture; tariff code; terms of sale; your signed declaration. We have not completed or corrected any field. The broker reviews the document, and receiving it is not clearance.

<a id="event-004"></a>
## 2026-04-20 09:45:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Ulla Fane, Oakhollow Press shipping lead
- **To:** Iona Quill, Rivet Delivery Desk

Commercial invoice INV-280 for DL-280, inline excerpt: “Invoice INV-280, dated 2026-04-20. Seller: Oakhollow Press. Buyer: Ulla Wick. Both full addresses shown. Goods: desk lamps, 1 carton, 12 units. Unit price, total value and currency: entered. Country of manufacture and tariff code: entered. Terms of sale: DAP. Declaration signed: Ulla Fane, shipping lead.” This replaces the pro-forma.

<a id="event-005"></a>
## 2026-04-20 10:05:00 UTC — event 005

- **Stage:** Follow-through / confirmation
- **Channel:** Broker portal
- **From:** Ossmere Trade Desk, appointed customs broker
- **To:** Iona Quill, Rivet Delivery Desk

INV-280 received through the desk and checked against OS-280 at 10:00 UTC. All listed fields are present; the document package is complete and the entry for DL-280 is lodged for customs review. No clearance decision has been made, and DL-280 remains held at import.
