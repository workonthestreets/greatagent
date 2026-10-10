#!/usr/bin/env python3
"""Build the delivery database on Andrey Zharkov's system model.

Usage:
    python3 -I build_db.py --cases data/delivery/agent/cases.jsonl --facts data/pipeline/facts_delivery.py \
        --out data/delivery/database/delivery.sqlite [--stress data/delivery/inputs/stress_raw.jsonl] [--schema-out ...] [--recon-out ...]

Entities (user/andrey/drafts/delivery-system-model.md): actors, orders, shipments, parcels, events (operational
observations extracted from message bodies), cases, tasks, evidence; plus messages (the 228 communications),
case_actors, reconciliation, and the dashboard / timeline views.  Policy: a value the data never states is the
literal string 'N/A', never NULL or ''.  Visibility at the decision point is kept on every message, event and
evidence row so the agent-facing cut can be reproduced with one WHERE clause.
"""
import argparse
import importlib.util
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime

NA = 'N/A'
HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


norm = load_module(os.path.join(HERE, 'normalize_delivery.py'), 'normdel')

SHIP_PREFIX = ('DL-', 'RT-', 'WP-', 'PA-', 'OF-')
DOC_PREFIX = {'POD': 'proof_of_delivery', 'COL': 'collection_receipt', 'WH': 'warehouse_receipt', 'MN': 'manifest',
              'CN': 'credit_note', 'CI': 'commercial_invoice', 'IC': 'charge_notice', 'KL': 'receiving_count',
              'CAN': 'cancellation_record', 'CLR': 'clearance_reference', 'MND': 'mandate', 'RL': 'return_label',
              'EX': 'exchange_approval', 'DR': 'duplicate_return_authorisation', 'SP': 'specialist_booking',
              'ARC': 'dock_appointment', 'SAFE': 'safety_incident', 'GC': 'guarantee_credit', 'RF': 'refund_review',
              'MD': 'misdelivery_intake_record', 'OF': 'packing_list', 'INV': 'invoice_or_investigation'}
LOC_RE = re.compile(r'(sort cage [A-Z]-\d+|inbound cage [A-Z]-\d+|outbound cage [A-Z]\d+|receiving lane L\d|lane L\d|dock D\d|receiving door R\d|dispatch door S\d|(?:North Sedgeglass|East Copperfin|Halverstone) depot|returns? depot|Copperfin Returns Counter|Copperfin Counter|Sedgeglass Counter|Copperfin Locker|transfer bay|returns bay|oversize rack|transfer trailer|destination depot|depot stock|wrong stop|adjacent building stop|\d+ [A-Z][a-z]+ (?:Court|Mews|Walk)[^,.;]*)', re.I)
T_A = re.compile(r'(\d{2}:\d{2}) UTC on (20\d{2}-\d{2}-\d{2})')
T_B = re.compile(r'(20\d{2}-\d{2}-\d{2}),? (\d{2}:\d{2}) UTC(?![–-])')
T_WIN = re.compile(r'(20\d{2}-\d{2}-\d{2}),? (\d{2}:\d{2})\s?[–-]\s?(\d{2}:\d{2}) UTC')
T_WIN2 = re.compile(r'(\d{2}:\d{2})\s?[–-]\s?(\d{2}:\d{2}) UTC')
T_AT = re.compile(r'\bat (\d{2}:\d{2})(?: UTC)?(?: today)?\b', re.I)
TIME_TOKEN = re.compile(r'(?:(?P<d1>20\d{2}-\d{2}-\d{2}),? )?(?P<t>\d{2}:\d{2})(?:\s?UTC)?(?: on (?P<d2>20\d{2}-\d{2}-\d{2}))?')
STATE_KEYWORDS = ('isolat', 'confirmed lost', 'hold reason', 'address hold', 'return-to-sender', 'returned to sender', 'back in our stock', 'dispatch stopped', 'suspend', 'keeping clear', 'stopped moving', 'marked hold', 'on hold', 'not been delivered', 'was not delivered', 'in depot custody')
T_DATE = re.compile(r'\b(20\d{2}-\d{2}-\d{2})\b')
EVENT_KEYWORDS = [
    ('safety_isolation', ('isolat', 'keeping clear', 'stopped moving')), ('failed_attempt', ('failed-attempt', 'failed attempt')),
    ('dispatch_stopped', ('dispatch stopped', 'dispatch stop')), ('route_failure', ('ended that route', 'was not delivered', 'vehicle fault', 'not been delivered', 'in depot custody')), ('lost_confirmed', ('confirmed lost', 'could not be located')),
    ('hold', ('hold reason', 'address hold', 'marked hold', ' hold ', 'on hold')), ('returned_to_sender', ('return-to-sender processing', 'returned to sender', 'back in our stock')),
    ('collection', ('collected', 'collection receipt')),
    ('receipt_scan', ('physically received', 'receipt scan', 'received and scanned', 'scanned here', 'scanned into', 'received at our', 'receipt confirmed', 'physical receipt')),
    ('evidence_receipt', ('requested views', 'received both', 'image views')),
    ('delivery_handover', ('handover', 'handed', 'delivered', 'received dl', 'arrived at', 'i received dl', 'met me', 'received at ')),
    ('booking', ('booked', 'rebook', 'reserved', 'booking', 'appointment', 'allocated', 'allocation', 'confirmed for', 'scheduled', 'assigned to', 'we confirmed', 'we accept ', 'confirmed dl')),
    ('ready_for_collection', ('ready at', 'is ready', 'ready for collection', 'ready until')),
    ('located', ('located', 'we found', 'found dl', 'in sort cage', 'in inbound cage', 'was in the', 'held on a separate')),
    ('removed_from_dispatch', ('removed', 'cancellation stock')), ('route_suspension', ('suspend',)),
    ('transfer', ('transferred', 'transfer dl')), ('temperature_reading', ('°c', 'logger')),
    ('cancellation', ('cancel',)), ('credit', ('credit',)), ('registration', ('registered',)),
    ('authorisation', ('approved', 'authorised', 'authorized', 'mandate')), ('customer_choice', ('accepted', 'chose', 'selection', 'applied your recorded', 'please choose', 'i choose', 'i will take', 'i nominate')),
    ('customer_availability', ('i can be home', 'i am available', 'available on', 'i can attend', 'i can collect', 'i am free')),
    ('document_issue', ('issued', 'is supplied', 'generated', 'placed')),
    ('release', ('released', 'release to routing', 'release date')),
    ('deadline', ('due to return', 'until ', 'before cutoff', 'before expiry', 'next update', 'will update', 'review conditions', 'reviewed at', 'next review', 'expire', 'deadline', 'guaranteed by', 'cutoff', 'was due', 'due on', 'will enter return')),
    ('offer', ('can offer', 'we can reach', 'inventory currently has', 'may be available', 'supports it', 'supports printer', 'open 10:00', 'is open', 'use 20')),
    ('charge', ('charge of', 'upgrade charge', 'service addition', 'gbp')), ('scan', ('scan',)), ('notification', ('notification',)), ('missed', ('missed',)),
]
ACK_KEYS = ('booking', 'notice', 'notification', 'hours', 'works for me', 'can open', 'can see', 'i have the')


def na(v):
    if v is None:
        return NA
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, (list, tuple)):
        return '|'.join(str(x) for x in v) if v else NA
    s = str(v).strip()
    return s if s else NA


def classify_event(sent, from_org_type='unknown'):
    low = sent.lower()
    if from_org_type == 'customer' and any(k in low for k in ACK_KEYS) and 'arrived' not in low and 'received dl' not in low:
        return 'acknowledgement'
    for etype, keys in EVENT_KEYWORDS:
        if any(k in low for k in keys):
            return etype
    return 'other'


def extract_events(case_id, primary_ref, messages):
    """Operational observations mentioned inside message bodies (append-only records in the draft's sense)."""
    out = []
    n = 0
    for m in messages:
        if m['from_org_type'] == 'desk':
            continue  # the desk records no operational events; its requests live in tasks/messages
        msg_date = m['timestamp'][:10]
        last_date = None
        for sent in norm.sentences(m['body']):
            if sent.rstrip().endswith('?'):
                continue  # a question is not an observation
            occurred, precision = None, None
            cands = []
            for tm in TIME_TOKEN.finditer(sent):
                prefix = sent[max(0, tm.start() - 9):tm.start()].lower()
                deadline_ctx = any(prefix.rstrip().endswith(w) for w in ('until', 'by', 'before', 'to', '–', '-', 'from'))
                date = tm.group('d1') or tm.group('d2')
                if not date:
                    if 'that day' in sent.lower() and last_date:
                        date = last_date
                    else:
                        date = msg_date
                cands.append((deadline_ctx, f"{date}T{tm.group('t')}:00Z", 'minute' if (tm.group('d1') or tm.group('d2')) else ('minute_date_from_prior_sentence' if 'that day' in sent.lower() and last_date else 'minute_date_from_message')))
            if cands:
                pick = next((c for c in cands if not c[0]), cands[0])
                occurred, precision = pick[1], pick[2]
            for dm in T_DATE.finditer(sent):
                last_date = dm.group(1)
            etype = classify_event(sent, m['from_org_type'])
            if occurred is None:
                dm = T_DATE.search(sent)
                low = sent.lower()
                if dm and etype != 'other':
                    occurred, precision = dm.group(1), 'date'
                elif any(k in low for k in STATE_KEYWORDS):
                    occurred, precision = m['timestamp'], 'message_time (state change reported without its own time)'
                else:
                    continue
            if etype == 'other' and precision == 'date':
                continue
            refs = [r for r in norm.refs_in(sent) if r.startswith(SHIP_PREFIX) or r.startswith(('TG-', 'BP-', 'OS-'))]
            sid = next((r for r in refs if r.startswith(SHIP_PREFIX)), primary_ref if str(primary_ref).startswith(SHIP_PREFIX) else NA)
            loc = LOC_RE.search(sent)
            n += 1
            src = m['from_org_type']
            out.append({'event_id': f'{case_id}-E{n:02d}', 'case_id': case_id, 'shipment_id': sid, 'event_type': etype,
                        'location': loc.group(1).strip() if loc else NA, 'occurred_at': occurred, 'time_precision': precision,
                        'is_planned': 1 if occurred > m['timestamp'] else 0,
                        'source_system': ('customer statement' if src == 'customer' else m['from_raw']),
                        'source_message_id': m['message_id'], 'visible_at_escalation': m['visible_at_escalation'],
                        'text': sent, 'extraction': 'regex-sentence'})
    return out


def extract_evidence(case_id, primary_ref, messages, attachments):
    out, seen, n = [], set(), 0
    for a in attachments:
        n += 1
        ext = os.path.splitext(a['name'])[1].lower()
        out.append({'evidence_id': f'{case_id}-V{n:02d}', 'case_id': case_id, 'shipment_id': primary_ref if str(primary_ref).startswith(SHIP_PREFIX) else NA,
                    'evidence_type': 'image' if ext == '.png' else ('document' if ext == '.pdf' else 'file'), 'reference': a['name'],
                    'description': (a.get('text') or NA)[:400] or NA, 'source': 'attachment', 'file_name': a['name'],
                    'first_seen_message_id': f"{case_id}-M{a['first_event_id']}" if a.get('first_event_id') else NA,
                    'visible_at_escalation': 1 if a.get('visible_at_escalation') else 0})
        seen.add(a['name'])
    for m in messages:
        for sent in norm.sentences(m['body']):
            low = sent.lower()
            for ref in norm.refs_in(sent):
                pre = ref.split('-')[0]
                if ref in seen:
                    continue
                if pre in DOC_PREFIX or ref == 'DL032R':
                    etype = DOC_PREFIX.get(pre, 'return_token')
                    if pre == 'INV':
                        etype = 'invoice' if 'invoice' in low else 'investigation_reference'
                    seen.add(ref); n += 1
                    out.append({'evidence_id': f'{case_id}-V{n:02d}', 'case_id': case_id, 'shipment_id': primary_ref if str(primary_ref).startswith(SHIP_PREFIX) else NA,
                                'evidence_type': etype, 'reference': ref, 'description': sent, 'source': m['from_raw'],
                                'file_name': NA, 'first_seen_message_id': m['message_id'], 'visible_at_escalation': m['visible_at_escalation']})
            if m['from_org_type'] != 'desk' and ('inline' in low or 'logger' in low or '°c' in low) and sent not in seen:
                seen.add(sent); n += 1
                out.append({'evidence_id': f'{case_id}-V{n:02d}', 'case_id': case_id, 'shipment_id': primary_ref if str(primary_ref).startswith(SHIP_PREFIX) else NA,
                            'evidence_type': 'temperature_reading' if ('°c' in low or 'logger' in low) else 'inline_record',
                            'reference': NA, 'description': sent, 'source': m['from_raw'], 'file_name': NA,
                            'first_seen_message_id': m['message_id'], 'visible_at_escalation': m['visible_at_escalation']})
    return out


CHANNEL_CLASS = {'Customer portal': 'Portal', 'Business portal': 'Portal', 'Freight portal': 'Portal', 'Broker portal': 'Portal',
                 'Pickup-point portal': 'Portal', 'Email': 'Email', 'Call transcript': 'Phone', 'Dispatch chat': 'Driver app / dispatch chat',
                 'Depot work queue': 'Work queue', 'Warehouse work queue': 'Work queue', 'Safety incident queue': 'Work queue',
                 'Note': 'Internal note', 'System': 'API', 'API log': 'API'}
RAISED_BY = {'consumer': 'Customer', 'business_counterparty': 'Business customer (shipper or consignee)', 'carrier_ops': 'Carrier',
             'merchant_ops': 'Merchant', 'customs_broker': 'Customs broker'}
OWNER_GROUP = {'customer_self': 'Customer (their move)', 'counterparty_business': 'Business counterparty', 'dispatch_scheduling': 'Carrier operations',
               'routing_redirect': 'Carrier operations', 'freight_planning': 'Carrier operations', 'recovery_collection': 'Carrier operations',
               'support_records': 'Carrier operations', 'pickup_point_operator': 'Pickup point', 'depot_physical': 'Depot', 'trace': 'Depot / trace',
               'investigation_review': 'Carrier investigations', 'safety': 'Safety', 'merchant_authorisation': 'Merchant', 'merchant_fulfilment': 'Merchant',
               'warehouse_execution': 'Merchant warehouse', 'billing': 'Billing'}
ORG_RAISED = {'customer': 'Customer', 'business_counterparty': 'Business customer (shipper or consignee)', 'carrier': 'Carrier', 'merchant': 'Merchant',
              'customs_broker': 'Customs broker', 'international_carrier': 'Carrier (international)', 'pickup_point': 'Pickup point', 'desk': 'Desk', 'unknown': NA}


def linked_type(ref):
    if not ref or ref == NA:
        return NA
    p = ref.split('-')[0]
    return {'DL': 'shipment', 'TG': 'order', 'BP': 'order', 'OS': 'order', 'RT': 'return shipment', 'MD': 'task record', 'OF': 'task record', 'KL': 'task record'}.get(p, 'reference')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', required=True)
    ap.add_argument('--facts', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--stress', default=None, help='raw parser output for unlabelled cases (loaded with N/A labels)')
    ap.add_argument('--stress-labels', default=None, help='CSV with complexity_level, complexity_name, stress_theme per stress case')
    ap.add_argument('--extra-cases', default=None, help='a second normalized cases.jsonl (e.g. the synthetic set)')
    ap.add_argument('--extra-facts', default=None, help='facts module for the extra set')
    ap.add_argument('--extra-source-set', default='synthetic_new')
    ap.add_argument('--schema-out', default=None)
    ap.add_argument('--recon-out', default=None)
    args = ap.parse_args()
    facts = load_module(args.facts, 'facts').CASE_FACTS
    if args.extra_facts and os.path.exists(args.extra_facts):
        facts = {**facts, **load_module(args.extra_facts, 'facts_extra').CASE_FACTS}
    import csv as _csv
    stress_labels = {}
    if args.stress_labels and os.path.exists(args.stress_labels):
        stress_labels = {r['case_id']: r for r in _csv.DictReader(open(args.stress_labels, encoding='utf-8'))}

    actors, actor_ids = {}, {}

    def actor_id(a):
        raw = a['raw'] if isinstance(a, dict) else str(a)
        if raw not in actor_ids:
            aid = f'A{len(actor_ids) + 1:03d}'
            actor_ids[raw] = aid
            actors[aid] = {'actor_id': aid, 'name': raw, 'party': na(a.get('party') if isinstance(a, dict) else raw),
                           'org': na(a.get('org') if isinstance(a, dict) else None), 'org_type': na(a.get('org_type') if isinstance(a, dict) else 'unknown'),
                           'role': na(a.get('role') if isinstance(a, dict) else None), 'is_person': 1 if (isinstance(a, dict) and a.get('is_person')) else 0}
        return actor_ids[raw]

    rows = defaultdict(list)

    # ---------- labelled delivery cases (public, plus an optional extra labelled set) ----------
    labelled_inputs = [(args.cases, 'public')] + ([(args.extra_cases, args.extra_source_set)] if args.extra_cases and os.path.exists(args.extra_cases) else [])
    for src_path, src_set in labelled_inputs:
      for line in open(src_path, encoding='utf-8'):
          r = json.loads(line)
          cid = r['case_id']; p = r['at_escalation']['params']; d = r['decision']; m = r['meta']; f = facts[cid]
          primary = m['primary_ref']
          msgs = []
          for e in r['events']:
              mid = f"{cid}-M{e['event_id']}"
              msgs.append({'message_id': mid, 'case_id': cid, 'seq': e['seq'], 'timestamp': e['timestamp'], 'stage': e['stage'], 'channel': na(e['channel']),
                           'from_actor_id': actor_id(e['from']), 'from_raw': e['from']['raw'], 'from_org_type': e['from']['org_type'],
                           'to_actor_ids': '|'.join(actor_id(t) for t in e['to']) or NA, 'direction': e['direction'],
                           'visible_at_escalation': 1 if e['visible_at_escalation'] else 0, 'body': e['body'],
                           'refs': na(e['refs']), 'amounts_gbp': na(e['amounts_gbp'])})
          rows['messages'] += msgs
          rows['events'] += extract_events(cid, primary, msgs)
          rows['evidence'] += extract_evidence(cid, primary, msgs, r['attachments'])
          # orders / shipments / parcels from the hand-curated facts
          if f['order_id'] != NA:
              rows['orders'].append({'order_id': f['order_id'], 'merchant_id': f['merchant_id'], 'customer_id': f['customer_id'],
                                     'order_status': f['order_status'], 'case_id': cid, 'note': 'hand-curated from the case text'})
          for s in f['shipments']:
              rows['shipments'].append({**s, 'case_id': cid, 'order_id': f['order_id']})
          for pc in f['parcels']:
              rows['parcels'].append({**pc, 'case_id': cid})
          # case
          req = r['parties']['requester']; rec = d['recipient']
          gold_msg = next((x for x in msgs if x['stage'] == 'agent_action'), None)
          later = [x for x in msgs if gold_msg and x['seq'] > gold_msg['seq'] and x['from_org_type'] != 'desk']
          if rec.get('org_type') == 'customer':
              confirm = next((x for x in later if x['from_org_type'] == 'customer'), None)
          else:
              confirm = next((x for x in later if x['from_org_type'] != 'customer'), None) or (later[0] if later else None)
          rows['cases'].append({
              'case_id': cid, 'source_set': src_set, 'labelled': 1, 'title': r['title'],
              'created_at': na(m['created']), 'escalated_at': na(m['escalated']), 'updated_at': na(m['updated']), 'completed_at': na(m['completed']),
              'case_type': p['issue_type'], 'case_category': ('exception' if p['requester_type'] in ('carrier_ops', 'merchant_ops', 'customs_broker') or p['issue_type'] in ('service_disruption', 'safety_hazard') else ('dispute' if p['evidence_conflict'] else ('investigation' if d['queue'] == 'investigations' else 'request'))),
              'raised_by': req['raw'], 'raised_by_type': ('Depot' if 'depot' in req['raw'].lower() else RAISED_BY.get(p['requester_type'], NA)), 'raised_by_actor_id': actor_id(req),
              'channel': na(r['at_escalation']['escalation_channel']), 'channel_class': CHANNEL_CLASS.get(r['at_escalation']['escalation_channel'], NA),
              'linked_object_id': na(primary), 'linked_object_type': linked_type(primary),
              'request_or_claim': r['at_escalation']['initial_request'], 'requested_action_by_raiser': f['requested_action'],
              'recorded_next_action': na(d['next_action_text']), 'recorded_action_message_id': f"{cid}-M{d['recorded_action_event']}" if d['recorded_action_event'] else NA,
              'case_state_at_escalation': {'awaiting_customer': 'waiting', 'awaiting_counterparty': 'waiting', 'investigations': 'investigating'}.get(d['queue'], 'open'),
              'case_state_final': 'resolved (coordination task only)', 'operational_effect': f['operational_effect'],
              'priority': NA, 'urgency': p['urgency'], 'cutoff_utc': na(p['cutoff_utc']), 'deadline': f['deadline'],
              'owner': na(d['recipient_raw']), 'owner_group': OWNER_GROUP.get(d['recipient_function'], NA), 'owner_function': d['recipient_function'], 'owner_actor_id': actor_id(rec) if rec.get('raw') else NA,
              'gold_channel': na(d['channel']), 'action_class': d['action_class'], 'proof_standard': d['proof_standard'], 'queue': d['queue'], 'human_gate': d['human_gate'],
              'resolution': na(r['disclosed_after_escalation']['outcome']), 'boundaries': na(r['disclosed_after_escalation']['boundaries']),
              'context_summary': na(r['disclosed_after_escalation']['context_summary']), 'grading_reference': 'see recorded_next_action and boundaries',
              'segment': p['segment'], 'requester_type': p['requester_type'], 'shipment_stage': p['shipment_stage'], 'owner_org_type': p['owner_org_type'],
              'customer_input_required': 1 if p['customer_input_required'] else 0, 'risk_flags': na(p['risk_flags']), 'money_involved': 1 if p['money_involved'] else 0,
              'amount_gbp_known': na(p['amount_gbp_known']), 'verification_state': p['verification_state'], 'evidence_conflict': 1 if p['evidence_conflict'] else 0,
              'refs_at_escalation': na(r['at_escalation']['refs']), 'n_messages': len(msgs), 'source_dir': m.get('source_dir', NA),
              'complexity_level': na(p.get('complexity_level')), 'complexity_name': na(p.get('complexity_name')), 'stress_theme': NA, 'label_source': ('recorded_action (event 003) + hand labels' if src_set == 'public' else 'generation recipe (gold by construction)')})
          if gold_msg:
              rows['tasks'].append({'task_id': f'{cid}-T01', 'case_id': cid, 'task_type': d['action_class'], 'description': gold_msg['body'],
                                    'assignee': na(d['recipient_raw']), 'assignee_org_type': na(rec.get('org_type')), 'channel': na(gold_msg['channel']),
                                    'created_at': gold_msg['timestamp'], 'completed_at': confirm['timestamp'] if confirm else NA,
                                    'status': 'confirmed' if confirm else 'open', 'source_message_id': gold_msg['message_id'], 'is_gold_action': 1,
                                    'confirmation_message_id': confirm['message_id'] if confirm else NA})
          for role, a in (('requester', req), ('agent', r['parties']['agent']), ('context_author', r['parties']['context_author']), ('recipient', rec)):
              if a and a.get('raw'):
                  rows['case_actors'].append({'case_id': cid, 'actor_id': actor_id(a), 'role_in_case': role})
          for a in r['parties']['actors']:
              rows['case_actors'].append({'case_id': cid, 'actor_id': actor_id(a), 'role_in_case': 'participant'})

    # ---------- unlabelled stress cases (raw parser output) ----------
    n_stress = 0
    if args.stress and os.path.exists(args.stress):
        for line in open(args.stress, encoding='utf-8'):
            r = json.loads(line); cid = r['case_id']; n_stress += 1
            det = r['details']; primary = det.get('Primary shipment') or det.get('Primary task reference') or NA
            evs = r['events']
            first_desk = next((i for i, e in enumerate(evs) if 'Rivet Delivery Desk' in e['meta'].get('From', '')), None)
            msgs = []
            for i, e in enumerate(evs):
                frm = norm.parse_actor(e['meta'].get('From', '')); tos = norm.parse_actors(e['meta'].get('To', ''))
                if first_desk is None:
                    stage = 'context' if i == 0 else 'escalation'
                elif i < first_desk:
                    stage = 'context' if i == 0 else 'escalation'
                elif i == first_desk:
                    stage = 'agent_action'
                else:
                    stage = 'agent_followup' if frm['org_type'] == 'desk' else 'follow_through'
                visible = first_desk is None or i < first_desk
                mid = f"{cid}-M{e['event_id']}"
                msgs.append({'message_id': mid, 'case_id': cid, 'seq': e['seq'], 'timestamp': e['timestamp'], 'stage': stage, 'channel': na(e['meta'].get('Channel')),
                             'from_actor_id': actor_id(frm), 'from_raw': frm['raw'], 'from_org_type': frm['org_type'],
                             'to_actor_ids': '|'.join(actor_id(t) for t in tos) or NA,
                             'direction': 'outbound_from_desk' if frm['org_type'] == 'desk' else ('inbound_to_desk' if any(t['org_type'] == 'desk' for t in tos) else 'third_party'),
                             'visible_at_escalation': 1 if visible else 0, 'body': e['body'], 'refs': na(norm.refs_in(e['body'])),
                             'amounts_gbp': na([float(x) for x in norm.GBP_RE.findall(e['body'])])})
            rows['messages'] += msgs
            rows['events'] += extract_events(cid, primary, msgs)
            atts = []
            for a in r['attachments']:
                first = next((x['event_id'] for x in evs if any(l['href'].endswith(a['name']) for l in x['links']) or a['name'] in x['body']), None)
                atts.append({**a, 'first_event_id': first, 'visible_at_escalation': bool(first) and first_desk is not None and int(first) <= evs[first_desk]['seq'] - 1})
            rows['evidence'] += extract_evidence(cid, primary, msgs, atts)
            ref_path = os.path.join(r['source_dir'], '_reference.md')
            grading = open(ref_path, encoding='utf-8').read().strip() if os.path.exists(ref_path) else NA
            req = norm.parse_actor(det.get('Source role', ''))
            esc = next((x for x in msgs if x['stage'] == 'escalation'), msgs[0] if msgs else None)
            gold = msgs[first_desk] if first_desk is not None else None
            rows['shipments'].append({'shipment_id': primary, 'case_id': cid, 'order_id': NA, 'carrier_id': 'Plover Arc Logistics' if any(x['from_org_type'] == 'carrier' for x in msgs) else NA,
                                      'kind': 'delivery', 'milestone_at_escalation': NA, 'milestone_final': NA, 'exception': NA, 'destination': NA, 'promised_at': NA,
                                      'model_gap': NA, 'shipper': NA, 'consignee': NA, 'note': 'stress case: no hand-curated facts'})
            rows['parcels'].append({'parcel_id': primary, 'shipment_id': primary, 'barcode': NA, 'parcel_status': NA, 'case_id': cid, 'note': 'stress case'})
            rows['cases'].append({
                'case_id': cid, 'source_set': 'stress', 'labelled': 0, 'title': na(r['title']),
                'created_at': msgs[0]['timestamp'] if msgs else NA, 'escalated_at': esc['timestamp'] if esc else NA, 'updated_at': msgs[-1]['timestamp'] if msgs else NA, 'completed_at': NA,
                'case_type': NA, 'case_category': NA, 'raised_by': na(det.get('Source role')), 'raised_by_type': ORG_RAISED.get(req['org_type'], NA), 'raised_by_actor_id': actor_id(req),
                'channel': esc['channel'] if esc else NA, 'channel_class': CHANNEL_CLASS.get(esc['channel'], NA) if esc else NA,
                'linked_object_id': na(primary), 'linked_object_type': linked_type(primary),
                'request_or_claim': na(r['sections'].get('Initial request')), 'requested_action_by_raiser': NA,
                'recorded_next_action': gold['body'] if gold else NA, 'recorded_action_message_id': gold['message_id'] if gold else NA,
                'case_state_at_escalation': 'open', 'case_state_final': NA, 'operational_effect': NA, 'priority': NA, 'urgency': NA, 'cutoff_utc': NA, 'deadline': NA,
                'owner': (actors[gold['to_actor_ids'].split('|')[0]]['name'] if gold and gold['to_actor_ids'] != NA else NA), 'owner_group': NA, 'owner_function': NA,
                'owner_actor_id': gold['to_actor_ids'].split('|')[0] if gold and gold['to_actor_ids'] != NA else NA,
                'gold_channel': gold['channel'] if gold else NA, 'action_class': NA, 'proof_standard': NA, 'queue': NA, 'human_gate': NA,
                'resolution': NA, 'boundaries': NA, 'context_summary': na(r['sections'].get('Context')), 'grading_reference': grading,
                'segment': NA, 'requester_type': NA, 'shipment_stage': NA, 'owner_org_type': NA, 'customer_input_required': NA, 'risk_flags': NA, 'money_involved': NA,
                'amount_gbp_known': NA, 'verification_state': NA, 'evidence_conflict': NA,
                'refs_at_escalation': na(sorted({x for mm in msgs if mm['visible_at_escalation'] for x in (mm['refs'].split('|') if mm['refs'] != NA else [])})),
                'n_messages': len(msgs), 'source_dir': r['source_dir'],
                'complexity_level': na(stress_labels.get(cid, {}).get('complexity_level')), 'complexity_name': na(stress_labels.get(cid, {}).get('complexity_name')),
                'stress_theme': na(stress_labels.get(cid, {}).get('stress_theme')), 'label_source': na(stress_labels.get(cid, {}).get('label_source'))})
            if gold:
                rows['tasks'].append({'task_id': f'{cid}-T01', 'case_id': cid, 'task_type': NA, 'description': gold['body'], 'assignee': rows['cases'][-1]['owner'],
                                      'assignee_org_type': actors[gold['to_actor_ids'].split('|')[0]]['org_type'] if gold['to_actor_ids'] != NA else NA,
                                      'channel': gold['channel'], 'created_at': gold['timestamp'], 'completed_at': NA, 'status': 'recorded', 'source_message_id': gold['message_id'],
                                      'is_gold_action': 1, 'confirmation_message_id': NA})
            rows['case_actors'].append({'case_id': cid, 'actor_id': actor_id(req), 'role_in_case': 'requester'})
            for mm in msgs:
                rows['case_actors'].append({'case_id': cid, 'actor_id': mm['from_actor_id'], 'role_in_case': 'participant'})

    # scan-type observations are evidence too (proof of delivery, receipt scans)
    for ev in rows['events']:
        if ev['event_type'] in ('scan', 'receipt_scan', 'delivery_handover', 'collection', 'failed_attempt') and ev['source_system'] != 'customer statement':
            rows['evidence'].append({'evidence_id': ev['event_id'].replace('-E', '-VS'), 'case_id': ev['case_id'], 'shipment_id': ev['shipment_id'],
                                     'evidence_type': 'scan_record', 'reference': ev['event_id'], 'description': ev['text'], 'source': ev['source_system'],
                                     'file_name': NA, 'first_seen_message_id': ev['source_message_id'], 'visible_at_escalation': ev['visible_at_escalation']})
    rows['actors'] = list(actors.values())
    # de-duplicate case_actors
    seen = set(); ca = []
    for x in rows['case_actors']:
        k = (x['case_id'], x['actor_id'], x['role_in_case'])
        if k not in seen:
            seen.add(k); ca.append(x)
    rows['case_actors'] = ca

    # ---------- reconciliation (Andrey's fields -> this database) ----------
    labelled = [c for c in rows['cases'] if c['labelled'] == 1 and c['source_set'] == 'public']
    lab_ids = {c['case_id'] for c in labelled}

    def cov(table, field, key='case_id'):
        """Number of the 50 public cases with at least one row whose field is not N/A."""
        if table == 'actors':
            good = {x['actor_id'] for x in rows['actors'] if str(x.get(field, NA)) not in (NA, '', 'None')}
            cases = {x['case_id'] for x in rows['case_actors'] if x['actor_id'] in good and x['case_id'] in lab_ids}
            return len(cases), len(lab_ids)
        cases = {x.get(key) for x in rows[table] if x.get(key) in lab_ids and str(x.get(field, NA)) not in (NA, '', 'None')}
        return len(cases), len(lab_ids)

    recon_spec = [
        ('ORDER', 'order_id', 'what the customer bought', 'merchant order references in the text: TG-, BP-, OS-', 'orders', 'order_id', 'N/A when the case only has a shipment reference (most consumer cases)', ''),
        ('ORDER', 'merchant_id', 'selling merchant', 'merchant team organisation or TG- prefix', 'orders', 'merchant_id', 'N/A when no merchant appears', 'TG- prefix inferred as Tallowmere Goods in DEL-020'),
        ('ORDER', 'customer_id', 'buyer', 'requester party; consignee organisation for business cases', 'orders', 'customer_id', 'N/A for internal cases', 'names, not ids: the data has no customer identifiers'),
        ('ORDER', 'order_status', 'order-level status', 'derived from outcome text', 'orders', 'order_status', 'N/A unless the case states an order-level fact', 'the draft asks for order status computed from parcel states; stored as text here'),
        ('SHIPMENT', 'shipment_id', 'transport movement reference', 'DL-, RT-, WP-, PA-, OF- references', 'shipments', 'shipment_id', 'always present', 'DL-044 is an implied consignment id for P1..P4'),
        ('SHIPMENT', 'order_id', 'link to the order', 'as ORDER.order_id', 'shipments', 'order_id', 'N/A when no order reference exists', ''),
        ('SHIPMENT', 'carrier_id', 'carrier', 'Plover Arc Logistics; Harbor Thread International for DL-048', 'shipments', 'carrier_id', 'always present', 'merchant-side returns are also carried by Plover'),
        ('SHIPMENT', 'shipment_status (milestone_at_escalation)', 'state-machine state', "draft's states, nearest fit", 'shipments', 'milestone_at_escalation', 'N/A for shipments created after escalation and for stress cases', 'see model_gap for pickup point, locker, customs, misdelivery, returns'),
        ('SHIPMENT', 'shipment_status (milestone_final)', 'state after the recorded follow-through', "draft's states, nearest fit", 'shipments', 'milestone_final', 'N/A for stress cases', ''),
        ('SHIPMENT', 'destination', 'delivery address or point', 'addresses and counters named in the text', 'shipments', 'destination', 'N/A when never stated (most cases)', 'the data has no postal addresses beyond a handful of streets'),
        ('SHIPMENT', 'promised_at', 'promised delivery time', 'booked windows, guarantees, appointments', 'shipments', 'promised_at', 'N/A when no window is stated', 'stored as the stated window text, not a single timestamp'),
        ('PARCEL', 'parcel_id', 'physical unit', 'sub-unit references (DL-020-A, DL-044-P4, DL-036-A) or 1:1 with the shipment', 'parcels', 'parcel_id', 'always present', ''),
        ('PARCEL', 'barcode', 'label barcode', 'not in the data', 'parcels', 'barcode', 'N/A always', 'no barcodes anywhere in the 50 cases'),
        ('PARCEL', 'parcel_status', 'unit status', 'text of the case', 'parcels', 'parcel_status', 'N/A for stress cases', ''),
        ('EVENT', 'event_id / shipment_id / event_type / location / occurred_at / source_system', 'append-only operational observation', 'sentences in message bodies carrying a time or date and an operational keyword (regex)', 'events', 'occurred_at', 'location N/A when no place is named; time precision column says whether the date came from the message', 'customer statements are kept but tagged source_system = customer statement'),
        ('CASE', 'case_id / case_type', 'request, dispute, exception or investigation', 'case id; issue_type label and derived case_category', 'cases', 'case_type', 'N/A for unlabelled stress cases', ''),
        ('CASE', 'raised_by', 'customer, merchant, carrier, depot, customs broker', 'Source role and requester_type', 'cases', 'raised_by_type', 'always present', ''),
        ('CASE', 'channel', 'portal, phone, email, driver app, API', 'escalation channel (event 002) mapped to channel_class', 'cases', 'channel_class', 'always present', 'work queues have no slot in the draft list; kept as Work queue'),
        ('CASE', 'linked_object', 'order, shipment, parcel, event', 'primary shipment or task reference', 'cases', 'linked_object_type', 'always present', 'MD-, OF-, KL- references are task records, not in the draft list'),
        ('CASE', 'request_or_claim', 'what is asked or disputed', 'Initial request', 'cases', 'request_or_claim', 'always present', ''),
        ('CASE', 'requested_action', 'the action the raiser wants', 'hand-written short phrase from events 001-002', 'cases', 'requested_action_by_raiser', 'N/A for stress cases', ''),
        ('CASE', 'case_state', 'open, waiting, investigating, resolved', 'queue label at escalation; index Status at the end', 'cases', 'case_state_at_escalation', 'final state N/A for stress cases', 'all 50 public cases end resolved for the coordination task only'),
        ('CASE', 'operational_effect', 'shipment hold, route block, refund review ...', 'hand-written from the outcome', 'cases', 'operational_effect', 'N/A for stress cases', ''),
        ('CASE', 'owner', 'support, depot, safety, customs, billing', 'gold recipient (owner) and owner_group', 'cases', 'owner_group', 'N/A for stress cases without a recorded action', ''),
        ('CASE', 'evidence', 'photo, scan, invoice, temperature log', 'evidence table', 'evidence', 'evidence_type', 'cases without evidence have no rows', ''),
        ('CASE', 'deadline', 'SLA or promised update', 'cutoff in events 001-002 or the next-update time a team gave', 'cases', 'deadline', 'N/A when no clock is stated', 'no SLA exists in the data'),
        ('CASE', 'resolution', 'address corrected, replacement approved ...', 'index Outcome', 'cases', 'resolution', 'N/A for stress cases', ''),
        ('CASE', 'priority', 'case priority', 'not in the data', 'cases', 'priority', 'N/A always', 'urgency label stored separately'),
        ('CASE', 'complexity level (draft section 6, easy-to-hard)', 'Level 1 simple status to 7 reconciliation across shipments', "hand-assigned per case from the draft's definitions; stress cases also carry Roman's stress theme", 'cases', 'complexity_level', 'always present', 'levels 1-7 cover 50/50 public cases; 4 stress cases map only loosely (fraud, noisy inbox, duplicate request, customer reversal)'),
        ('TASK', 'task', 'concrete action created by a case', 'the recorded agent action (event 003) with assignee, channel and confirming message', 'tasks', 'status', 'completed_at N/A when no confirming message exists', ''),
        ('ACTOR', 'actor', 'who raises cases and records events', 'every From/To label, canonicalized', 'actors', 'org_type', 'org N/A for people without an organisation', ''),
        ('DASHBOARD', 'Shipment, Order, Current milestone, Exception, Next action, Owner, ETA', 'shipment-level table', 'view v_shipment_dashboard', 'shipments', 'milestone_final', 'Order and ETA show N/A when unknown', ''),
    ]
    recon = []
    for ent, field, defi, src, table, col, pol, note in recon_spec:
        n, tot = cov(table, col)
        recon.append({'entity': ent, 'field': field, 'andrey_definition': defi, 'source_in_data': src, 'table_column': f'{table}.{col}',
                      'coverage_n': n, 'coverage_total': tot, 'coverage_pct': round(100 * n / tot, 1) if tot else 0.0, 'na_policy': pol, 'note': note or NA})
    rows['reconciliation'] = recon

    # ---------- write sqlite ----------
    if os.path.exists(args.out):
        os.remove(args.out)
    con = sqlite3.connect(args.out)
    cur = con.cursor()
    ddl = {
        'actors': 'CREATE TABLE actors (actor_id TEXT PRIMARY KEY, name TEXT NOT NULL, party TEXT NOT NULL, org TEXT NOT NULL, org_type TEXT NOT NULL, role TEXT NOT NULL, is_person INTEGER NOT NULL)',
        'orders': 'CREATE TABLE orders (order_id TEXT PRIMARY KEY, merchant_id TEXT NOT NULL, customer_id TEXT NOT NULL, order_status TEXT NOT NULL, case_id TEXT NOT NULL REFERENCES cases(case_id), note TEXT NOT NULL)',
        'shipments': 'CREATE TABLE shipments (shipment_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id), order_id TEXT NOT NULL, carrier_id TEXT NOT NULL, kind TEXT NOT NULL, milestone_at_escalation TEXT NOT NULL, milestone_final TEXT NOT NULL, exception TEXT NOT NULL, destination TEXT NOT NULL, promised_at TEXT NOT NULL, model_gap TEXT NOT NULL, shipper TEXT NOT NULL, consignee TEXT NOT NULL, note TEXT NOT NULL)',
        'parcels': 'CREATE TABLE parcels (parcel_id TEXT PRIMARY KEY, shipment_id TEXT NOT NULL REFERENCES shipments(shipment_id), barcode TEXT NOT NULL, parcel_status TEXT NOT NULL, case_id TEXT NOT NULL REFERENCES cases(case_id), note TEXT NOT NULL)',
        'events': 'CREATE TABLE events (event_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id), shipment_id TEXT NOT NULL, event_type TEXT NOT NULL, location TEXT NOT NULL, occurred_at TEXT NOT NULL, time_precision TEXT NOT NULL, is_planned INTEGER NOT NULL, source_system TEXT NOT NULL, source_message_id TEXT NOT NULL REFERENCES messages(message_id), visible_at_escalation INTEGER NOT NULL, text TEXT NOT NULL, extraction TEXT NOT NULL)',
        'cases': 'CREATE TABLE cases (case_id TEXT PRIMARY KEY, source_set TEXT NOT NULL, labelled INTEGER NOT NULL, title TEXT NOT NULL, created_at TEXT NOT NULL, escalated_at TEXT NOT NULL, updated_at TEXT NOT NULL, completed_at TEXT NOT NULL, case_type TEXT NOT NULL, case_category TEXT NOT NULL, raised_by TEXT NOT NULL, raised_by_type TEXT NOT NULL, raised_by_actor_id TEXT NOT NULL, channel TEXT NOT NULL, channel_class TEXT NOT NULL, linked_object_id TEXT NOT NULL, linked_object_type TEXT NOT NULL, request_or_claim TEXT NOT NULL, requested_action_by_raiser TEXT NOT NULL, recorded_next_action TEXT NOT NULL, recorded_action_message_id TEXT NOT NULL, case_state_at_escalation TEXT NOT NULL, case_state_final TEXT NOT NULL, operational_effect TEXT NOT NULL, priority TEXT NOT NULL, urgency TEXT NOT NULL, cutoff_utc TEXT NOT NULL, deadline TEXT NOT NULL, owner TEXT NOT NULL, owner_group TEXT NOT NULL, owner_function TEXT NOT NULL, owner_actor_id TEXT NOT NULL, gold_channel TEXT NOT NULL, action_class TEXT NOT NULL, proof_standard TEXT NOT NULL, queue TEXT NOT NULL, human_gate TEXT NOT NULL, resolution TEXT NOT NULL, boundaries TEXT NOT NULL, context_summary TEXT NOT NULL, grading_reference TEXT NOT NULL, segment TEXT NOT NULL, requester_type TEXT NOT NULL, shipment_stage TEXT NOT NULL, owner_org_type TEXT NOT NULL, customer_input_required TEXT NOT NULL, risk_flags TEXT NOT NULL, money_involved TEXT NOT NULL, amount_gbp_known TEXT NOT NULL, verification_state TEXT NOT NULL, evidence_conflict TEXT NOT NULL, refs_at_escalation TEXT NOT NULL, n_messages INTEGER NOT NULL, source_dir TEXT NOT NULL, complexity_level TEXT NOT NULL, complexity_name TEXT NOT NULL, stress_theme TEXT NOT NULL, label_source TEXT NOT NULL)',
        'tasks': 'CREATE TABLE tasks (task_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id), task_type TEXT NOT NULL, description TEXT NOT NULL, assignee TEXT NOT NULL, assignee_org_type TEXT NOT NULL, channel TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT NOT NULL, status TEXT NOT NULL, source_message_id TEXT NOT NULL, is_gold_action INTEGER NOT NULL, confirmation_message_id TEXT NOT NULL)',
        'evidence': 'CREATE TABLE evidence (evidence_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id), shipment_id TEXT NOT NULL, evidence_type TEXT NOT NULL, reference TEXT NOT NULL, description TEXT NOT NULL, source TEXT NOT NULL, file_name TEXT NOT NULL, first_seen_message_id TEXT NOT NULL, visible_at_escalation INTEGER NOT NULL)',
        'messages': 'CREATE TABLE messages (message_id TEXT PRIMARY KEY, case_id TEXT NOT NULL REFERENCES cases(case_id), seq INTEGER NOT NULL, timestamp TEXT NOT NULL, stage TEXT NOT NULL, channel TEXT NOT NULL, from_actor_id TEXT NOT NULL REFERENCES actors(actor_id), from_raw TEXT NOT NULL, from_org_type TEXT NOT NULL, to_actor_ids TEXT NOT NULL, direction TEXT NOT NULL, visible_at_escalation INTEGER NOT NULL, body TEXT NOT NULL, refs TEXT NOT NULL, amounts_gbp TEXT NOT NULL)',
        'case_actors': 'CREATE TABLE case_actors (case_id TEXT NOT NULL REFERENCES cases(case_id), actor_id TEXT NOT NULL REFERENCES actors(actor_id), role_in_case TEXT NOT NULL, PRIMARY KEY (case_id, actor_id, role_in_case))',
        'reconciliation': 'CREATE TABLE reconciliation (entity TEXT NOT NULL, field TEXT NOT NULL, andrey_definition TEXT NOT NULL, source_in_data TEXT NOT NULL, table_column TEXT NOT NULL, coverage_n INTEGER NOT NULL, coverage_total INTEGER NOT NULL, coverage_pct REAL NOT NULL, na_policy TEXT NOT NULL, note TEXT NOT NULL)',
    }
    for t in ('actors', 'cases', 'orders', 'shipments', 'parcels', 'messages', 'events', 'tasks', 'evidence', 'case_actors', 'reconciliation'):
        cur.execute(ddl[t])
        cols = re.findall(r'\(?\b([a-z_]+) (?:TEXT|INTEGER|REAL)', ddl[t])
        for x in rows[t]:
            vals = [na(x.get(c)) if not isinstance(x.get(c), (int, float)) or isinstance(x.get(c), bool) else x.get(c) for c in cols]
            vals = [(v if v is not None else NA) for v in vals]
            cur.execute(f"INSERT INTO {t} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", vals)
    cur.executescript('''
CREATE INDEX idx_messages_case ON messages(case_id, seq);
CREATE INDEX idx_events_case ON events(case_id, occurred_at);
CREATE INDEX idx_shipments_case ON shipments(case_id);
CREATE VIEW v_shipment_dashboard AS
SELECT s.shipment_id AS shipment_id, s.shipment_id AS shipment, s.order_id AS "order",
       s.milestone_final AS current_milestone, s.milestone_at_escalation AS milestone_at_escalation, s.exception AS exception,
       CASE WHEN s.milestone_final IN ('Delivered', 'Collected', 'Lost') THEN 'none recorded (case closed)' ELSE c.recorded_next_action END AS next_action,
       c.recorded_next_action AS next_action_at_escalation,
       CASE WHEN s.milestone_final IN ('Delivered', 'Collected', 'Lost') THEN 'N/A' ELSE c.owner_group END AS owner,
       c.owner_group AS owner_at_escalation, c.owner AS owner_team_at_escalation,
       CASE WHEN s.milestone_final IN ('Delivered', 'Collected', 'Lost') THEN 'N/A (completed)' ELSE s.promised_at END AS eta,
       s.promised_at AS promised_window, c.case_state_final AS case_state, s.case_id AS case_id, c.queue AS queue, c.human_gate AS human_gate, c.deadline AS deadline,
       c.complexity_level AS complexity_level, c.complexity_name AS complexity_name, c.stress_theme AS stress_theme
FROM shipments s LEFT JOIN cases c ON c.case_id = s.case_id;
CREATE VIEW v_case_timeline AS
SELECT case_id, timestamp AS at, 'message' AS kind, message_id AS id, stage AS type, from_raw AS source, body AS text, visible_at_escalation FROM messages
UNION ALL
SELECT case_id, occurred_at AS at, 'event' AS kind, event_id AS id, event_type AS type, source_system AS source, text, visible_at_escalation FROM events
ORDER BY case_id, at;
CREATE VIEW v_decision_input AS
SELECT c.case_id, c.title, c.raised_by, c.channel, c.linked_object_id, c.request_or_claim,
       m.seq, m.timestamp, m.channel AS message_channel, m.from_raw, m.body
FROM cases c JOIN messages m ON m.case_id = c.case_id WHERE m.visible_at_escalation = 1;
''')
    con.commit()
    counts = {t: cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in ddl}
    if args.schema_out:
        with open(args.schema_out, 'w', encoding='utf-8') as fh:
            fh.write('-- Delivery database schema (generated by build_db.py). Policy: unknown values are the string N/A, never NULL.\n')
            for (sql,) in cur.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type DESC, name"):
                fh.write(sql + ';\n\n')
    if args.recon_out:
        with open(args.recon_out, 'w', encoding='utf-8') as fh:
            fh.write(RECON_PREAMBLE)
            fh.write('| Entity | Field (draft) | Draft meaning | Source in the cases | Table.column | Cases with a value (of 50) | N/A policy | Note |\n|---|---|---|---|---|---|---|---|\n')
            for x in recon:
                fh.write(f"| {x['entity']} | {x['field']} | {x['andrey_definition']} | {x['source_in_data']} | `{x['table_column']}` | {x['coverage_n']}/{x['coverage_total']} ({x['coverage_pct']}%) | {x['na_policy']} | {x['note']} |\n")
            fh.write(RECON_POSTAMBLE.format(**counts, n_stress=n_stress))
    con.close()
    print(json.dumps({'db': args.out, 'counts': counts, 'stress_cases': n_stress}, indent=1))


RECON_PREAMBLE = '''# Reconciliation: Andrey's delivery system model vs the normalized data

Source model: `user/andrey/drafts/delivery-system-model.md` (commit dc42265 on origin/main). Database: `data/delivery/database/delivery.sqlite`, built by `data/pipeline/build_db.py` from `agent/cases.jsonl`, the hand-curated `facts_delivery.py` and the stress cases on origin/main. Rule applied throughout: a value the cases never state is stored as the literal string `N/A`; nothing from the draft is dropped.

## Entity by entity

- **Order, Shipment, Parcel** come from the case text, hand-curated per case (`facts_delivery.py`). Most consumer cases have only a shipment reference, so `order_id` is N/A there; merchant orders (TG-, BP-, OS-) exist in 14 cases. Shipments carry two state-machine columns: `milestone_at_escalation` (what the agent could know) and `milestone_final` (after the recorded follow-through). Where the draft has no state for the situation (pickup point, locker, customs hold, misdelivery, return legs) the nearest state is used and `model_gap` says so.
- **Event** in the draft is an append-only operational observation (scan, handover, failed attempt, receipt). The case files contain no event feed; observations are embedded in message bodies. The `events` table extracts them sentence by sentence (time or date plus an operational keyword), keeps the source message and its visibility, and tags customer statements as `source_system = customer statement` so that, as the draft requires, a customer statement is never a carrier event.
- **Case** carries every field of the draft's case table (raised by, channel, linked object, request or claim, requested action, state, operational effect, owner, evidence, deadline, resolution) plus the 24 decision parameters. `priority` is N/A for all cases: the data has none; `urgency` is the labelled substitute.
- **Task** is the recorded agent action (event 003) with its assignee, channel and the message that confirmed it. **Evidence** holds the six attachments and every documentary reference (receipts, labels, invoices, credit notes, mandates, inline records, the temperature reading).
- **Messages** are the 228 communications of the public cases plus those of the 20 stress cases; `visible_at_escalation` reproduces the agent-facing cut (`v_decision_input`).
- **Dashboard** (`v_shipment_dashboard`) projects Shipment, Order, Current milestone, Exception, Next action, Owner and ETA exactly as the draft sketches; Order and ETA read N/A when unknown.

## Field table

'''

RECON_POSTAMBLE = '''
## Row counts

cases {cases} (public labelled 50, stress unlabelled {n_stress}) · orders {orders} · shipments {shipments} · parcels {parcels} · events {events} · messages {messages} · tasks {tasks} · evidence {evidence} · actors {actors} · case_actors {case_actors}

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
'''

if __name__ == '__main__':
    main()
