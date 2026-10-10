# Case 291: Customer reverses a redelivery request minutes later

## Case details

- **Source role:** Vane Yarrow, recipient
- **Status:** Completed — specific coordination task only
- **Created:** 2026-05-01 09:00:00 UTC
- **Escalated:** 2026-05-01 09:10:00 UTC
- **Updated:** 2026-05-01 10:05:00 UTC
- **Completed:** 2026-05-01 10:05:00 UTC
- **Primary shipment:** DL-291
- **Coordinator:** Iona Quill, Rivet Delivery Desk
- **Data:** Synthetic new; generated 2026-10-10 from the normalized public cases; English; fictional geography; all times UTC

## Context

DL-291 is held at Quillmere depot after a missed delivery, and Dispatch holds a pending redelivery request recorded at 08:50 UTC from Vane Yarrow, whom it verified as the recipient. A later request does not cancel an earlier one automatically. Dispatch, not the desk, books and cancels redelivery and depot collection.

## Initial request

Change of plan, sorry. Please cancel the redelivery I asked for at 08:50 UTC on DL-291. I’ll collect the wool blanket from Quillmere depot myself instead, and I don’t want a driver coming out tomorrow as well.

## Overview

The escalation snapshot comprises history events 001–002. Event 003 records the next agent action; the subsequent events provide the disclosed calibration follow-through. Facts learned later must not be used as if already known at escalation.

## Next action at escalation

Ask Dispatch to apply the recipient’s latest instruction by booking depot collection, cancelling the earlier redelivery request and confirming which instruction stands.

- **Recipient:** Dispatch, Plover Arc Logistics
- **Channel:** Email
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

Dispatch cancels the 2026-05-02 redelivery and books depot collection under COL-291, now the only active instruction on DL-291. A collection booking is not a collection; the parcel is still at Quillmere depot.

## Boundaries and remaining work

The latest verified instruction stands; do not leave both the redelivery and the collection open. The desk books and cancels nothing itself, and collection by the recipient remains pending.

## History

[Read the complete dated history](history.md).

## Attachments

None. Any documentary record is an explicitly inline excerpt in the history, not a separate file.
