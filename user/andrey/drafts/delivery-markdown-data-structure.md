# Delivery Markdown data structure and agent actions

This describes how the Delivery & Logistics cases are actually represented in the Markdown files, what each field means, and what an agent can reasonably do from the available data.

## 1. File package per case

Each of the 50 cases has the same basic package:

```text
Delivery & Logistics/
└── 001/
    ├── index.md
    ├── history.md
    └── attachments/       # only for some cases
```

There are two different kinds of information:

| File | Role |
|---|---|
| `index.md` | Current case summary, key identifiers, next action, outcome, boundaries |
| `history.md` | Chronological event log and the detailed communication record |
| `attachments/*` | Supporting document/image artifacts referenced by the case |

The index is a convenient projection. The history is the important source for chronology and who said or did what.

## 2. `index.md` structure

All 50 Delivery cases use the same sections:

```text
# Case NNN: title

## Case details
## Context
## Initial request
## Overview
## Next action at escalation
## Outcome
## Boundaries and remaining work
## History
## Attachments
```

### Case details

The common metadata fields are:

| Field | Meaning |
|---|---|
| Source role | The party who originated the case/request |
| Status | Status of the coordination case, not necessarily delivery status |
| Created | Time the case record was created |
| Escalated | Time the request entered the escalation workflow |
| Updated | Last recorded case update |
| Completed | Time the narrow coordination task was marked complete |
| Recipient | Customer, business contact, or operational requester |
| Primary shipment | Main shipment ID, present in 41 cases |
| Primary task reference | Alternative reference used in 9 cases |
| Coordinator | Usually Iona Quill / Rivet Delivery Desk |
| Data | Synthetic-data and time-zone note |

The nine cases using `Primary task reference` rather than `Primary shipment` are:

| Case | Reference | Why it matters |
|---|---|---|
| 020 | TG-020 | Multi-parcel order rather than one shipment |
| 027 | MD-027 | Misdelivery intake/reference |
| 033 | RT-033 | Return collection |
| 034 | RT-034 | Return movement to merchant |
| 035 | TG-035 | Refund-review workflow |
| 036 | OF-036 | Outbound consignment |
| 037 | RT-037 | Specialist return |
| 039 | TG-039 | Original/replacement reconciliation |
| 044 | KL-044 | Multi-pallet consignment |

This is a useful warning: the primary object is not always a single parcel. It can be an order, return, consignment, or task reference.

### Context

Context describes the authoritative starting condition known before the customer-facing escalation.

Examples:

- **002**: address hold because the apartment number is missing.
- **011**: last public scan is arrival at the destination depot.
- **023**: visible leakage at a depot; movement has stopped.
- **029**: temperature reading is 9.2°C against a documented 0–5°C range.
- **040**: cancellation is authorized but the parcel is still in an outbound cage.

Context is not necessarily the final truth. It is the starting snapshot for the task.

### Initial request

This is usually the requester’s plain-language problem or desired action:

- “Please move my delivery.”
- “Can you locate the missing parcel?”
- “Please arrange the exchange.”
- “Please explain this import charge.”

It is a request, not automatically an authorization. The request may still need verification, customer choice, merchant approval, or specialist review.

### Overview

The Delivery cases use the overview to explain the temporal boundary of the task. In particular, it generally distinguishes:

```text
Events 001–002: escalation snapshot
Event 003: recorded next agent action
Later events: disclosed follow-through/calibration
```

This is critical for an agent answering at escalation time: later facts should not be presented as if they were already known.

### Next action at escalation

This is the most important field for deciding what the agent should do next. It normally includes:

| Subfield | Meaning |
|---|---|
| Recipient | Who the agent should contact or ask |
| Channel | Approved channel for the action |
| Recorded action | The action actually recorded in history event 003 |

Examples:

- **001**: ask the recipient to choose from dispatcher-confirmed slots.
- **002**: ask only for the missing apartment number.
- **021**: request two specific damage views through the upload channel.
- **023**: escalate immediately to safety; do not route to a driver or customer.
- **045**: request a complete commercial invoice; do not invent values.

This section usually describes the agent’s next action, not the final outcome.

### Outcome

Outcome summarizes what the later history eventually confirmed.

It may say that:

- a booking was made;
- an address hold was cleared;
- evidence was received;
- a return was collected;
- a replacement was approved;
- a credit was issued.

It may also preserve an incomplete result:

- **001**: booking confirmed, delivery still pending.
- **024**: investigation registered, no finding yet.
- **034**: merchant receipt confirmed, inspection/refund pending.
- **045**: invoice complete, customs clearance still undecided.

“Completed” therefore means the specific coordination task was completed, not necessarily that the whole commercial or physical situation is finished.

### Boundaries and remaining work

This section contains explicit negative constraints. These are operationally important, not decorative prose.

Examples:

- Do not promise a precise arrival time.
- Do not mark a delivery complete from a booking.
- Do not treat synthetic photos as real physical evidence.
- Do not promise compensation.
- Do not ask a customer to handle an unsafe parcel.
- Do not treat document receipt as customs clearance.
- Do not treat an investigation registration as a loss finding.

An agent should read this section before drafting the response.

### Attachments

Most cases state that no attachments are available and that records are inline in the history. Six cases contain actual files:

| Case | Artifact |
|---|---|
| 021 | Two packaging-damage images |
| 031 | Printable return-label PDF |
| 032 | Printer-free return QR image |
| 045 | Commercial invoice PDF |
| 049 | Credit statement PDF |

An attachment is evidence or an operational artifact. Its presence does not automatically prove that the underlying business decision is complete.

## 3. `history.md` structure

The history has this shape:

```text
# Case NNN history — title

Total events: N.

<a id="event-001"></a>
## YYYY-MM-DD HH:MM:SS UTC — event 001

- **Stage:** Context
- **Channel:** Email
- **From:** Dispatch, Plover Arc Logistics
- **To:** Iona Quill, Rivet Delivery Desk

Operational or conversational message.
```

Every event has:

1. Stable event anchor, such as `event-003`.
2. Timestamp in UTC.
3. Event number.
4. Stage.
5. Channel.
6. Sender.
7. Recipient.
8. Free-text message or inline record.

### Stage values

Across the full Delivery set there are 228 events:

| Stage | Count | Meaning |
|---|---:|---|
| Context | 50 | Existing operational fact or record |
| Escalation | 50 | Request or problem raised |
| Agent action | 50 | The next action the agent records |
| Follow-through / confirmation | 78 | Later confirmation, evidence, or result |

The stage is a narrative workflow label, not the shipment’s operational status. For example, a `Follow-through / confirmation` event can say that a parcel is still pending, that an investigation has only been registered, or that a booking is confirmed but delivery has not happened.

### Channels

Observed channels include:

- Email;
- Customer portal;
- Business portal;
- Dispatch chat;
- Call transcript;
- Depot work queue;
- Warehouse work queue;
- Safety incident queue;
- Broker portal;
- Freight portal;
- Pickup-point portal.

The channel helps determine what kind of action is valid. For example:

- a customer choice may need to come through an order-linked portal;
- a safety escalation goes through a safety incident queue;
- a customs mandate goes through a verified business portal;
- a physical location update comes from a depot or warehouse queue.

### From and To

The sender and recipient fields show the handoff graph of the case. The same case may move through several organizational boundaries:

```text
Customer
  → Rivet Delivery Desk
  → Carrier specialist team
  → Merchant or warehouse
  → Rivet Delivery Desk
  → Customer
```

The sender is not automatically authoritative for every claim. A customer can report non-receipt; the carrier can provide a delivery scan; a merchant can decide a replacement; a safety lead can isolate a parcel.

## 4. Temporal reasoning

The data is intentionally designed around “what was known when”.

For an escalation-time answer, use:

```text
Known facts = Context + Escalation
Required response = Agent action at event 003
Do not use yet = Later follow-through events
```

Example: **Case 024**

At escalation:

```text
Known: tracking says delivered
Known: recipient says no one received it
Action: open an investigation
Unknown: whether the parcel was lost, misdelivered, or recovered
```

The later confirmation that an investigation was registered does not turn into a loss finding.

## 5. What can be extracted into structured data

A parser could convert each case into roughly these records:

```text
case {
  case_id,
  title,
  source_role,
  recipient,
  coordinator,
  status,
  created_at,
  escalated_at,
  updated_at,
  completed_at,
  primary_reference,
  context,
  initial_request,
  next_action,
  outcome,
  boundaries
}

event {
  event_id,
  case_id,
  sequence_number,
  occurred_at,
  stage,
  channel,
  sender,
  recipient,
  message,
  attachment_refs
}

attachment {
  attachment_id,
  case_id,
  filename,
  media_type,
  referenced_in_event
}
```

The free-text message still matters. It often contains the actual shipment IDs, parcel IDs, dates, quantities, measurements, temperature readings, prices, and negative statements such as “not yet delivered” or “decision pending”.

## 6. Actions an agent can take

The `Next action at escalation` section plus event 003 usually indicates the allowed action. Common actions are:

| Agent action | Examples | Result |
|---|---|---|
| Ask for missing information | 002, 009, 043, 045 | More data is requested through the appropriate channel |
| Offer choices | 001, 006, 018 | Customer selects from confirmed options |
| Record a preference | 004, 005, 010 | Route/order note is updated |
| Request a booking or rebooking | 008, 012, 014, 033, 041 | Carrier or receiving appointment is created |
| Trace or locate a shipment | 011, 015, 020, 026, 044 | Physical or routing status is checked |
| Open an investigation | 024, 025, 026 | Investigation reference and next-update time are created |
| Request evidence | 021, 030, 045 | Specific document/photo/record is requested |
| Escalate to safety | 023, 029 | Handling is restricted and specialist review begins |
| Request merchant approval | 022, 025, 028, 038 | Merchant decides replacement, exchange, or reshipment |
| Issue a return artifact | 031, 032 | Label or QR token is generated |
| Reconcile or credit billing | 049, 050 | Duplicate/guarantee credit is applied under the relevant rules |
| Confirm a verified result | 002, 034, 048 | The agent communicates the result without extending it beyond the evidence |

## 7. Actions an agent should not take from this data alone

The cases repeatedly prohibit or limit these actions:

- Do not promise an exact delivery time when only a slot or callback exists: **001, 004, 008**.
- Do not mark an order complete from partial parcel scans: **020**.
- Do not infer a loss from a delivered/no-receipt conflict: **024**.
- Do not promise compensation merely because damage or delay is reported: **021, 022, 050**.
- Do not treat “investigation registered” as “loss confirmed”: **024–025**.
- Do not ask the customer to handle a leaking or unsafe parcel: **023, 029**.
- Do not treat an uploaded invoice as customs clearance: **045**.
- Do not treat a booking as a physical delivery or collection: **001, 033, 037, 041**.
- Do not change a shipment using facts that only appear in later follow-through events.
- Do not invent missing measurements, document fields, prices, addresses, or origin information: **043, 045**.

## 8. Practical agent decision sequence

```text
1. Identify the case and primary reference.
2. Read Context and Escalation only.
3. Identify the requester and their authority.
4. Check the current shipment/order/task reference.
5. Read the Boundaries section.
6. Determine the narrow action in event 003.
7. Use the permitted channel and recipient.
8. Ask for confirmation or missing evidence when required.
9. Do not claim the later outcome unless it is already available.
10. When responding later, distinguish booking, receipt, approval, investigation, and completion.
```

## 9. Main design takeaway

The Markdown is not a normalized shipment database. It is a synthetic case packet designed to test temporal and operational reasoning.

```text
Index summary
    → tells you what the case is about and what action is expected

History
    → tells you who said what, when, through which channel

Attachments
    → provide evidence or operational artifacts

Boundaries
    → define what the agent must not claim
```

The most important distinction is:

```text
Case status = status of the coordination task
Shipment status = status described by operational events
Event = observation or communication
Action = what the agent is allowed to do next
Outcome = what later became true
```

Confusing these levels is what would cause most errors in the Delivery cases.
