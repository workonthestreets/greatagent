# Delivery roles and actors

This maps the roles visible in the Delivery & Logistics cases to the things they can raise, answer, or change. The case numbers below are from the public Delivery set.

The useful distinction is:

```text
Requester / claimant
    Who raised the issue?

Coordinator
    Who owns the conversation and routes the work?

Authoritative operator
    Who can verify or change the operational fact?

Decision authority
    Who can approve the remedy or final disposition?
```

The first two are often the same person, but the authoritative operator and decision authority are frequently different.

## 1. Recipient or customer

This is the most common case-raising role.

Examples:

- **001** — asks to reschedule delivery.
- **002** — supplies the missing apartment number.
- **004** — requests a pre-arrival call.
- **005** — nominates an alternate household receiver.
- **008** — asks for a timed-delivery quote.
- **013** — disputes a failed-delivery attempt.
- **021** — reports damaged packaging and uploads evidence.
- **024** — disputes a `delivered` scan.
- **028** — requests an exchange for the wrong item.
- **031–032** — requests a printable or printer-free return method.
- **047** — asks for an explanation of an import charge.
- **050** — requests a guaranteed-delivery surcharge credit.

Customers can normally report problems, provide information, choose from offered options, upload evidence, and request an investigation or remedy.

They normally cannot directly mark a shipment delivered, declare it lost, approve a merchant refund, bypass a safety/customs hold, or rewrite carrier scan history.

## 2. Merchant or seller

The merchant owns the commercial order and product-level decision.

Examples:

- **021** — Tallowmere Goods’ damage-intake team specifies required photos.
- **022** — the merchant damage assessor accepts broken-item evidence.
- **025** — replacement authorizations decides whether a replacement is approved after carrier loss.
- **028** — returns authorization approves an exchange.
- **029** — Brineleaf Pantry food-safety staff issue the food disposition and replacement.
- **031–032** — returns teams issue a label or QR token.
- **035** — refunds registers the refund review.
- **038** — reshipment authorizations approves reshipment.
- **039** — order reconciliation handles the duplicate original/replacement shipment.
- **040** — order control and warehouse dispatch stop a packed order.

The merchant can approve replacements, exchanges, returns, cancellations, credits, refunds, product remedies, and commercial documents. It should not invent carrier scans, delivery completion, physical parcel location, or customs clearance.

## 3. Carrier or logistics operator

The carrier appears through specialist functions rather than one generic team. Plover Arc Logistics is used repeatedly in the cases.

Examples:

- **001** — Dispatch provides replacement delivery slots.
- **003** — a route driver handles gated-building access.
- **008** — Scheduling provides timed-delivery capacity and price.
- **011** — the destination depot locates a parcel in a sort cage.
- **013** — Dispatch Review corrects a failed-attempt exception.
- **015** — Routing Control transfers a parcel to the correct depot.
- **018** — Exception Desk handles an approaching return deadline.
- **020** — Parcel Trace locates the missing parcel.
- **024–026** — delivery-investigation, loss-investigation, and recovery teams investigate problems.
- **033** — Collections Control and a collection driver handle a missed return collection.
- **041–044** — freight dispatch, planning, and trace teams handle pallets.
- **048** — Last-mile Intake confirms physical handover.
- **050** — service-guarantees and guarantee-billing teams process a surcharge credit.

The carrier can create scans and routing events, allocate slots, confirm depot possession, record attempts, rebook delivery, investigate delivery anomalies, and arrange collections or redelivery. It normally cannot independently approve a merchant replacement or product refund.

## 4. Delivery desk or support coordinator

Iona Quill of the Rivet Delivery Desk is the recurring coordination layer in the histories, appearing across the ordinary delivery, exception, returns, freight, customs, and billing cases.

The desk’s workflow is:

```text
Receive query
    → identify the linked order/shipment
    → determine the responsible team
    → create or update a case
    → request missing information
    → communicate the verified result
```

For example, in **021**:

```text
Lessa Vire, recipient
    → Rivet Delivery Desk
    → Damage Intake, Tallowmere Goods
    → evidence requirements returned
    → Lessa uploads images
    → merchant confirms evidence is sufficient
```

The desk coordinates, but the merchant still owns the damage assessment.

## 5. Driver or collection crew

Drivers generally do not own customer-service cases, but they create important physical-operation events.

Examples:

- **003** — driver cannot access a gated building.
- **013** — route handset records a failed attempt against the wrong building.
- **026** — recovery driver retrieves and redelivers a misdelivered parcel.
- **033** — collection driver physically collects the return.
- **039** — carrier collects the duplicate original item.
- **037** — specialist crew is booked to collect a 54 kg cabinet in-home.

Driver evidence can include scans, GPS/location, handover time, failed-attempt reason, collection receipt, photos, and site/access assessment. A driver normally cannot decide compensation, replacement, or refund.

## 6. Depot, warehouse, or pickup point

These are physical-operation entities.

Examples:

- **006** — Copperfin Counter receives a redirected parcel.
- **007** — Sedgeglass Counter confirms a pickup extension.
- **011** — destination depot locates a parcel in cage C-17.
- **015** — East Copperfin depot receives a misrouted parcel.
- **016** — locker routing offers a staffed-counter alternative.
- **023** — depot reports leakage and stops movement.
- **034** — returns depot passes a parcel to merchant warehouse receiving.
- **040** — warehouse dispatch removes a cancelled parcel from outbound stock.
- **044** — receiving reports one missing pallet and later signs the revised count.

They can scan physical possession, assign storage, place operational holds, receive or dispatch parcels, count consignments, and isolate unsafe shipments. They normally cannot decide merchant compensation or alter order terms.

## 7. Business sender or consignee

These roles appear in freight and business-delivery cases.

### Business sender / shipping coordinator

- **036** — Fesk Rowan coordinates collection of four labelled cartons.
- **043** — Nessa Dray supplies pallet dimensions and weight.
- **045** — Mavelle Export Studio must provide the commercial invoice.

They provide carton/pallet count, dimensions, weight, dispatch-door information, collection windows, invoice details, and origin information.

### Business consignee / receiving coordinator

- **014** — Rellin Vos provides a staffed receiving window and door.
- **041** — Ossa Rell accepts a receiving-dock appointment.
- **042** — Voren Tesk confirms no forklift and authorizes extra unloading cost.
- **044** — Eron Leth reports the missing pallet and later confirms receipt.
- **049** — Vera Senn, finance coordinator, disputes a duplicate delivery charge.

They can confirm receiving capacity, appointments, dock/access constraints, consignment counts, and certain business costs.

## 8. Customs and import roles

These appear mainly in **045–047**.

### Customs broker

- **045** — Ossmere Trade Desk requests and validates a commercial invoice.
- **046** — Ossmere requires a consignee mandate before processing.

### Import-side account authority

- **046** — Celand Arc Imports’ account administrator and authorized director Mara Vesk complete the broker mandate.
- **047** — recipient Teren Osk asks for an import-charge explanation.

These roles can request documents, confirm document completeness, accept shipment-specific mandates, and explain import/handling charges. They do not automatically guarantee clearance, delivery, or refund.

## 9. Specialist teams

| Specialist | Cases | Typical decision |
|---|---|---|
| Damage assessment | 021–022 | Whether evidence is sufficient and replacement is appropriate |
| Safety lead | 023 | Isolation and safe handling |
| Loss investigation | 024–026 | Whether loss, misdelivery, or recovery is established |
| Food safety | 029 | Whether food should be consumed/disposed of and whether replacement is appropriate |
| Returns | 031–039 | Labels, QR tokens, collections, exchanges, and reshipment |
| Warehouse receiving | 034–035 | Physical return receipt |
| Refunds/billing | 035, 047, 049–050 | Review, credit, charge explanation, or surcharge adjustment |

## 10. Automated systems

The cases also imply non-human actors:

- tracking and status service;
- barcode and scan system;
- route-planning system;
- notification service;
- order-management system;
- returns-label generator;
- customs/document queue;
- billing/invoice system.

Examples:

- **017** — notification template produces an unusable tracking link.
- **020** — parcel-level tracking distinguishes A/B/C shipments.
- **024** — a customer-facing `delivered` status triggers an investigation when disputed.
- **030** — proof of delivery exists internally but has not populated in the customer view.
- **049** — billing contains duplicate invoice lines.
- **050** — guarantee logic determines surcharge-credit eligibility.

These systems can create or project statuses, but they are not equivalent to a human decision owner. A `delivered` scan is an event; it is not automatically the final answer to “I never received it.”

## 11. Role separation in concrete cases

### Case 023 — leaking parcel

```text
Requester: depot shift coordinator
Coordinator: Rivet Delivery Desk
Authoritative operator: Plover Arc safety lead
Decision authority: safety function
Customer: should not handle the parcel
```

### Case 039 — duplicate original and replacement

```text
Requester: customer Dessa Kelm
Coordinator: Rivet Delivery Desk
Authoritative operator: carrier collection team
Decision authority: Tallowmere duplicate-returns/order-reconciliation team
```

### Case 045 — missing commercial invoice

```text
Requester: Ossmere Trade Desk, customs broker
Coordinator: Rivet Delivery Desk
Document provider: Mavelle Export Studio
Validator: Ossmere Trade Desk
Outcome: document package complete; clearance still pending
```

The system should preserve these distinctions. The party who raises a query is not necessarily the party allowed to change the shipment, approve the remedy, or declare the case resolved.
