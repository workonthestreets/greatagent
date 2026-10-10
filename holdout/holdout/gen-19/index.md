# Case gen-19: Merchant asks whether a collection is booked after two carrier booking API calls returned HTTP 503

## Case details

- **Source role:** Tamsin Hool, shipping coordinator, Fennick & Daw Ceramics
- **Status:** Escalated — awaiting desk action
- **Created:** 2026-04-14 08:02:00 UTC
- **Escalated:** 2026-04-14 13:18:00 UTC
- **Primary shipment:** SHP-40917
- **Coordinator:** Odile Marrow, Kestrel Lane Delivery Desk
- **Data:** Entirely synthetic evaluation case generated for this repository; fictional people and places; all times UTC

## Context

Fennick & Daw Ceramics ships through Kestrel Lane Delivery Desk. The desk books collections with Brindlewick Freight through Kestrel's TMS, which calls Brindlewick's Booking API. Brindlewick Collections Planning decides whether a collection is accepted and issues the booking references. Brindlewick Integration Support owns the API and its incident status. The merchant decides what goes in the consignment and where it is collected from.

## Initial request

Please book a Brindlewick collection for SHP-40917 (order ORD-55130) for tomorrow, 15 April, from 10:00 UTC. 6 cartons, manifest attached. It has to reach Pellin Home Store by 16 April.

## History

[Read the complete dated history](history.md).

## Attachments

- [manifest-SHP-40917.csv](attachments/manifest-SHP-40917.csv)
- [brindlewick-api-response-SHP-40917.json](attachments/brindlewick-api-response-SHP-40917.json)
