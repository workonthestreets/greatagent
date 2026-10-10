# Delivery & Logistics track: data exploration, normalization and decision parameters

Source: `DwellyOrg/HackatonPublicCases`, folder `Delivery & Logistics`, commit `9bcdca5`. 50 public cases, 228 events, 6 attachments. Built on 10 Oct 2026 with `data/pipeline/run_all.sh`; every number below is computed by that pipeline (`catalogue/stats.json`) or by the peer validator in `data/pipeline_qa/`.

## 1. What the data is

One case is a single coordination handoff by the agent persona, Iona Quill of the Rivet Delivery Desk. The desk sits between a carrier (Plover Arc Logistics), merchants (Tallowmere Goods, Brineleaf Pantry), pickup points, business shippers and consignees, a customs broker (Ossmere Trade Desk) and an international carrier (Harbor Thread). The desk owns nothing: it never books, prices, approves, investigates or handles goods. Its job is to send one message to the party that owns the next step, with the right facts and limits, and to say what is not yet established.

Every case has the same shape. The history has four or five events on a fixed clock:

| Event | Stage tag | Offset | Who writes | What it contains |
|---|---|---|---|---|
| 001 | Context | +0 min | carrier 32, merchant 11, business 3, broker 2, pickup point 1, international 1 | shipment state, options, policy, constraints, and who owns the decision |
| 002 | Escalation | +10 min | consumer 37, business counterparty 7, carrier 4, merchant 1, broker 1 | the request, availability, preferences, authority limits |
| 003 | Agent action | +25 min | the desk, 50/50 | one message to one owner: the gold label |
| 004-005 | Follow-through | +35 min to next day | owner, then customer | confirmation, receipt, scan; attachments appear here |

Stage pattern is CEAFF in 28 cases and CEAF in 22. Nine cases have a follow-through event on the following day (006, 015, 020, 026, 027, 033, 034, 039, 044), always a physical receipt or collection.

The index file carries structured labels the other tracks lack: `Escalated` timestamp, `Primary shipment` (41) or `Primary task reference` (9), `Coordinator`, a `Context` summary, and under `Next action at escalation` the gold `Recipient`, `Channel` and `Recorded action: event 003` in 50/50 cases, plus an `Outcome` and a `Boundaries and remaining work` disclaimer.

Channels. Escalations arrive by Customer portal 37, Business portal 7, Dispatch chat 2, Depot work queue 1, Warehouse work queue 1, Freight portal 1, Broker portal 1. Gold agent messages go by Email 35, Customer portal 5, Business portal 4, Call transcript 2, Dispatch chat 1, Depot work queue 1, Safety incident queue 1, Warehouse work queue 1. Channel follows the recipient: customers get the portal (or a call when a cutoff is hours away), business counterparties get the business portal, teams get email unless the request arrived in a work queue or chat, and safety goes to the safety incident queue.

Attachments. Six files in five cases (021 two PNGs, 031 PDF, 032 PNG, 045 PDF, 049 PDF). All six are first linked at event 004, after the decision point, so no attachment is ever an input to the decision. PDFs extract cleanly with pdftotext; the PNGs carry a "synthetic rendered scene" banner and a few lines of text readable by tesseract.

Leakage (measured by the peer validator). In 24 cases a reference ID first appears at event 004 or later, never at event 003; 99 reference mentions, 14 dates, 6 GBP amounts and 3 measurements first appear after the cutoff. Later references use prefixes outside the obvious set (SAFE-, EX-, BP-, POD-, RF-, SP-, ARC-, KL-, PA-, GC-) and one token, DL032R, has no dash. A builder that collects references from all events leaked future facts into 33 of 50 inputs. The index `Context`, `Overview`, `Outcome`, `Boundaries`, the `Stage` tags, the title and the `Updated`/`Completed` timestamps all narrate the ending and are kept out of the agent input.

## 2. What was built

| File | Purpose |
|---|---|
| `agent/cases.jsonl` | one record per case: `meta`, `parties`, `at_escalation` (inputs only), `decision` (gold), `disclosed_after_escalation` (hidden), `events`, `attachments`. Schema: `pipeline/case.schema.json` |
| `agent/decision_points.jsonl` | the README test protocol made concrete: `input` (events 001-002, whitelisted case details, initial request, no attachments), `gold`, `hidden`, `scoring_hints` |
| `agent/events.jsonl`, `human/events.csv` | 228 events with canonical actors (`party`, `org`, `org_type`), direction, stage, visibility flag, references, amounts |
| `human/cases.csv`, `human/cases_readable.md` | the human-readable copies: one row or one block per case with every decision parameter |
| `catalogue/parameters.json` | the parameter catalogue: tier, role, source, enum, coverage, distinct values, entropy |
| `catalogue/routing_table.json` | (issue_type, owner) cells with action, recipient-function and channel distributions, the conflict list, and a graph spec |
| `catalogue/escalation_queues.json` | nine queues with triggers, member cases, human-gate policy, channel rule |
| `inputs/attachments_text/` | extracted text of the six attachments |
| `../../pipeline/gold_labels_delivery.csv` | the hand-labelled gold parameters for all 50 cases |

Actor labels were canonicalized from the "Name, Organisation" convention into `org_type` in {desk, carrier, merchant, pickup_point, customer, business_counterparty, customs_broker, international_carrier}. The parser is track-agnostic and also produced structural dumps for the other three tracks (banking 258 events, insurance 292, property 1,505, zero parse warnings).

Validation. The pipeline's own checks pass 50/50: no post-cutoff reference in any input, no attachment visible before its first mention, gold recipient present in event 003's addressees, index channel equal to the event 003 channel, monotonic timestamps. An independent validator written by a peer session (`data/pipeline_qa/validate_cases.py`, 14 tests) passes on schema, leakage, raw consistency and decision points.

Label reliability. A second annotator (a peer session fenced off from my labels) relabelled all 50 cases from the visible events only. Agreement with my labels on the original enum: owner 96% (kappa 0.94), queue 92% (0.90), customer_input_required 100%, action class 82% (0.78), risk flags 78% exact set with mean Jaccard 0.82 (0.70), urgency 64% (0.28), human gate 66% (0.35). Disclosures: the peer consulted event 003 for 11 cases and changed 6 labels, and saw the index next-action line for DEL-001. The weak columns are definitional, not factual: the peer marked `deadline_bound` whenever a future booking date existed and `soft` gates for any merchant approval. The definitions in `parameters.json` were tightened accordingly and both columns are marked low-reliability. Three of the nine action-class disagreements came from my enum mixing *who* (merchant) with *what* (authorise vs execute), and two more from lumping physical traces with record requests; the enum was refactored into nine purely action-based classes, with the owner carried by `owner_org_type`.

## 3. Decision parameters

The agent's output has four parts: the recipient, the channel, the action asked for, and the guardrail and disclaimer clauses. The inputs that determine them are below, in three tiers. Roles: input = read from events 001-002 or the case details, derived = computed from inputs, output = part of the decision.

| # | Parameter | Tier | Role | Values in the 50 cases | Why it matters |
|---|---|---|---|---|---|
| 1 | requester_type | min | input | consumer 37, business_counterparty 7, carrier_ops 4, merchant_ops 1, customs_broker 1 | sets the register and the default reply channel |
| 2 | issue_type | min | input | 14 values: tracking_visibility 8, reschedule 7, redirect_or_hold 5, address_or_access 4, loss_or_misdelivery 4, freight_booking 4, money_and_billing 4, return_processing 3, 2 each for damage, safety, wrong/duplicate item, cancel/reship, customs, 1 disruption | the first routing key |
| 3 | shipment_stage | min | input | 17 values: at_depot 11, booked_not_dispatched 9, delivered 8, return_approved 4, customs_hold 3, delivered_partial 2, one each for the rest | which operations are still possible (redirect only before route release, hold only in depot stock) |
| 4 | owner_org_type | min | input | carrier 25, merchant 11, customer 7, business_counterparty 5, pickup_point 1, international_carrier 1 | event 001 names the owner in 50/50 cases; the recipient is the owner, or the customer when input is needed |
| 5 | customer_input_required | min | derived | true 14 | a choice, confirmation or datum from the customer or counterparty gates the next step |
| 6 | urgency | min | input | none 43, immediate 4 (003, 023, 029, 040), deadline_today 1 (018), deadline_bound 2 (007, 016) | switches the channel to call, chat or work queue |
| 7 | risk_flags | min | derived | 26 cases carry a flag: money 10, physical_handling 7, credentials 5, authority 4, privacy_third_party 3, fraud_dispute 2, safety 2, consumption 1 | selects the guardrail sentences and the human gate |
| 8 | primary_ref | standard | input | 50 distinct | every message is anchored on it; sub-units (DL-020-C, DL-044-P4, DL-036-A..D) must be traced by their own ID |
| 9 | verification_state | standard | input | authenticated_session 35, verified_by_operator 13, internal_party 2, asserted_only 0 | the agent may not infer verification from a customer's assertion (case 002 boundary); expect asserted_only in unseen cases |
| 10 | recipient_function | standard | output | 16 values, 46 distinct raw labels | exact team names are not derivable: only 11/50 recipients are the context author and 34/50 are named in visible text; score at org + function level |
| 11 | action_class | standard | output | 9 values: operator_action 15, ask_customer 7, authorisation_or_decision 6, physical_trace 5, ask_counterparty 5, review_or_investigation 4, record_or_statement 4, options_for_customer 2, escalate_safety 2 | what the message asks for |
| 12 | channel | standard | output | 8 values, Email 35 | mirrors recipient type and urgency |
| 13 | money_involved | standard | input | true 10 | the desk never sets, waives or multiplies amounts |
| 14 | evidence_conflict | standard | derived | true 5 (013, 024, 039, 044, 049) | a record contradicts a statement: route to review, assert nothing |
| 15 | proof_standard | standard | output | 16 values: operator_confirmation 10, booking_reference 8, physical_scan 6 ... | what the agent must demand before calling the step done: a receipt scan, not a planned linehaul; physical acceptance, not a departure scan |
| 16 | options_offered | max | input | present in 23 cases | the alternatives the owner has already put on the table |
| 17 | policy_constraints | max | input | present in 23 cases | eligibility rules stated by the owner (hold up to three days, one extension, nominee must be an adult household member) |
| 18 | constraint_sentences | max | input | present in 38 cases | explicit prohibitions: no reusable code, do not fill in values, do not route to a driver |
| 19 | customer_availability | max | input | present in 10 cases | dates and windows the customer offers |
| 20 | cutoff_utc | max | input | 3 cases (003 10:00, 007 next-day 18:00, 018 16:00) | the clock the agent must beat; event-based cutoffs (next sweep, hazard) have no timestamp |
| 21 | amount_gbp_known | max | input | 4 cases (30 limit, 32, 18, 7.50) | amounts the message may quote |
| 22 | boundaries | max | output | 50/50 | the disclaimer the final reply must carry |
| 23 | queue | max | output | 9 values | where the case waits after the message |
| 24 | human_gate | max | output | hard 7, soft 3, none 40 | policy knob; low inter-annotator reliability |

A caveat on the word "input" in the table: it means known at the decision point, not provided. Only the primary reference, the requester's role and the created and escalated times are given as fields. Five parameters are literal extractions from the visible text (cutoff, known amount, customer availability, options offered, constraint sentences). The rest, issue type, shipment stage, owner, urgency, verification state, money, customer input required, risk flags and evidence conflict, are hand labels that an agent must predict from the raw text, as it must predict the outputs. An agent that is fed the gold labels as inputs will score higher on the public set than it will on the challenge set. Two related checks for the hidden set: the Stage tags exist only in this track's raw history and are stripped from `decision_points.jsonl` inputs, and event 001 names the acting owner in 50 of 50 public cases, so routing becomes much harder if the challenge cases arrive without that context event.

Minimum: 7 parameters (rows 1-7). On the public set they form 50 distinct keys for 50 cases, so they route every case to its gold action class and owner with zero conflicts. That is also the caveat: 50 keys for 50 cases is memorisation, not evidence of generalisation.

Standard: 15 parameters (rows 1-15). This is what the graph state should carry in production. With only three of them, issue_type, owner_org_type and customer_input_required, 18 of the 24 (issue, owner) cells are already deterministic; the six remaining cells are split by evidence_conflict (013, 024, 049, 050), by approval-versus-execution at the merchant (038 vs 040), by physical-versus-record requests (011, 020, 034, 044 vs 017, 030) and by whether the carrier must present options first (008, 016).

Maximum normal: 24 parameters (all rows). Beyond this point fields belong in the event log, not in decision state: individual timestamps, actor name strings, free-text bodies, attachment bytes.

Constants that must not be modelled: coordinator (1 value), status (1), data note (1), overview text (1), escalation offset (+10 min in 50/50), agent action position (event 003 in 50/50), case number (encodes the request family: 031-035 and 037 are returns, 041-044 freight, 045-048 international). Mask IDs and split folds across blocks or the agent learns the number instead of the request.

## 4. Escalation queues

Nine operational queues cover the 50 cases. Five of them are escalation queues in the human sense, where variability is high or the cost of a wrong message is irreversible.

| Queue | Cases | Trigger | Human gate | Channel rule |
|---|---|---|---|---|
| safety | 2 (023, 029) | risk_flags contains safety or consumption | hard | safety incident queue or the merchant food-safety lead; never a driver or the customer |
| investigations | 2 (013, 024) | evidence_conflict with a fraud_dispute flag | hard for delivered-not-received, soft for a disputed attempt | email to the carrier review or investigations team; register, do not conclude |
| billing_review | 3 (047, 049, 050) | money_involved and issue money_and_billing | hard when an amount is to be credited, none for a pure explanation | email to the owning billing team; no payment links in the customer reply |
| urgent_cutoff | 3 (003, 018, 040) | urgency immediate or deadline_today | none, but escalate to a human if the party does not answer before the cutoff | call, chat or work queue, never email |
| awaiting_counterparty | 5 (014, 041, 043, 045, 046) | customer_input_required and owner business_counterparty | hard when a signing authority is involved (046) | business portal or email to the named authorised person |
| awaiting_customer | 5 (001, 002, 005, 009, 021) | customer_input_required and owner customer | none | customer portal |
| merchant_authorisation | 9 | owner merchant | none (the merchant team is the human) | email to the specific merchant team |
| carrier_trace | 5 (011, 020, 034, 044, 048) | action physical_trace | none | depot work queue or email to the trace team; demand a scan |
| carrier_ops | 16 | operator action, options or record request to the carrier | none unless money or authority flags are present | email, or the originating chat or queue |

Which parameters have the high variability that justifies a queue instead of a rule:

- The recipient team label: 46 distinct labels in 50 cases (variability index 0.97). It cannot be a lookup table. It is derivable only as (organisation, function) from the Context text, which names or implies the owning team in all 50 cases, so the scorer and the router should both work at that level.
- proof_standard (16 values) and shipment_stage (17 values): what counts as done depends on where the goods are; the gold messages spell it out ("the destination receipt scan, not just a planned linehaul entry", "physical acceptance rather than a departure scan", "do not close using P1-P3 alone").
- Money amounts and authority limits: GBP 6.00 quote, GBP 30.00 limit against GBP 24.00 actual, GBP 32.00 split 20 + 12, GBP 36.00 with an 18.00 duplicate, GBP 7.50 surcharge for a 40-minute delay. Each is decided by a billing or planning team; the desk only relays.
- Conflicting records (5 cases): a delivered scan against a verified no-receipt report, a failed-attempt scan against a customer at home, two handover scans for one order, three of four pallets, two identical invoice lines. The right message registers a review and draws no conclusion.
- Cutoffs: a driver waiting 50 minutes, a return timer at 16:00, a warehouse sweep. These change the channel and the tone, and they are the only places where the gold channel is a call.

Hard human gates in the public set: 023, 024, 029, 042, 046, 049, 050 (14%). Soft: 013, 026, 027. Over-escalation costs points under the hackathon rubric, so the gate list is deliberately short; the peer annotator would have gated 20 cases softly, which is the other defensible calibration.

## 5. Graph engineering summary

State = the 15 standard parameters plus the visible events and references. Nodes: load_and_cut (whitelist fields, events 001-002 only, attachments only if referenced before the cutoff), normalize (actors, references, amounts, dates), extract_params (tiers 1-15), owner_resolver (owner from Context), risk_screen (safety goes straight to the human gate), policy_gate (narrow the allowed actions by issue, owner, input-required and money), decide (choose recipient, action, channel; cite event IDs), critic (recipient equals owner or customer, no promise, no credentials, no third-party data, no handling advice, no money decision, no post-cutoff fact), draft (message plus the boundary sentence), human_gate, emit. The full spec with edge conditions, the channel rule and the ordered action rule is in `routing_table.json` under `graph`.

Hard-violation list for the critic and the scorer: promising an arrival time; requesting credentials or reusable codes; sharing third-party personal data; advising physical handling or consumption; setting, waiving or multiplying money; stating a fraud, loss or liability finding; citing a fact first seen after the cutoff.

## 6. Limits and next steps

- The public set has no `asserted_only` verification, no refused request, no injected instruction and no unresolved outcome. Unseen cases will differ exactly there; the parameter set already has the slots (verification_state, evidence_conflict, human_gate).
- Labels are one annotator's reading, checked by a second: routing columns are reliable (kappa 0.78 to 1.00), urgency and human_gate are not (0.28 and 0.35) and should be treated as policy settings with the tightened definitions.
- `issue_type` and `shipment_stage` are hand-labelled; an intake classifier for unseen cases should be trained or prompted from `cases_readable.md` and evaluated with `decision_points.jsonl`, scoring the recipient at org + function level, the action class exactly, and the channel strictly only for safety and cutoff cases.
