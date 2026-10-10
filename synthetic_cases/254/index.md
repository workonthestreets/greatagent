# Case 254: Delivery service charged twice on one invoice

## Case details

- **Source role:** Hest Orme, Brindlewick Studio receiving coordinator
- **Status:** Completed — specific coordination task only
- **Created:** 2026-05-24 09:00:00 UTC
- **Escalated:** 2026-05-24 09:10:00 UTC
- **Updated:** 2026-05-24 09:50:00 UTC
- **Completed:** 2026-05-24 09:50:00 UTC
- **Primary shipment:** DL-254
- **Coordinator:** Iona Quill, Rivet Delivery Desk
- **Data:** Synthetic new; generated 2026-10-10 from the normalized public cases; English; fictional geography; all times UTC

## Context

Invoice INV-254 bills the same DL-254 delivery service twice at GBP 24.00, and Brindlewick Studio has paid nothing on it. Freight dispatch verified the coordinator by call-back and records one delivery; Business billing, not the desk, reviews invoice lines and decides any credit.

## Initial request

Inline excerpt, invoice INV-254: line 3, DL-254 delivery service, 2026-05-22, GBP 24.00; line 4, DL-254 delivery service, 2026-05-22, GBP 24.00; total due GBP 66.00. Lines 1 and 2 are not in question. We received one delivery and have paid nothing on this invoice. Please have the repeated line reviewed and credited if it is a duplicate.

## Overview

The escalation snapshot comprises history events 001–002. Event 003 records the next agent action; the subsequent events provide the disclosed calibration follow-through. Facts learned later must not be used as if already known at escalation.

## Next action at escalation

Ask Business billing to review INV-254 lines 3 and 4 and issue a credit if it confirms duplication.

- **Recipient:** Business billing, Plover Arc Logistics
- **Channel:** Email
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

Business billing confirms line 4 as a duplicate, raises CN-254 for GBP 24.00 and revises the INV-254 balance to GBP 42.00. No money has moved; a credit note is not cash received.

## Boundaries and remaining work

A credit note is not cash received. The desk does not judge the lines itself or advise Brindlewick Studio on payment.

## History

[Read the complete dated history](history.md).

## Attachments

None. Any documentary record is an explicitly inline excerpt in the history, not a separate file.
