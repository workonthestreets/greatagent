#!/usr/bin/env python3
"""Render an ANSWERS/ folder (or an eval run's answers/) as one self-contained HTML page.

  python viewer.py ANSWERS            -> ANSWERS/index.html
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

BADGE = {"act": ("Act", "act"), "request_information": ("Ask", "ask"), "escalate_to_human": ("Human", "esc"),
         "hold_no_action": ("Hold", "hold"), "decline": ("Decline", "dec")}

CSS = """
:root{--bg:#f6f5f2;--card:#fff;--ink:#1c1b19;--mute:#6b6862;--line:#e4e1da;--act:#1f7a4d;--ask:#2a5db0;--esc:#b4462b;--hold:#7a6a1f;--dec:#6b3fa0;--quote:#f1efe9}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1d1c1a;--ink:#ecebe7;--mute:#a19e96;--line:#33312d;--quote:#262522;--act:#5fc391;--ask:#7ea6ec;--esc:#ec8a70;--hold:#d8c46a;--dec:#b897e6}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}
main{max-width:1040px;margin:0 auto;padding:28px 16px 60px}h1{font-size:26px;margin:0 0 4px}.sub{color:var(--mute);margin:0 0 20px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:22px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.stat b{font-size:24px;display:block}.stat span{color:var(--mute);font-size:13px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:10px 0;overflow:hidden}
summary{cursor:pointer;padding:14px 16px;display:flex;gap:12px;align-items:baseline;list-style:none}summary::-webkit-details-marker{display:none}
.num{color:var(--mute);font-variant-numeric:tabular-nums;min-width:34px}.ttl{font-weight:600;flex:1}.one{color:var(--mute);font-size:14px;display:block;font-weight:400}
.b{font-size:12px;font-weight:700;padding:2px 9px;border-radius:99px;border:1.5px solid currentColor;white-space:nowrap}
.act{color:var(--act)}.ask{color:var(--ask)}.esc{color:var(--esc)}.hold{color:var(--hold)}.dec{color:var(--dec)}
.body{padding:0 16px 16px;border-top:1px solid var(--line)}h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);margin:16px 0 6px}
.msg{background:var(--quote);border-radius:8px;padding:10px 12px;margin:6px 0;white-space:pre-wrap}.meta{font-size:13px;color:var(--mute)}
ul{margin:4px 0;padding-left:20px}.catch{border-left:3px solid var(--esc);padding-left:10px;margin:6px 0}.ok{color:var(--act)}
.flag{display:inline-block;font-size:12px;color:var(--esc);margin-left:6px}
"""


def esc(s) -> str:
    return html.escape(str(s or ""))


def render(answers: Path) -> str:
    results = []
    for rj in answers.glob("*/result.json"):
        try:
            results.append(json.loads(rj.read_text()))
        except Exception:  # noqa: BLE001
            continue
    results.sort(key=lambda r: (0, int(r["answer_id"])) if str(r["answer_id"]).isdigit() else (1, str(r["answer_id"])))
    failures = [p.parent.name for p in answers.glob("*/ANSWER.md") if not (p.parent / "result.json").exists()]

    n = len(results)
    by = {k: sum(1 for r in results if r["plan"].get("decision_type") == k) for k in BADGE}
    catches = sum(1 for r in results for rd in r.get("review_rounds") or [] if (rd.get("review") or {}).get("verdict") in ("revise", "escalate_instead"))
    sent = sum(1 for r in results for e in r["executed"] if e["action"].get("tool") == "send_message" and e["status"] == "done")
    recovered = sum(1 for r in results for e in r["executed"] if e["status"] == "failed" or e.get("recovered_after"))

    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>Desk Agent Results</title><style>{CSS}</style></head><body><main>",
           "<h1>Delivery Desk Agent — results</h1>",
           f"<p class=sub>{n} cases decided{' · ' + str(len(failures)) + ' system failures' if failures else ''} · every action reviewed before sending</p>",
           "<div class=stats>"]
    for label, val in [("Act", by["act"]), ("Ask", by["request_information"]), ("Human handover", by["escalate_to_human"]),
                       ("Hold / no action", by["hold_no_action"]), ("Messages sent", sent), ("Reviewer catches", catches),
                       ("Tool failures recovered", recovered)]:
        out.append(f"<div class=stat><b>{val}</b><span>{label}</span></div>")
    out.append("</div>")

    for r in results:
        p = r["plan"]
        lab, cls = BADGE.get(p.get("decision_type"), (p.get("decision_type"), "hold"))
        flags = ""
        if not r.get("approved", True):
            flags += "<span class=flag>reviewer blocked autonomy</span>"
        out.append(f"<details><summary><span class=num>{esc(r['answer_id'])}</span><span class=ttl>{esc(r['title'])}"
                   f"<span class=one>{esc(p.get('decision_summary'))}</span></span>{flags}<span class='b {cls}'>{esc(lab)}</span></summary><div class=body>")
        out.append(f"<h3>Situation</h3><div>{esc(p.get('situation') or (r.get('pre_handover_plan') or {}).get('situation'))}</div>")
        out.append("<h3>Actions</h3>")
        if not r["executed"]:
            out.append("<div class=meta>No outbound action (deliberate hold).</div>")
        for e in r["executed"]:
            a = e["action"]
            ref = ""
            if e.get("result"):
                ref = e["result"].get("message_id") or e["result"].get("ticket_id") or e["result"].get("follow_up_id") or ""
            who = esc(a.get("to_name") or a.get("to_role") or "Desk supervisor")
            out.append(f"<div class=meta>{esc(a.get('tool'))} → {who}{(' · ' + esc(a.get('channel'))) if a.get('channel') else ''} · "
                       f"<b class={'ok' if e['status'] == 'done' else 'esc'}>{esc(e['status'])}</b> {esc(ref)}{(' · ' + esc(e.get('error'))) if e.get('error') else ''}</div>")
            if a.get("body"):
                out.append(f"<div class=msg>{esc(a.get('body'))}</div>")
        caught = [(rd, i) for rd in r.get("review_rounds") or [] for i in ((rd.get("review") or {}).get("issues") or [])
                  if i.get("severity") in ("critical", "major")]
        if caught:
            out.append("<h3>Caught by the reviewer before sending</h3>")
            for rd, i in caught:
                out.append(f"<div class=catch><b>{esc(i.get('severity'))}</b> (round {rd['round']}): {esc(i.get('problem'))}<br><span class=meta>fix: {esc(i.get('fix'))}</span></div>")
        if p.get("not_doing"):
            out.append("<h3>Deliberately not done</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in p["not_doing"]) + "</ul>")
        if p.get("risk_flags"):
            out.append("<h3>Risk flags</h3><ul>" + "".join(f"<li>{esc(x)}</li>" for x in p["risk_flags"]) + "</ul>")
        out.append(f"<h3>Closes when</h3><div>{esc(p.get('closes_when'))}</div>")
        out.append("</div></details>")
    for f in failures:
        out.append(f"<details><summary><span class=num>{esc(f)}</span><span class=ttl>System failure — handed to a human</span><span class='b esc'>Error</span></summary></details>")
    out.append("</main></body></html>")
    return "\n".join(out)


def main():
    answers = Path(sys.argv[1] if len(sys.argv) > 1 else "ANSWERS")
    if (answers / "answers").is_dir():
        answers = answers / "answers"
    html_text = render(answers)
    target = answers / "index.html"
    target.write_text(html_text, encoding="utf-8")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
