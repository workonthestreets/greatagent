"""Tests for validate_cases.py. Run: python3.13 -I -m pytest data/pipeline_qa/tests/test_validate_cases.py"""
import copy
import json
import os
import subprocess
import sys

import pytest

QA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, QA)
import validate_cases as vc  # noqa: E402

REAL_RAW = os.environ.get('DELIVERY_RAW_DIR', '/private/tmp/claude-501/-Users-matveidanisheuski-greatagent/'
                          '2c2f72f0-cdbb-4e40-a92e-542fe728ca4d/scratchpad/repo/cases/Delivery & Logistics')

INDEX = """# Case 001: Commercial invoice missing

## Case details

- **Source role:** Ossmere Trade Desk, appointed customs broker
- **Status:** Completed — specific coordination task only
- **Created:** 2026-03-18 09:00:00 UTC
- **Escalated:** 2026-03-18 09:10:00 UTC
- **Updated:** 2026-03-18 10:05:00 UTC
- **Completed:** 2026-03-18 10:05:00 UTC
- **Primary shipment:** DL-045
- **Coordinator:** Iona Quill, Rivet Delivery Desk

## Context

The broker needs the shipper's commercial invoice for DL-045.

## Initial request

Please request the complete invoice from the authorised shipper.

## Next action at escalation

Ask the shipper for the invoice.

- **Recipient:** Fera Noll, Mavelle Export Studio shipping lead
- **Channel:** Email
- **Recorded action:** [History event 003](history.md#event-003)

## Outcome

The shipper supplies invoice CI-045 worth GBP 96.00 and the broker accepts the document package.

## Boundaries and remaining work

Customs clearance and charges remain undecided by the broker.

## Attachments

- [commercial-invoice.pdf](attachments/commercial-invoice.pdf)
"""


def _event(n, ts, stage, frm, to, body):
    return (f'<a id="event-{n:03d}"></a>\n## 2026-03-18 {ts} UTC — event {n:03d}\n\n'
            f'- **Stage:** {stage}\n- **Channel:** Email\n- **From:** {frm}\n- **To:** {to}\n\n{body}\n\n')


HISTORY = ('# Case 001 history\n\nAll fictional. Total events: 4.\n\n'
           + _event(1, '09:00:00', 'Context', 'Broker', 'Desk', 'For DL-045 we need the commercial invoice.')
           + _event(2, '09:10:00', 'Escalation', 'Broker', 'Desk', 'Please request the complete invoice.')
           + _event(3, '09:25:00', 'Agent action', 'Desk', 'Fera Noll, Mavelle Export Studio shipping lead',
                    'Please supply your commercial invoice for DL-045.')
           + _event(4, '09:50:00', 'Follow-through / confirmation', 'Fera', 'Desk',
                    'Our [commercial invoice CI-045](attachments/commercial-invoice.pdf) totals GBP 96.00, '
                    'collect on 2026-03-20 at 14:30.'))


@pytest.fixture
def raw_dir(tmp_path):
    case = tmp_path / 'raw' / '001'
    (case / 'attachments').mkdir(parents=True)
    (case / 'index.md').write_text(INDEX, encoding='utf-8')
    (case / 'history.md').write_text(HISTORY, encoding='utf-8')
    (case / 'attachments' / 'commercial-invoice.pdf').write_bytes(b'%PDF-1.4 fixture')
    return str(tmp_path / 'raw')


def _ev(n, ts, stage, body, visible):
    return {'event_id': f'{n:03d}', 'seq': n, 'timestamp': f'2026-03-18T{ts}Z', 'stage': stage,
            'channel': 'Email', 'from': {'raw': 'x', 'org_type': 'unknown'},
            'to': [{'raw': 'y', 'org_type': 'unknown'}], 'body': body, 'visible_at_escalation': visible}


@pytest.fixture
def clean_record():
    return {
        'case_id': 'DEL-001', 'track': 'Delivery & Logistics', 'title': 'Commercial invoice missing',
        'meta': {'created': '2026-03-18T09:00:00Z', 'escalated': '2026-03-18T09:10:00Z', 'primary_ref': 'DL-045',
                 'primary_ref_kind': 'shipment', 'coordinator': 'Iona Quill', 'status': 'Completed', 'n_events': 4},
        'parties': {'requester_type': 'customs_broker'},
        'at_escalation': {'initial_request': 'Please request the complete invoice from the authorised shipper.',
                          'visible_event_ids': ['001', '002'], 'refs': ['DL-045'], 'amounts_gbp': [],
                          'dates_mentioned': ['2026-03-18'], 'params': {'urgency': 'none'}},
        'decision': {'recipient_raw': 'Fera Noll, Mavelle Export Studio shipping lead',
                     'recipient': {'raw': 'Fera Noll', 'org_type': 'business_counterparty'}, 'channel': 'Email',
                     'action_class': 'ask_counterparty',
                     'message': 'Please supply your commercial invoice for DL-045.', 'queue': 'awaiting_counterparty'},
        'disclosed_after_escalation': {'outcome': 'The shipper supplies invoice CI-045.'},
        'events': [_ev(1, '09:00:00', 'context', 'For DL-045 we need the commercial invoice.', True),
                   _ev(2, '09:10:00', 'escalation', 'Please request the complete invoice.', True),
                   _ev(3, '09:25:00', 'agent_action', 'Please supply your commercial invoice for DL-045.', False),
                   _ev(4, '09:50:00', 'follow_through', 'Invoice CI-045 attached.', False)],
        'attachments': [{'name': 'commercial-invoice.pdf', 'first_event_id': '004', 'visible_at_escalation': False}],
    }


def _write(tmp_path, name, rows):
    p = tmp_path / name
    p.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
    return str(p)


def _run(tmp_path, raw_dir, cases=None, **kw):
    argv = ['--raw', raw_dir, '--expect-cases', '1', '--expect-events', '4',
            '--json-report', str(tmp_path / 'report.json')]
    if cases is not None:
        argv += ['--cases', _write(tmp_path, 'cases.jsonl', cases)]
    for flag, rows in kw.items():
        argv += ['--' + flag.replace('_', '-'), _write(tmp_path, flag + '.jsonl', rows)]
    code = vc.main(argv)
    report = json.load(open(tmp_path / 'report.json'))
    return code, {c['check']: c for c in report['checks']}


def test_clean_record_passes(tmp_path, raw_dir, clean_record):
    code, checks = _run(tmp_path, raw_dir, [clean_record])
    assert code == 0, checks
    for name in ('schema', 'leakage', 'consistency', 'monotonic', 'case_count'):
        assert checks[name]['status'] == 'PASS', checks[name]


def test_leaky_record_fails_leakage(tmp_path, raw_dir, clean_record):
    leaky = copy.deepcopy(clean_record)
    ae = leaky['at_escalation']
    ae['refs'].append('CI-045')                       # ref introduced at event 004
    ae['amounts_gbp'] = [96.0]                        # amount introduced at event 004 / Outcome
    ae['dates_mentioned'].append('2026-03-20')        # date introduced at event 004
    ae['visible_event_ids'].append('004')             # future event exposed
    ae['initial_request'] += ' Customs clearance and charges remain undecided by the broker.'  # Boundaries
    ae['notes'] = 'collect at 14:30'                   # time from event 004
    leaky['attachments'][0]['visible_at_escalation'] = True
    code, checks = _run(tmp_path, raw_dir, [leaky])
    assert code == 1
    assert checks['leakage']['status'] == 'FAIL'
    probs = '\n'.join(checks['leakage']['problems']['DEL-001'])
    for needle in ("'CI-045'", 'GBP 96.0', "'2026-03-20'", "'14:30'", "contains '004'",
                   'Boundaries sentence', 'commercial-invoice.pdf visible_at_escalation'):
        assert needle in probs, (needle, probs)
    assert checks['schema']['status'] == 'PASS'      # leakage is independent of schema validity


def test_paraphrased_outcome_caught_by_token_overlap(tmp_path, raw_dir, clean_record):
    rec = copy.deepcopy(clean_record)
    rec['at_escalation']['initial_request'] = 'Broker accepts document package; shipper supplies invoice.'
    _code, checks = _run(tmp_path, raw_dir, [rec])
    assert 'high token overlap with Outcome' in '\n'.join(checks['leakage']['problems']['DEL-001'])


def test_schema_and_consistency_failures(tmp_path, raw_dir, clean_record):
    bad = copy.deepcopy(clean_record)
    bad['case_id'] = 'del-1'
    bad['meta']['created'] = '18/03/2026'
    bad['decision']['queue'] = 'somewhere'
    del bad['decision']['channel']
    bad['events'][0]['from']['org_type'] = 'alien'      # nested $ref enum
    code, checks = _run(tmp_path, raw_dir, [bad])
    assert code == 1
    errs = '\n'.join(checks['schema']['problems']['del-1'])
    for needle in ('does not match', 'ISO-8601', "'somewhere' not in enum", "missing required 'channel'",
                   "'alien' not in enum"):
        assert needle in errs, (needle, errs)

    inc = copy.deepcopy(clean_record)
    inc['events'] = inc['events'][:3]
    inc['decision']['message'] = 'Something else.'
    inc['decision']['recipient_raw'] = 'Someone else'
    inc['attachments'] = []
    _code, checks = _run(tmp_path, raw_dir, [inc])
    probs = '\n'.join(checks['consistency']['problems']['DEL-001'])
    for needle in ('events count 3 != raw Total events 4', 'decision.message differs',
                   'recipient_raw', 'index-listed'):
        assert needle in probs, (needle, probs)


def test_missing_attachment_file_and_monotonic(tmp_path, raw_dir, clean_record):
    os.remove(os.path.join(raw_dir, '001', 'attachments', 'commercial-invoice.pdf'))
    rec = copy.deepcopy(clean_record)
    rec['events'][1]['timestamp'] = '2026-03-18T08:00:00Z'
    _code, checks = _run(tmp_path, raw_dir, [rec])
    assert 'file is missing' in '\n'.join(checks['consistency']['problems']['DEL-001'])
    assert checks['monotonic']['status'] == 'FAIL'


def test_counts(tmp_path, raw_dir, clean_record):
    events = [dict(e, case_id='DEL-001') for e in clean_record['events']]
    code, checks = _run(tmp_path, raw_dir, [clean_record, clean_record], events=events[:3])
    assert checks['case_count']['status'] == 'FAIL'       # 2 records (duplicate) vs expected 1
    assert checks['events_count']['status'] == 'FAIL'     # 3 rows vs expected 4
    assert code == 1


def test_decision_points(tmp_path, raw_dir, clean_record):
    good = {'case_id': 'DEL-001', 'input': {'initial_request': 'Please request the complete invoice.',
                                            'events': [{'event_id': '001', 'seq': 1, 'body': 'For DL-045.'},
                                                       {'event_id': '002', 'seq': 2, 'body': 'Request it.'}]},
            'attachments_available': []}
    code, checks = _run(tmp_path, raw_dir, decision_points=[good])
    assert code == 0 and checks['decision_points']['status'] == 'PASS', checks['decision_points']
    assert checks['schema']['status'] == 'SKIP'           # cases file optional

    bad = copy.deepcopy(good)
    bad['input']['events'].append({'event_id': '003', 'seq': 3, 'body': 'Please supply your invoice.'})
    bad['input']['note'] = 'The shipper supplies invoice CI-045 worth GBP 96.00 and the broker accepts the document package.'
    bad['attachments_available'] = ['commercial-invoice.pdf']
    bad['input']['attachments_available'] = [{'name': 'commercial-invoice.pdf'}]
    code, checks = _run(tmp_path, raw_dir, decision_points=[bad])
    probs = '\n'.join(checks['decision_points']['problems']['DEL-001'])
    assert code == 1
    for needle in ('event seq 3', 'Outcome sentence', "'CI-045'", 'attachments_available', 'input.attachments_available'):
        assert needle in probs, (needle, probs)


@pytest.mark.skipif(not os.path.isdir(REAL_RAW), reason='real raw cases not available')
def test_fixture_against_real_raw(tmp_path):
    """Integration: TEST FIXTURE (not pipeline output) built from the real raw data must pass; a careless
    variant that copies all event refs into at_escalation must fail leakage."""
    out = tmp_path / 'fx'
    subprocess.run([sys.executable, '-I', os.path.join(QA, 'fixtures', 'build_fixture.py'), REAL_RAW, str(out)],
                   check=True, capture_output=True)
    files = ['--cases', str(out / 'cases.fixture.jsonl'), '--events', str(out / 'events.fixture.jsonl'),
             '--decision-points', str(out / 'decision_points.fixture.jsonl')]
    assert vc.main(files + ['--raw', REAL_RAW]) == 0
    rows = [json.loads(line) for line in open(out / 'cases.fixture.jsonl')]
    for r in rows:
        r['at_escalation']['refs'] = sorted(set(vc.REF_RE.findall(' '.join(e['body'] for e in r['events']))))
    careless = _write(tmp_path, 'careless.jsonl', rows)
    assert vc.main(['--cases', careless, '--raw', REAL_RAW, '--json-report', str(tmp_path / 'r.json')]) == 1
    leak = {c['check']: c for c in json.load(open(tmp_path / 'r.json'))['checks']}['leakage']
    assert 'DEL-045' in leak['problems'] and any('CI-045' in p for p in leak['problems']['DEL-045'])
    assert 'DEL-032' in leak['problems']   # dash-less token DL032R introduced at event 004
