# Reconciliation: Andrey's delivery system model vs the normalized data

Source model: `user/andrey/drafts/delivery-system-model.md` (commit dc42265 on origin/main). Database: `data/delivery/database/delivery.sqlite`, built by `data/pipeline/build_db.py` from `agent/cases.jsonl`, the hand-curated `facts_delivery.py` and the stress cases on origin/main. Rule applied throughout: a value the cases never state is stored as the literal string `N/A`; nothing from the draft is dropped.

## Entity by entity

- **Order, Shipment, Parcel** come from the case text, hand-curated per case (`facts_delivery.py`). Most consumer cases have only a shipment reference, so `order_id` is N/A there; merchant orders (TG-, BP-, OS-) exist in 14 cases. Shipments carry two state-machine columns: `milestone_at_escalation` (what the agent could know) and `milestone_final` (after the recorded follow-through). Where the draft has no state for the situation (pickup point, locker, customs hold, misdelivery, return legs) the nearest state is used and `model_gap` says so.
- **Event** in the draft is an append-only operational observation (scan, handover, failed attempt, receipt). The case files contain no event feed; observations are embedded in message bodies. The `events` table extracts them sentence by sentence (time or date plus an operational keyword), keeps the source message and its visibility, and tags customer statements as `source_system = customer statement` so that, as the draft requires, a customer statement is never a carrier event.
- **Case** carries every field of the draft's case table (raised by, channel, linked object, request or claim, requested action, state, operational effect, owner, evidence, deadline, resolution) plus the 24 decision parameters. `priority` is N/A for all cases: the data has none; `urgency` is the labelled substitute.
- **Task** is the recorded agent action (event 003) with its assignee, channel and the message that confirmed it. **Evidence** holds the six attachments and every documentary reference (receipts, labels, invoices, credit notes, mandates, inline records, the temperature reading).
- **Messages** are the 228 communications of the public cases plus those of the 20 stress cases; `visible_at_escalation` reproduces the agent-facing cut (`v_decision_input`).
- **Dashboard** (`v_shipment_dashboard`) projects Shipment, Order, Current milestone, Exception, Next action, Owner and ETA exactly as the draft sketches; Order and ETA read N/A when unknown.

## Field table

| Entity | Field (draft) | Draft meaning | Source in the cases | Table.column | Cases with a value (of 50) | N/A policy | Note |
|---|---|---|---|---|---|---|---|
| ORDER | order_id | what the customer bought | merchant order references in the text: TG-, BP-, OS- | `orders.order_id` | 14/50 (28.0%) | N/A when the case only has a shipment reference (most consumer cases) | N/A |
| ORDER | merchant_id | selling merchant | merchant team organisation or TG- prefix | `orders.merchant_id` | 14/50 (28.0%) | N/A when no merchant appears | TG- prefix inferred as Tallowmere Goods in DEL-020 |
| ORDER | customer_id | buyer | requester party; consignee organisation for business cases | `orders.customer_id` | 13/50 (26.0%) | N/A for internal cases | names, not ids: the data has no customer identifiers |
| ORDER | order_status | order-level status | derived from outcome text | `orders.order_status` | 14/50 (28.0%) | N/A unless the case states an order-level fact | the draft asks for order status computed from parcel states; stored as text here |
| SHIPMENT | shipment_id | transport movement reference | DL-, RT-, WP-, PA-, OF- references | `shipments.shipment_id` | 50/50 (100.0%) | always present | DL-044 is an implied consignment id for P1..P4 |
| SHIPMENT | order_id | link to the order | as ORDER.order_id | `shipments.order_id` | 14/50 (28.0%) | N/A when no order reference exists | N/A |
| SHIPMENT | carrier_id | carrier | Plover Arc Logistics; Harbor Thread International for DL-048 | `shipments.carrier_id` | 37/50 (74.0%) | always present | merchant-side returns are also carried by Plover |
| SHIPMENT | shipment_status (milestone_at_escalation) | state-machine state | draft's states, nearest fit | `shipments.milestone_at_escalation` | 50/50 (100.0%) | N/A for shipments created after escalation and for stress cases | see model_gap for pickup point, locker, customs, misdelivery, returns |
| SHIPMENT | shipment_status (milestone_final) | state after the recorded follow-through | draft's states, nearest fit | `shipments.milestone_final` | 50/50 (100.0%) | N/A for stress cases | N/A |
| SHIPMENT | destination | delivery address or point | addresses and counters named in the text | `shipments.destination` | 12/50 (24.0%) | N/A when never stated (most cases) | the data has no postal addresses beyond a handful of streets |
| SHIPMENT | promised_at | promised delivery time | booked windows, guarantees, appointments | `shipments.promised_at` | 18/50 (36.0%) | N/A when no window is stated | stored as the stated window text, not a single timestamp |
| PARCEL | parcel_id | physical unit | sub-unit references (DL-020-A, DL-044-P4, DL-036-A) or 1:1 with the shipment | `parcels.parcel_id` | 50/50 (100.0%) | always present | N/A |
| PARCEL | barcode | label barcode | not in the data | `parcels.barcode` | 0/50 (0.0%) | N/A always | no barcodes anywhere in the 50 cases |
| PARCEL | parcel_status | unit status | text of the case | `parcels.parcel_status` | 50/50 (100.0%) | N/A for stress cases | N/A |
| EVENT | event_id / shipment_id / event_type / location / occurred_at / source_system | append-only operational observation | sentences in message bodies carrying a time or date and an operational keyword (regex) | `events.occurred_at` | 44/50 (88.0%) | location N/A when no place is named; time precision column says whether the date came from the message | customer statements are kept but tagged source_system = customer statement |
| CASE | case_id / case_type | request, dispute, exception or investigation | case id; issue_type label and derived case_category | `cases.case_type` | 50/50 (100.0%) | N/A for unlabelled stress cases | N/A |
| CASE | raised_by | customer, merchant, carrier, depot, customs broker | Source role and requester_type | `cases.raised_by_type` | 50/50 (100.0%) | always present | N/A |
| CASE | channel | portal, phone, email, driver app, API | escalation channel (event 002) mapped to channel_class | `cases.channel_class` | 50/50 (100.0%) | always present | work queues have no slot in the draft list; kept as Work queue |
| CASE | linked_object | order, shipment, parcel, event | primary shipment or task reference | `cases.linked_object_type` | 50/50 (100.0%) | always present | MD-, OF-, KL- references are task records, not in the draft list |
| CASE | request_or_claim | what is asked or disputed | Initial request | `cases.request_or_claim` | 50/50 (100.0%) | always present | N/A |
| CASE | requested_action | the action the raiser wants | hand-written short phrase from events 001-002 | `cases.requested_action_by_raiser` | 50/50 (100.0%) | N/A for stress cases | N/A |
| CASE | case_state | open, waiting, investigating, resolved | queue label at escalation; index Status at the end | `cases.case_state_at_escalation` | 50/50 (100.0%) | final state N/A for stress cases | all 50 public cases end resolved for the coordination task only |
| CASE | operational_effect | shipment hold, route block, refund review ... | hand-written from the outcome | `cases.operational_effect` | 50/50 (100.0%) | N/A for stress cases | N/A |
| CASE | owner | support, depot, safety, customs, billing | gold recipient (owner) and owner_group | `cases.owner_group` | 50/50 (100.0%) | N/A for stress cases without a recorded action | N/A |
| CASE | evidence | photo, scan, invoice, temperature log | evidence table | `evidence.evidence_type` | 34/50 (68.0%) | cases without evidence have no rows | N/A |
| CASE | deadline | SLA or promised update | cutoff in events 001-002 or the next-update time a team gave | `cases.deadline` | 8/50 (16.0%) | N/A when no clock is stated | no SLA exists in the data |
| CASE | resolution | address corrected, replacement approved ... | index Outcome | `cases.resolution` | 50/50 (100.0%) | N/A for stress cases | N/A |
| CASE | priority | case priority | not in the data | `cases.priority` | 0/50 (0.0%) | N/A always | urgency label stored separately |
| CASE | complexity level (draft section 6, easy-to-hard) | Level 1 simple status to 7 reconciliation across shipments | hand-assigned per case from the draft's definitions; stress cases also carry Roman's stress theme | `cases.complexity_level` | 50/50 (100.0%) | always present | levels 1-7 cover 50/50 public cases; 4 stress cases map only loosely (fraud, noisy inbox, duplicate request, customer reversal) |
| TASK | task | concrete action created by a case | the recorded agent action (event 003) with assignee, channel and confirming message | `tasks.status` | 50/50 (100.0%) | completed_at N/A when no confirming message exists | N/A |
| ACTOR | actor | who raises cases and records events | every From/To label, canonicalized | `actors.org_type` | 50/50 (100.0%) | org N/A for people without an organisation | N/A |
| DASHBOARD | Shipment, Order, Current milestone, Exception, Next action, Owner, ETA | shipment-level table | view v_shipment_dashboard | `shipments.milestone_final` | 50/50 (100.0%) | Order and ETA show N/A when unknown | N/A |

## Row counts

cases 170 (public labelled 50, stress unlabelled 20) · orders 38 · shipments 177 · parcels 180 · events 528 · messages 809 · tasks 152 · evidence 301 · actors 263 · case_actors 1235

## Notes for the model author (from the peer review, kept locally in dump-research/pipeline_qa/reports/reconciliation_review.md)

- The dashboard example cites order ids TG-001, TG-002 and TG-023 that exist nowhere in the cases; DL-002 is shown as "Depot hold" while the text says address hold.
- The authority list uses states missing from the diagram: Rebooked, Investigation, Released, Reshipped. Rebooked and Manifested are now used in this database; the others are not.
- Holds (address, safety) have no exit transition in the diagram.
- DL-020-C is a shipment in sections 1 and 2 but a parcel in section 6; here each separately tracked unit is a shipment with a 1:1 parcel.
- The raised-by list omits business shippers and consignees, which raise 7 of the 50 cases.

## Known gaps in the draft that the data exposes

1. The shipment state machine has no states for pickup-point or locker custody, customs holds, misdelivery or return legs; 13 shipments carry a `model_gap` note.
2. The case channel list (portal, phone, email, driver app, API) has no slot for internal work queues (depot, warehouse, safety), which carry 4 escalations and 3 gold actions.
3. `priority` and `barcode` never occur in the data; they are N/A on every row.
4. The draft's `requested_action` is the raiser's ask; the recorded agent action is a different thing and is stored separately as `recorded_next_action` so the two are never conflated.
5. Orders are referenced by prefix only; there are no customer or merchant identifiers, so `customer_id` and `merchant_id` hold names.
