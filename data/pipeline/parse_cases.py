#!/usr/bin/env python3
"""Track-agnostic parser for HackatonPublicCases (index.md + history.md + attachments/).

Usage:
    python3 -I parse_cases.py <track_dir> <out.jsonl> [--attachments-text <dir>] [--case-prefix DEL]

Reads every <track_dir>/<NNN>/ case folder and writes one JSON object per case.
Nothing here is track-specific: sections, bullets and events are captured as found.
Attachment text is extracted with pdftotext (PDF), tesseract (PNG, if installed) or read directly.
"""
import argparse
import json
import os
import re
import subprocess
import sys

H1_RE = re.compile(r'^#\s+Case\s+(\d+):\s*(.*)$', re.M)
SECTION_RE = re.compile(r'^##\s+(.+?)\s*$', re.M)
BULLET_RE = re.compile(r'^-\s+\*\*(.+?):\*\*\s*(.*)$', re.M)
EVENT_RE = re.compile(
    r'<a id="event-(\d+)"></a>\s*\n##\s+(.+?)\s+—\s+event\s+(\d+)\s*\n(.*?)(?=\n<a id="event-|\Z)', re.S)
TOTAL_RE = re.compile(r'Total events:\s*(\d+)')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
TS_RE = re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) UTC$')


def iso(ts_raw):
    m = TS_RE.match(ts_raw.strip())
    return f"{m.group(1)}T{m.group(2)}Z" if m else ts_raw.strip()


def split_sections(md):
    parts = SECTION_RE.split(md)
    secs, order = {}, []
    for i in range(1, len(parts), 2):
        name, body = parts[i].strip(), parts[i + 1].strip()
        secs[name] = body
        order.append(name)
    return secs, order


def parse_bullets(text):
    return {k.strip(): v.strip() for k, v in BULLET_RE.findall(text)}


def strip_bullets(text):
    return BULLET_RE.sub('', text).strip()


def parse_index(path):
    md = open(path, encoding='utf-8').read()
    m = H1_RE.search(md)
    number, title = (m.group(1), m.group(2).strip()) if m else (None, None)
    secs, order = split_sections(md)
    details = parse_bullets(secs.get('Case details', ''))
    next_action = None
    for name in order:
        if name.lower().startswith('next action'):
            body = secs[name]
            next_action = {'section': name, 'text': strip_bullets(body)}
            next_action.update({k.lower().replace(' ', '_'): v for k, v in parse_bullets(body).items()})
    listed = [{'name': n, 'href': h} for n, h in LINK_RE.findall(secs.get('Attachments', ''))]
    plain = {k: v for k, v in secs.items() if k not in ('Case details',)}
    return {'number': number, 'title': title, 'details': details, 'sections': plain,
            'section_order': order, 'next_action': next_action, 'attachments_listed': listed}


def parse_history(path):
    md = open(path, encoding='utf-8').read()
    total = TOTAL_RE.search(md)
    events = []
    for m in EVENT_RE.finditer(md):
        eid, ts, _eid2, rest = m.groups()
        meta = parse_bullets(rest)
        body = strip_bullets(rest)
        events.append({'event_id': eid, 'seq': int(eid), 'timestamp': iso(ts), 'timestamp_raw': ts.strip(),
                       'meta': meta, 'body': body,
                       'links': [{'name': n, 'href': h} for n, h in LINK_RE.findall(body)]})
    return {'total_events_declared': int(total.group(1)) if total else None, 'events': events}


def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.pdf':
            out = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True, timeout=60)
            return out.stdout, 'pdftotext'
        if ext in ('.png', '.jpg', '.jpeg'):
            out = subprocess.run(['tesseract', path, '-'], capture_output=True, text=True, timeout=120)
            return (out.stdout if out.returncode == 0 else ''), 'tesseract'
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read(), 'plain'
    except FileNotFoundError as exc:  # extractor missing
        return '', f'extractor-missing:{exc.filename}'
    except Exception as exc:  # pragma: no cover
        return '', f'error:{exc}'


def collect_attachments(case_dir, text_dir, case_id):
    att_dir = os.path.join(case_dir, 'attachments')
    out = []
    if not os.path.isdir(att_dir):
        return out
    for name in sorted(os.listdir(att_dir)):
        p = os.path.join(att_dir, name)
        if not os.path.isfile(p):
            continue
        text, method = extract_text(p)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        rec = {'name': name, 'href': f'attachments/{name}', 'bytes': os.path.getsize(p),
               'extractor': method, 'text': text}
        if text_dir:
            os.makedirs(text_dir, exist_ok=True)
            tp = os.path.join(text_dir, f'{case_id}__{name}.txt')
            with open(tp, 'w', encoding='utf-8') as fh:
                fh.write(text)
            rec['text_path'] = os.path.relpath(tp, os.path.dirname(text_dir.rstrip('/')))
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('track_dir')
    ap.add_argument('out_jsonl')
    ap.add_argument('--attachments-text', default=None)
    ap.add_argument('--case-prefix', default=None, help='e.g. DEL -> case_id DEL-001')
    args = ap.parse_args()

    track_name = os.path.basename(os.path.normpath(args.track_dir))
    prefix = args.case_prefix or re.sub(r'[^A-Za-z]', '', track_name)[:3].upper()
    n = 0
    os.makedirs(os.path.dirname(os.path.abspath(args.out_jsonl)), exist_ok=True)
    with open(args.out_jsonl, 'w', encoding='utf-8') as out:
        for case in sorted(os.listdir(args.track_dir)):
            cdir = os.path.join(args.track_dir, case)
            if not os.path.isdir(cdir) or not re.fullmatch(r'\d+', case):
                continue
            idx = parse_index(os.path.join(cdir, 'index.md'))
            hist_path = os.path.join(cdir, 'history.md')
            hist = parse_history(hist_path) if os.path.exists(hist_path) else {'total_events_declared': None, 'events': []}
            case_id = f'{prefix}-{case}'
            rec = {'case_id': case_id, 'track': track_name, 'case_number': case, 'title': idx['title'],
                   'source_dir': os.path.abspath(cdir),
                   'details': idx['details'], 'sections': idx['sections'], 'section_order': idx['section_order'],
                   'next_action': idx['next_action'], 'attachments_listed': idx['attachments_listed'],
                   'total_events_declared': hist['total_events_declared'], 'events': hist['events'],
                   'attachments': collect_attachments(cdir, args.attachments_text, case_id)}
            if hist['total_events_declared'] is not None and hist['total_events_declared'] != len(hist['events']):
                rec['warnings'] = [f"declared {hist['total_events_declared']} events, parsed {len(hist['events'])}"]
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            n += 1
    print(f'{track_name}: {n} cases -> {args.out_jsonl}', file=sys.stderr)


if __name__ == '__main__':
    main()
