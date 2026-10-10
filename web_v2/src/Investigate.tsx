import { nice, pct, type CaseItem, type Run, type Spec } from "./api";
import type { Runs } from "./App";

type Row = [string, string | [string, number][] | null | undefined];
type Tile = {
  id: string; name: string; tag?: string; purpose?: string; top: string; p?: number; threshold?: number;
  tone?: "" | "warn" | "bad"; cap?: string; details: Row[];
};

function buildTiles(run: Run, spec: Spec | null) {
  const pre = run.preprocess, raw = run.classifier_raw;
  const model: Tile[] = [], rule: Tile[] = [];
  const cls = (id: string) => spec?.classifications.find((c) => c.id === id);
  const rmap = spec?.routing_map;
  const route = pre.routing;
  const rr = spec?.routing_rules ?? [];
  const findRule = (re: RegExp) => rr.find((x) => re.test(x));

  if (pre.request) {
    const top = pre.request.intent, c = cls("request_intent");
    const probs = raw.request_intent?.probabilities ?? Object.fromEntries([[top, pre.request.confidence], ...pre.request.alternatives.map((a) => [a.intent, a.p])]);
    const p = probs[top] ?? pre.request.confidence;
    const low = p < 0.6 || pre.request.low_margin;
    model.push({
      id: "request_intent", name: "Request intent", tag: "Choice", purpose: c?.purpose, top: nice(top), p, tone: low ? "warn" : "",
      cap: low ? (pre.request.low_margin ? "Close call: the top two intents are within 15 points" : "Low confidence (under 60%)") : "Confidence",
      details: [["Description", c?.options?.[top]], ["Next most likely", Object.entries(probs).filter(([k]) => k !== top).sort((a, b) => b[1] - a[1]).slice(0, 3)]],
    });
  }
  for (const [fid, f] of Object.entries(pre.flags ?? {})) {
    model.push({
      id: fid, name: nice(fid), tag: "Yes or no", purpose: cls(fid)?.purpose, top: f.fired ? "Yes" : "No", p: f.p, threshold: f.threshold,
      tone: f.fired ? "bad" : "", cap: `Probability of yes. Flags at ${pct(f.threshold)} or above.`, details: [["Question asked", cls(fid)?.instructions]],
    });
  }
  for (const r of route?.required_info ?? []) {
    model.push({
      id: "ri_" + r.id, name: "Required info: " + nice(r.id).toLowerCase(), tag: "Yes or no",
      purpose: "Whether the customer side has already supplied what the owner needs before acting.",
      top: r.present ? "Present" : "Missing", p: r.p_present, threshold: 0.5, tone: r.present ? "" : "bad",
      cap: "Probability it is present. Counts as present at 50% or above.", details: [["Question asked", r.question]],
    });
  }
  const intentTeams = rmap?.intents?.[pre.request?.intent ?? ""]?.teams ?? [];
  if (raw.team) {
    const top = raw.team.choice, p = raw.team.probabilities[top];
    const t = intentTeams.find((x) => x.id === top);
    model.push({
      id: "team", name: "Team", tag: "Choice", purpose: "Which team inside the responsible party receives the message.", top: t?.label ?? nice(top), p,
      tone: p < 0.6 ? "warn" : "", cap: p < 0.6 ? "Low confidence (under 60%)" : "Confidence",
      details: [["Description", t?.pick_when], ["Next most likely", Object.entries(raw.team.probabilities).filter(([k]) => k !== top).sort((a, b) => b[1] - a[1]).slice(0, 3)]],
    });
  } else if (route?.team?.id) {
    const t = intentTeams.find((x) => x.id === route.team.id);
    rule.push({ id: "team", name: "Team", purpose: "Which team inside the responsible party receives the message.", top: route.team.label ?? nice(route.team.id),
      details: [["Description", "This intent has only one candidate team, so no model call was needed. " + (t?.pick_when ?? "")]] });
  }
  if (route) {
    rule.push({ id: "party", name: "Party", purpose: "Which kind of organisation or person receives the message.", top: nice(route.party),
      details: [["Description", rmap?.parties?.[route.party] ?? "Looked up from the routing map for the resolved intent."]] });
    const missing = route.required_info.filter((r) => !r.present).map((r) => nice(r.id).toLowerCase());
    rule.push({ id: "missing", name: "Missing information", purpose: "Whether the customer side must supply something before the owner can act.",
      top: route.missing_information ? "Yes" : "No", tone: route.missing_information ? "bad" : "",
      details: [["Description", route.missing_information ? "Still needed: " + missing.join(", ") + "." : "Nothing is required, or everything required is already present."], ["Rule", findRule(/^missing_information/)]] });
    const t = route.target;
    const value = t.kind === "customer" ? "Customer" : t.kind === "team" ? t.label ?? "Team" : "Human review";
    rule.push({ id: "target", name: "Target", purpose: "Who the generated message is addressed to.", top: value,
      details: [["Description", t.kind === "customer" ? t.note : t.kind === "team" ? "Nothing is missing, so the message goes to the responsible team." : rmap?.parties?.human_review], ["Rule", findRule(/^target = the customer/)]] });
  }
  if (pre.channel) {
    const alt = pre.channel.generator_alternate;
    rule.push({ id: "channel", name: "Channel", purpose: "Which kind of channel the message goes out on.", top: nice(pre.channel.kind),
      details: [["Description", "Basis: " + pre.channel.basis + "."], ["Generator option", alt ? `May switch to ${alt.channel} when: ${alt.use_when}` : null]] });
  }
  rule.push({ id: "review", name: "Needs human review", purpose: "Whether a person should look at this case before anything is sent.",
    top: pre.needs_human_review ? "Yes" : "No", tone: pre.needs_human_review ? "bad" : "",
    details: [["Description", pre.needs_human_review ? (pre.review_reasons.join("; ") || "Flagged for review.") : "The intent is a known one and no safety, injection or unauthorised-ask flag fired."]] });
  return { model, rule };
}

const Chevron = () => <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>;

function TileView({ t, isRule }: { t: Tile; isRule: boolean }) {
  const blocks = t.details.filter(([, v]) => v && (!Array.isArray(v) || v.length));
  return (
    <article className={`tile${isRule ? " rule" : ""}${t.tone ? " " + t.tone : ""}`}>
      <div className="row"><div className="name">{t.name}</div><div className="ttag">{isRule ? "Rule" : t.tag}</div></div>
      {t.purpose && <p className="purpose">{t.purpose}</p>}
      <div className="result"><div className="top-choice">{t.top}</div>{!isRule && t.p != null && <div className="pct">{pct(t.p)}</div>}</div>
      {!isRule && t.p != null && (
        <>
          <div className="bar"><i style={{ width: `${Math.max(1, t.p * 100)}%` }} />{t.threshold != null && <u style={{ left: `calc(${t.threshold * 100}% - 1px)` }} />}</div>
          <div className="cap">{t.cap}</div>
        </>
      )}
      {blocks.length ? (
        <details>
          <summary><span>{isRule ? "Why this decision" : t.tag === "Choice" ? "About this choice" : "About this question"}</span><Chevron /></summary>
          <div className="more">
            {blocks.map(([label, val]) => (
              <div key={label}>
                <h4>{label}</h4>
                {Array.isArray(val) ? val.map(([k, v]) => <div className="runner" key={k}><span>{nice(k)}</span><span>{pct(v)}</span></div>) : <p>{val}</p>}
              </div>
            ))}
          </div>
        </details>
      ) : <div style={{ height: 12 }} />}
    </article>
  );
}

function Section({ title, tiles, isRule }: { title: string; tiles: Tile[]; isRule: boolean }) {
  return (
    <section>
      <div className="sec-head"><h2>{title} <span className="muted small">{tiles.length}</span></h2></div>
      <div className="grid">{tiles.map((t) => <TileView key={t.id} t={t} isRule={isRule} />)}</div>
    </section>
  );
}

const LEVEL = { low: 1, medium: 2, high: 3 } as const;
const MARK = { pass: "✓", warn: "!", fail: "✕", na: "–" } as const;

export default function Investigate({ runs, cases, selected, onSelect, spec, onBack }: {
  runs: Runs; cases: CaseItem[] | null; selected: string; onSelect: (id: string) => void; spec: Spec | null; onBack: () => void;
}) {
  const run: Run | undefined = runs[selected];
  const ran = Object.keys(runs).sort();
  const picker = ran.length > 1 && (
    <select value={selected} onChange={(e) => onSelect(e.target.value)}>
      {ran.map((id) => <option key={id} value={id}>{cases?.find((c) => c.id === id)?.title ?? id}</option>)}
    </select>
  );
  if (!run) return <main><div className="row">{picker}</div><div className="card muted">{selected} has not been run yet. <a onClick={onBack}>Go to Cases</a>, select it and press Run agent.</div></main>;
  const pre = run.preprocess, r = run.response;
  const { model, rule } = buildTiles(run, spec);
  const passed = run.checks.filter((c) => c.status === "pass").length;
  const worst = run.checks.some((c) => c.status === "fail") ? "bad" : run.checks.some((c) => c.status === "warn") ? "warn" : "";
  const u = run.meta.usage;

  return (
    <main>
      <div className="row"><h1>{cases?.find((c) => c.id === run.case)?.title ?? run.case} <span className="muted small">confidence report</span></h1><div className="demo">{picker}<button className="small" onClick={onBack}>← Back to case</button></div></div>
      {pre.status === "error" && <div className="card error">Pre-processing failed ({pre.error}). The agent ran on the events alone.</div>}
      {run.error && <div className="card error">The agent did not return a response: {run.error}</div>}

      <div className="stats">
        <div className="stat"><div className="stat-v">{r ? <span className={`badge conf-${r.confidence}`}>{r.confidence}</span> : "–"}</div><div className="muted small">Agent confidence (self-reported)</div></div>
        <div className="stat"><div className="stat-v">{pre.request ? pct(pre.request.confidence) : "–"}</div><div className="muted small">Intent confidence (classifier)</div></div>
        <div className="stat"><div className="stat-v"><span className={`badge ${pre.needs_human_review ? "bad" : "ok"}`}>{pre.needs_human_review ? "Needed" : "Not needed"}</span></div><div className="muted small">Human review (classifier)</div></div>
        <div className={`stat ${worst ? "hl-" + worst : ""}`}><div className="stat-v">{passed}/{run.checks.length}</div><div className="muted small">Agreement checks passed</div></div>
        <div className="stat"><div className="stat-v">{run.meta.total_s != null ? `${run.meta.total_s}s` : "–"}</div><div className="muted small">{run.meta.model ?? "no model"}</div></div>
        <div className="stat"><div className="stat-v">{u ? (u.input_tokens + u.cache_read_input_tokens + u.output_tokens).toLocaleString() : "–"}</div><div className="muted small">Agent tokens</div></div>
      </div>

      {r && (
        <section>
          <div className="sec-head"><h2>Agent</h2></div>
          <div className="grid two">
            <article className="tile">
              <div className="row"><div className="name">Agent confidence</div><div className="ttag">Self-reported</div></div>
              <p className="purpose">The model's own rating of its decision. The API gives no token probabilities, so this is a level, not a percentage. Read it next to the agreement checks.</p>
              <div className="result"><div className="top-choice">{nice(r.confidence)}</div></div>
              <div className="meter">{[1, 2, 3].map((i) => <i key={i} className={i <= LEVEL[r.confidence] ? `on conf-${r.confidence}` : ""} />)}</div>
              <div style={{ height: 12 }} />
            </article>
            <article className="tile">
              <div className="row"><div className="name">Rationale</div><div className="ttag">Agent</div></div>
              <p className="rationale">{r.rationale}</p>
              <div className="flagrow">
                {(["safety", "injection_suspected", "authority_boundary"] as const).map((k) =>
                  <span key={k} className={`tag ${r.flags[k] ? "tag-bad" : ""}`}>{nice(k)}: {r.flags[k] ? "yes" : "no"}</span>)}
              </div>
            </article>
          </div>
        </section>
      )}

      {run.checks.length > 0 && (
        <section>
          <div className="sec-head"><h2>Agreement checks <span className="muted small">classifier hints vs agent output</span></h2></div>
          <ul className="checks">
            {run.checks.map((c) => (
              <li key={c.id} className={`chk ${c.status}`}>
                <span className="mark">{MARK[c.status]}</span>
                <div><strong>{c.label}</strong><div className="muted small">{c.detail}</div></div>
              </li>
            ))}
          </ul>
        </section>
      )}

      <Section title="Classifier: model classifications" tiles={model} isRule={false} />
      <Section title="Classifier: rule-based decisions" tiles={rule} isRule />

      {pre.guardrails && pre.guardrails.length > 0 && (
        <section>
          <div className="sec-head"><h2>Guardrails given to the agent <span className="muted small">{pre.guardrails.length}</span></h2></div>
          <ul className="card guardrails">{pre.guardrails.map((g, i) => <li key={i}>{g}</li>)}</ul>
        </section>
      )}
      <p className="muted small foot">
        Descriptions from the classifier spec{spec ? "" : " (not loaded: api_v2 unreachable)"}.
        {pre.usage && ` Classifier: ${pre.usage.calls} calls, ${pre.usage.input_tokens.toLocaleString()} input tokens, $${pre.usage.cost_usd.toFixed(5)} via ${pre.usage.provider}.`}
      </p>
    </main>
  );
}
