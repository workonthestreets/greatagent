"""The desk's parameter vocabulary, copied verbatim from the normalised Delivery catalogue
(data/delivery/catalogue/parameters.json, routing_table.json, escalation_queues.json and the
gold label files). tests/test_catalogue_sync.py fails if these literals drift from the data.

Everything here is VERIFIED against the labelled cases (50 public + 100 synthetic, plus the
20 stress cases where noted). Rules that come only from the hard-30 stress set are marked in
prompts.py, not here."""
from __future__ import annotations

# ---- enums (parameters.json -> enums) ---------------------------------------------------
REQUESTER_TYPE = ["consumer", "business_counterparty", "carrier_ops", "merchant_ops", "customs_broker"]
ISSUE_TYPE = ["address_or_access", "cancel_or_reship", "customs_and_import", "damage_or_condition", "freight_booking",
              "loss_or_misdelivery", "money_and_billing", "redirect_or_hold", "reschedule", "return_processing",
              "safety_hazard", "service_disruption", "tracking_visibility", "wrong_or_duplicate_item"]
SHIPMENT_STAGE = ["at_depot", "at_pickup_point", "booked_not_dispatched", "cleared_pending_handover", "customs_hold",
                  "delivered", "delivered_disputed", "delivered_partial", "lost_confirmed", "misdelivered",
                  "misrouted_depot", "on_route", "pre_collection", "return_approved", "return_in_transit",
                  "return_received", "returned_to_sender"]
OWNER_ORG_TYPE = ["customer", "business_counterparty", "carrier", "merchant", "pickup_point", "international_carrier"]
URGENCY = ["none", "deadline_bound", "deadline_today", "immediate"]
RISK_FLAGS = ["safety", "physical_handling", "privacy_third_party", "credentials", "money", "fraud_dispute",
              "authority", "consumption"]
VERIFICATION_STATE = ["verified_by_operator", "authenticated_session", "internal_party", "asserted_only"]
RECIPIENT_FUNCTION = ["billing", "counterparty_business", "customer_self", "depot_physical", "dispatch_scheduling",
                      "freight_planning", "investigation_review", "merchant_authorisation", "merchant_fulfilment",
                      "pickup_point_operator", "recovery_collection", "routing_redirect", "safety", "support_records",
                      "trace", "warehouse_execution"]
ACTION_CLASS = ["ask_customer", "ask_counterparty", "request_operator_action", "request_options_for_customer",
                "request_physical_trace", "request_record_or_statement", "request_review_or_investigation",
                "request_authorisation_or_decision", "escalate_safety"]
PROOF_STANDARD = ["approval_reference", "approved_statement", "booking_reference", "credit_note", "customer_confirmation",
                  "document_from_party", "handover_scan", "incident_reference", "investigation_reference",
                  "operator_confirmation", "physical_scan", "receipt_document", "record_document", "review_finding",
                  "review_reference", "signed_count"]
QUEUE = ["safety", "investigations", "billing_review", "urgent_cutoff", "awaiting_customer", "awaiting_counterparty",
         "merchant_authorisation", "carrier_trace", "carrier_ops"]
HUMAN_GATE = ["none", "soft", "hard"]

# Channel strings exactly as they appear in the normalised event log (events.jsonl).
CHANNELS = ["Email", "Customer portal", "Business portal", "Dispatch chat", "Depot work queue", "Call transcript",
            "Warehouse work queue", "Safety incident queue", "Freight portal", "Broker portal", "Pickup-point portal"]

# The agent's own decision vocabulary and how the gold action classes map onto it.
DECISION_TYPE = ["act", "request_information", "escalate_to_human", "hold_no_action", "decline"]
ACTION_CLASS_TO_DECISION = {
    "ask_customer": "request_information", "ask_counterparty": "request_information",
    "request_operator_action": "act", "request_options_for_customer": "act", "request_physical_trace": "act",
    "request_record_or_statement": "act", "request_review_or_investigation": "act",
    "request_authorisation_or_decision": "act", "escalate_safety": "act",
}

# ---- routing: owner_org_type -> recipient_function (gold pairs, 150 labelled cases) ------------
# Every (owner_org_type, recipient_function) pair below occurs in the gold labels; no other pair does.
ROUTING = {
    "customer": {"customer_self": "choose, confirm, supply a datum"},
    "business_counterparty": {"counterparty_business": "data, mandate, decision"},
    "carrier": {
        "dispatch_scheduling": "rebook, hold, redelivery, driver, slots",
        "routing_redirect": "redirect, address change",
        "trace": "locate, scan",
        "depot_physical": "floor, transfer, dock",
        "recovery_collection": "misdelivery recovery, collection",
        "investigation_review": "record vs statement",
        "support_records": "statement, confirmation",
        "billing": "charges, credits, claims",
        "freight_planning": "capacity, pallets, appointment",
        "safety": "hazard",
    },
    "merchant": {
        "merchant_authorisation": "replacement, exchange, reshipment, label, refund, cancellation",
        "merchant_fulfilment": "packing, stop/amend order, reconciliation",
        "warehouse_execution": "warehouse work",
        "safety": "food/product safety",
    },
    "pickup_point": {"pickup_point_operator": "deadline, extension, hold, release"},
    "international_carrier": {"trace": "cross-border location"},
}

# Channel the gold message used, by recipient organisation (routing_table.json -> channel_by_recipient_org_type).
CHANNEL_BY_ORG = {
    "customer": ["Customer portal", "Call transcript"],
    "business_counterparty": ["Business portal", "Email"],
    "carrier": ["Email", "Dispatch chat", "Depot work queue", "Safety incident queue"],
    "merchant": ["Email", "Warehouse work queue"],
    "pickup_point": ["Email"],
    "international_carrier": ["Email"],
}

# Operational queues after the action (escalation_queues.json): what triggers them, where to write, when to follow up.
QUEUES = {
    "safety": ("risk_flags safety or consumption, or issue_type safety_hazard", "Safety incident queue (carrier) or the merchant food-safety lead by email; never a driver or the customer", "immediate; no batching", "hard"),
    "investigations": ("evidence_conflict, or risk_flags fraud_dispute", "Email to the carrier review/investigation team", "register same day; follow up at the next-update time the team gives", "hard for delivered-not-received; soft for attempt disputes"),
    "billing_review": ("money_involved, or issue_type money_and_billing", "Email to the owning billing team; reply to the customer in the verified order thread without payment links", "same day; follow up on the billing team's stated date", "hard when an amount is to be credited; none for a pure explanation"),
    "urgent_cutoff": ("urgency immediate or deadline_today", "Call or chat/work queue, never email", "act within minutes; verify before the cutoff", "none, but escalate to a human if the party does not answer before the cutoff"),
    "awaiting_customer": ("customer_input_required and owner customer", "Customer portal (order-linked thread); call only when a cutoff applies", "wait state with reminder timer; resume on reply", "none"),
    "awaiting_counterparty": ("customer_input_required and owner business_counterparty", "Business portal (verified channel) or email to the named authorised person", "wait state; chase before the carrier slot lapses", "hard when a signing authority is involved (mandate)"),
    "merchant_authorisation": ("owner merchant with request_authorisation_or_decision or request_operator_action", "Email to the specific merchant team", "same day; approval reference expected", "none (merchant team is the human)"),
    "carrier_trace": ("action_class request_physical_trace", "Depot work queue or email to the trace team", "scan expected same day; otherwise escalate to investigations", "none"),
    "carrier_ops": ("request_operator_action, request_options_for_customer or request_record_or_statement with owner carrier or pickup_point", "Email to the owning carrier team; dispatch chat when the request originates in chat", "confirmation expected within the working day", "none unless money or authority flags are present"),
}

# One-line working summaries of QUEUES for the prompt (QUEUES above stays verbatim and is the tested source).
QUEUE_BRIEF = {
    "safety": "safety/consumption, safety_hazard | Safety incident queue or merchant food-safety lead, never driver/customer | immediate | hard",
    "investigations": "evidence_conflict, fraud_dispute | email carrier review team | same day, then at the team's time | hard (delivered-not-received), soft (attempt dispute)",
    "billing_review": "money_involved, money_and_billing | email owning billing team; customer reply in verified thread, no payment links | the team's date | hard when crediting",
    "urgent_cutoff": "immediate, deadline_today | call/chat/work queue, never email | minutes; escalate if unanswered before cutoff | none",
    "awaiting_customer": "customer_input_required, owner customer | Customer portal (call only on a cutoff) | reminder timer | none",
    "awaiting_counterparty": "customer_input_required, owner business_counterparty | Business portal or email the named authorised person | before the carrier slot lapses | hard for a mandate",
    "merchant_authorisation": "owner merchant, authorisation/operator action | email the specific team | approval reference same day | none",
    "carrier_trace": "request_physical_trace | Depot work queue or trace team | scan same day, else investigations | none",
    "carrier_ops": "operator action/options/statement, owner carrier/pickup_point | email owning carrier team; dispatch chat if begun in chat | within the working day | none unless money/authority",
}

HUMAN_GATE_RULE = ("hard = the message commits or credits money with an amount, concerns safety or a "
                   "delivered-not-received/loss dispute, or relies on a signing authority; soft = third-party privacy "
                   "or a disputed record framed neutrally; none = routine relay, option request or customer question.")
URGENCY_RULE = ("only when an explicit cutoff makes the state irreversible (return-to-sender timer, driver departure, "
                "dispatch sweep, offer/extension expiry, hazard); a future booking date alone is none. "
                "immediate = within ~2 h; deadline_today = later today; deadline_bound = a dated cutoff beyond today.")


def render_routing() -> str:
    return "\n".join(f"- {org} [{'; '.join(CHANNEL_BY_ORG[org])}]: " + "; ".join(f"{fn} ({what})" for fn, what in funcs.items())
                     for org, funcs in ROUTING.items())


def render_queues() -> str:
    return "\n".join(f"- {q} | {QUEUE_BRIEF[q]}" for q in QUEUES)
