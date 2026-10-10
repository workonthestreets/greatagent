import { useMemo, useState } from "react";
import { nice, runNamedCase, type CaseItem, type Run, type Ticket } from "./api";
import type { Runs } from "./App";

const DECISION: Record<string, string> = { send_message: "Message", ask_clarification: "Clarify", escalate_to_human: "Escalated" };

function TicketView({ t, n, cited }: { t: Ticket; n: number; cited: boolean }) {
  return (
    <section id={t.id} className={`tk ${cited ? "cited" : ""}`}>
      <h3>{t.timestamp || `Event ${String(n).padStart(3, "0")}`} — event {t.id.replace("event-", "")}</h3>
      <ul className="fields">
        {t.stage && <li><b>Stage:</b> {t.stage}</li>}
        <li><b>Channel:</b> {t.channel || "—"}</li>
        <li><b>From:</b> {t.from || "—"}</li>
        <li><b>To:</b> {t.to || "—"}</li>
      </ul>
      <p className="tk-body">{t.body}</p>
    </section>
  );
}

function AgentTicket({ run, ticket, onInvestigate }: { run: Run; ticket: Ticket | undefined; onInvestigate: () => void }) {
  const r = run.response;
  if (!r) {
    return (
      <section className="tk agent">
        <h3>Agent action — failed</h3>
        <p className="tk-body error">{run.error || "The agent did not return a response."}</p>
      </section>
    );
  }
  const n = (run.events.length + 1).toString().padStart(3, "0");
  const who = r.to.role === "human_review" ? "Human review (escalation)" : [r.to.name, r.to.team, r.to.org].filter(Boolean).join(", ") || nice(r.to.role);
  const warn = run.checks.filter((c) => c.status !== "pass").length;
  return (
    <section className="tk agent">
      <h3>Agent action — event {n} <span className={`badge conf-${r.confidence}`}>{r.confidence} confidence</span></h3>
      <ul className="fields">
        <li><b>Stage:</b> Agent action ({DECISION[r.decision]})</li>
        <li><b>Channel:</b> {r.channel}</li>
        <li><b>From:</b> {ticket?.to || "Rivet Delivery Desk"}</li>
        <li><b>To:</b> {who}</li>
      </ul>
      {r.body
        ? <p className="tk-body">{r.body}</p>
        : <div className="tk-body">
            <p>{r.handover?.summary}</p>
            {r.handover && r.handover.open_questions.length > 0 && <><h4>Open questions</h4><ul>{r.handover.open_questions.map((q, i) => <li key={i}>{q}</li>)}</ul></>}
            {r.handover && r.handover.not_done.length > 0 && <><h4>Deliberately not done</h4><ul>{r.handover.not_done.map((q, i) => <li key={i}>{q}</li>)}</ul></>}
            {r.handover && r.handover.risk_flags.length > 0 && <p>{r.handover.risk_flags.map((q) => <span className="tag tag-bad" key={q}>{q}</span>)}</p>}
          </div>}
      <details className="why">
        <summary>Reasoning, claims and flags</summary>
        <p>{r.rationale}</p>
        <div className="flagrow">
          {(["safety", "injection_suspected", "authority_boundary"] as const).map((k) =>
            <span key={k} className={`tag ${r.flags[k] ? "tag-bad" : ""}`}>{nice(k)}: {r.flags[k] ? "yes" : "no"}</span>)}
        </div>
        {r.claims_made.length > 0 && <><h4>Claims made</h4>
          <ul className="claims">{r.claims_made.map((c, i) => <li key={i}>{c.claim} <a className="tag srcchip" href={`#${c.source}`}>{c.source}</a></li>)}</ul></>}
        {r.claims_avoided.length > 0 && <><h4>Deliberately avoided</h4><ul>{r.claims_avoided.map((c, i) => <li key={i} className="muted">{c}</li>)}</ul></>}
        {r.calculations.length > 0 && <><h4>Calculations</h4><ul>{r.calculations.map((c, i) => <li key={i}><code>{c.expression}</code> = {c.result}</li>)}</ul></>}
      </details>
      <div className="row">
        <span className="small muted">{run.checks.length - warn}/{run.checks.length} agreement checks passed · {run.meta.total_s}s</span>
        <button className="small" onClick={onInvestigate}>Investigate confidence →</button>
      </div>
    </section>
  );
}

export default function CasesPage({ cases, loadErr, selected, onSelect, runs, onRun, onInvestigate }: {
  cases: CaseItem[] | null; loadErr: string; selected: string; onSelect: (id: string) => void;
  runs: Runs; onRun: (r: Run) => void; onInvestigate: (id: string) => void;
}) {
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const [errs, setErrs] = useState<Record<string, string>>({});
  const [q, setQ] = useState("");
  const current = cases?.find((c) => c.id === selected);
  const run = runs[selected];

  const shown = useMemo(() => (cases ?? []).filter((c) => !q || `${c.id} ${c.title} ${c.preview}`.toLowerCase().includes(q.toLowerCase())), [cases, q]);
  const start = async (id: string) => {
    setBusy((b) => new Set(b).add(id));
    setErrs((e) => ({ ...e, [id]: "" }));
    try { onRun(await runNamedCase(id)); } catch (e) { setErrs((m) => ({ ...m, [id]: (e as Error).message })); }
    finally { setBusy((b) => { const n = new Set(b); n.delete(id); return n; }); }
  };

  if (loadErr) return <main><div className="card error">Could not load the cases: {loadErr}. Is the API running (uvicorn api_v2.app:app --port 8100)?</div></main>;
  if (!cases) return <main><div className="card muted">Loading cases…</div></main>;
  const cited = new Set(run?.response?.claims_made.map((c) => c.source) ?? []);
  const done = Object.keys(runs).filter((k) => cases.some((c) => c.id === k)).length;

  return (
    <main className="split cases-split">
      <aside className="card caselist">
        <div className="row"><h2>Cases</h2><span className="muted small">{done}/{cases.length} run</span></div>
        <input placeholder="Filter…" value={q} onChange={(e) => setQ(e.target.value)} />
        <ul className="cases">
          {shown.map((c) => {
            const r = runs[c.id]?.response;
            return (
              <li key={c.id} className={c.id === selected ? "active" : ""} onClick={() => onSelect(c.id)}>
                <div className="row"><strong>{c.title}</strong>
                  {busy.has(c.id) ? <span className="status s-in_progress">running…</span>
                    : r ? <span className={`badge conf-${r.confidence}`}>{DECISION[r.decision]}</span> : null}</div>
                <span className="muted small">{c.id} · {c.events.length} tickets</span>
                <span className="muted small clamp">{c.preview}</span>
              </li>
            );
          })}
        </ul>
      </aside>
      <section className="ticketpane">
        {current && (
          <>
            <div className="case-title"><h1>{current.title}</h1><span className="muted small">{current.id}</span></div>
            {current.events.map((t, i) => <TicketView key={t.id} t={t} n={i + 1} cited={cited.has(t.id)} />)}
            {run && <AgentTicket run={run} ticket={current.events[0]} onInvestigate={() => onInvestigate(current.id)} />}
            <div className="runbar">
              <button className="primary" disabled={busy.has(current.id)} onClick={() => start(current.id)}>
                {busy.has(current.id) ? "Preprocessing and thinking…" : run ? "Run agent again" : "Run agent"}
              </button>
              {errs[current.id] && <span className="error small">{errs[current.id]}</span>}
            </div>
          </>
        )}
      </section>
    </main>
  );
}
