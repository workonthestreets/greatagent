#!/usr/bin/env python3
"""Collect planner JSON files written by the proxy agents into plans.jsonl.
Usage: python3 -I proxy_eval_collect.py <results_dir> <plans.jsonl>
Each file <case_id>.json holds the propose_plan object (optionally wrapped in {"plan": ...}).
"""
import json, os, sys
d, out = sys.argv[1], sys.argv[2]
n = bad = 0
with open(out, 'w', encoding='utf-8') as fh:
    for name in sorted(os.listdir(d)):
        if not name.endswith('.json'):
            continue
        cid = name[:-5]
        try:
            raw = open(os.path.join(d, name), encoding='utf-8').read().strip()
            raw = raw[raw.find('{'):raw.rfind('}') + 1]
            obj = json.loads(raw)
            plan = obj.get('plan', obj)
            fh.write(json.dumps({'case_id': cid, 'plan': plan}, ensure_ascii=False) + '\n'); n += 1
        except Exception as exc:
            bad += 1; print('bad', name, exc, file=sys.stderr)
print(json.dumps({'collected': n, 'bad': bad, 'out': out}))
