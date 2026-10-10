# Case 231 history — Guarantee claim covers three parcels but only one was late

All identities, records and communications are fictional. Total events: 4.

<a id="event-001"></a>
## 2026-05-01 09:00:00 UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Service guarantees, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Inline guarantee record DL-231, order TG-231 from Harlow Reach Interiors, booked by Wren Marrow: one floor light sent from Harlow Reach depot as three parcels, each on the 12:00 UTC guaranteed service for 2026-04-30 at GBP 32.00 per parcel. Doorstep handovers: DL-231-1 at 11:04 UTC; DL-231-2 at 11:04 UTC; DL-231-3 at 14:19 UTC. No parcel was redirected to Ashvane Counter. The guarantee and its surcharge apply to each parcel separately. Recipient Rask Fane has an authenticated order-linked portal session for TG-231. Guarantee billing decides credits; this record is not a credit decision.

<a id="event-002"></a>
## 2026-05-01 09:10:00 UTC — event 002

- **Stage:** Escalation
- **Channel:** Customer portal
- **From:** Rask Fane, recipient
- **To:** Iona Quill, Rivet Delivery Desk

My floor light came in three parcels on the guaranteed service and the last one only turned up after 14:00, so the order missed its guarantee. Please refund the guarantee surcharge on all three parcels: 3 × GBP 32.00 = GBP 96.00.

<a id="event-003"></a>
## 2026-05-01 09:25:00 UTC — event 003

- **Stage:** Agent action
- **Channel:** Email
- **From:** Iona Quill, Rivet Delivery Desk
- **To:** Guarantee billing, Plover Arc Logistics

Please review a guarantee credit for DL-231-3 only: handed over at 14:19 UTC on 2026-04-30 against the 12:00 UTC guarantee, recorded surcharge GBP 32.00. DL-231-1 and DL-231-2 were handed over at 11:04 UTC, inside the guarantee. The recipient’s portal claim asks for GBP 96.00 across all three parcels; I am not requesting credit on the on-time parcels and have promised the recipient no amount.

<a id="event-004"></a>
## 2026-05-01 09:50:00 UTC — event 004

- **Stage:** Follow-through / confirmation
- **Channel:** Email
- **From:** Guarantee billing, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Credit approved for DL-231-3: GBP 32.00 under credit note CN-231, against that parcel’s guaranteed-time surcharge. DL-231-1 and DL-231-2 met the 12:00 UTC guarantee and receive no credit. CN-231 is posted to the TG-231 order account as an approved credit; it is not yet a settled refund.
