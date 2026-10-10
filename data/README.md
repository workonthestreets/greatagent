# data/ — normalized hackathon cases

Normalized, agent-ready copies of the public cases from `DwellyOrg/HackatonPublicCases` (commit `9bcdca5`), plus the pipeline that produces them. The Delivery & Logistics track is fully normalized and labelled; the other three tracks have structural parses only.

## Regenerate

```bash
bash data/pipeline/run_all.sh            # expects the repo at ~/HackatonPublicCases
bash data/pipeline/run_all.sh /path/to/HackatonPublicCases
```

Stdlib Python only, run in isolated mode (`python3 -I`) because the case files are downloaded, untrusted data. PDF text needs `pdftotext`; PNG text needs `tesseract` (optional).

## Layout

```
data/
  README.md                 this map
  pipeline/                 the code that produces everything below
    run_all.sh              one command regenerates all of data/delivery/
    parse_cases.py          track-agnostic parser: index.md + history.md + attachments -> raw_cases.jsonl
    normalize_delivery.py   delivery layer: actors, references, visibility split, gold labels, statistics, queues
    build_db.py             the database on Andrey's system model
    facts_delivery.py       hand-curated order, shipment and parcel facts per case
    gold_labels_delivery.csv  hand-labelled decision parameters for the 50 public cases (the ground truth)
    case.schema.json        JSON Schema for one record of agent/cases.jsonl
  delivery/
    inputs/                 what the pipeline reads: raw_cases.jsonl, stress_raw.jsonl, attachments_text/
    agent/                  what the agent and the scorer read: cases.jsonl, decision_points.jsonl, events.jsonl
    human/                  what people read: REPORT.md, RECONCILIATION.md, cases_readable.md, cases.csv, events.csv
    catalogue/              parameters.json (tiers), routing_table.json, escalation_queues.json, stats.json
    database/               delivery.sqlite and its schema.sql
  pipeline_qa/              independent guards: validate_cases.py, test_db.py and their fixtures
```

| File | What it is | Produced by | Read by |
|---|---|---|---|
| delivery/inputs/raw_cases.jsonl | the 50 public cases parsed, nothing interpreted | parse_cases.py | normalize_delivery.py |
| delivery/inputs/stress_raw.jsonl | the 20 stress cases from `stress_cases/`, parsed | parse_cases.py | build_db.py |
| delivery/inputs/attachments_text/ | extracted text of every attachment | parse_cases.py | people |
| delivery/agent/cases.jsonl | one agent-ready record per case, inputs separated from the hidden ending | normalize_delivery.py | the agent, build_db.py, validate_cases.py |
| delivery/agent/decision_points.jsonl | evaluation snapshots: input, gold, hidden, scoring hints | normalize_delivery.py | the scorer |
| delivery/agent/events.jsonl | 228 normalized communications | normalize_delivery.py | the agent, analysis |
| delivery/human/REPORT.md | the data report: profile, parameters, queues, graph | written by hand from catalogue/stats.json | people |
| delivery/human/RECONCILIATION.md | Andrey's model field by field: source, coverage, N/A policy, gaps | build_db.py | people, Andrey |
| delivery/human/cases_readable.md, cases.csv, events.csv | the same data as agent/ in readable form | normalize_delivery.py | people, spreadsheets |
| delivery/catalogue/parameters.json | the 24 parameters in three tiers with measured coverage and variability | normalize_delivery.py | graph design |
| delivery/catalogue/routing_table.json | issue-by-owner routing cells, conflicts, channel rule, graph spec | normalize_delivery.py | graph design |
| delivery/catalogue/escalation_queues.json | nine queues with triggers, members, human-gate policy | normalize_delivery.py | graph design |
| delivery/catalogue/stats.json | every number used in REPORT.md | normalize_delivery.py | REPORT.md |
| delivery/database/delivery.sqlite | the database on Andrey's model (see below) | build_db.py | anyone with sqlite |
| delivery/database/schema.sql | its DDL | build_db.py | people |

## Database (Andrey's system model)

`data/delivery/database/delivery.sqlite` is a SQLite database laid out on the system model in `user/andrey/drafts/delivery-system-model.md` (origin/main): `orders`, `shipments`, `parcels`, `events` (operational observations extracted from message bodies), `cases`, `tasks`, `evidence`, `actors`, plus `messages` (the communications), `case_actors` and a `reconciliation` table. Views: `v_shipment_dashboard` (Shipment, Order, Current milestone, Exception, Next action, Owner, ETA), `v_case_timeline` (messages and events interleaved), `v_decision_input` (what the agent may see). Policy: a value the cases never state is the literal string `N/A`, never NULL. Every message, event and evidence row carries `visible_at_escalation`.

- Built by `data/pipeline/build_db.py` from `cases.jsonl`, the hand-curated `data/pipeline/facts_delivery.py` (orders, shipments, parcels, destinations, promised windows, requested action, operational effect, deadline per case) and the 20 stress cases from the repo (`inputs/stress_raw.jsonl`, loaded with `labelled = 0` and `N/A` parameters).
- DDL in `data/delivery/database/schema.sql`; field-by-field mapping, coverage and the draft's gaps in `data/delivery/human/RECONCILIATION.md`.
- Quick start: `sqlite3 data/delivery/database/delivery.sqlite "SELECT * FROM v_shipment_dashboard WHERE case_id='DEL-020'"` or, in Python, `sqlite3.connect('data/delivery/database/delivery.sqlite')`.

## Record layout (cases.jsonl)

- `meta`: created, escalated, updated, completed, primary_ref (+kind), coordinator, n_events, duration.
- `parties`: requester (+type), agent, context_author, all actors with `org_type` in {desk, carrier, merchant, pickup_point, customer, business_counterparty, customs_broker, international_carrier}.
- `at_escalation`: everything the agent may read before deciding: initial request, visible event ids (001-002), references, sub-units, amounts, measurements, dates, time windows, constraint sentences, option/policy sentences, customer availability, attachments available (always empty in this set), and `params` (the labelled decision parameters).
- `decision`: the gold label: recipient (raw + canonical), recipient_function, channel, action_class, the event 003 message, proof_standard, queue, human_gate, notes.
- `disclosed_after_escalation`: context summary, outcome, boundaries, follow-through ids, references introduced later, next update due, attachments after cutoff.
- `events`, `attachments`: full normalized lists with `visible_at_escalation` flags.

## Using decision_points.jsonl

Give the agent only `input` (file: `delivery/agent/decision_points.jsonl`) (case details whitelist, initial request, events 001-002, no attachments). Compare its answer with `gold`: recipient at `recipient_org_type` + `recipient_function` level, `action_class` exactly, `channel` strictly only when `scoring_hints.channel_strict` is true, and check `scoring_hints.hard_violations` against the drafted message. `hidden` holds what the README says to withhold; use it only for a "consistent with later evidence" judge.

## Enums

`action_class`: ask_customer, ask_counterparty, request_operator_action, request_options_for_customer, request_physical_trace, request_record_or_statement, request_review_or_investigation, request_authorisation_or_decision, escalate_safety.
`queue`: awaiting_customer, awaiting_counterparty, urgent_cutoff, carrier_ops, carrier_trace, investigations, safety, merchant_authorisation, billing_review.
`urgency`: none, deadline_bound, deadline_today, immediate (only for cutoffs that make the state irreversible).
`human_gate`: none, soft, hard. Full definitions and measured coverage: `delivery/catalogue/parameters.json`.
