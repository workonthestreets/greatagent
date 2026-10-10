# Case 21 — reasoning

## What the system received

- Case folder: `021` (track: Delivery & Logistics, mode: public-eval)
- Files read: index.md, history.md
- Attachments read: none
- Hidden for evaluation (after escalation point): events [3, 4, 5], attachments ['attachments/carton-detail.png', 'attachments/carton-overview.png']

## Situation

Lessa Vire, the recipient, has a carton with a dented outside corner. She has not opened it, and she is asking which photos the merchant needs. Tallowmere Goods' damage intake team has already said what it needs for TG-021 / DL-021: one photo of the whole carton with the shipment label visible, and one closer photo of the dented corner. Both go through the upload channel linked to the order. The merchant has also said the customer must not be asked to unpack anything she thinks is unsafe.

## Facts

| Fact | Source | Status |
|---|---|---|
| The merchant needs two photos: the whole carton with the shipment marking visible, and a closer view of the dented corner | event 001 | verified |
| The photos must be sent through the upload channel linked to the order | event 001 | verified |
| The customer must not be asked to unpack an item she considers unsafe | event 001 | verified |
| The outside corner of the carton is dented and the carton has not been opened | event 002 | claimed |
| The photo request does not decide whether there will be compensation | index: Context | verified |

## Case parameters

- requester_type: consumer
- issue_type: damage_or_condition
- shipment_stage: delivered
- owner_org_type: customer
- verification_state: authenticated_session
- urgency: none
- risk_flags: physical_handling
- evidence_conflict: False
- money_involved: False
- customer_input_required: True
- queue: awaiting_customer
- human_gate: none

## Conflicts

None.

## Missing information

- The two photos themselves, which only the customer can supply

## Risk flags

- physical_handling: do not ask the customer to open, unpack or handle the contents; outside photos only
- No compensation or outcome may be promised; the merchant decides after reviewing the photos

## Who controls what

- **Lessa Vire (recipient)** — Taking and uploading the two photos
- **Damage intake, Tallowmere Goods** — Which evidence is needed, the damage assessment, and any remedy or compensation

## Decision and rationale

**REQUEST INFORMATION — ask the right party for what is missing** — Tell the customer exactly which two outside photos the merchant needs and how to upload them, without asking her to open the carton and without promising any outcome.

The merchant has already said what evidence it needs, and only the customer can take those photos. She contacted us through the Customer portal, so we reply there with the merchant's exact requirements.

## Independent review (before anything was sent)

### Round 0 — planner decision: request_information
Automated policy lint:
- [WARN] action 0: unsafe_handling_advice 'open the carton' (negated context)
Reviewer verdict: **approve** — I'm approving this plan. The portal reply gives the customer exactly the two outside photos the merchant asked for and points her to the order-linked upload channel. It doesn't ask her to unpack anything, sends no links and promises no outcome. Since there's no earlier promise to her and she asked a real question, a reply now is the right next step.
- [minor] action 0: The merchant asked for the 'shipment marking' to be visible, and the message says 'shipment label'. The marking may not be a label. → fix: You could say 'shipment label or marking' to match the merchant's wording.
- [minor] action -1: case_parameters.owner_org_type is set to 'customer', but the damage assessment belongs to the merchant (Tallowmere Goods). The customer only owns the next input. → fix: Set owner_org_type to merchant and keep queue awaiting_customer.
- [minor] action 0: The lint warning about 'open the carton' is a false positive. The phrase only appears in a 'you don't need to' context, which is safe. → fix: No change needed.

## Execution log

- 0: `send_message` → done after 1 attempt(s) — {"status": "sent", "message_id": "MSG-21-01", "channel": "Customer portal", "note": "queued on channel"}

## What failed

Nothing failed during execution.

## Run metadata

- Models: claude-opus-5-5; LLM calls: 2; tokens in/out: 3734/2895
- Elapsed: 27.1 s; full trace: `trace.json`
