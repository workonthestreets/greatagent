#!/usr/bin/env python3
"""TEST FIXTURE BUILDER -- NOT the real pipeline output.

Emits schema-shaped, deliberately minimal records from the raw "Delivery & Logistics" cases so
validate_cases.py can be exercised before data/delivery/ exists. Routing labels (action_class,
queue, org_type, ...) are crude placeholders, not gold labels. Every record carries
"_fixture": "TEST FIXTURE - not real pipeline output".

Usage:
    python3 -I build_fixture.py "<Delivery & Logistics dir>" <out_dir>
Writes <out_dir>/cases.fixture.jsonl, events.fixture.jsonl, decision_points.fixture.jsonl.
"""
import json
import os
import re
import sys

MARK = 'TEST FIXTURE - not real pipeline output'
SEC = re.compile(r'^##\s+(.+?)\s*$', re.M)
BUL = re.compile(r'^-\s+\*\*(.+?):\*\*\s*(.*)$', re.M)
EVT = re.compile(r'<a id="event-(\d+)"></a>\s*\n##\s+(\S+) (\S+) UTC\s+—\s+event\s+\d+\s*\n(.*?)(?=\n<a id="event-|\Z)', re.S)
LINK = re.compile(r'\[[^\]]+\]\(attachments/([^)]+)\)')
STAGES = {'Context': 'context', 'Escalation': 'escalation', 'Agent action': 'agent_action',
          'Follow-through / confirmation': 'follow_through'}
REF = re.compile(r'\b[A-Z]{2,5}(?:-[A-Z0-9]+)+\b')
GBP = re.compile(r'GBP\s?(\d[\d,]*(?:\.\d+)?)')
DATE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
WIN = re.compile(r'\b\d{2}:\d{2}–\d{2}:\d{2}\b')


def iso(s):  # "2026-02-02 09:00:00 UTC" -> "2026-02-02T09:00:00Z"
    d, t = s.replace(' UTC', '').split(' ')
    return f'{d}T{t}Z'


def actor(raw):
    low = raw.lower()
    org = ('desk' if 'delivery desk' in low else 'customer' if 'recipient' in low or 'customer' in low
           else 'customs_broker' if 'broker' in low else 'unknown')
    return {'raw': raw, 'org_type': org}


def uniq(xs):
    return list(dict.fromkeys(xs))


def build_case(cdir, num):
    idx = open(os.path.join(cdir, 'index.md'), encoding='utf-8').read()
    parts = SEC.split(idx)
    secs = {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts), 2)}
    det = {k.strip(): v.strip() for k, v in BUL.findall(secs['Case details'])}
    na = next(v for k, v in secs.items() if k.startswith('Next action'))
    nab = {k.strip(): v.strip() for k, v in BUL.findall(na)}
    hist = open(os.path.join(cdir, 'history.md'), encoding='utf-8').read()
    cid = f'DEL-{num}'
    events = []
    for eid, d, t, rest in EVT.findall(hist):
        m = {k.strip(): v.strip() for k, v in BUL.findall(rest)}
        events.append({'event_id': eid, 'seq': int(eid), 'timestamp': f'{d}T{t}Z',
                       'stage': STAGES[m['Stage']], 'channel': m['Channel'], 'from': actor(m['From']),
                       'to': [actor(x.strip()) for x in m['To'].split(';')],
                       'visible_at_escalation': int(eid) <= 2, 'body': BUL.sub('', rest).strip()})
    visible = [e for e in events if e['seq'] <= 2]
    vis_text = '\n'.join([secs['Initial request']] + [e['body'] for e in visible])
    first = {}
    for e in events:
        for name in LINK.findall(e['body']):
            first.setdefault(name, e['event_id'])
    listed = re.findall(r'\(attachments/([^)]+)\)', secs['Attachments'])
    to_customer = 'recipient' in nab['Recipient'].lower() or 'customer' in nab['Recipient'].lower()
    ref_key = 'Primary shipment' if 'Primary shipment' in det else 'Primary task reference'
    rec = {
        '_fixture': MARK, 'case_id': cid, 'track': 'Delivery & Logistics', 'title': idx.splitlines()[0][2:],
        'meta': {'created': iso(det['Created']), 'escalated': iso(det['Escalated']),
                 'updated': iso(det['Updated']), 'completed': iso(det['Completed']), 'status': det['Status'],
                 'primary_ref': det[ref_key],
                 'primary_ref_kind': 'shipment' if ref_key == 'Primary shipment' else 'task',
                 'coordinator': det['Coordinator'], 'n_events': len(events)},
        'parties': {'requester': actor(det['Source role'])},
        'at_escalation': {
            'initial_request': secs['Initial request'],
            'visible_event_ids': [e['event_id'] for e in visible],
            'refs': uniq(REF.findall(vis_text)),
            'amounts_gbp': uniq(float(a.replace(',', '')) for a in GBP.findall(vis_text)),
            'dates_mentioned': uniq(DATE.findall(vis_text)),
            'time_windows': uniq(WIN.findall(vis_text)),
            'params': {},
        },
        'decision': {'recipient_raw': nab['Recipient'], 'recipient': actor(nab['Recipient']),
                     'channel': nab['Channel'],
                     'action_class': 'ask_customer' if to_customer else 'request_operator_action',
                     'message': next(e['body'] for e in events if e['seq'] == 3),
                     'queue': 'awaiting_customer' if to_customer else 'carrier_ops'},
        'disclosed_after_escalation': {
            'context_summary': secs['Context'], 'outcome': secs['Outcome'],
            'boundaries': secs['Boundaries and remaining work'],
            'follow_through_event_ids': [e['event_id'] for e in events if e['seq'] >= 4]},
        'events': events,
        'attachments': [{'name': n, 'href': f'attachments/{n}', 'first_event_id': first.get(n),
                         'visible_at_escalation': first.get(n) in ('001', '002')} for n in listed],
    }
    dp = {'_fixture': MARK, 'case_id': cid,
          'input': {'initial_request': secs['Initial request'], 'case_details': {
              k: v for k, v in det.items() if k not in ('Status', 'Updated', 'Completed')},
              'events': [{k: e[k] for k in ('event_id', 'seq', 'timestamp', 'channel', 'body')}
                         for e in visible]},
          'attachments_available': [a['name'] for a in rec['attachments'] if a['visible_at_escalation']]}
    ev_rows = [dict({'_fixture': MARK, 'case_id': cid}, **e) for e in events]
    return rec, ev_rows, dp


def main():
    raw, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    files = {k: open(os.path.join(out, f'{k}.fixture.jsonl'), 'w', encoding='utf-8')
             for k in ('cases', 'events', 'decision_points')}
    n = 0
    for num in sorted(x for x in os.listdir(raw) if re.fullmatch(r'\d{3}', x)):
        rec, evs, dp = build_case(os.path.join(raw, num), num)
        files['cases'].write(json.dumps(rec, ensure_ascii=False) + '\n')
        for e in evs:
            files['events'].write(json.dumps(e, ensure_ascii=False) + '\n')
        files['decision_points'].write(json.dumps(dp, ensure_ascii=False) + '\n')
        n += 1
    for f in files.values():
        f.close()
    print(f'[fixture] {n} cases -> {out} ({MARK})', file=sys.stderr)


if __name__ == '__main__':
    main()
