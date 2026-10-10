#!/usr/bin/env python3
"""Render planner prompts for a proxy run of the desk agent (Roman's planner manual executed by Claude Code agents).

Usage: python3 -I proxy_eval_prepare.py <raw_cases.jsonl> <out_dir> [--mode cutoff|full] [--track "Delivery & Logistics"]
For every case writes <out_dir>/<case_id>.prompt.md containing the case exactly as deskagent/loader.py shows it:
  cutoff mode (public-eval): index without Overview / Next action / Outcome / Boundaries and without Status/Updated/Completed,
  history with only the events before the first "Agent action" stage (Stage lines kept, as the loader keeps them).
  full mode: everything (used for stress cases, which carry a _reference.md rubric in Roman's eval).
Also writes <out_dir>/_manifest.json with the hidden events and the later references per case, for leakage scoring.
"""
import argparse
import json
import os
import re

REF_RE = re.compile(r'\b[A-Z]{2,5}-\d{3}(?:-[A-Z0-9]{1,3})?\b')
HIDE_SECTIONS = {'overview', 'next action at escalation', 'outcome', 'boundaries and remaining work', 'summary', 'resolution', 'result'}
HIDE_KEYS = ('status', 'updated', 'completed', 'resolved', 'closed')
TEMPLATE = """Below is the case record as it stands now. The current time is just after the latest visible event ({now}).

<case id="{case_id}" track="{track}" mode="{mode}">
<file name="index.md">
{index}
</file>

<file name="history.md">
{history}
</file>
</case>

Known channels in the record: {channels}
Known parties in the record: {parties}

If the case contains explicit questions addressed to you or the desk, answer them directly in `direct_answer`.
Analyse the case and produce the plan (the propose_plan object)."""


def render_index(rec, mode):
    d = rec['details']
    out = [f"# Case {rec['case_number']}: {rec['title']}", '', '## Case details', '']
    for k, v in d.items():
        if mode == 'cutoff' and k.lower().startswith(HIDE_KEYS):
            continue
        out.append(f'- **{k}:** {v}')
    out.append('')
    for name in rec['section_order']:
        if name == 'Case details':
            continue
        if mode == 'cutoff' and name.lower() in HIDE_SECTIONS:
            continue
        body = rec['sections'].get(name, '')
        if name == 'Attachments' and mode == 'cutoff':
            body = 'Only attachments referenced in the visible history are provided.'
        if name == 'Next action at escalation' and mode == 'full':
            body = rec['next_action']['text'] if rec.get('next_action') else body
        out += [f'## {name}', '', body.strip(), '']
    return '\n'.join(out).strip()


def render_history(rec, events, total_declared, cut):
    head = f"# Case {rec['case_number']} history — {rec['title']}\n\n"
    head += (f"All identities, records and communications are fictional. Events available at this point: {len(events)}." if cut
             else f"All identities, records and communications are fictional. Total events: {total_declared or len(events)}.")
    parts = [head]
    for e in events:
        meta = ''.join(f"- **{k}:** {v}\n" for k, v in e['meta'].items())
        parts.append(f'<a id="event-{e["event_id"]}"></a>\n## {e["timestamp_raw"]} — event {e["event_id"]}\n\n{meta}\n{e["body"]}')
    return '\n\n'.join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw'); ap.add_argument('out_dir'); ap.add_argument('--mode', default='cutoff', choices=['cutoff', 'full'])
    ap.add_argument('--track', default='Delivery & Logistics')
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    manifest = {}
    for line in open(a.raw, encoding='utf-8'):
        rec = json.loads(line); events = rec['events']
        cut_idx = None
        if a.mode == 'cutoff':
            stages = [e['meta'].get('Stage', '').lower() for e in events]
            if any(stages):
                cut_idx = next((i for i, s in enumerate(stages) if 'agent action' in s), None)
                if cut_idx is None:
                    esc = [i for i, s in enumerate(stages) if 'escalation' in s]
                    cut_idx = esc[-1] + 1 if esc else None
        visible = events[:cut_idx] if cut_idx is not None else events
        hidden = events[cut_idx:] if cut_idx is not None else []
        vis_text = '\n'.join(e['body'] for e in visible)
        later_refs = sorted(set(REF_RE.findall('\n'.join(e['body'] for e in hidden))) - set(REF_RE.findall(vis_text)))
        channels, parties = [], []
        for e in visible:
            for key, bucket in (('Channel', channels), ('From', parties), ('To', parties)):
                v = e['meta'].get(key, '').strip()
                if v and v not in bucket:
                    bucket.append(v)
        prompt = TEMPLATE.format(now=visible[-1]['timestamp_raw'] if visible else 'unknown', case_id=rec['case_number'], track=a.track,
                                 mode='public-eval' if a.mode == 'cutoff' else 'reality', index=render_index(rec, a.mode),
                                 history=render_history(rec, visible, rec.get('total_events_declared'), cut_idx is not None),
                                 channels=', '.join(channels) or '(none recorded)', parties='; '.join(parties) or '(none recorded)')
        with open(os.path.join(a.out_dir, f"{rec['case_id']}.prompt.md"), 'w', encoding='utf-8') as fh:
            fh.write(prompt)
        manifest[rec['case_id']] = {'case_number': rec['case_number'], 'visible_events': [e['event_id'] for e in visible],
                                    'hidden_events': [e['event_id'] for e in hidden], 'later_refs': later_refs,
                                    'gold_recipient': (rec.get('next_action') or {}).get('recipient'), 'gold_channel': (rec.get('next_action') or {}).get('channel'),
                                    'gold_message': next((e['body'] for e in hidden if 'agent action' in e['meta'].get('Stage', '').lower()), None)}
    json.dump(manifest, open(os.path.join(a.out_dir, '_manifest.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'{len(manifest)} prompts -> {a.out_dir}')


if __name__ == '__main__':
    main()
