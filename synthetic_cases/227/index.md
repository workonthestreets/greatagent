# Case 227: Cancelled order still packed in the outbound cage

## Case details

- **Source role:** Order control, Tallowmere Goods
- **Status:** Completed — specific coordination task only
- **Created:** 2026-04-27 09:00:00 UTC
- **Escalated:** 2026-04-27 09:10:00 UTC
- **Updated:** 2026-04-27 10:05:00 UTC
- **Completed:** 2026-04-27 10:05:00 UTC
- **Primary shipment:** DL-227
- **Coordinator:** Iona Quill, Rivet Delivery Desk
- **Data:** Synthetic new; generated 2026-10-10 from the normalized public cases; English; fictional geography; all times UTC

## Context

Rask Marrow cancelled order TG-227 from the authenticated order-linked portal and Order control has authorised cancellation CAN-227, but DL-227 is still packed in outbound cage B2 for the 16:00 UTC carrier sweep. Warehouse dispatch, not the desk, stops physical dispatch, and the GBP 32.00 refund is the Refunds team’s task.

## Initial request

CAN-227 is authorised, but DL-227 is still physically sitting in cage B2. Please have Warehouse dispatch pull it before the 16:00 UTC sweep and confirm it is out of outbound.

## Overview

The escalation snapshot comprises history events 001–002. Event 003 records the next agent action; the subsequent events provide the disclosed calibration follow-through. Facts learned later must not be used as if already known at escalation.

## Next action at escalation

Ask Warehouse dispatch to apply CAN-227 to DL-227 and confirm its physical removal from outbound before the 16:00 UTC sweep.

- **Recipient:** Warehouse dispatch, Tallowmere Goods
- **Channel:** Warehouse work queue
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

Warehouse dispatch moves DL-227 into cancellation stock and records dispatch stopped. The GBP 32.00 refund is still a separate Refunds team task and has not been paid.

## Boundaries and remaining work

A dispatch stop is not a refund. Do not confirm or promise the GBP 32.00 refund to anyone; only the Refunds team can action it.

## History

[Read the complete dated history](history.md).

## Attachments

None. Any documentary record is an explicitly inline excerpt in the history, not a separate file.
