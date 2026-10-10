# Case 254 history — Delivery service charged twice on one invoice

All identities, records and communications are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-05-24 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Freight portal
- **From:** Freight dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

DL-254, one carton of kitchen scales, left Harlow Reach depot and was delivered to Brindlewick Studio at 11:20 UTC on 2026-05-22 under POD-254. Our run sheet shows one stop for it. We verified Hest Orme as Brindlewick Studio’s registered receiving coordinator by call-back to the account number on file at 08:45 UTC today. Freight dispatch cannot see invoices; Business billing reviews invoice lines and any credit.

<a id="event-002"></a>
## 2026-05-24 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Business portal
- **From:** Hest Orme, Brindlewick Studio receiving coordinator
- **To:** Iona Quill, Rivet Delivery Desk

Inline excerpt, invoice INV-254: line 3, DL-254 delivery service, 2026-05-22, GBP 24.00; line 4, DL-254 delivery service, 2026-05-22, GBP 24.00; total due GBP 66.00. Lines 1 and 2 are not in question. We received one delivery and have paid nothing on this invoice. Please have the repeated line reviewed and credited if it is a duplicate.

<a id="event-003"></a>
## 2026-05-24 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Business billing, Plover Arc Logistics

Please review lines 3 and 4 of INV-254, each DL-254 delivery service, 2026-05-22, GBP 24.00. Freight dispatch records one delivery that day under POD-254 and verified Hest Orme by call-back; Hest reports nothing on the invoice paid. If duplication is confirmed, please issue a credit and state the revised balance. The desk has drawn no conclusion on either line and given no payment advice.

<a id="event-004"></a>
## 2026-05-24 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Business billing, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

INV-254 checked against POD-254: line 4 duplicates line 3, with no second service behind it. CN-254 credits GBP 24.00 against line 4, and the revised INV-254 balance is GBP 42.00 due. No payment or refund has moved; a credit note is not cash received.
