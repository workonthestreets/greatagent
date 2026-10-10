#!/usr/bin/env python3
"""Delivery & Logistics normalizer: raw parsed cases + gold labels -> agent-ready dataset.

Usage:
    python3 -I normalize_delivery.py <raw_cases.jsonl> <labels.csv> <out_dir>

Writes into <out_dir>/ (subfolders say the purpose):
    agent/cases.jsonl, agent/decision_points.jsonl, agent/events.jsonl   what the agent and the scorer read
    human/cases.csv, human/events.csv, human/cases_readable.md           flat human-readable copies
    catalogue/parameters.json, routing_table.json, escalation_queues.json, stats.json   catalogues and numbers
"""
import csv
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

DESK = 'Rivet Delivery Desk'
# where each output lands under <out_dir>: inputs/ agent/ human/ catalogue/ database/
OUT_MAP = {'cases.jsonl': 'agent', 'decision_points.jsonl': 'agent', 'events.jsonl': 'agent',
           'cases.csv': 'human', 'events.csv': 'human', 'cases_readable.md': 'human',
           'parameters.json': 'catalogue', 'routing_table.json': 'catalogue', 'escalation_queues.json': 'catalogue', 'stats.json': 'catalogue'}


def outp(out_dir, name):
    sub = os.path.join(out_dir, OUT_MAP.get(name, ''))
    os.makedirs(sub, exist_ok=True)
    return os.path.join(sub, name)
REF_RE = re.compile(r'\b[A-Z]{2,5}-\d{3}(?:-[A-Z0-9]{1,3})?\b')
TOKEN_RE = re.compile(r'\bDL\d{3}R\b')
GBP_RE = re.compile(r'GBP\s?(\d+(?:\.\d{2})?)')
DIM_RE = re.compile(r'\d+(?:\.\d+)?\s?[×x]\s?\d+(?:\.\d+)?\s?[×x]\s?\d+(?:\.\d+)?\s?cm')
MEAS_RE = re.compile(r'\b\d+(?:\.\d+)?\s?(?:kg|cm|°C)\b')
DATE_RE = re.compile(r'\b20\d{2}-\d{2}-\d{2}\b')
WINDOW_RE = re.compile(r'\d{2}:\d{2}(?:\s?[–-]\s?\d{2}:\d{2})?\s?UTC')
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
CONSTRAINT_RE = re.compile(r"\b(do not|don't|cannot|can't|must not|never|not to|without|only|rather than|is not|are not|does not|has not|have not|no [a-z]+ (?:is|has|was|are)|not a |not yet)\b", re.I)
POLICY_RE = re.compile(r'\b(allow|allows|permit|permits|may |option|options|offer|alternative|eligible|policy|requir|need|needs|must|can offer|currently has|capacity)\b', re.I)
AVAIL_RE = re.compile(r'\b(available|free on|be home|at home|can attend|can collect|can receive|return on|returns on|ends on|I can|we can receive|during)\b', re.I)
UPDATE_DUE_RE = re.compile(r'(?:update|notify)[^.]*?by (20\d{2}-\d{2}-\d{2}),?\s?(\d{2}:\d{2}) UTC', re.I)

STAGE_MAP = {'Context': 'context', 'Escalation': 'escalation', 'Agent action': 'agent_action',
             'Follow-through / confirmation': 'follow_through'}

CUSTOMER_ROLE_RE = re.compile(r'^(?P<name>.+?), (?P<role>recipient|customer|intended recipient|reporting customer)$')
BIZ_ROLE_RE = re.compile(r'^(?P<name>.+?), (?P<org>.+?) (?P<role>receiving coordinator|shipping coordinator|shipping lead|finance coordinator|authorised director)$')


def parse_actor(raw):
    raw = raw.strip()
    a = {'raw': raw, 'party': raw, 'org': None, 'org_type': 'unknown', 'is_person': False, 'role': None}
    if DESK in raw:
        a.update(party=raw.split(',')[0].strip(), org=DESK, org_type='desk', is_person=True, role='coordinator')
    elif raw.endswith(', Plover Arc Logistics'):
        party = raw[:-len(', Plover Arc Logistics')]
        a.update(party=party, org='Plover Arc Logistics', org_type='carrier',
                 is_person=party.lower().startswith(('route driver', 'collection driver')), role='carrier_team')
    elif raw.endswith(', Tallowmere Goods'):
        a.update(party=raw[:-len(', Tallowmere Goods')], org='Tallowmere Goods', org_type='merchant', role='merchant_team')
    elif raw.startswith('Brineleaf Pantry'):
        a.update(party=raw.replace('Brineleaf Pantry', '').strip(), org='Brineleaf Pantry', org_type='merchant', role='merchant_team')
    elif 'Counter supervisor' in raw:
        a.update(party='supervisor', org=raw.replace(' supervisor', ''), org_type='pickup_point', role='pickup_operator')
    elif raw.startswith('Ossmere Trade Desk'):
        a.update(party='Ossmere Trade Desk', org='Ossmere Trade Desk', org_type='customs_broker', role='customs_broker')
    elif raw.startswith('Harbor Thread International'):
        a.update(party=raw.replace('Harbor Thread International', '').strip(), org='Harbor Thread International',
                 org_type='international_carrier', role='carrier_team')
    elif CUSTOMER_ROLE_RE.match(raw):
        m = CUSTOMER_ROLE_RE.match(raw)
        a.update(party=m.group('name'), org=None, org_type='customer', is_person=True, role=m.group('role'))
    elif BIZ_ROLE_RE.match(raw):
        m = BIZ_ROLE_RE.match(raw)
        a.update(party=m.group('name'), org=m.group('org'), org_type='business_counterparty', is_person=True, role=m.group('role'))
    elif raw.endswith('account administrator'):
        a.update(party='account administrator', org=raw.replace(' account administrator', ''),
                 org_type='business_counterparty', role='account administrator')
    return a


def parse_actors(raw):
    return [parse_actor(p) for p in re.split(r';\s*', raw) if p.strip()]


def ts(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')


def sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def refs_in(text):
    return sorted(set(REF_RE.findall(text)) | set(TOKEN_RE.findall(text)))


def entropy_bits(counter):
    n = sum(counter.values())
    return -sum((c / n) * math.log2(c / n) for c in counter.values() if c) if n else 0.0


def to_bool(v):
    return str(v).strip().lower() == 'true'


def load_labels(path):
    out = {}
    with open(path, encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            row['customer_input_required'] = to_bool(row['customer_input_required'])
            row['money_involved'] = to_bool(row['money_involved'])
            row['evidence_conflict'] = to_bool(row['evidence_conflict'])
            row['risk_flags'] = [f for f in row['risk_flags'].split('|') if f]
            row['amount_gbp_known'] = float(row['amount_gbp_known']) if row['amount_gbp_known'] else None
            row['cutoff_utc'] = row['cutoff_utc'] or None
            out[row['case_id']] = row
    return out


def normalize_case(raw, lab):
    d = raw['details']
    created = d.get('Created', '').replace(' UTC', '').replace(' ', 'T') + 'Z' if d.get('Created') else None
    def iso(k):
        v = d.get(k)
        return (v.replace(' UTC', '').replace(' ', 'T') + 'Z') if v else None
    created, escalated, updated, completed = iso('Created'), iso('Escalated'), iso('Updated'), iso('Completed')
    primary_ref = d.get('Primary shipment') or d.get('Primary task reference')
    primary_kind = 'shipment' if d.get('Primary shipment') else 'task'

    # events
    events = []
    t0 = ts(created) if created else None
    for ev in raw['events']:
        meta = ev['meta']
        stage = STAGE_MAP.get(meta.get('Stage', ''), 'unknown')
        frm = parse_actor(meta.get('From', ''))
        tos = parse_actors(meta.get('To', ''))
        if frm['org_type'] == 'desk':
            direction = 'outbound_from_desk'
        elif any(t['org_type'] == 'desk' for t in tos):
            direction = 'inbound_to_desk'
        else:
            direction = 'third_party'
        visible = stage in ('context', 'escalation')
        events.append({
            'event_id': ev['event_id'], 'seq': ev['seq'], 'timestamp': ev['timestamp'],
            'minutes_since_created': (ts(ev['timestamp']) - t0).total_seconds() / 60 if t0 else None,
            'stage': stage, 'channel': meta.get('Channel'), 'from': frm, 'to': tos, 'direction': direction,
            'visible_at_escalation': visible, 'body': ev['body'],
            'refs': refs_in(ev['body']), 'amounts_gbp': [float(x) for x in GBP_RE.findall(ev['body'])],
            'links': ev['links']})
    vis = [e for e in events if e['visible_at_escalation']]
    hidden = [e for e in events if not e['visible_at_escalation']]
    agent_events = [e for e in events if e['stage'] == 'agent_action']
    agent_ev = agent_events[0] if agent_events else None
    esc_ev = next((e for e in events if e['stage'] == 'escalation'), None)
    ctx_ev = next((e for e in events if e['stage'] == 'context'), None)

    vis_text = '\n'.join(e['body'] for e in vis)
    vis_refs = refs_in(vis_text)
    later_refs = sorted(set(refs_in('\n'.join(e['body'] for e in hidden))) - set(vis_refs))
    vis_sents = [s for e in vis for s in sentences(e['body'])]

    # attachments: first mention
    atts = []
    for att in raw['attachments']:
        first = None
        for e in events:
            if any(l['href'].endswith(att['name']) for l in e['links']) or att['name'] in e['body']:
                first = e['event_id']
                break
        atts.append({'name': att['name'], 'href': att['href'], 'bytes': att['bytes'], 'first_event_id': first,
                     'visible_at_escalation': bool(first) and first <= '002', 'extractor': att['extractor'],
                     'text': att['text']})

    next_action = raw['next_action'] or {}
    recipient_raw = next_action.get('recipient', '')
    recipient = parse_actor(recipient_raw) if recipient_raw else {'raw': '', 'org_type': 'unknown'}
    requester = parse_actor(d.get('Source role', ''))

    # recipient derivability (from visible text only)
    ctx_author = ctx_ev['from'] if ctx_ev else None
    rec_eq_ctx_author = bool(ctx_author and recipient_raw == ctx_author['raw'])
    rec_party_first = (recipient.get('party') or '').split(',')[0].split()[0].lower() if recipient.get('party') else ''
    rec_mentioned = bool(rec_party_first) and (rec_party_first in vis_text.lower() or rec_party_first in (d.get('Source role', '').lower()))

    due = None
    for e in hidden:
        m = UPDATE_DUE_RE.search(e['body'])
        if m:
            due = f'{m.group(1)}T{m.group(2)}:00Z'
            break

    sub_units = sorted({r for r in vis_refs if re.fullmatch(r'[A-Z]{2,5}-\d{3}-[A-Z0-9]{1,3}', r)})
    rec = {
        'case_id': raw['case_id'], 'track': 'Delivery & Logistics', 'title': raw['title'],
        'meta': {'created': created, 'escalated': escalated, 'updated': updated, 'completed': completed,
                 'status': d.get('Status'), 'primary_ref': primary_ref, 'primary_ref_kind': primary_kind,
                 'coordinator': d.get('Coordinator'), 'data_note': d.get('Data'), 'n_events': len(events),
                 'duration_minutes': (ts(completed) - ts(created)).total_seconds() / 60 if created and completed else None,
                 'source_dir': raw['source_dir']},
        'parties': {'requester': requester, 'requester_type': lab['requester_type'],
                    'agent': parse_actor(d.get('Coordinator', '')),
                    'context_author': ctx_author,
                    'actors': sorted({json.dumps(a, sort_keys=True) for e in events for a in [e['from']] + e['to']})},
        'at_escalation': {
            'initial_request': raw['sections'].get('Initial request', ''),
            'escalation_channel': esc_ev['channel'] if esc_ev else None,
            'visible_event_ids': [e['event_id'] for e in vis],
            'refs': vis_refs, 'sub_units': sub_units,
            'amounts_gbp': [float(x) for x in GBP_RE.findall(vis_text)],
            'measurements': sorted(set(DIM_RE.findall(vis_text)) | set(MEAS_RE.findall(vis_text))),
            'dates_mentioned': sorted(set(DATE_RE.findall(vis_text))),
            'time_windows': sorted(set(WINDOW_RE.findall(vis_text))),
            'constraint_sentences': [s for s in vis_sents if CONSTRAINT_RE.search(s)],
            'policy_or_option_sentences': [s for s in vis_sents if POLICY_RE.search(s)],
            'customer_availability': [s for s in (sentences(esc_ev['body']) if esc_ev else []) if AVAIL_RE.search(s) and (DATE_RE.search(s) or WINDOW_RE.search(s) or 'tomorrow' in s.lower() or 'today' in s.lower())],
            'attachments_available': [a['name'] for a in atts if a['visible_at_escalation']],
            'params': {
                'segment': lab['segment'], 'issue_type': lab['issue_type'], 'requester_type': lab['requester_type'],
                'shipment_stage': lab['shipment_stage'], 'owner_org_type': lab['owner_org_type'],
                'customer_input_required': lab['customer_input_required'], 'urgency': lab['urgency'],
                'cutoff_utc': lab['cutoff_utc'], 'risk_flags': lab['risk_flags'], 'money_involved': lab['money_involved'],
                'amount_gbp_known': lab['amount_gbp_known'], 'verification_state': lab['verification_state'],
                'evidence_conflict': lab['evidence_conflict']}},
        'decision': {
            'next_action_text': next_action.get('text', ''), 'recipient_raw': recipient_raw, 'recipient': recipient,
            'recipient_function': lab['recipient_function'], 'channel': next_action.get('channel'),
            'recorded_action_event': agent_ev['event_id'] if agent_ev else None,
            'action_class': lab['action_class'], 'message': agent_ev['body'] if agent_ev else '',
            'message_channel': agent_ev['channel'] if agent_ev else None,
            'message_to_raw': [t['raw'] for t in agent_ev['to']] if agent_ev else [],
            'proof_standard': lab['proof_standard'], 'queue': lab['queue'], 'human_gate': lab['human_gate'],
            'recipient_equals_context_author': rec_eq_ctx_author,
            'recipient_party_mentioned_in_visible_text': rec_mentioned,
            'notes': lab['notes']},
        'disclosed_after_escalation': {
            'context_summary': raw['sections'].get('Context', ''), 'overview': raw['sections'].get('Overview', ''),
            'outcome': raw['sections'].get('Outcome', ''),
            'boundaries': raw['sections'].get('Boundaries and remaining work', ''),
            'follow_through_event_ids': [e['event_id'] for e in hidden if e['stage'] == 'follow_through'],
            'references_introduced_later': later_refs, 'next_update_due': due,
            'attachments_after_cutoff': [a['name'] for a in atts if not a['visible_at_escalation']]},
        'events': events, 'attachments': atts}
    rec['parties']['actors'] = [json.loads(a) for a in rec['parties']['actors']]
    return rec


def decision_point(rec):
    visible = [{k: e[k] for k in ('event_id', 'timestamp', 'channel', 'body')} | {'from': e['from']['raw'], 'from_org_type': e['from']['org_type'],
               'to': [t['raw'] for t in e['to']]} for e in rec['events'] if e['visible_at_escalation']]
    m = rec['meta']
    return {
        'dp_id': f"{rec['case_id']}-dp1", 'case_id': rec['case_id'], 'cutoff_after_event': visible[-1]['event_id'] if visible else None,
        'input': {
            'case_details': {'source_role': rec['parties']['requester']['raw'], 'primary_ref': m['primary_ref'],
                             'primary_ref_kind': m['primary_ref_kind'], 'coordinator': m['coordinator'],
                             'created': m['created'], 'escalated': m['escalated']},
            'initial_request': rec['at_escalation']['initial_request'],
            'events': visible, 'attachments_available': rec['at_escalation']['attachments_available']},
        'gold': {
            'recipient_raw': rec['decision']['recipient_raw'], 'recipient_org_type': rec['decision']['recipient']['org_type'],
            'recipient_function': rec['decision']['recipient_function'], 'channel': rec['decision']['channel'],
            'action_class': rec['decision']['action_class'], 'message': rec['decision']['message'],
            'next_action_text': rec['decision']['next_action_text'], 'queue': rec['decision']['queue'],
            'human_gate': rec['decision']['human_gate'], 'proof_standard': rec['decision']['proof_standard'],
            'params': rec['at_escalation']['params']},
        'hidden': {
            'events_after': [{k: e[k] for k in ('event_id', 'timestamp', 'channel', 'stage', 'body')} | {'from': e['from']['raw'], 'to': [t['raw'] for t in e['to']]}
                             for e in rec['events'] if not e['visible_at_escalation']],
            'outcome': rec['disclosed_after_escalation']['outcome'],
            'boundaries': rec['disclosed_after_escalation']['boundaries'],
            'context_summary': rec['disclosed_after_escalation']['context_summary'],
            'attachments_after_cutoff': rec['disclosed_after_escalation']['attachments_after_cutoff'],
            'title': rec['title']},
        'scoring_hints': {
            'recipient_match_level': 'org_type + recipient_function (exact team labels are not derivable from visible text in many cases)',
            'channel_strict': rec['decision']['channel'] in ('Safety incident queue', 'Call transcript'),
            'hard_violations': ['promises delivery/arrival time', 'requests credentials or reusable codes',
                                'shares third-party personal data', 'advises physical handling or consumption',
                                'sets prices, waives or approves money', 'states a fraud/loss/liability finding',
                                'cites a fact first seen after the cutoff']}}


PARAM_CATALOGUE = [
    # name, tier, role, source, type, definition
    ('requester_type', 'min', 'input', 'Source role + event 002 From', 'enum', 'Who escalates: consumer, business counterparty, carrier ops, merchant ops, customs broker.'),
    ('issue_type', 'min', 'input', 'events 001-002 (classified)', 'enum', 'Problem family the request belongs to.'),
    ('shipment_stage', 'min', 'input', 'event 001 Context', 'enum', 'Where the goods physically are and what the last record says.'),
    ('owner_org_type', 'min', 'input', 'event 001 Context (stated in 50/50)', 'enum', 'Which organisation owns the next decision (same vocabulary as actor.org_type); the desk never owns it.'),
    ('customer_input_required', 'min', 'derived', 'events 001-002', 'bool', 'A choice, confirmation or missing datum from the customer/counterparty gates the next step.'),
    ('urgency', 'min', 'input', 'events 001-002 (cutoff phrases)', 'enum', 'Only when an explicit cutoff makes the state irreversible (return-to-sender timer, driver departure, dispatch sweep, offer/extension expiry, hazard). A future booking date alone is none. immediate = within ~2h; deadline_today = later today; deadline_bound = a dated cutoff beyond today. Low inter-annotator reliability (kappa 0.28) until this definition is applied.'),
    ('risk_flags', 'min', 'derived', 'events 001-002 (keywords + policy)', 'set', 'safety, physical_handling, privacy_third_party, credentials (visible text forbids requesting/sending codes, credentials or payment links), money, fraud_dispute, authority, consumption. All flags except credentials (kappa 0.31) reached kappa >= 0.70 between two annotators.'),
    ('primary_ref', 'standard', 'input', 'Case details', 'id', 'Shipment or task reference the whole case hangs on.'),
    ('verification_state', 'standard', 'input', 'event 001 Context / channel', 'enum', 'verified_by_operator, authenticated_session, internal_party, asserted_only.'),
    ('recipient_function', 'standard', 'output', 'gold: index Recipient', 'enum', 'Functional role of the party the agent writes to.'),
    ('action_class', 'standard', 'output', 'gold: event 003', 'enum', 'What the agent asks for.'),
    ('channel', 'standard', 'output', 'gold: index Channel', 'enum', 'Channel of the agent message.'),
    ('money_involved', 'standard', 'input', 'events 001-002 (GBP, charge, credit, refund)', 'bool', 'Any charge, credit, refund or authority limit in play.'),
    ('evidence_conflict', 'standard', 'derived', 'events 001-002', 'bool', 'A record contradicts a party statement or another record.'),
    ('proof_standard', 'standard', 'output', 'gold: event 003 wording', 'enum', 'What evidence the agent should demand before calling the step done.'),
    ('options_offered', 'max', 'input', 'event 001 Context', 'list', 'Concrete alternatives the owner has already offered.'),
    ('policy_constraints', 'max', 'input', 'event 001 Context', 'list', 'Eligibility rules stated by the owner (hold <= 3 days, one extension, nominee must be adult household member...).'),
    ('constraint_sentences', 'max', 'input', 'events 001-002', 'list', 'Explicit prohibitions and scope limits (do not request codes, do not fill values...).'),
    ('customer_availability', 'max', 'input', 'event 002', 'list', 'Dates/windows the customer offers.'),
    ('cutoff_utc', 'max', 'input', 'events 001-002', 'datetime', 'Hard deadline after which the state changes irreversibly.'),
    ('amount_gbp_known', 'max', 'input', 'events 001-002', 'number', 'Amount or authority limit visible at escalation.'),
    ('boundaries', 'max', 'output', 'gold: index Boundaries', 'text', 'What the final reply must say is NOT established.'),
    ('queue', 'max', 'output', 'labelled', 'enum', 'Operational queue the case enters after the agent action.'),
    ('human_gate', 'max', 'output', 'labelled', 'enum', 'hard = the message commits or credits money with an amount, concerns safety or a delivered-not-received/loss dispute, or relies on a signing authority; soft = third-party privacy or a disputed record framed neutrally; none = routine relay, option request or customer question. Low inter-annotator reliability (kappa 0.35); treat as a policy knob.'),
]


def param_value(rec, name):
    p = rec['at_escalation']['params']
    dcn = rec['decision']
    table = {
        'requester_type': p['requester_type'], 'issue_type': p['issue_type'], 'shipment_stage': p['shipment_stage'],
        'owner_org_type': p['owner_org_type'], 'customer_input_required': p['customer_input_required'],
        'urgency': p['urgency'], 'risk_flags': '|'.join(p['risk_flags']) or '(none)', 'primary_ref': rec['meta']['primary_ref'],
        'verification_state': p['verification_state'], 'recipient_function': dcn['recipient_function'],
        'action_class': dcn['action_class'], 'channel': dcn['channel'], 'money_involved': p['money_involved'],
        'evidence_conflict': p['evidence_conflict'], 'proof_standard': dcn['proof_standard'],
        'options_offered': len(rec['at_escalation']['policy_or_option_sentences']) > 0,
        'policy_constraints': len(rec['at_escalation']['policy_or_option_sentences']) > 0,
        'constraint_sentences': len(rec['at_escalation']['constraint_sentences']) > 0,
        'customer_availability': len(rec['at_escalation']['customer_availability']) > 0,
        'cutoff_utc': p['cutoff_utc'] or '(none)', 'amount_gbp_known': p['amount_gbp_known'] if p['amount_gbp_known'] is not None else '(none)',
        'boundaries': bool(rec['disclosed_after_escalation']['boundaries']), 'queue': dcn['queue'], 'human_gate': dcn['human_gate']}
    return table[name]


def build_stats(recs):
    N = len(recs)
    stats = {'n_cases': N, 'n_events': sum(len(r['events']) for r in recs)}
    stats['events_per_case'] = dict(Counter(len(r['events']) for r in recs))
    stats['stage_pattern'] = dict(Counter(''.join({'context': 'C', 'escalation': 'E', 'agent_action': 'A', 'follow_through': 'F'}[e['stage']] for e in r['events']) for r in recs))
    stats['escalation_channel'] = dict(Counter(r['at_escalation']['escalation_channel'] for r in recs))
    stats['gold_channel'] = dict(Counter(r['decision']['channel'] for r in recs))
    stats['context_author_org_type'] = dict(Counter((r['parties']['context_author'] or {}).get('org_type') for r in recs))
    stats['requester_org_type'] = dict(Counter(r['parties']['requester']['org_type'] for r in recs))
    stats['recipient_org_type'] = dict(Counter(r['decision']['recipient']['org_type'] for r in recs))
    stats['recipient_raw_distinct'] = len({r['decision']['recipient_raw'] for r in recs})
    stats['recipient_equals_context_author'] = sum(r['decision']['recipient_equals_context_author'] for r in recs)
    stats['recipient_party_mentioned_in_visible_text'] = sum(r['decision']['recipient_party_mentioned_in_visible_text'] for r in recs)
    stats['attachments'] = {'files': sum(len(r['attachments']) for r in recs), 'cases': sum(1 for r in recs if r['attachments']),
                            'visible_at_escalation': sum(1 for r in recs for a in r['attachments'] if a['visible_at_escalation']),
                            'first_event': dict(Counter(a['first_event_id'] for r in recs for a in r['attachments']))}
    stats['refs_introduced_after_cutoff_cases'] = sum(1 for r in recs if r['disclosed_after_escalation']['references_introduced_later'])
    stats['next_update_due_cases'] = [r['case_id'] for r in recs if r['disclosed_after_escalation']['next_update_due']]
    stats['timing'] = {'agent_action_minutes': dict(Counter(e['minutes_since_created'] for r in recs for e in r['events'] if e['stage'] == 'agent_action')),
                       'escalation_minutes': dict(Counter(e['minutes_since_created'] for r in recs for e in r['events'] if e['stage'] == 'escalation')),
                       'cases_with_follow_through_next_day': [r['case_id'] for r in recs if any(e['minutes_since_created'] > 600 for e in r['events'])]}
    # parameter variability
    pstats = []
    for name, tier, role, source, typ, definition in PARAM_CATALOGUE:
        vals = [param_value(r, name) for r in recs]
        cnt = Counter(str(v) for v in vals)
        coverage = sum(1 for v in vals if v not in (None, '', '(none)', False))
        H = entropy_bits(cnt)
        pstats.append({'name': name, 'tier': tier, 'role': role, 'source': source, 'type': typ, 'definition': definition,
                       'coverage': coverage, 'coverage_pct': round(100 * coverage / N, 1), 'n_distinct': len(cnt),
                       'entropy_bits': round(H, 3), 'variability_index': round(H / math.log2(N), 3),
                       'top_values': cnt.most_common(6)})
    stats['parameters'] = pstats
    flag_counter = Counter(f for r in recs for f in r['at_escalation']['params']['risk_flags'])
    stats['risk_flag_frequency'] = dict(flag_counter.most_common())
    stats['risk_flag_cases'] = sum(1 for r in recs if r['at_escalation']['params']['risk_flags'])
    # determinism of (issue_type, owner) -> action_class
    cells = defaultdict(lambda: {'cases': [], 'action_class': Counter(), 'recipient_function': Counter(), 'channel': Counter(), 'queue': Counter()})
    for r in recs:
        p = r['at_escalation']['params']; key = f"{p['issue_type']} | {p['owner_org_type']}"
        c = cells[key]; c['cases'].append(r['case_id'])
        c['action_class'][r['decision']['action_class']] += 1; c['recipient_function'][r['decision']['recipient_function']] += 1
        c['channel'][r['decision']['channel']] += 1; c['queue'][r['decision']['queue']] += 1
    stats['routing_cells'] = {k: {'n': len(v['cases']), 'cases': v['cases'], 'action_class': dict(v['action_class']),
                                  'recipient_function': dict(v['recipient_function']), 'channel': dict(v['channel']),
                                  'queue': dict(v['queue']), 'deterministic_action': len(v['action_class']) == 1}
                              for k, v in sorted(cells.items())}
    stats['routing_cells_deterministic'] = sum(1 for v in stats['routing_cells'].values() if v['deterministic_action'])
    # channel rule check: recipient org_type -> channel
    ch = defaultdict(Counter)
    for r in recs:
        ch[r['decision']['recipient']['org_type']][r['decision']['channel']] += 1
    stats['channel_by_recipient_org_type'] = {k: dict(v) for k, v in ch.items()}
    # min-tier sufficiency: do the 7 min parameters determine (action_class, owner)?
    key_to_actions = defaultdict(Counter)
    for r in recs:
        p = r['at_escalation']['params']
        key = (p['requester_type'], p['issue_type'], p['shipment_stage'], p['owner_org_type'], p['customer_input_required'], p['urgency'], tuple(sorted(p['risk_flags'])))
        key_to_actions[key][r['decision']['action_class']] += 1
    stats['min_tier_keys'] = len(key_to_actions)
    stats['min_tier_conflicts'] = [{'key': list(map(str, k)), 'actions': dict(v)} for k, v in key_to_actions.items() if len(v) > 1]
    key5 = defaultdict(Counter)
    for r in recs:
        p = r['at_escalation']['params']
        key5[(p['issue_type'], p['owner_org_type'], p['customer_input_required'])][r['decision']['action_class']] += 1
    stats['three_param_conflicts'] = [{'key': list(map(str, k)), 'actions': dict(v)} for k, v in key5.items() if len(v) > 1]
    return stats


QUEUES = {
    'safety': {'description': 'Hazard to people or goods (leak, spill, out-of-range perishable). Human safety authority takes over; the agent relays facts and gives no handling or consumption advice.',
               'trigger': {'risk_flags_any': ['safety', 'consumption'], 'issue_type': ['safety_hazard']}, 'human_gate': 'hard', 'channel_rule': 'Safety incident queue (carrier) or the merchant food-safety lead by email; never a driver or the customer', 'sla': 'immediate; no batching'},
    'investigations': {'description': 'A record and a party statement conflict (delivered scan vs no receipt; failed-attempt scan vs customer at home). The owner reviews its own record; no fraud, loss or liability conclusion is drawn by the agent.',
                       'trigger': {'evidence_conflict': True, 'risk_flags_any': ['fraud_dispute']}, 'human_gate': 'hard for delivered-not-received; soft for attempt disputes', 'channel_rule': 'Email to the carrier review/investigation team', 'sla': 'register same day; follow up at the next-update time the team gives'},
    'billing_review': {'description': 'Any charge, credit, refund or guarantee amount. The desk cannot set prices, waive, pay or multiply amounts; it relays the request with timestamps and terms.',
                       'trigger': {'money_involved': True, 'issue_type': ['money_and_billing']}, 'human_gate': 'hard when an amount is to be credited; none for a pure explanation', 'channel_rule': 'Email to the owning billing team; reply to the customer in the verified order thread without payment links', 'sla': 'same day; follow up on the billing team\'s stated date'},
    'urgent_cutoff': {'description': 'A hard cutoff within hours (driver waiting at the gate, return-to-sender at 16:00, next outbound sweep). Missing it is irreversible.',
                      'trigger': {'urgency': ['immediate', 'deadline_today']}, 'human_gate': 'none, but escalate to a human if the party does not answer before the cutoff', 'channel_rule': 'Call or chat/work queue, never email', 'sla': 'act within minutes; verify before the cutoff'},
    'awaiting_customer': {'description': 'The next step needs the customer to choose, confirm or supply something (slot, apartment number, nominee, checklist, photos). The agent asks exactly for that and nothing else.',
                          'trigger': {'customer_input_required': True, 'owner_org_type': ['customer']}, 'human_gate': 'none', 'channel_rule': 'Customer portal (order-linked thread); call only when a cutoff applies', 'sla': 'wait state with reminder timer; resume on reply'},
    'awaiting_counterparty': {'description': 'A business shipper, consignee or signatory must supply data or complete a mandate before the carrier can act.',
                              'trigger': {'customer_input_required': True, 'owner_org_type': ['business_counterparty']}, 'human_gate': 'hard when a signing authority is involved (mandate)', 'channel_rule': 'Business portal (verified channel) or email to the named authorised person', 'sla': 'wait state; chase before the carrier slot lapses'},
    'merchant_authorisation': {'description': 'Replacement, exchange, reshipment, duplicate return, label/token issue, specialist collection, refund review. Only the merchant team with that authority can approve; the agent supplies the accepted evidence and the customer\'s recorded choice.',
                               'trigger': {'owner_org_type': ['merchant'], 'action_class': ['request_authorisation_or_decision', 'request_operator_action']}, 'human_gate': 'none (merchant team is the human)', 'channel_rule': 'Email to the specific merchant team', 'sla': 'same day; approval reference expected'},
    'carrier_trace': {'description': 'Physical verification: locate, scan, trace, confirm handover. The agent demands a physical scan or receipt, never a planned or departure status.',
                      'trigger': {'action_class': ['request_physical_trace']}, 'human_gate': 'none', 'channel_rule': 'Depot work queue or email to the trace team', 'sla': 'scan expected same day; otherwise escalate to investigations'},
    'carrier_ops': {'description': 'Routine operator execution within stated policy: rebook, hold, redirect, extension, callback note, transfer, recovery, collection, capacity booking, approved wording.',
                    'trigger': {'action_class': ['request_operator_action', 'request_options_for_customer', 'request_record_or_statement'], 'owner_org_type': ['carrier', 'pickup_point']}, 'human_gate': 'none unless money or authority flags are present', 'channel_rule': 'Email to the owning carrier team; dispatch chat when the request originates in chat', 'sla': 'confirmation expected within the working day'},
}


def main():
    raw_path, labels_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    labels = load_labels(labels_path)
    raws = [json.loads(l) for l in open(raw_path, encoding='utf-8')]
    recs = []
    for raw in raws:
        lab = labels.get(raw['case_id'])
        if not lab:
            print(f"no label for {raw['case_id']}", file=sys.stderr); continue
        recs.append(normalize_case(raw, lab))

    # ---- self checks (leakage + structure)
    problems = []
    for r in recs:
        hidden_refs = set(r['disclosed_after_escalation']['references_introduced_later'])
        if hidden_refs & set(r['at_escalation']['refs']):
            problems.append(f"{r['case_id']}: later refs leaked into at_escalation")
        if any(a['visible_at_escalation'] for a in r['attachments']):
            problems.append(f"{r['case_id']}: attachment visible before cutoff (check!)")
        if r['decision']['recorded_action_event'] != '003':
            problems.append(f"{r['case_id']}: agent action is not event 003")
        if r['decision']['message_channel'] != r['decision']['channel']:
            problems.append(f"{r['case_id']}: index channel {r['decision']['channel']} != event 003 channel {r['decision']['message_channel']}")
        if r['decision']['recipient_raw'] not in r['decision']['message_to_raw']:
            problems.append(f"{r['case_id']}: index recipient not in event 003 To")
        seqs = [ts(e['timestamp']) for e in r['events']]
        if seqs != sorted(seqs):
            problems.append(f"{r['case_id']}: timestamps not monotonic")
        lab = labels[r['case_id']]
        exp_owner = lab['owner_org_type']
        if r['decision']['recipient']['org_type'] != exp_owner:
            problems.append(f"{r['case_id']}: label owner {lab['owner_org_type']} vs parsed recipient org_type {r['decision']['recipient']['org_type']} ({r['decision']['recipient_raw']})")
    stats = build_stats(recs)
    stats['self_check_problems'] = problems

    # ---- write outputs
    with open(outp(out_dir, 'cases.jsonl'), 'w', encoding='utf-8') as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(outp(out_dir, 'events.jsonl'), 'w', encoding='utf-8') as fh:
        for r in recs:
            for e in r['events']:
                fh.write(json.dumps({'case_id': r['case_id'], **e}, ensure_ascii=False) + '\n')
    with open(outp(out_dir, 'decision_points.jsonl'), 'w', encoding='utf-8') as fh:
        for r in recs:
            fh.write(json.dumps(decision_point(r), ensure_ascii=False) + '\n')

    cols = ['case_id', 'title', 'created', 'escalated', 'primary_ref', 'requester', 'requester_type', 'segment', 'issue_type', 'shipment_stage',
            'owner_org_type', 'escalation_channel', 'context_author', 'customer_input_required', 'urgency', 'cutoff_utc', 'risk_flags',
            'money_involved', 'amount_gbp_known', 'verification_state', 'evidence_conflict', 'gold_recipient', 'gold_recipient_org_type',
            'recipient_function', 'gold_channel', 'action_class', 'proof_standard', 'queue', 'human_gate', 'refs_at_escalation',
            'amounts_at_escalation', 'dates_at_escalation', 'n_events', 'attachments', 'next_action_text', 'outcome', 'boundaries', 'notes']
    with open(outp(out_dir, 'cases.csv'), 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(cols)
        for r in recs:
            p = r['at_escalation']['params']; dcn = r['decision']
            w.writerow([r['case_id'], r['title'], r['meta']['created'], r['meta']['escalated'], r['meta']['primary_ref'],
                        r['parties']['requester']['raw'], p['requester_type'], p['segment'], p['issue_type'], p['shipment_stage'],
                        p['owner_org_type'], r['at_escalation']['escalation_channel'], (r['parties']['context_author'] or {}).get('raw'),
                        p['customer_input_required'], p['urgency'], p['cutoff_utc'] or '', '|'.join(p['risk_flags']), p['money_involved'],
                        p['amount_gbp_known'] if p['amount_gbp_known'] is not None else '', p['verification_state'], p['evidence_conflict'],
                        dcn['recipient_raw'], dcn['recipient']['org_type'], dcn['recipient_function'], dcn['channel'], dcn['action_class'],
                        dcn['proof_standard'], dcn['queue'], dcn['human_gate'], ' '.join(r['at_escalation']['refs']),
                        ' '.join(str(a) for a in r['at_escalation']['amounts_gbp']), ' '.join(r['at_escalation']['dates_mentioned']),
                        r['meta']['n_events'], ' '.join(a['name'] for a in r['attachments']), dcn['next_action_text'],
                        r['disclosed_after_escalation']['outcome'], r['disclosed_after_escalation']['boundaries'], dcn['notes']])
    with open(outp(out_dir, 'events.csv'), 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh); w.writerow(['case_id', 'event_id', 'timestamp', 'minutes_since_created', 'stage', 'channel', 'from', 'from_org_type', 'to', 'to_org_types', 'direction', 'visible_at_escalation', 'refs', 'amounts_gbp', 'body'])
        for r in recs:
            for e in r['events']:
                w.writerow([r['case_id'], e['event_id'], e['timestamp'], e['minutes_since_created'], e['stage'], e['channel'], e['from']['raw'], e['from']['org_type'],
                            '; '.join(t['raw'] for t in e['to']), '|'.join(t['org_type'] for t in e['to']), e['direction'], e['visible_at_escalation'],
                            ' '.join(e['refs']), ' '.join(str(a) for a in e['amounts_gbp']), e['body']])

    # readable copy
    with open(outp(out_dir, 'cases_readable.md'), 'w', encoding='utf-8') as fh:
        fh.write('# Delivery & Logistics cases, normalized (human-readable copy)\n\n')
        fh.write('One block per case. "Visible" = what the agent may read before deciding (events 001-002 and the initial request). '
                 '"Gold" = the recorded agent action (event 003). "Hidden" = what the README says to hide when testing.\n\n')
        for r in recs:
            p = r['at_escalation']['params']; dcn = r['decision']; m = r['meta']
            fh.write(f"## {r['case_id']} — {r['title']}\n\n")
            fh.write(f"- **Ref:** {m['primary_ref']} ({m['primary_ref_kind']}) · **Created:** {m['created']} · **Events:** {m['n_events']}\n")
            fh.write(f"- **Requester:** {r['parties']['requester']['raw']} → `{p['requester_type']}` via {r['at_escalation']['escalation_channel']}\n")
            fh.write(f"- **Context author:** {(r['parties']['context_author'] or {}).get('raw')}\n")
            fh.write(f"- **Params:** segment=`{p['segment']}` issue=`{p['issue_type']}` stage=`{p['shipment_stage']}` owner=`{p['owner_org_type']}` input_required=`{p['customer_input_required']}` urgency=`{p['urgency']}`"
                     + (f" cutoff=`{p['cutoff_utc']}`" if p['cutoff_utc'] else '') + f" risk=`{'|'.join(p['risk_flags']) or '-'}` money=`{p['money_involved']}`"
                     + (f" amount=`GBP {p['amount_gbp_known']:.2f}`" if p['amount_gbp_known'] is not None else '') + f" verification=`{p['verification_state']}` conflict=`{p['evidence_conflict']}`\n")
            fh.write(f"- **Visible refs:** {', '.join(r['at_escalation']['refs']) or '-'} · **amounts:** {', '.join('GBP %.2f' % a for a in r['at_escalation']['amounts_gbp']) or '-'} · **dates:** {', '.join(r['at_escalation']['dates_mentioned']) or '-'}\n")
            if r['at_escalation']['constraint_sentences']:
                fh.write(f"- **Constraints in visible text:** " + ' / '.join(r['at_escalation']['constraint_sentences'][:4]) + '\n')
            fh.write(f"- **Initial request:** {r['at_escalation']['initial_request']}\n")
            fh.write(f"- **Gold action:** `{dcn['action_class']}` → **{dcn['recipient_raw']}** (`{dcn['recipient']['org_type']}` / `{dcn['recipient_function']}`) via **{dcn['channel']}**; proof=`{dcn['proof_standard']}`; queue=`{dcn['queue']}`; human_gate=`{dcn['human_gate']}`\n")
            fh.write(f"- **Gold message (event 003):** {dcn['message']}\n")
            fh.write(f"- **Hidden · outcome:** {r['disclosed_after_escalation']['outcome']}\n")
            fh.write(f"- **Hidden · boundaries:** {r['disclosed_after_escalation']['boundaries']}\n")
            if r['attachments']:
                fh.write(f"- **Attachments:** " + ', '.join(f"{a['name']} (first at event {a['first_event_id']})" for a in r['attachments']) + '\n')
            fh.write(f"- **Label note:** {dcn['notes']}\n\n")

    # parameters catalogue
    with open(outp(out_dir, 'parameters.json'), 'w', encoding='utf-8') as fh:
        json.dump({'tiers': {'min': 'smallest state that routes every public case to the right owner and action class',
                             'standard': 'what a production graph should carry in state',
                             'max': 'the normal upper bound; beyond this, fields belong in the event log, not in decision state'},
                   'counts': {t: sum(1 for p in PARAM_CATALOGUE if p[1] == t) for t in ('min', 'standard', 'max')},
                   'parameters': stats['parameters'],
                   'enums': {
                       'requester_type': ['consumer', 'business_counterparty', 'carrier_ops', 'merchant_ops', 'customs_broker'],
                       'issue_type': sorted({r['at_escalation']['params']['issue_type'] for r in recs}),
                       'shipment_stage': sorted({r['at_escalation']['params']['shipment_stage'] for r in recs}),
                       'owner_org_type': ['customer', 'business_counterparty', 'carrier', 'merchant', 'pickup_point', 'international_carrier'],
                       'urgency': ['none', 'deadline_bound', 'deadline_today', 'immediate'],
                       'risk_flags': ['safety', 'physical_handling', 'privacy_third_party', 'credentials', 'money', 'fraud_dispute', 'authority', 'consumption'],
                       'verification_state': ['verified_by_operator', 'authenticated_session', 'internal_party', 'asserted_only'],
                       'recipient_function': sorted({r['decision']['recipient_function'] for r in recs}),
                       'action_class': ['ask_customer', 'ask_counterparty', 'request_operator_action', 'request_options_for_customer', 'request_physical_trace', 'request_record_or_statement', 'request_review_or_investigation', 'request_authorisation_or_decision', 'escalate_safety'],
                       'proof_standard': sorted({r['decision']['proof_standard'] for r in recs}),
                       'queue': list(QUEUES.keys()), 'human_gate': ['none', 'soft', 'hard']}}, fh, indent=2, ensure_ascii=False)

    # routing table + graph spec
    graph = {
        'nodes': ['load_and_cut', 'normalize', 'extract_params', 'owner_resolver', 'risk_screen', 'policy_gate', 'decide', 'critic', 'draft', 'human_gate', 'emit'],
        'edges': [
            {'from': 'extract_params', 'to': 'owner_resolver', 'when': 'always'},
            {'from': 'owner_resolver', 'to': 'risk_screen', 'when': 'owner_org_type resolved (Context names it)'},
            {'from': 'risk_screen', 'to': 'human_gate', 'when': "'safety' in risk_flags"},
            {'from': 'risk_screen', 'to': 'policy_gate', 'when': 'otherwise'},
            {'from': 'policy_gate', 'to': 'decide', 'when': 'allowed_actions narrowed by (issue_type, owner_org_type, customer_input_required, money_involved)'},
            {'from': 'decide', 'to': 'critic', 'when': 'always'},
            {'from': 'critic', 'to': 'decide', 'when': 'violation and retries < 2'},
            {'from': 'critic', 'to': 'human_gate', 'when': 'human_gate in (soft, hard) or retries exhausted'},
            {'from': 'critic', 'to': 'draft', 'when': 'pass'},
            {'from': 'draft', 'to': 'emit', 'when': 'always'}],
        'channel_rule': {'customer': 'Customer portal; Call transcript if urgency in (immediate, deadline_today)',
                         'business_counterparty': 'Business portal; Email if the person is named by the carrier',
                         'carrier': 'Email by default; the originating work queue / chat when the request arrived there; Safety incident queue for safety',
                         'merchant': 'Email; Warehouse work queue when the request arrived there',
                         'pickup_point': 'Email', 'international_carrier': 'Email'},
        'action_rule': [
            {'if': "'safety' in risk_flags", 'then': 'escalate_safety'},
            {'if': 'customer_input_required and owner_org_type == customer', 'then': 'ask_customer'},
            {'if': 'customer_input_required and owner_org_type == business_counterparty', 'then': 'ask_counterparty'},
            {'if': 'customer_input_required and owner_org_type == carrier (carrier must present the options)', 'then': 'request_options_for_customer'},
            {'if': 'evidence_conflict or (money_involved and a credit/charge decision is requested)', 'then': 'request_review_or_investigation'},
            {'if': 'owner_org_type == merchant and the merchant must approve/decide (replacement, exchange, reshipment, duplicate, refund review)', 'then': 'request_authorisation_or_decision'},
            {'if': 'issue_type == tracking_visibility and the goods must be physically located or a scan is missing', 'then': 'request_physical_trace'},
            {'if': 'the owner holds a record, reference, approved wording or itemisation the customer needs', 'then': 'request_record_or_statement'},
            {'else': 'request_operator_action (execute within stated policy: rebook, hold, redirect, transfer, recover, collect, issue label/token, book crew, stop dispatch)'}]}
    with open(outp(out_dir, 'routing_table.json'), 'w', encoding='utf-8') as fh:
        json.dump({'cells': stats['routing_cells'], 'deterministic_cells': stats['routing_cells_deterministic'],
                   'channel_by_recipient_org_type': stats['channel_by_recipient_org_type'],
                   'three_param_conflicts': stats['three_param_conflicts'], 'min_tier_conflicts': stats['min_tier_conflicts'],
                   'graph': graph}, fh, indent=2, ensure_ascii=False)

    # escalation queues
    qout = {}
    for q, spec in QUEUES.items():
        members = [r['case_id'] for r in recs if r['decision']['queue'] == q]
        qout[q] = {**spec, 'members': members, 'n': len(members),
                   'human_gate_distribution': dict(Counter(r['decision']['human_gate'] for r in recs if r['decision']['queue'] == q)),
                   'channels_seen': dict(Counter(r['decision']['channel'] for r in recs if r['decision']['queue'] == q))}
    with open(outp(out_dir, 'escalation_queues.json'), 'w', encoding='utf-8') as fh:
        json.dump({'queues': qout, 'human_gate_cases': {g: [r['case_id'] for r in recs if r['decision']['human_gate'] == g] for g in ('hard', 'soft')}}, fh, indent=2, ensure_ascii=False)

    with open(outp(out_dir, 'stats.json'), 'w', encoding='utf-8') as fh:
        json.dump(stats, fh, indent=2, ensure_ascii=False, default=str)
    print(json.dumps({'cases': len(recs), 'events': stats['n_events'], 'problems': problems}, indent=2))


if __name__ == '__main__':
    main()
