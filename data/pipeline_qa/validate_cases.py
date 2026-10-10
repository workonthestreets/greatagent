#!/usr/bin/env python3
"""Validator for the normalized delivery-case dataset (QA side, read-only on inputs).

Python 3 stdlib only. Every input file is optional; checks run on whatever exists.

Usage:
    python3 -I validate_cases.py [cases.jsonl] [--cases cases.jsonl] [--events events.jsonl]
        [--decision-points decision_points.jsonl] --raw "<Delivery & Logistics dir>"
    With no file arguments it validates data/delivery/agent/{cases,events,decision_points}.jsonl.
        [--schema case.schema.json] [--expect-cases 50] [--expect-events 228]
        [--json-report out.json]

Checks (each reported pass/fail with the first offending case ids):
  schema            cases.jsonl vs case.schema.json (required/enum/type/pattern/date-time,
                    walked recursively, $ref resolved only within #/$defs)
  case_count        exactly --expect-cases case records
  leakage           at_escalation must not contain refs/GBP amounts/dates/times/measurements
                    that first appear in raw event 003+ (or only in Outcome/Boundaries/
                    completion metadata), event ids >= 003, or Outcome/Boundaries sentences;
                    attachments first linked at event 003+ must not be visible_at_escalation
  consistency       events count == raw "Total events"; decision.message == raw event 003 body;
                    decision.recipient_raw == index Recipient bullet; index-listed attachments
                    exist on disk and match the record
  monotonic         event timestamps non-decreasing per case (cases.jsonl and events.jsonl)
  events_count      events.jsonl has exactly --expect-events rows
  decision_points   no event with seq >= 3 in `input`, no Outcome/Boundaries text or late
                    tokens in `input`, `attachments_available` excludes attachments first
                    mentioned at event 003 or later
Exit code 1 if any check fails (or an input cannot be read).
"""
import argparse
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCHEMA = os.path.join(os.path.dirname(HERE), 'pipeline', 'case.schema.json')
AGENT_DIR = os.path.join(os.path.dirname(HERE), 'delivery', 'agent')

# ---------------------------------------------------------------- token extraction
REF_PREFIXES = ('DL', 'RT', 'TG', 'COL', 'MN', 'INV', 'CN', 'DR', 'CI', 'MND', 'RL', 'OS', 'WH',
                'EST', 'OF')
# Generic "PREFIX-SUFFIX[-SUFFIX]" (covers the listed prefixes and the others the raw data
# uses: MD-, KL-, BP-, POD-, SAFE-, ...) plus dash-less codes such as DL032R.
REF_RE = re.compile(r'\b[A-Z]{2,5}(?:-[A-Z0-9]+)+\b|\b[A-Z]{2,5}\d{2,}[A-Z0-9]*\b')
GBP_RE = re.compile(r'(?:GBP|£)\s?(\d[\d,]*(?:\.\d+)?)')
DATE_RE = re.compile(r'\b(\d{4}-\d{2}-\d{2})')
TIME_RE = re.compile(r'(?<![\d:])(\d{2}:\d{2})(?::\d{2})?(?![\d])')
MEAS_RE = re.compile(r'\b(\d+(?:\.\d+)?)\s?(kg|cm|mm|m|g)\b')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
WORD_RE = re.compile(r"[a-z0-9£]+(?:[.'][a-z0-9]+)*")

STOP = set('a an the and or of to for in on at by is are be it this that with as from our your we '
           'you i not no has have was were will can may please do does any all its their them '
           'they he she his her if but so been only'.split())


def amount(s):
    try:
        return round(float(s.replace(',', '')), 2)
    except ValueError:
        return None


def extract_tokens(text):
    """Return {('ref'|'gbp'|'date'|'time'|'meas', value)} found in text."""
    out = set()
    if not text:
        return out
    for m in REF_RE.finditer(text):
        out.add(('ref', m.group(0)))
    for m in GBP_RE.finditer(text):
        a = amount(m.group(1))
        if a is not None:
            out.add(('gbp', a))
    for m in DATE_RE.finditer(text):
        out.add(('date', m.group(1)))
    for m in TIME_RE.finditer(text):
        out.add(('time', m.group(1)))
    for m in MEAS_RE.finditer(text):
        out.add(('meas', f'{m.group(1)} {m.group(2)}'))
    return out


def norm(text):
    text = LINK_RE.sub(r'\1', text or '')
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    text = text.replace('–', '-').replace('—', '-')
    return re.sub(r'\s+', ' ', text).strip().lower()


def content_words(text):
    return [w for w in WORD_RE.findall(norm(text)) if w not in STOP]


def sentences(text):
    text = LINK_RE.sub(r'\1', text or '')
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"“‘\'(])', re.sub(r'\s+', ' ', text).strip())
    return [p.strip() for p in parts if p.strip()]


# ---------------------------------------------------------------- raw parsing (independent of pipeline)
H1_RE = re.compile(r'^#\s+Case\s+(\d+):\s*(.*)$', re.M)
SECTION_RE = re.compile(r'^##\s+(.+?)\s*$', re.M)
BULLET_RE = re.compile(r'^-\s+\*\*(.+?):\*\*\s*(.*)$', re.M)
EVENT_RE = re.compile(
    r'<a id="event-(\d+)"></a>\s*\n##\s+(.+?)\s+—\s+event\s+(\d+)\s*\n(.*?)(?=\n<a id="event-|\Z)', re.S)
TOTAL_RE = re.compile(r'Total events:\s*(\d+)')
HIDDEN_DETAILS = ('Status', 'Updated', 'Completed')  # reveal the ending


def _sections(md):
    parts = SECTION_RE.split(md)
    return OrderedDict((parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2))


def load_raw_case(case_dir):
    idx = open(os.path.join(case_dir, 'index.md'), encoding='utf-8').read()
    secs = _sections(idx)
    details = dict(BULLET_RE.findall(secs.get('Case details', '')))
    details = {k.strip(): v.strip() for k, v in details.items()}
    next_action = next((v for k, v in secs.items() if k.lower().startswith('next action')), '')
    na_bullets = {k.strip(): v.strip() for k, v in BULLET_RE.findall(next_action)}
    listed = [h for _n, h in LINK_RE.findall(secs.get('Attachments', ''))]
    hist_md = open(os.path.join(case_dir, 'history.md'), encoding='utf-8').read()
    total = TOTAL_RE.search(hist_md)
    events = []
    for eid, ts, _e2, rest in EVENT_RE.findall(hist_md):
        meta = {k.strip(): v.strip() for k, v in BULLET_RE.findall(rest)}
        body = BULLET_RE.sub('', rest).strip()
        events.append({'seq': int(eid), 'event_id': eid, 'ts': ts.strip(), 'meta': meta, 'body': body})
    att_dir = os.path.join(case_dir, 'attachments')
    on_disk = sorted(os.listdir(att_dir)) if os.path.isdir(att_dir) else []
    first_mention = {}
    for ev in events:
        for _n, href in LINK_RE.findall(ev['body']):
            if href.startswith('attachments/'):
                first_mention.setdefault(os.path.basename(href), ev['seq'])
    return {'dir': case_dir, 'details': details, 'sections': secs, 'recipient': na_bullets.get('Recipient'),
            'listed_attachments': listed, 'attachments_on_disk': on_disk,
            'attachment_first_seq': first_mention,
            'total_events': int(total.group(1)) if total else None, 'events': events}


def leak_profile(raw):
    """Tokens and sentences that must not appear at the decision point."""
    secs, det = raw['sections'], raw['details']
    visible_texts = [secs.get('Context', ''), secs.get('Initial request', '')]
    visible_texts += [v for k, v in det.items() if k not in HIDDEN_DETAILS]
    visible_texts += [ev['body'] + '\n' + ev['ts'] for ev in raw['events'] if ev['seq'] <= 2]
    visible = set()
    for t in visible_texts:
        visible |= extract_tokens(t)
    late = {}
    def add(text, origin):
        for tok in extract_tokens(text):
            if tok not in visible:
                late.setdefault(tok, origin)
    for ev in raw['events']:
        if ev['seq'] >= 3:
            add(ev['body'], f"event {ev['event_id']}")
    add(secs.get('Outcome', ''), 'Outcome')
    add(secs.get('Boundaries and remaining work', ''), 'Boundaries')
    for k in ('Updated', 'Completed'):
        if det.get(k) and det.get(k) not in (det.get('Created'), det.get('Escalated')):
            add(det[k], f'details.{k}')
    vis_words = [set(content_words(s)) for t in visible_texts for s in sentences(t)]
    secret_sents = []
    for name in ('Outcome', 'Boundaries and remaining work'):
        for s in sentences(secs.get(name, '')):
            w = set(content_words(s))
            if len(w) < 3:
                continue
            # skip sentences that merely restate visible text (not a leak if already known)
            if any(len(w & v) / len(w) >= 0.8 for v in vis_words if v):
                continue
            secret_sents.append((name.split()[0], s, w))
    return {'late': late, 'sentences': secret_sents, 'visible_words': vis_words}


def iter_strings(obj, path=''):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_strings(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_strings(v, f'{path}[{i}]')


def iter_numbers(obj, path=''):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_numbers(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_numbers(v, f'{path}[{i}]')


def _overlaps(secret, sw, visible_words):
    """True if a string sentence `sw` paraphrases the secret sentence: it covers >= 80% of the
    secret's content words, or >= 6 of its own words are >= 80% secret words -- unless that string
    sentence is itself a near-copy of visible (decision-time) text."""
    inter = len(secret & sw)
    hit = (inter >= 4 and inter / len(secret) >= 0.8) or (inter >= 6 and inter / max(len(sw), 1) >= 0.8)
    if not hit:
        return False
    return not any(v and len(sw & v) / len(sw) >= 0.8 for v in visible_words)


def scan_for_leaks(obj, prof, root):
    """Problems for any outcome-bearing token/sentence found anywhere under obj."""
    probs = []
    late = prof['late']
    for path, s in iter_strings(obj, root):
        for tok in extract_tokens(s):
            if tok in late:
                probs.append(f'{path}: {tok[0]} {tok[1]!r} first appears in {late[tok]}')
        ns, ws = norm(s), set(content_words(s))
        str_sents = [set(content_words(x)) for x in sentences(s)] or [ws]
        for sec, sent, w in prof['sentences']:
            if norm(sent) in ns:
                probs.append(f'{path}: contains {sec} sentence {sent[:70]!r}')
            elif any(_overlaps(w, sw, prof['visible_words']) for sw in str_sents):
                probs.append(f'{path}: high token overlap with {sec} sentence {sent[:70]!r}')
    for path, n in iter_numbers(obj, root):
        if 'amount' in path or 'gbp' in path.lower():
            if ('gbp', round(float(n), 2)) in late:
                probs.append(f'{path}: GBP {n} first appears in {late[("gbp", round(float(n), 2))]}')
    return probs


def event_seq(v):
    m = re.search(r'(\d+)\s*$', str(v if v is not None else ''))
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- schema walking
ISO_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$')
TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}


def _type_ok(v, t):
    if t == 'integer':
        return isinstance(v, int) and not isinstance(v, bool)
    if t == 'number':
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, TYPES[t])


def schema_errors(inst, sch, root, path='$'):
    if '$ref' in sch:
        ref = sch['$ref']
        if not ref.startswith('#/$defs/'):
            return [f'{path}: unsupported $ref {ref}']
        sch = root.get('$defs', {}).get(ref[len('#/$defs/'):])
        if sch is None:
            return [f'{path}: unresolved $ref {ref}']
        return schema_errors(inst, sch, root, path)
    errs = []
    t = sch.get('type')
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_type_ok(inst, x) for x in ts):
            return [f'{path}: expected {"/".join(ts)}, got {type(inst).__name__}']
    if 'enum' in sch and inst not in sch['enum']:
        errs.append(f'{path}: {inst!r} not in enum {sch["enum"]}')
    if isinstance(inst, str):
        if 'pattern' in sch and not re.search(sch['pattern'], inst):
            errs.append(f'{path}: {inst!r} does not match {sch["pattern"]}')
        if sch.get('format') == 'date-time' and not ISO_RE.match(inst):
            errs.append(f'{path}: {inst!r} is not an ISO-8601 date-time')
    if isinstance(inst, dict):
        for k in sch.get('required', []):
            if k not in inst:
                errs.append(f'{path}: missing required {k!r}')
        for k, sub in sch.get('properties', {}).items():
            if k in inst:
                errs += schema_errors(inst[k], sub, root, f'{path}.{k}')
    if isinstance(inst, list) and 'items' in sch:
        for i, v in enumerate(inst):
            errs += schema_errors(v, sch['items'], root, f'{path}[{i}]')
    return errs


# ---------------------------------------------------------------- reporting
class Check:
    def __init__(self, name):
        self.name, self.passed, self.failed, self.problems, self.skipped = name, 0, 0, OrderedDict(), None

    def record(self, cid, probs):
        if probs:
            self.failed += 1
            self.problems.setdefault(cid, []).extend(probs)
        else:
            self.passed += 1

    def as_dict(self):
        return {'check': self.name, 'status': self.status(), 'passed': self.passed, 'failed': self.failed,
                'skipped_reason': self.skipped, 'problems': self.problems}

    def status(self):
        return 'SKIP' if self.skipped else ('FAIL' if self.failed else 'PASS')


def read_jsonl(path):
    rows, errs = [], []
    with open(path, encoding='utf-8') as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errs.append(f'line {n}: {exc}')
    return rows, errs


def case_num(cid):
    m = re.search(r'(\d+)\s*$', str(cid or ''))
    return m.group(1).zfill(3) if m else None


# ---------------------------------------------------------------- checks
def run(args):
    checks = OrderedDict((n, Check(n)) for n in (
        'parse', 'schema', 'case_count', 'leakage', 'consistency', 'monotonic', 'events_count',
        'decision_points'))
    raw_cache = {}

    def raw_for(cid):
        num = case_num(cid)
        if not args.raw or not num:
            return None
        if num not in raw_cache:
            d = os.path.join(args.raw, num)
            raw_cache[num] = load_raw_case(d) if os.path.isfile(os.path.join(d, 'index.md')) else None
        return raw_cache[num]

    cases_path = args.cases or args.cases_pos
    inputs = {'cases': cases_path, 'events': args.events, 'decision_points': args.decision_points}
    data = {}
    for k, p in inputs.items():
        if not p:
            continue
        if not os.path.isfile(p):
            checks['parse'].record(k, [f'{p}: file not found'])
            continue
        rows, errs = read_jsonl(p)
        checks['parse'].record(k, errs)
        data[k] = rows
    if not any(inputs.values()):
        checks['parse'].skipped = 'no inputs'

    cases = data.get('cases')
    if cases is None:
        for n in ('schema', 'case_count', 'leakage', 'consistency'):
            checks[n].skipped = 'no cases file'
    else:
        try:
            schema = json.load(open(args.schema, encoding='utf-8'))
        except (OSError, ValueError) as exc:
            schema = None
            checks['schema'].skipped = f'schema unreadable: {exc}'
        ids = [r.get('case_id') for r in cases]
        cc = [] if len(cases) == args.expect_cases else [f'{len(cases)} case records, expected {args.expect_cases}']
        dup = sorted({i for i in ids if ids.count(i) > 1}, key=str)
        if dup:
            cc.append(f'duplicate case_ids: {dup}')
        checks['case_count'].record('cases.jsonl', cc)
        if not args.raw:
            checks['leakage'].skipped = checks['consistency'].skipped = 'no --raw dir'
        for rec in cases:
            cid = rec.get('case_id', '<missing case_id>')
            if schema is not None:
                checks['schema'].record(cid, schema_errors(rec, schema, schema))
            checks['monotonic'].record(cid, monotonic_problems(rec.get('events') or [], 'events'))
            raw = raw_for(cid)
            if args.raw:
                if raw is None:
                    checks['consistency'].record(cid, [f'no raw case folder for {cid}'])
                    checks['leakage'].record(cid, [f'no raw case folder for {cid}'])
                    continue
                checks['leakage'].record(cid, leakage_problems(rec, raw))
                checks['consistency'].record(cid, consistency_problems(rec, raw))

    evs = data.get('events')
    if evs is None:
        checks['events_count'].skipped = 'no events file'
    else:
        checks['events_count'].record('events.jsonl', [] if len(evs) == args.expect_events
                                      else [f'{len(evs)} event rows, expected {args.expect_events}'])
        by_case = OrderedDict()
        for e in evs:
            by_case.setdefault(e.get('case_id'), []).append(e)
        for cid, rows in by_case.items():
            checks['monotonic'].record(f'{cid} (events.jsonl)', monotonic_problems(rows, 'events.jsonl'))
            raw = raw_for(cid)
            if raw is not None and raw['total_events'] is not None and len(rows) != raw['total_events']:
                checks['consistency'].record(f'{cid} (events.jsonl)',
                                             [f'{len(rows)} rows, raw Total events {raw["total_events"]}'])
    if cases is None and evs is None:
        checks['monotonic'].skipped = 'no cases/events file'

    dps = data.get('decision_points')
    if dps is None:
        checks['decision_points'].skipped = 'no decision-points file'
    else:
        for i, dp in enumerate(dps):
            cid = dp.get('case_id', f'<row {i + 1}>')
            checks['decision_points'].record(cid, decision_point_problems(dp, raw_for(cid), bool(args.raw)))
    return checks


def monotonic_problems(events, label):
    probs, prev = [], None
    for e in events:
        ts = e.get('timestamp')
        if not isinstance(ts, str):
            continue
        if prev is not None and ts < prev:
            probs.append(f'{label}: event {e.get("event_id")} at {ts} precedes previous {prev}')
        prev = ts
    return probs


def leakage_problems(rec, raw):
    prof = leak_profile(raw)
    ae = rec.get('at_escalation') or {}
    probs = scan_for_leaks(ae, prof, 'at_escalation')
    for v in ae.get('visible_event_ids') or []:
        s = event_seq(v)
        if s is None or s >= 3:
            probs.append(f'at_escalation.visible_event_ids contains {v!r} (>= 003)')
    for ev in rec.get('events') or []:
        if ev.get('visible_at_escalation') and (event_seq(ev.get('event_id')) or 0) >= 3:
            probs.append(f'events[{ev.get("event_id")}].visible_at_escalation is true')
    for att in rec.get('attachments') or []:
        first = raw['attachment_first_seq'].get(att.get('name'))
        if att.get('visible_at_escalation') and (first is None or first >= 3):
            probs.append(f'attachment {att.get("name")} visible_at_escalation but first linked at '
                         f'{"no event" if first is None else "event %03d" % first}')
    return probs


def consistency_problems(rec, raw):
    probs = []
    n = len(rec.get('events') or [])
    if raw['total_events'] is None:
        probs.append('raw history has no "Total events"')
    else:
        if n != raw['total_events']:
            probs.append(f'events count {n} != raw Total events {raw["total_events"]}')
        ne = (rec.get('meta') or {}).get('n_events')
        if ne is not None and ne != raw['total_events']:
            probs.append(f'meta.n_events {ne} != raw Total events {raw["total_events"]}')
    if len(raw['events']) != raw['total_events']:
        probs.append(f'raw history parses {len(raw["events"])} events but declares {raw["total_events"]}')
    dec = rec.get('decision') or {}
    ev3 = next((e for e in raw['events'] if e['seq'] == 3), None)
    if ev3 is None:
        probs.append('raw history has no event 003')
    elif norm(dec.get('message', '')) != norm(ev3['body']):
        probs.append(f'decision.message differs from raw event 003 body: {dec.get("message", "")[:60]!r} '
                     f'vs {ev3["body"][:60]!r}')
    if norm(dec.get('recipient_raw', '')) != norm(raw['recipient'] or ''):
        probs.append(f'decision.recipient_raw {dec.get("recipient_raw")!r} != index Recipient '
                     f'{raw["recipient"]!r}')
    disk = set(raw['attachments_on_disk'])
    for href in raw['listed_attachments']:
        if os.path.basename(href) not in disk:
            probs.append(f'index lists {href} but file is missing')
    listed = {os.path.basename(h) for h in raw['listed_attachments']}
    rec_names = {a.get('name') for a in rec.get('attachments') or []}
    if rec_names != listed:
        probs.append(f'record attachments {sorted(rec_names, key=str)} != index-listed {sorted(listed)}')
    return probs


def _event_seqs_in(obj, path='input'):
    """Yield (path, seq) for every event-like object or event-id list inside obj."""
    if isinstance(obj, dict):
        if 'seq' in obj or 'event_id' in obj:
            s = obj.get('seq') if isinstance(obj.get('seq'), int) else event_seq(obj.get('event_id'))
            if s is not None:
                yield path, s
        for k, v in obj.items():
            if k in ('visible_event_ids', 'event_ids') and isinstance(v, list):
                for i, x in enumerate(v):
                    s = event_seq(x)
                    yield f'{path}.{k}[{i}]', (s if s is not None else 999)
            else:
                yield from _event_seqs_in(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _event_seqs_in(v, f'{path}[{i}]')


def decision_point_problems(dp, raw, have_raw):
    probs = []
    if 'input' not in dp:
        return ['record has no `input` field']
    for p, s in _event_seqs_in(dp['input']):
        if s >= 3:
            probs.append(f'{p}: event seq {s} (>= 3) in input')
    if raw is None:
        if have_raw:
            probs.append('no raw case folder to compare against')
        return probs
    probs += scan_for_leaks(dp['input'], leak_profile(raw), 'input')
    avail = [('attachments_available', a) for a in dp.get('attachments_available') or []]
    if isinstance(dp['input'], dict):
        avail += [('input.attachments_available', a) for a in dp['input'].get('attachments_available') or []]
    for i, (where, a) in enumerate(avail):
        name = a.get('name') or os.path.basename(a.get('href', '')) if isinstance(a, dict) else os.path.basename(str(a))
        first = raw['attachment_first_seq'].get(name)
        if first is None or first >= 3:
            probs.append(f'{where} {name!r} first mentioned at '
                         f'{"no event" if first is None else "event %03d" % first}')
    return probs


def summarize(checks, limit=5):
    lines, ok = [], True
    for c in checks.values():
        st = c.status()
        ok &= st != 'FAIL'
        if st == 'SKIP':
            lines.append(f'[SKIP] {c.name:<16} {c.skipped}')
            continue
        lines.append(f'[{st}] {c.name:<16} pass={c.passed} fail={c.failed}')
        for cid in list(c.problems)[:limit]:
            lines.append(f'         {cid}: {c.problems[cid][0]}' +
                         (f'  (+{len(c.problems[cid]) - 1} more)' if len(c.problems[cid]) > 1 else ''))
        if c.failed > limit:
            lines.append(f'         ... first offenders: {", ".join(map(str, list(c.problems)[:limit]))} '
                         f'(+{c.failed - limit} more)')
    lines.append('RESULT: ' + ('PASS' if ok else 'FAIL'))
    return '\n'.join(lines), ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cases_pos', nargs='?', help='cases.jsonl (same as --cases)')
    ap.add_argument('--cases')
    ap.add_argument('--events')
    ap.add_argument('--decision-points', dest='decision_points')
    ap.add_argument('--raw', help='"Delivery & Logistics" raw case directory')
    ap.add_argument('--schema', default=DEFAULT_SCHEMA)
    ap.add_argument('--expect-cases', type=int, default=50)
    ap.add_argument('--expect-events', type=int, default=228)
    ap.add_argument('--json-report')
    args = ap.parse_args(argv)
    if not (args.cases_pos or args.cases or args.events or args.decision_points):
        # no file named: validate the agent-facing outputs in data/delivery/agent/
        for attr, name in (('cases', 'cases.jsonl'), ('events', 'events.jsonl'),
                           ('decision_points', 'decision_points.jsonl')):
            path = os.path.join(AGENT_DIR, name)
            if os.path.exists(path):
                setattr(args, attr, path)
    checks = run(args)
    text, ok = summarize(checks)
    print(text)
    if args.json_report:
        with open(args.json_report, 'w', encoding='utf-8') as fh:
            json.dump({'ok': ok, 'checks': [c.as_dict() for c in checks.values()]}, fh, indent=2,
                      ensure_ascii=False)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
