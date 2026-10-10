import { useMemo, useState, type ReactNode } from "react";
import {
  fmtTime, go, hub, useLive, type Action, type AgentEvent, type AgentRun, type Case, type CaseEvent, type Profile,
} from "./lib";
import { Composer, Timeline } from "./Timeline";
import SwipeDeck from "./SwipeDeck";
import { ArrowUpRight, Mail, Pause, User, X } from "./icons";
import { Status, statusText } from "./ui";

const STATUSES = ["all", "open", "in_progress", "waiting", "escalated", "resolved"];

export default function Ops({ profile, initialCase }: { profile: Profile; initialCase?: string }) {
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const pending = useLive<Action>("actions", (q) => q.eq("status", "pending_approval").order("created_at"));
  const runs = useLive<AgentRun>("agent_runs", (q) => q.order("updated_at", { ascending: false }).limit(200));
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<string | null>(initialCase ?? null);

  const shown = cases.filter((c) => filter === "all" || c.status === filter);
  const totalCost = runs.reduce((s, r) => s + (r.list_cost_cents ?? 0), 0);
  const counts = useMemo(() => {
    const m: Record<string, number> = {};
    cases.forEach((c) => (m[c.status] = (m[c.status] ?? 0) + 1));
    return m;
  }, [cases]);

  return (
    <main className="view ops" id="top">
      <header className="view-head">
        <h1 className="headline-lg">Today on the <span className="emphasis">desk</span>.</h1>
        <p className="text-muted body-lg">
          The agent plans each next step, a reviewer checks it, and nothing reaches a customer until you approve it.
        </p>
      </header>

      <dl className="stats">
        <Stat label="Cases" value={cases.length} />
        <Stat label="Escalated" value={counts.escalated ?? 0} />
        <Stat label="Waiting" value={counts.waiting ?? 0} />
        <Stat label="Awaiting approval" value={pending.length} highlight={pending.length > 0} />
        <Stat label="Agent runs" value={runs.length} />
        <Stat label="Agent spend" value={`$${(totalCost / 100).toFixed(2)}`} />
      </dl>

      <SwipeDeck pending={pending} onOpen={setSelected} />

      <div className="split">
        <section className="split__list" aria-labelledby="cases-title">
          <h2 className="section-title" id="cases-title">Cases</h2>
          <div className="tabs tabs--scroll" role="tablist" aria-label="Filter cases by status">
            {STATUSES.map((s) => (
              <button key={s} role="tab" className="tab" aria-selected={filter === s} onClick={() => setFilter(s)}>
                {s === "all" ? "All" : statusText(s)}
                <span className="tab__count">{s === "all" ? cases.length : counts[s] ?? 0}</span>
              </button>
            ))}
          </div>
          <ul className="case-list">
            {shown.map((c) => (
              <li key={c.id} className="case-row" aria-current={c.id === selected ? "true" : undefined}
                onClick={() => setSelected(c.id)}>
                <div className="case-row__top">
                  <span className="case-row__title">#{c.id} {c.title}</span>
                  <Status status={c.status} />
                </div>
                {c.decision_summary && <div className="case-row__summary">AI: {c.decision_summary}</div>}
              </li>
            ))}
            {!shown.length && <li className="empty text-muted">No cases with this status.</li>}
          </ul>
        </section>
        <section className="split__detail">
          {selected ? <CaseDetail key={selected} caseId={selected} runs={runs} profile={profile} /> :
            <p className="text-muted empty">Pick a case to see its timeline, the agent's actions and its live activity.</p>}
        </section>
      </div>
    </main>
  );
}

function Stat({ label, value, highlight }: { label: string; value: number | string; highlight?: boolean }) {
  return (
    <div className="stat">
      <dt className="stat__label">{label}</dt>
      <dd className="stat__value">
        {highlight && <span className="stat__dot" aria-hidden="true" />}
        {value}
      </dd>
    </div>
  );
}

const DECISION: Record<string, { label: string; icon: ReactNode }> = {
  act: { label: "Acting", icon: <ArrowUpRight /> },
  request_information: { label: "Asking for information", icon: <Mail /> },
  escalate_to_human: { label: "Handed to a human", icon: <User /> },
  hold_no_action: { label: "Holding, nothing to send", icon: <Pause /> },
  decline: { label: "Declined", icon: <X /> },
};

function DecisionPanel({ decision }: { decision: Record<string, string> }) {
  const type = decision.decision_type;
  const d = DECISION[type] ?? { label: statusText(type ?? "decision"), icon: <ArrowUpRight /> };
  return (
    <section className={`card decision decision--${type}`} aria-label="Agent decision">
      <div className="decision__type">
        <span className="decision__icon">{d.icon}</span>
        {d.label}
      </div>
      {decision.summary && <p className="decision__summary">{decision.summary}</p>}
      {decision.not_doing && <p className="decision__line"><span className="decision__key">Not doing:</span> {decision.not_doing}</p>}
      {decision.next_trigger && (
        <p className="decision__line decision__line--next"><span className="decision__key">Next:</span> {decision.next_trigger}</p>
      )}
    </section>
  );
}

function CaseDetail({ caseId, runs, profile }: { caseId: string; runs: AgentRun[]; profile: Profile }) {
  const [c] = useLive<Case>("cases", (q) => q.eq("id", caseId), [caseId]);
  const events = useLive<CaseEvent>("case_events", (q) => q.eq("case_id", caseId).order("ts").order("id"), [caseId]);
  const actions = useLive<Action>("actions", (q) => q.eq("case_id", caseId).order("id"), [caseId]);
  const agentEvents = useLive<AgentEvent>("agent_events",
    (q) => q.eq("case_id", caseId).order("id", { ascending: false }).limit(60), [caseId]);
  const [tab, setTab] = useState<"timeline" | "actions" | "agent">("timeline");
  const [busy, setBusy] = useState(false);
  const run = runs.find((r) => r.session_id === c?.session_id);

  if (!c) return <p className="text-muted empty">Loading…</p>;
  const rerun = async () => { setBusy(true); try { await hub(`/api/cases/${caseId}/run`, {}); } finally { setBusy(false); } };

  return (
    <div className="detail">
      <div className="detail__head">
        <h2 className="headline-md">#{c.id}&nbsp; {c.title}</h2>
        <button className="btn btn--secondary" disabled={busy} onClick={rerun}>{busy ? "Waking agent…" : "Ask agent to re-assess"}</button>
      </div>
      <div className="meta">
        <Status status={c.status} />
        {c.shipment_id && <span>Shipment {c.shipment_id}</span>}
        {c.source_name && <span>Raised by {c.source_name}</span>}
        {run && <span>{runText(run)}</span>}
        {run?.list_cost_cents != null && <span>${(run.list_cost_cents / 100).toFixed(2)}</span>}
        {run && <a className="meta__link" href={run.trace_url} target="_blank" rel="noreferrer">Trace <ArrowUpRight size={14} /></a>}
        <AgentLink caseId={c.id} />
      </div>
      {c.decision && <DecisionPanel decision={c.decision} />}
      <div className="tabs detail__tabs" role="tablist">
        {(["timeline", "actions", "agent"] as const).map((t) => (
          <button key={t} role="tab" className="tab" aria-selected={tab === t} onClick={() => setTab(t)}>
            {t === "timeline" ? "Timeline" : t === "actions" ? "Actions" : "Agent live log"}
            {t !== "agent" && <span className="tab__count">{t === "timeline" ? events.length : actions.length}</span>}
          </button>
        ))}
      </div>
      {tab === "timeline" && (
        <>
          <Timeline events={events} />
          <Composer caseId={caseId} placeholder={`Write on the case as ${profile.party_name || "desk staff"}; the agent will pick it up.`} />
        </>
      )}
      {tab === "actions" && <ActionsTable actions={actions} />}
      {tab === "agent" && <><AgentLink caseId={caseId} label="Open the full live log" /><AgentLog events={agentEvents} /></>}
    </div>
  );
}

const RUN_STATUS: Record<string, string> = {
  idle: "idle", running: "running", rescheduling: "restarting", terminated: "stopped", error: "failed",
};
const STOP_REASON: Record<string, string> = {
  requires_action: "needs action", end_turn: "finished", max_tokens: "hit its length limit", retries_exhausted: "gave up after retries",
};
const words = (s: string) => s.replace(/_/g, " ");

/** "Agent idle, needs action" rather than the raw enums. */
function runText(run: AgentRun): string {
  const status = RUN_STATUS[run.status] ?? words(run.status);
  const stop = run.stop_reason ? STOP_REASON[run.stop_reason] ?? words(run.stop_reason) : "";
  return `Agent ${status}${stop ? `, ${stop}` : ""}`;
}

function ActionsTable({ actions }: { actions: Action[] }) {
  if (!actions.length) return <p className="text-muted empty">The agent hasn't acted on this case yet.</p>;
  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead><tr><th>When</th><th>Tool</th><th>Status</th><th>Details</th><th>Policy</th></tr></thead>
        <tbody>
          {actions.map((a) => (
            <tr key={a.id}>
              <td className="nowrap text-muted">{fmtTime(a.created_at)}</td>
              <td className="mono">{a.tool}</td>
              <td><Status status={a.status} />{a.decided_by && <div className="text-muted body-sm">by {a.decided_by}</div>}</td>
              <td><div className="pre">{summarize(a.args)}</div></td>
              <td>{a.policy?.filter((p) => !p.negated_context).map((p, i) => (
                <span key={i} className={`policy ${p.level === "BLOCK" ? "policy--block" : ""}`}>{p.rule}</span>))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function summarize(args: Record<string, unknown>): string {
  return Object.entries(args).map(([k, v]) => `${k}: ${typeof v === "string" ? v : JSON.stringify(v)}`).join("\n");
}

function AgentLog({ events }: { events: AgentEvent[] }) {
  const lines = events.map((e) => describe(e)).filter(Boolean) as { id: number; when: string; kind: string; text: string }[];
  if (!lines.length) return <p className="text-muted empty">No agent activity yet.</p>;
  return (
    <ul className="agentlog">
      {lines.map((l) => (
        <li key={l.id} className={l.kind === "error" ? "agentlog__row agentlog__row--error" : "agentlog__row"}>
          <span className="agentlog__when">{l.when}</span>
          <span className="agentlog__kind">{l.kind}</span>
          <span className="agentlog__text">{l.text}</span>
        </li>
      ))}
    </ul>
  );
}

function describe(e: AgentEvent) {
  const p = e.payload ?? {};
  const base = { id: e.id, when: fmtTime(e.created_at) };
  switch (e.type) {
    case "agent.message":
      return { ...base, kind: "says", text: (p.content ?? []).map((b: any) => b.text ?? "").join(" ").slice(0, 400) };
    case "agent.mcp_tool_use":
      return { ...base, kind: p.evaluated_permission === "ask" ? "asks approval" : "tool", text: `${p.name}(${JSON.stringify(p.input ?? {}).slice(0, 200)})` };
    case "agent.mcp_tool_result":
      return { ...base, kind: "result", text: JSON.stringify(p.content ?? p.result ?? "").slice(0, 200) };
    case "user.message":
      return { ...base, kind: "wake-up", text: (p.content ?? []).map((b: any) => b.text ?? "").join(" ").slice(0, 300) };
    case "user.tool_confirmation":
      return { ...base, kind: "approval", text: `${p.result}${p.deny_message ? `: ${p.deny_message}` : ""}` };
    case "session.status_idle":
      return { ...base, kind: "idle", text: p.stop_reason?.type ?? "" };
    case "session.error":
      return { ...base, kind: "error", text: JSON.stringify(p.error ?? p).slice(0, 300) };
    default:
      return null;
  }
}

/** Link into /agents/<case>; a plain href too, so cmd-click opens it in a new tab. */
function AgentLink({ caseId, label = "Agent log" }: { caseId: string; label?: string }) {
  const href = `/agents/${encodeURIComponent(caseId)}`;
  return (
    <a className="meta__link" href={href} onClick={(e) => { if (!e.metaKey && !e.ctrlKey) { e.preventDefault(); go(href); } }}>
      {label} <ArrowUpRight size={14} />
    </a>
  );
}
