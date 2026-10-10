import { nice, pct, type CaseItem, type Run, type Spec } from "./api";
import type { Runs } from "./App";
import { ArrowLeft, Check, X } from "./icons";
import { Conf } from "./ui";

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
    <article className={`tile${isRule ? " tile--rule" : ""}${t.tone ? " tile--" + t.tone : ""}`}>
      <div className="tile__top"><h3 className="tile__name">{t.name}</h3><span className="tile__tag">{isRule ? "Rule" : t.tag}</span></div>
      {t.purpose && <p className="tile__purpose">{t.purpose}</p>}
      <div className="tile__result"><span className="tile__choice">{t.top}</span>{!isRule && t.p != null && <span className="tile__pct">{pct(t.p)}</span>}</div>
      {!isRule && t.p != null && (
        <>
          <div className="bar"><i style={{ width: `${Math.max(1, t.p * 100)}%` }} />{t.threshold != null && <u style={{ left: `calc(${t.threshold * 100}% - 1px)` }} />}</div>
          <p className="tile__cap">{t.cap}</p>
        </>
      )}
      {blocks.length ? (
        <details>
          <summary><span>{isRule ? "Why this decision" : t.tag === "Choice" ? "About this choice" : "About this question"}</span><Chevron /></summary>
          <div className="tile__more">
            {blocks.map(([label, val]) => (
              <div key={label}>
                <h4 className="mini">{label}</h4>
                {Array.isArray(val) ? val.map(([k, v]) => <div className="runner" key={k}><span>{nice(k)}</span><span>{pct(v)}</span></div>) : <p>{val}</p>}
              </div>
            ))}
          </div>
        </details>
      ) : <div className="tile__pad" />}
    </article>
  );
}

function Section({ title, hint, count, children }: { title: string; hint?: string; count?: number; children: React.ReactNode }) {
  return (
    <section className="trace-section">
      <div className="section-head">
        <h2 className="section-title">{title}{count != null && <span className="tab__count">{count}</span>}</h2>
        {hint && <span className="text-muted body-sm">{hint}</span>}
      </div>
      {children}
    </section>
  );
}

const LEVEL = { low: 1, medium: 2, high: 3 } as const;

export default function Investigate({ runs, cases, selected, onSelect, spec, onBack }: {
  runs: Runs; cases: CaseItem[] | null; selected: string; onSelect: (id: string) => void; spec: Spec | null; onBack: () => void;
}) {
  const run: Run | undefined = runs[selected];
  const ran = Object.keys(runs).sort();
  const titleOf = (id: string) => cases?.find((c) => c.id === id)?.title ?? id;
  const picker = ran.length > 1 && (
    <select className="input input--select" aria-label="Case" value={selected} onChange={(e) => onSelect(e.target.value)}>
      {ran.map((id) => <option key={id} value={id}>{titleOf(id)}</option>)}
    </select>
  );
  if (!run) {
    return (
      <main className="view" id="trace">
        <header className="view-head">
          <h1 className="headline-lg">Decision <span className="emphasis">trace</span>.</h1>
          <p className="text-muted body-lg">{titleOf(selected) || "No case selected"} has not been run yet.</p>
        </header>
        <div className="cluster trace-actions">{picker}<button className="btn btn--secondary" onClick={onBack}><ArrowLeft size={16} /> Go to Cases</button></div>
      </main>
    );
  }

  const pre = run.preprocess, r = run.response;
  const { model, rule } = buildTiles(run, spec);
  const passed = run.checks.filter((c) => c.status === "pass").length;
  const u = run.meta.usage;
  const top = pre.request;

  return (
    <main className="view" id="trace">
      <header className="view-head">
        <h1 className="headline-lg">Decision <span className="emphasis">trace</span>.</h1>
        <p className="text-muted body-lg">{titleOf(run.case)}: how the classifier read the case, what the agent chose, and where the two agree.</p>
        <div className="cluster trace-actions">{picker}<button className="btn btn--secondary" onClick={onBack}><ArrowLeft size={16} /> Back to case</button></div>
      </header>
      {pre.status === "error" && <p className="error-text empty">Pre-processing failed ({pre.error}). The agent ran on the events alone.</p>}
      {run.error && <p className="error-text empty">The agent did not return a response: {run.error}</p>}

      <section className="band-block">
        <div className="spectrum-band" aria-hidden="true" />
        <div className="spectrum-cards">
          <article className="card-feature">
            <p className="card-feature__kicker">Agent confidence</p>
            <h2 className="headline-md">{r ? nice(r.confidence) : "No response"}</h2>
            {r && <div className="meter meter--dark" aria-hidden="true">{[1, 2, 3].map((i) => <i key={i} className={i <= LEVEL[r.confidence] ? `on on--${r.confidence}` : ""} />)}</div>}
            <p className="card-feature__body">The model's own rating of its decision. The API gives no token probabilities, so this is a level, not a percentage: read it next to the checks below.</p>
          </article>
          <article className="card-feature">
            <p className="card-feature__kicker">Classifier intent</p>
            <h2 className="headline-md">{top ? nice(top.intent) : "Unavailable"}{top && <span className="card-feature__pct"> {pct(top.confidence)}</span>}</h2>
            {top && <div className="meter meter--dark" aria-hidden="true"><i className="on on--high" style={{ flex: top.confidence }} /><i style={{ flex: 1 - top.confidence }} /></div>}
            <p className="card-feature__body">
              {pre.needs_human_review ? `Human review suggested: ${pre.review_reasons.join("; ") || "flagged"}.` : "No human review suggested."}
              {top?.low_margin ? " The top two intents are a close call." : ""}
            </p>
          </article>
        </div>
      </section>

      <dl className="stats stats--4">
        <div className="stat"><dt className="stat__label">Agreement checks passed</dt><dd className="stat__value">{passed}/{run.checks.length}</dd></div>
        <div className="stat"><dt className="stat__label">Model</dt><dd className="stat__value stat__value--text">{run.meta.model ?? "none"}</dd></div>
        <div className="stat"><dt className="stat__label">Time</dt><dd className="stat__value">{run.meta.total_s != null ? `${run.meta.total_s}s` : "–"}</dd></div>
        <div className="stat"><dt className="stat__label">Agent tokens</dt><dd className="stat__value">{u ? (u.input_tokens + u.cache_read_input_tokens + u.output_tokens).toLocaleString() : "–"}</dd></div>
      </dl>

      <Section title="Classifier: model classifications" count={model.length} hint="What the pre-processing model read from the case">
        <div className="tile-grid">{model.map((t) => <TileView key={t.id} t={t} isRule={false} />)}</div>
      </Section>
      <Section title="Classifier: rule-based decisions" count={rule.length} hint="Looked up from those answers, no model call">
        <div className="tile-grid">{rule.map((t) => <TileView key={t.id} t={t} isRule />)}</div>
      </Section>

      {r && (
        <Section title="Agent" hint="Its own account of the decision">
          <article className="tile tile--wide">
            <div className="tile__top"><h3 className="tile__name">Rationale</h3><Conf level={r.confidence} /></div>
            <p className="tile__rationale">{r.rationale}</p>
            <p className="chips">
              {(["safety", "injection_suspected", "authority_boundary"] as const).map((k) =>
                <span key={k} className={`chip ${r.flags[k] ? "chip--alert" : ""}`}>{nice(k)}: {r.flags[k] ? "yes" : "no"}</span>)}
            </p>
            <div className="tile__pad" />
          </article>
        </Section>
      )}

      {run.checks.length > 0 && (
        <Section title="Agreement checks" count={run.checks.length} hint="Classifier hints against the agent's output">
          <ul className="checks">
            {run.checks.map((c) => (
              <li key={c.id} className={`chk chk--${c.status}`}>
                <span className="chk__mark" aria-hidden="true">{c.status === "pass" ? <Check size={13} /> : c.status === "fail" ? <X size={13} /> : "!"}</span>
                <div><div className="chk__label">{c.label}</div><div className="text-muted body-sm">{c.detail}</div></div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {pre.guardrails && pre.guardrails.length > 0 && (
        <Section title="Guardrails given to the agent" count={pre.guardrails.length}>
          <ul className="guardrails">{pre.guardrails.map((g, i) => <li key={i}>{g}</li>)}</ul>
        </Section>
      )}
      <p className="text-muted body-sm trace-foot">
        Descriptions from the classifier spec{spec ? "" : " (not loaded: api_v2 unreachable)"}.
        {pre.usage && ` Classifier: ${pre.usage.calls} calls, ${pre.usage.input_tokens.toLocaleString()} input tokens, $${pre.usage.cost_usd.toFixed(5)} via ${pre.usage.provider}.`}
      </p>
    </main>
  );
}
