# Case 299: Customer reverses a redelivery request minutes later

## Case details

- **Source role:** Kira Vosk, recipient
- **Status:** Completed — specific coordination task only
- **Created:** 2026-05-09 09:00:00 UTC
- **Escalated:** 2026-05-09 09:10:00 UTC
- **Updated:** 2026-05-09 10:05:00 UTC
- **Completed:** 2026-05-09 10:05:00 UTC
- **Primary shipment:** DL-299
- **Coordinator:** Iona Quill, Rivet Delivery Desk
- **Data:** Synthetic new; generated 2026-10-10 from the normalized public cases; English; fictional geography; all times UTC

## Context

DL-299 is held at Harlow Reach depot after a missed delivery, and Dispatch holds a pending redelivery request recorded at 08:50 UTC from Kira Vosk, whom it verified as the recipient. A later request does not cancel an earlier one by itself. Dispatch, not the desk, changes delivery instructions.

## Initial request

I’ve changed my mind about DL-299. Please cancel the redelivery I booked at 08:50 UTC. I’ll pick the printer cartridges up from Harlow Reach depot instead, as I’m passing it later today anyway.

## Overview

The escalation snapshot comprises history events 001–002. Event 003 records the next agent action; the subsequent events provide the disclosed calibration follow-through. Facts learned later must not be used as if already known at escalation.

## Next action at escalation

Ask Dispatch to apply the recipient’s latest instruction by booking depot collection, cancelling the earlier redelivery request and confirming which instruction stands.

- **Recipient:** Dispatch, Plover Arc Logistics
- **Channel:** Email
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

Dispatch cancels the 2026-05-11 redelivery and books depot collection under COL-299, the only active instruction on DL-299. The parcel is ready at Harlow Reach depot but has not been collected.

## Boundaries and remaining work

The latest verified instruction stands; do not leave both the redelivery and the collection open. The desk changes no booking itself and handles no collection code.

## History

[Read the complete dated history](history.md).

## Attachments

None. Any documentary record is an explicitly inline excerpt in the history, not a separate file.
