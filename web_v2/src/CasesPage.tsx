import { useMemo, useState, type ReactNode } from "react";
import { nice, runNamedCase, type CaseItem, type Run, type Ticket } from "./api";
import type { Runs } from "./App";
import { ArrowRight, ArrowUpRight, Mail, Pause, User } from "./icons";
import { Conf } from "./ui";

const DECISION: Record<string, { label: string; short: string; icon: ReactNode }> = {
  send_message: { label: "Sending a message", short: "Message", icon: <ArrowUpRight /> },
  ask_clarification: { label: "Asking for clarification", short: "Clarify", icon: <Mail /> },
  escalate_to_human: { label: "Handed to a human", short: "Escalated", icon: <User /> },
  hold_no_action: { label: "Holding, nothing to send", short: "Held", icon: <Pause /> },
};

function Field({ k, v }: { k: string; v: string }) {
  return <span className="ev__field"><span className="ev__key">{k}</span>{v || "—"}</span>;
}

function TicketView({ t, cited }: { t: Ticket; cited: boolean }) {
  return (
    <li id={t.id} className={`ev ev--other ${cited ? "ev--cited" : ""}`}>
      <span className="ev__dot" aria-hidden="true" />
      <div className="ev__head">
        <span className="ev__who">
          <span className="ev__author">{t.from || "Unknown"}</span>
          <span className="ev__kind">{t.id.replace("-", " ")}{t.stage ? ` · ${t.stage}` : ""}</span>
        </span>
        <time className="ev__time">{t.timestamp}</time>
      </div>
      <div className="ev__fields"><Field k="Via" v={t.channel} /><Field k="To" v={t.to} /></div>
      <div className="ev__body">{t.body}</div>
    </li>
  );
}

function AgentTicket({ run, desk, onTrace }: { run: Run; desk: string; onTrace: () => void }) {
  const r = run.response;
  if (!r) {
    return (
      <li className="ev ev--alert">
        <span className="ev__dot" aria-hidden="true" />
        <div className="ev__head"><span className="ev__who"><span className="ev__author">{desk}</span><span className="ev__kind">Desk (AI) · failed</span></span></div>
        <div className="ev__body error-text">{run.error || "The agent did not return a response."}</div>
      </li>
    );
  }
  const d = DECISION[r.decision];
  const n = String(run.events.length + 1).padStart(3, "0");
  const who = r.to.role === "human_review" ? "Human review" : [r.to.name, r.to.team, r.to.org].filter(Boolean).join(", ") || nice(r.to.role);
  const attention = run.checks.filter((c) => c.status !== "pass").length;
  return (
    <li className="ev ev--desk">
      <span className="ev__dot" aria-hidden="true" />
      <div className="ev__head">
        <span className="ev__who">
          <span className="ev__author">{desk}</span>
          <span className="ev__kind ev__kind--ai">Desk (AI) · event {n}</span>
        </span>
        <Conf level={r.confidence} />
      </div>
      <div className="ev__fields"><Field k="Via" v={r.channel} /><Field k="To" v={who} /></div>

      <section className={`card decision decision--${r.decision}`} aria-label="Agent decision">
        <div className="decision__type"><span className="decision__icon">{d.icon}</span>{d.label}</div>
        <p className="decision__summary">{r.rationale}</p>
        {r.claims_avoided.length > 0 && <p className="decision__line"><span className="decision__key">Not doing:</span> {r.claims_avoided.join("; ")}</p>}
      </section>

      {r.body
        ? <div className="ev__body">{r.body}</div>
        : r.handover && (
          <div className="ev__body handover">
            <p>{r.handover.summary}</p>
            {r.handover.open_questions.length > 0 && <><h4 className="mini">Open questions</h4><ul>{r.handover.open_questions.map((q, i) => <li key={i}>{q}</li>)}</ul></>}
            {r.handover.not_done.length > 0 && <><h4 className="mini">Deliberately not done</h4><ul>{r.handover.not_done.map((q, i) => <li key={i}>{q}</li>)}</ul></>}
            {r.handover.risk_flags.length > 0 && <p className="chips">{r.handover.risk_flags.map((q) => <span className="chip chip--alert" key={q}>{q}</span>)}</p>}
          </div>)}
      {r.body && r.references.length > 0 && <p className="text-muted body-sm refs">References: {r.references.join(", ")}</p>}

      <details className="why">
        <summary>Claims, flags and calculations</summary>
        <p className="chips">
          {(["safety", "injection_suspected", "authority_boundary"] as const).map((k) =>
            <span key={k} className={`chip ${r.flags[k] ? "chip--alert" : ""}`}>{nice(k)}: {r.flags[k] ? "yes" : "no"}</span>)}
        </p>
        {r.flags.out_of_scope_items.length > 0 && <p className="text-muted body-sm">Out of scope: {r.flags.out_of_scope_items.join("; ")}</p>}
        {r.claims_made.length > 0 && <><h4 className="mini">Claims made</h4>
          <ul className="claims">{r.claims_made.map((c, i) => <li key={i}>{c.claim} <a className="chip chip--link" href={`#${c.source}`}>{c.source}</a></li>)}</ul></>}
        {r.calculations.length > 0 && <><h4 className="mini">Calculations</h4><ul>{r.calculations.map((c, i) => <li key={i}><span className="mono">{c.expression}</span> = {c.result}</li>)}</ul></>}
      </details>

      <div className="ev__foot">
        <span className="text-muted body-sm">
          {run.checks.length - attention}/{run.checks.length} agreement checks passed · {run.meta.total_s}s
        </span>
        <button className="btn btn--secondary btn--sm" onClick={onTrace}>View decision trace <ArrowRight size={16} /></button>
      </div>
    </li>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  return <div className="stat"><dt className="stat__label">{label}</dt><dd className="stat__value">{value}</dd></div>;
}

export default function CasesPage({ cases, loadErr, selected, onSelect, runs, onRun, onTrace }: {
  cases: CaseItem[] | null; loadErr: string; selected: string; onSelect: (id: string) => void;
  runs: Runs; onRun: (r: Run) => void; onTrace: (id: string) => void;
}) {
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const [errs, setErrs] = useState<Record<string, string>>({});
  const [q, setQ] = useState("");
  const shown = useMemo(() => (cases ?? []).filter((c) => !q || `${c.id} ${c.title} ${c.preview}`.toLowerCase().includes(q.toLowerCase())), [cases, q]);

  if (loadErr) return <main className="view"><p className="error-text empty">Could not load the cases: {loadErr}. Is the API running (uvicorn api_v2.app:app --port 8100)?</p></main>;
  if (!cases) return <main className="view"><p className="text-muted empty">Loading cases…</p></main>;

  const current = cases.find((c) => c.id === selected);
  const run = runs[selected];
  const mine = cases.map((c) => runs[c.id]).filter((r): r is Run => !!r);
  const start = async (id: string) => {
    setBusy((b) => new Set(b).add(id));
    setErrs((e) => ({ ...e, [id]: "" }));
    try { onRun(await runNamedCase(id)); } catch (e) { setErrs((m) => ({ ...m, [id]: (e as Error).message })); }
    finally { setBusy((b) => { const n = new Set(b); n.delete(id); return n; }); }
  };
  const cited = new Set(run?.response?.claims_made.map((c) => c.source) ?? []);

  return (
    <main className="view" id="top">
      <header className="view-head">
        <h1 className="headline-lg">Every case, one <span className="emphasis">ticket</span> at a time.</h1>
        <p className="text-muted body-lg">Pick a case, press Run agent, and the desk's next step lands as a new ticket at the end of the thread.</p>
      </header>

      <dl className="stats">
        <Stat label="Cases" value={cases.length} />
        <Stat label="Agent runs" value={mine.length} />
        <Stat label="Messages" value={mine.filter((r) => r.response && ["send_message", "ask_clarification"].includes(r.response.decision)).length} />
        <Stat label="Escalated" value={mine.filter((r) => r.response?.decision === "escalate_to_human").length} />
        <Stat label="Held" value={mine.filter((r) => r.response?.decision === "hold_no_action").length} />
        <Stat label="Checks to review" value={mine.filter((r) => r.checks.some((c) => c.status !== "pass")).length} />
      </dl>

      <div className="split">
        <section className="split__list" aria-labelledby="cases-title">
          <h2 className="section-title" id="cases-title">Cases</h2>
          <label className="sr-only" htmlFor="case-filter">Filter cases</label>
          <input id="case-filter" className="input" placeholder="Filter cases" value={q} onChange={(e) => setQ(e.target.value)} />
          <ul className="case-list">
            {shown.map((c) => {
              const r = runs[c.id]?.response;
              const esc = r?.decision === "escalate_to_human";
              return (
                <li key={c.id} className="case-row" aria-current={c.id === selected ? "true" : undefined} onClick={() => onSelect(c.id)}>
                  <div className="case-row__top">
                    <span className="case-row__title">{c.title}</span>
                    {busy.has(c.id) ? <span className="status status--live"><span className="status__dot" />Running</span>
                      : r ? <span className={`status ${esc ? "status--alert" : "status--live"}`}><span className="status__dot" />{DECISION[r.decision].short}</span> : null}
                  </div>
                  <div className="case-row__summary">{c.id} · {c.preview}</div>
                </li>
              );
            })}
            {!shown.length && <li className="empty text-muted">No cases match.</li>}
          </ul>
        </section>

        <section className="split__detail">
          {current ? (
            <div className="detail">
              <div className="detail__head">
                <h2 className="headline-md">{current.title}</h2>
                <button className="btn btn--primary" disabled={busy.has(current.id)} onClick={() => start(current.id)}>
                  {busy.has(current.id) ? "Preprocessing and thinking…" : run ? "Run agent again" : "Run agent"}
                </button>
              </div>
              <div className="meta"><span>{current.id}</span><span>{current.events.length} tickets</span>{run?.response && <span>{run.meta.model}</span>}</div>
              {errs[current.id] && <p className="error-text" role="alert">{errs[current.id]}</p>}
              <ol className="timeline">
                {current.events.map((t) => <TicketView key={t.id} t={t} cited={cited.has(t.id)} />)}
                {run && <AgentTicket run={run} desk={current.events[0]?.to || "Rivet Delivery Desk"} onTrace={() => onTrace(current.id)} />}
              </ol>
              {!run && <p className="text-muted empty">Not run yet. Run agent to see what the desk would do next.</p>}
            </div>
          ) : <p className="text-muted empty">Pick a case to see its tickets.</p>}
        </section>
      </div>
    </main>
  );
}
