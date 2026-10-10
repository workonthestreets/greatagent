#!/usr/bin/env python3
"""Validate written synthetic cases against their recipes and install them into the repo.

Usage: python3 -I synth_integrate.py <recipes.jsonl> <written_dir> <dest_dir> [--report report.json]
<written_dir>/<NNN>/{index.md,history.md} (from the writer agents) -> <dest_dir>/<NNN>/{index.md,history.md,_labels.json}
Checks: both files exist; index sections; Case details keys; Data line marks the set as synthetic; history parses; Stage tags;
event count equals the Total line and the recipe; event 002 From == recipe requester; event 003 From is the desk, To == gold recipient,
Channel == gold channel; timestamps monotonic; primary reference present in events 001-002; no outcome text before the cutoff.
Cases failing a hard check are reported and NOT installed (fix or regenerate them).
"""
import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_cases import parse_index, parse_history  # noqa: E402

REQUIRED_SECTIONS = ['Case details', 'Context', 'Initial request', 'Overview', 'Next action at escalation', 'Outcome', 'Boundaries and remaining work', 'History', 'Attachments']
REQUIRED_DETAILS = ['Source role', 'Status', 'Created', 'Escalated', 'Updated', 'Completed', 'Coordinator', 'Data']


def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())


def check_case(r, folder):
    hard, soft = [], []
    ip, hp = os.path.join(folder, 'index.md'), os.path.join(folder, 'history.md')
    if not (os.path.exists(ip) and os.path.exists(hp)):
        return ['missing index.md or history.md'], soft, None, None
    idx, hist = parse_index(ip), parse_history(hp)
    for s in REQUIRED_SECTIONS:
        if s not in idx['sections'] and s != 'Case details':
            hard.append(f'missing section {s}')
    for k in REQUIRED_DETAILS:
        if k not in idx['details']:
            hard.append(f'missing detail {k}')
    if 'synthetic new' not in idx['details'].get('Data', '').lower():
        hard.append('Data line does not mark the case as Synthetic new')
    if not any(k in idx['details'] for k in ('Primary shipment', 'Primary task reference')):
        hard.append('no Primary shipment / Primary task reference')
    evs = hist['events']
    if hist['total_events_declared'] != len(evs):
        hard.append(f"Total events {hist['total_events_declared']} != parsed {len(evs)}")
    if len(evs) != r['n_events']:
        soft.append(f"event count {len(evs)} != recipe {r['n_events']}")
    if len(evs) < 3:
        hard.append('fewer than 3 events'); return hard, soft, idx, hist
    stages = [e['meta'].get('Stage', '') for e in evs]
    if stages[0] != 'Context' or stages[1] != 'Escalation' or stages[2] != 'Agent action' or any(s != 'Follow-through / confirmation' for s in stages[3:]):
        hard.append(f'stage sequence wrong: {stages}')
    if norm(evs[1]['meta'].get('From')) != norm(r['requester_raw']):
        soft.append(f"event 002 From '{evs[1]['meta'].get('From')}' != requester '{r['requester_raw']}'")
    if 'rivet delivery desk' not in norm(evs[2]['meta'].get('From')):
        hard.append('event 003 is not from the desk')
    if norm(r['recipient_raw']) not in norm(evs[2]['meta'].get('To')):
        hard.append(f"event 003 To '{evs[2]['meta'].get('To')}' != gold recipient '{r['recipient_raw']}'")
    if norm(evs[2]['meta'].get('Channel')) != norm(r['gold_channel']):
        hard.append(f"event 003 Channel '{evs[2]['meta'].get('Channel')}' != gold '{r['gold_channel']}'")
    na = idx.get('next_action') or {}
    if norm(na.get('recipient')) != norm(r['recipient_raw']):
        soft.append(f"index Recipient '{na.get('recipient')}' != gold recipient")
    if norm(na.get('channel')) != norm(r['gold_channel']):
        soft.append(f"index Channel '{na.get('channel')}' != gold channel")
    ts = [e['timestamp'] for e in evs]
    if ts != sorted(ts):
        hard.append('timestamps not monotonic')
    vis = '\n'.join(e['body'] for e in evs[:2])
    if r['primary_ref'] not in vis and r['primary_ref'] not in idx['details'].get('Primary shipment', '') + idx['details'].get('Primary task reference', ''):
        soft.append(f"primary ref {r['primary_ref']} not in events 001-002")
    if norm(idx['sections'].get('Initial request')) != norm(evs[1]['body']):
        soft.append('Initial request differs from event 002 body')
    outcome = norm(idx['sections'].get('Outcome'))
    if outcome and outcome[:60] in norm(vis):
        hard.append('outcome text appears before the cutoff')
    return hard, soft, idx, hist


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('recipes'); ap.add_argument('written'); ap.add_argument('dest'); ap.add_argument('--report', default=None)
    a = ap.parse_args(); os.makedirs(a.dest, exist_ok=True)
    recipes = [json.loads(l) for l in open(a.recipes, encoding='utf-8')]
    report = {'installed': [], 'rejected': {}, 'soft': {}}
    for r in recipes:
        src = os.path.join(a.written, r['case_number'])
        hard, soft, idx, hist = check_case(r, src)
        if soft:
            report['soft'][r['case_id']] = soft
        if hard:
            report['rejected'][r['case_id']] = hard; continue
        dst = os.path.join(a.dest, r['case_number']); os.makedirs(dst, exist_ok=True)
        shutil.copy(os.path.join(src, 'index.md'), dst); shutil.copy(os.path.join(src, 'history.md'), dst)
        labels = {k: r[k] for k in ('case_id', 'source_set', 'complexity_level', 'complexity_name', 'issue_type', 'segment', 'requester_type', 'shipment_stage', 'owner_org_type', 'recipient_raw', 'recipient_function', 'action_class', 'gold_channel', 'queue', 'human_gate', 'risk_flags', 'money_involved', 'amount_gbp', 'customer_input_required', 'urgency', 'cutoff_utc', 'verification_state', 'evidence_conflict', 'proof_standard', 'twist', 'gold_ask', 'boundary')}
        labels['label_source'] = 'generation recipe (gold by construction); file starts with _ so deskagent/loader.py ignores it'
        json.dump(labels, open(os.path.join(dst, '_labels.json'), 'w'), indent=1, ensure_ascii=False)
        report['installed'].append(r['case_id'])
    if a.report:
        json.dump(report, open(a.report, 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({'installed': len(report['installed']), 'rejected': len(report['rejected']), 'soft_warnings': len(report['soft'])}))
    for cid, h in report['rejected'].items():
        print('REJECT', cid, h)


if __name__ == '__main__':
    main()
