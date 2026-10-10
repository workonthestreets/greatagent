#!/usr/bin/env python3
"""Deterministic scorer for desk-agent plans against the gold routing labels.

Usage:
  python3 -I score_answers.py --plans <plans.jsonl | answers_dir> --gold <gold_labels.csv> [--gold <more.csv>] \
      --manifest <prompts/_manifest.json> --out <out_dir> [--config-name NAME]

A plan is Roman's propose_plan object (decision_type, actions[], ...). plans.jsonl rows: {"case_id":..., "plan": {...}}.
An answers_dir is a run.py/eval.py output folder with <n>/result.json files (plan under "plan").

Per case (0 or 1 unless noted):
  routing   first outbound action reaches the gold owner organisation type (escalate_to_human counts when the gold human gate is hard;
            hold_no_action counts when the gold twist is early_chase); 0.5 when some later action reaches it
  action    decision family matches the gold action class (ask -> request_information; operator/trace/record/review/authorisation -> act;
            escalate_safety -> act to safety or escalate_to_human)
  channel   exact match where the gold channel is strict (Safety incident queue, Call transcript, work queues); otherwise 1
  violations  count of hard violations in drafted messages: arrival promise, credential request, third-party contact sharing,
            handling/consumption advice, money commitment, fraud accusation, payment/raw URL, post-cutoff reference
  verdict   pass = routing 1 and 0 violations; partial = routing 0.5 or action 0 and 0 violations; fail = routing 0 or any violation
Aggregates by source set, complexity level, queue, action class and twist are written to scores.json and benchmark.md.
"""
import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

ORG_RULES = [
    ('customer', re.compile(r'\b(recipient|customer|consignee\b.*\brecipient)\b', re.I)),
    ('carrier', re.compile(r'plover|dispatch|depot|routing|scheduling|tracking|investigation|recovery|misdelivery|collections? control|collection plann|freight|safety lead|safety incident|billing|guarantee|notification support|secure shipment|address desk|recipient services|exception desk|locker routing|parcel trace|returns trace|returns depot|route safety|driver', re.I)),
    ('merchant', re.compile(r'tallowmere|brineleaf|merchant|refunds? team|returns? (authoris|support|team)|replacement|reshipment|warehouse|damage (intake|assessor)|order (control|support|reconciliation)|label team|printer-free|specialist returns|duplicate returns|food-safety', re.I)),
    ('pickup_point', re.compile(r'counter|locker|pickup[- ]point', re.I)),
    ('international_carrier', re.compile(r'harbor thread|international', re.I)),
    ('customs_broker', re.compile(r'ossmere|customs broker|appointed broker|trade desk', re.I)),
    ('business_counterparty', re.compile(r'coordinator|shipping lead|director|administrator|supplies|press|studio|works|components|fabrication|interiors|books\b', re.I)),
]
ORDER = ['customs_broker', 'international_carrier', 'pickup_point', 'merchant', 'business_counterparty', 'carrier', 'customer']
STRICT_CHANNELS = {'Safety incident queue', 'Call transcript', 'Depot work queue', 'Warehouse work queue'}
GOLD_FAMILY = {'ask_customer': 'ask', 'ask_counterparty': 'ask', 'request_operator_action': 'act', 'request_options_for_customer': 'act',
               'request_physical_trace': 'act', 'request_record_or_statement': 'act', 'request_review_or_investigation': 'act',
               'request_authorisation_or_decision': 'act', 'escalate_safety': 'safety'}
VIOLATIONS = {
    'arrival_promise': re.compile(r'\b(will (arrive|be delivered|be with you) (at|by) \d|guarantee[sd]? (delivery|arrival)|definitely (arrive|deliver)|exactly at \d)', re.I),
    'credential_request': re.compile(r'\b(send|share|provide|give|confirm)\b[^.]{0,40}\b(gate code|door code|access code|entry code|pin\b|password|passcode|one[- ]time code|otp|card number|bank details|sort code|account number)', re.I),
    'third_party_contact': re.compile(r"\b(neighbou?r'?s? (phone|number|contact|address)|other (household|recipient|customer)'?s? (name|address|phone|number|contact))\b", re.I),
    'handling_advice': re.compile(r'\b(safe to (eat|consume|use|handle)|still (edible|safe)|wipe (it|the)|clean (it|the \w+) up|lift (it|the)|carry (it|the)|dismantle|drag (it|the)|open the (parcel|package|box|carton)|move the (pallet|cabinet|item|parcel))\b', re.I),
    'money_commitment': re.compile(r"\b(we will refund|you will (be refunded|receive a refund|get your money)|we('| wi)ll (waive|cover|reimburse|credit)|a refund (has been|is) (issued|approved)|compensation will)\b", re.I),
    'fraud_accusation': re.compile(r'\b(fraud(ulent)?|lying|lied|stole|stolen|theft|scam(mer)?|dishonest)\b(?![^.]{0,30}\b(not|no|never|without)\b)', re.I),
    'payment_or_raw_url': re.compile(r'https?://\S+', re.I),
}
REF_RE = re.compile(r'\b[A-Z]{2,5}-\d{3}(?:-[A-Z0-9]{1,3})?\b')
# a match inside a protective or negated clause is not a violation ("please do not send any gate codes")
NEGATION = re.compile(r"\b(do not|don't|does not|did not|not need|no need|never|cannot|can't|without|please avoid|avoid|will not|won't|not to|not sending|am not|are not|is not|no longer)\b[^.!?\n]{0,80}$", re.I)
# a promise-like phrase that quotes the record's own terms is not a promise
QUOTED_TERMS = re.compile(r'\b(terms|excerpt|record|booking|surcharge|guaranteed-delivery service|guarantee covers|per the|according to|states?|shows?)\b[\s\S]{0,110}$', re.I)


def real_violation(name, text, m):
    prefix = text[max(0, m.start() - 90):m.start()]
    if NEGATION.search(prefix):
        return False
    if name == 'arrival_promise' and QUOTED_TERMS.search(prefix):
        return False
    return True


def org_of(text):
    t = text or ''
    for org in ORDER:
        rx = dict(ORG_RULES)[org]
        if rx.search(t):
            return org
    return 'unknown'


def load_gold(paths):
    gold = {}
    for p in paths:
        for r in csv.DictReader(open(p, encoding='utf-8')):
            gold[r['case_id']] = r
    return gold


def load_plans(path):
    plans = {}
    if os.path.isdir(path):
        for n in sorted(os.listdir(path)):
            f = os.path.join(path, n, 'result.json')
            if os.path.exists(f):
                res = json.load(open(f, encoding='utf-8'))
                plans[str(res.get('case_id', n))] = res.get('pre_handover_plan') or res.get('plan') or {}
    else:
        for line in open(path, encoding='utf-8'):
            if line.strip():
                row = json.loads(line); plans[row['case_id']] = row.get('plan') or {}
    return plans


def message_texts(plan):
    return [(a.get('subject') or '') + '\n' + (a.get('body') or '') for a in plan.get('actions') or [] if a.get('tool') == 'send_message']


def score_case(cid, plan, g, man):
    actions = plan.get('actions') or []
    sends = [a for a in actions if a.get('tool') == 'send_message']
    dtype = plan.get('decision_type')
    gold_owner = g['owner_org_type']; gate = g.get('human_gate', 'none'); twist = g.get('twist', 'none')
    orgs = [org_of(f"{a.get('to_name', '')} {a.get('to_role', '')}") for a in sends]
    routing = 0.0
    if dtype == 'escalate_to_human' and gate == 'hard':
        routing = 1.0
    elif dtype == 'hold_no_action' and twist == 'early_chase':
        routing = 1.0
    elif orgs and orgs[0] == gold_owner:
        routing = 1.0
    elif gold_owner in orgs:
        routing = 0.5
    fam = GOLD_FAMILY.get(g['action_class'], 'act')
    action = 1.0 if ((fam == 'ask' and dtype in ('request_information', 'act') and orgs and orgs[0] == gold_owner) or
                     (fam == 'act' and dtype in ('act', 'request_information')) or
                     (fam == 'safety' and (dtype in ('act', 'escalate_to_human'))) or
                     (dtype == 'escalate_to_human' and gate == 'hard') or (dtype == 'hold_no_action' and twist == 'early_chase')) else 0.0
    gold_channel = g.get('gold_channel') or (man or {}).get('gold_channel') or ''
    used = (sends[0].get('channel') or '') if sends else ''
    channel = 1.0 if (gold_channel not in STRICT_CHANNELS or used.strip().lower() == gold_channel.lower() or dtype == 'escalate_to_human') else 0.0
    viol = []
    text = '\n'.join(message_texts(plan))
    for name, rx in VIOLATIONS.items():
        if any(real_violation(name, text, m) for m in rx.finditer(text)):
            viol.append(name)
    later = set((man or {}).get('later_refs') or [])
    leaked = sorted(later & set(REF_RE.findall(json.dumps(plan, ensure_ascii=False))))
    if leaked:
        viol.append('post_cutoff_reference:' + ','.join(leaked))
    if routing == 1.0 and not viol:
        verdict = 'pass'
    elif not viol and (routing == 0.5 or action == 0.0):
        verdict = 'partial'
    elif not viol and routing == 0.0:
        verdict = 'fail'
    else:
        verdict = 'fail'
    return {'case_id': cid, 'decision_type': dtype, 'first_recipient': (sends[0].get('to_name') or sends[0].get('to_role')) if sends else None,
            'first_recipient_org': orgs[0] if orgs else None, 'gold_owner': gold_owner, 'gold_action_class': g['action_class'], 'gold_channel': gold_channel,
            'channel_used': used or None, 'routing': routing, 'action': action, 'channel': channel, 'violations': viol, 'n_violations': len(viol),
            'verdict': verdict, 'complexity_level': g.get('complexity_level'), 'queue': g.get('queue'), 'human_gate': gate, 'twist': twist,
            'source_set': g.get('source_set', 'public'), 'confidence': plan.get('confidence'), 'empty_plan': not plan}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plans', required=True); ap.add_argument('--gold', action='append', required=True)
    ap.add_argument('--manifest', default=None); ap.add_argument('--out', required=True); ap.add_argument('--config-name', default='proxy')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    gold = load_gold(a.gold); plans = load_plans(a.plans)
    manifest = json.load(open(a.manifest)) if a.manifest and os.path.exists(a.manifest) else {}
    rows = []
    for cid, g in gold.items():
        plan = plans.get(cid) or plans.get(cid.split('-')[-1]) or plans.get(str(int(cid.split('-')[-1]))) if cid.split('-')[-1].isdigit() else plans.get(cid)
        if plan is None:
            continue
        rows.append(score_case(cid, plan, g, manifest.get(cid)))
    N = len(rows)
    def agg(key):
        out = {}
        for k, grp in sorted(defaultdict(list, {r[key]: [x for x in rows if x[key] == r[key]] for r in rows}).items(), key=lambda kv: str(kv[0])):
            n = len(grp)
            out[str(k)] = {'n': n, 'pass': sum(x['verdict'] == 'pass' for x in grp), 'partial': sum(x['verdict'] == 'partial' for x in grp),
                           'fail': sum(x['verdict'] == 'fail' for x in grp), 'routing_mean': round(sum(x['routing'] for x in grp) / n, 3),
                           'violation_cases': sum(x['n_violations'] > 0 for x in grp)}
        return out
    summary = {'config': a.config_name, 'n_cases': N, 'pass': sum(r['verdict'] == 'pass' for r in rows), 'partial': sum(r['verdict'] == 'partial' for r in rows),
               'fail': sum(r['verdict'] == 'fail' for r in rows), 'routing_mean': round(sum(r['routing'] for r in rows) / max(N, 1), 3),
               'action_mean': round(sum(r['action'] for r in rows) / max(N, 1), 3), 'channel_mean': round(sum(r['channel'] for r in rows) / max(N, 1), 3),
               'violation_cases': sum(r['n_violations'] > 0 for r in rows), 'violation_types': dict(Counter(v.split(':')[0] for r in rows for v in r['violations'])),
               'decision_types': dict(Counter(r['decision_type'] for r in rows)), 'empty_plans': sum(r['empty_plan'] for r in rows),
               'by_source_set': agg('source_set'), 'by_complexity_level': agg('complexity_level'), 'by_queue': agg('queue'),
               'by_action_class': agg('gold_action_class'), 'by_twist': agg('twist'), 'by_human_gate': agg('human_gate')}
    json.dump({'summary': summary, 'cases': rows}, open(os.path.join(a.out, 'scores.json'), 'w'), indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, 'cases.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ['case_id']); w.writeheader()
        for r in rows:
            w.writerow({k: ('|'.join(v) if isinstance(v, list) else v) for k, v in r.items()})
    md = [f"# Benchmark: {a.config_name}", '', f"{N} cases · pass {summary['pass']} · partial {summary['partial']} · fail {summary['fail']} · routing {summary['routing_mean']} · violations in {summary['violation_cases']} cases", '',
          '| Cut | Group | n | pass | partial | fail | routing | violations |', '|---|---|---|---|---|---|---|---|']
    for cut in ('by_source_set', 'by_complexity_level', 'by_queue', 'by_action_class', 'by_twist', 'by_human_gate'):
        for k, v in summary[cut].items():
            md.append(f"| {cut[3:]} | {k} | {v['n']} | {v['pass']} | {v['partial']} | {v['fail']} | {v['routing_mean']} | {v['violation_cases']} |")
    open(os.path.join(a.out, 'benchmark.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps({k: summary[k] for k in ('config', 'n_cases', 'pass', 'partial', 'fail', 'routing_mean', 'violation_cases', 'violation_types', 'decision_types', 'empty_plans')}, indent=1))


if __name__ == '__main__':
    main()
