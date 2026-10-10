import { useMemo, useState } from "react";
import {
  fmtTime, go, hub, useLive, type Action, type AgentEvent, type AgentRun, type Case, type CaseEvent, type Profile,
} from "./lib";
import { Composer, Timeline } from "./Timeline";

const STATUSES = ["all", "open", "in_progress", "waiting", "escalated", "resolved"];

export default function Ops({ profile }: { profile: Profile }) {
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const pending = useLive<Action>("actions", (q) => q.eq("status", "pending_approval").order("created_at"));
  const runs = useLive<AgentRun>("agent_runs", (q) => q.order("updated_at", { ascending: false }).limit(200));
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<string | null>(null);

  const shown = cases.filter((c) => filter === "all" || c.status === filter);
  const totalCost = runs.reduce((s, r) => s + (r.list_cost_cents ?? 0), 0);
  const counts = useMemo(() => {
    const m: Record<string, number> = {};
    cases.forEach((c) => (m[c.status] = (m[c.status] ?? 0) + 1));
    return m;
  }, [cases]);

  return (
    <main className="ops">
      <section className="stats">
        <Stat label="Cases" value={cases.length} />
        <Stat label="Escalated" value={counts.escalated ?? 0} />
        <Stat label="Waiting" value={counts.waiting ?? 0} />
        <Stat label="Awaiting approval" value={pending.length} highlight={pending.length > 0} />
        <Stat label="Agent runs" value={runs.length} />
        <Stat label="Agent spend" value={`$${(totalCost / 100).toFixed(2)}`} />
      </section>

      {pending.length > 0 && (
        <section className="card">
          <h2>Approvals</h2>
          {pending.map((a) => <Approval key={a.id} action={a} onOpen={() => setSelected(a.case_id)} />)}
        </section>
      )}

      <div className="split">
        <section className="card list">
          <div className="row">
            <h2>Cases</h2>
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              {STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
            </select>
          </div>
          <ul className="cases">
            {shown.map((c) => (
              <li key={c.id} className={c.id === selected ? "active" : ""} onClick={() => setSelected(c.id)}>
                <div className="row">
                  <strong>#{c.id}</strong>
                  <span className={`status s-${c.status}`}>{c.status.replace("_", " ")}</span>
                </div>
                <div>{c.title}</div>
                {c.decision_summary && <div className="muted small">AI: {c.decision_summary}</div>}
              </li>
            ))}
          </ul>
        </section>
        <section className="card detail">
          {selected ? <CaseDetail key={selected} caseId={selected} runs={runs} profile={profile} /> :
            <p className="muted">Pick a case to see its timeline, the agent's actions and its live activity.</p>}
        </section>
      </div>
    </main>
  );
}

function Stat({ label, value, highlight }: { label: string; value: number | string; highlight?: boolean }) {
  return (
    <div className={`stat ${highlight ? "hl" : ""}`}>
      <div className="stat-v">{value}</div>
      <div className="muted small">{label}</div>
    </div>
  );
}

function Approval({ action, onOpen }: { action: Action; onOpen: () => void }) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const decide = async (verb: "approve" | "reject") => {
    setBusy(true);
    setErr("");
    try { await hub(`/api/actions/${action.id}/${verb}`, { reason }); } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  };
  const a = action.args as Record<string, string>;
  return (
    <div className="approval">
      <div className="row">
        <span><span className="tag">{action.tool}</span> case <a onClick={onOpen}>#{action.case_id}</a>
          {a.to_party && <> → <strong>{a.to_party}</strong> via {a.channel}</>}</span>
        <span className="muted small">{fmtTime(action.created_at)}</span>
      </div>
      {a.subject && <div><strong>{a.subject}</strong></div>}
      <pre className="msg">{a.body ?? JSON.stringify(action.args, null, 2)}</pre>
      <div className="row">
        <input placeholder="Reason (sent to the agent if rejected)" value={reason} onChange={(e) => setReason(e.target.value)} />
        <button className="danger" disabled={busy} onClick={() => decide("reject")}>Reject</button>
        <button className="primary" disabled={busy} onClick={() => decide("approve")}>Approve</button>
      </div>
      {err && <p className="error">{err}</p>}
    </div>
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

  if (!c) return <p className="muted">Loading…</p>;
  const rerun = async () => { setBusy(true); try { await hub(`/api/cases/${caseId}/run`, {}); } finally { setBusy(false); } };

  return (
    <div>
      <div className="row">
        <h2>#{c.id} {c.title}</h2>
        <button disabled={busy} onClick={rerun}>{busy ? "Waking agent…" : "Ask agent to re-assess"}</button>
      </div>
      <div className="meta">
        <span className={`status s-${c.status}`}>{c.status.replace("_", " ")}</span>
        {c.shipment_id && <span>Shipment {c.shipment_id}</span>}
        {c.source_name && <span>Raised by {c.source_name}</span>}
        {run && <span>Agent: {run.status}{run.stop_reason ? ` (${run.stop_reason})` : ""}
          {run.list_cost_cents != null && ` · $${(run.list_cost_cents / 100).toFixed(2)}`}
          {" · "}<a href={run.trace_url} target="_blank" rel="noreferrer">trace</a></span>}
        <AgentLink caseId={c.id} />
      </div>
      {c.decision && (
        <div className="decision">
          <div><span className="tag">{c.decision.decision_type}</span> {c.decision.summary}</div>
          <div className="muted small">Not doing: {c.decision.not_doing}</div>
          <div className="muted small">Next: {c.decision.next_trigger}</div>
        </div>
      )}
      <div className="tabs">
        {(["timeline", "actions", "agent"] as const).map((t) => (
          <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
            {t === "timeline" ? `Timeline (${events.length})` : t === "actions" ? `Actions (${actions.length})` : "Agent live log"}
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
      {tab === "agent" && <><AgentLink caseId={caseId} label="Open the full live agent view" /><AgentLog events={agentEvents} /></>}
    </div>
  );
}

function ActionsTable({ actions }: { actions: Action[] }) {
  if (!actions.length) return <p className="muted">The agent hasn't acted on this case yet.</p>;
  return (
    <table className="tbl">
      <thead><tr><th>When</th><th>Tool</th><th>Status</th><th>Details</th><th>Policy</th></tr></thead>
      <tbody>
        {actions.map((a) => (
          <tr key={a.id}>
            <td className="nowrap">{fmtTime(a.created_at)}</td>
            <td>{a.tool}</td>
            <td><span className={`status s-${a.status}`}>{a.status.replace("_", " ")}</span>{a.decided_by && <div className="muted small">by {a.decided_by}</div>}</td>
            <td><pre className="msg">{summarize(a.args)}</pre></td>
            <td>{a.policy?.filter((p) => !p.negated_context).map((p, i) => (
              <span key={i} className={`tag ${p.level === "BLOCK" ? "tag-bad" : "tag-warn"}`}>{p.rule}</span>))}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function summarize(args: Record<string, unknown>): string {
  return Object.entries(args).map(([k, v]) => `${k}: ${typeof v === "string" ? v : JSON.stringify(v)}`).join("\n");
}

function AgentLog({ events }: { events: AgentEvent[] }) {
  const lines = events.map((e) => describe(e)).filter(Boolean) as { id: number; when: string; kind: string; text: string }[];
  if (!lines.length) return <p className="muted">No agent activity yet.</p>;
  return (
    <ul className="agentlog">
      {lines.map((l) => (
        <li key={l.id}><span className="muted small">{l.when}</span> <span className="tag">{l.kind}</span> {l.text}</li>
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
      return { ...base, kind: "approval", text: `${p.result}${p.deny_message ? ` — ${p.deny_message}` : ""}` };
    case "session.status_idle":
      return { ...base, kind: "idle", text: p.stop_reason?.type ?? "" };
    case "session.error":
      return { ...base, kind: "error", text: JSON.stringify(p.error ?? p).slice(0, 300) };
    default:
      return null;
  }
}

function AgentLink({ caseId, label = "agent view" }: { caseId: string; label?: string }) {
  const href = `/agents/${encodeURIComponent(caseId)}`;
  return (
    <a href={href} onClick={(e) => { if (!e.metaKey && !e.ctrlKey) { e.preventDefault(); go(href); } }}>{label} →</a>
  );
}
