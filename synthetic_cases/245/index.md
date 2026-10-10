# Case 245: Delivery service charged twice on one invoice

## Case details

- **Source role:** Ulla Marrow, Ferncastle Supplies receiving coordinator
- **Status:** Completed — specific coordination task only
- **Created:** 2026-05-15 09:00:00 UTC
- **Escalated:** 2026-05-15 09:10:00 UTC
- **Updated:** 2026-05-15 09:50:00 UTC
- **Completed:** 2026-05-15 09:50:00 UTC
- **Primary shipment:** DL-245
- **Coordinator:** Iona Quill, Rivet Delivery Desk
- **Data:** Synthetic new; generated 2026-10-10 from the normalized public cases; English; fictional geography; all times UTC

## Context

Freight dispatch records one pallet delivery service on DL-245, and Plover Arc Logistics has verified Ulla Marrow as Ferncastle Supplies’ registered invoice contact. Business billing, not the desk, decides whether an invoice line is a duplicate and issues any credit.

## Initial request

Invoice INV-245 bills the DL-245 delivery service twice. Inline excerpt, INV-245 dated 2026-05-14: line 1, DL-245 pallet delivery service, 2026-05-12, GBP 30.00; line 2, DL-245 pallet delivery service, 2026-05-12, GBP 30.00; total GBP 60.00. We took one delivery that day. We have paid neither line. Please have the invoice checked and corrected.

## Overview

The escalation snapshot comprises history events 001–002. Event 003 records the next agent action; the subsequent events provide the disclosed calibration follow-through. Facts learned later must not be used as if already known at escalation.

## Next action at escalation

Ask Business billing to review the two identical DL-245 lines on INV-245 and issue a credit if it confirms duplication.

- **Recipient:** Business billing, Plover Arc Logistics
- **Channel:** Email
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

Business billing confirms that line 2 duplicates line 1 and issues credit note CN-245 for GBP 30.00, leaving a revised unpaid balance of GBP 30.00. A credit note is not cash received.

## Boundaries and remaining work

A credit note is not cash received. The desk does not conclude duplication or promise a credit; Business billing decides after its review.

## History

[Read the complete dated history](history.md).

## Attachments

None. Any documentary record is an explicitly inline excerpt in the history, not a separate file.
