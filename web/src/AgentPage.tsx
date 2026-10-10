import { useEffect, useMemo, useRef, useState } from "react";
import {
  fmtTime, go, hub, useLive, type Action, type AgentEvent, type AgentLive, type AgentRun, type Case,
} from "./lib";

/** /agents: an inbox of agent runs (newest activity first); /agents/<case id> opens that case's live log.
 *  Staff only (agent_events and agent_runs are staff-only under RLS). */
export default function AgentsPage({ caseId }: { caseId: string | null }) {
  const runs = useLive<AgentRun>("agent_runs", (q) => q.order("updated_at", { ascending: false }).limit(300));
  const cases = useLive<Case>("cases", (q) => q);
  const pending = useLive<Action>("actions", (q) => q.eq("status", "pending_approval"));
  const titles = useMemo(() => new Map(cases.map((c) => [c.id, c])), [cases]);
  const waiting = useMemo(() => {
    const m = new Map<string, number>();
    pending.forEach((a) => m.set(a.case_id, (m.get(a.case_id) ?? 0) + 1));
    return m;
  }, [pending]);
  // One inbox row per case: its latest run, with the case's total spend across runs.
  const rows = useMemo(() => {
    const seen = new Map<string, { run: AgentRun; runs: number; cents: number }>();
    for (const r of runs) {
      const row = seen.get(r.case_id);
      if (row) { row.runs++; row.cents += r.list_cost_cents ?? 0; }
      else seen.set(r.case_id, { run: r, runs: 1, cents: r.list_cost_cents ?? 0 });
    }
    return [...seen.values()];
  }, [runs]);

  return (
    <main className="agents">
      <section className="card inbox">
        <div className="row"><h2>Agent runs</h2><span className="muted small">{rows.length} cases</span></div>
        <ul className="cases">
          {rows.map(({ run, runs: n, cents }) => {
            const c = titles.get(run.case_id);
            const live = run.status === "running";
            const ask = waiting.get(run.case_id) ?? 0;
            return (
              <li key={run.case_id} className={run.case_id === caseId ? "active" : ""}
                  onClick={() => go(`/agents/${encodeURIComponent(run.case_id)}`)}>
                <div className="row">
                  <strong>{live && <span className="dot" />}#{run.case_id}</strong>
                  <span className="muted small">{fmtTime((run as any).updated_at)}</span>
                </div>
                <div className="ellipsis-2">{c?.title ?? ""}</div>
                <div className="row small">
                  <span>
                    <span className={`status s-${live ? "in_progress" : ask ? "pending_approval" : run.stop_reason === "end_turn" ? "done" : "open"}`}>
                      {live ? "running" : ask ? `${ask} awaiting approval` : run.stop_reason ?? run.status}
                    </span>
                    {run.session_id.startsWith("pipeline-") && <span className="tag">pipeline</span>}
                  </span>
                  <span className="muted">{n > 1 ? `${n} runs · ` : ""}${(cents / 100).toFixed(2)}</span>
                </div>
              </li>
            );
          })}
          {!rows.length && <li className="muted">No agent runs yet.</li>}
        </ul>
      </section>
      <section className="detail">
        {caseId ? <CaseAgent key={caseId} caseId={caseId} />
          : <p className="muted card">Pick a run to watch what the agent did: wake-ups, model calls, tool calls with their
              results, approvals and its messages, live as they happen.</p>}
      </section>
    </main>
  );
}

function CaseAgent({ caseId }: { caseId: string }) {
  const [c] = useLive<Case>("cases", (q) => q.eq("id", caseId), [caseId]);
  const runs = useLive<AgentRun>("agent_runs", (q) => q.eq("case_id", caseId).order("created_at", { ascending: false }), [caseId]);
  const [picked, setPicked] = useState<string | null>(null);
  const sessionId = picked ?? c?.session_id ?? runs[0]?.session_id ?? null;
  const run = runs.find((r) => r.session_id === sessionId);

  return (
    <div className="agentpage">
      <div className="row">
        <div>
          <a className="small" onClick={() => go("/")}>← Dashboard</a>
          <h1>#{caseId}{c ? ` ${c.title}` : ""}</h1>
        </div>
        <RunControls caseId={caseId} />
      </div>

      {runs.length > 1 && (
        <div className="runs">
          {runs.map((r, i) => (
            <button key={r.session_id} className={r.session_id === sessionId ? "tab active" : "tab"}
                    onClick={() => setPicked(r.session_id)}>
              Run {runs.length - i} · {fmtTime((r as any).created_at)}
            </button>
          ))}
        </div>
      )}

      {sessionId ? <SessionLog key={sessionId} caseId={caseId} sessionId={sessionId} run={run} />
        : <p className="muted card">The agent hasn't worked this case yet. Use “Ask agent to re-assess” to start it.</p>}
    </div>
  );
}

function RunControls({ caseId }: { caseId: string }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const wake = async () => {
    setBusy(true); setErr("");
    try { await hub(`/api/cases/${caseId}/run`, {}); } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  };
  return (
    <div className="stack right-align">
      <button className="primary" disabled={busy} onClick={wake}>{busy ? "Waking agent…" : "Ask agent to re-assess"}</button>
      {err && <span className="error small">{err}</span>}
    </div>
  );
}

type Item =
  | { kind: "wake"; ev: AgentEvent; text: string }
  | { kind: "model"; ev: AgentEvent; end?: AgentEvent }
  | { kind: "thinking"; ev: AgentEvent }
  | { kind: "say"; ev: AgentEvent; text: string }
  | { kind: "tool"; ev: AgentEvent; result?: AgentEvent; confirm?: AgentEvent; action?: Action }
  | { kind: "result"; ev: AgentEvent }
  | { kind: "status"; ev: AgentEvent; label: string }
  | { kind: "error"; ev: AgentEvent }
  | { kind: "other"; ev: AgentEvent };

const textOf = (content: any): string =>
  Array.isArray(content) ? content.map((b) => (typeof b === "string" ? b : b?.text ?? "")).join("\n").trim() : String(content ?? "");

function SessionLog({ caseId, sessionId, run }: { caseId: string; sessionId: string; run?: AgentRun }) {
  const events = useLive<AgentEvent>("agent_events", (q) => q.eq("session_id", sessionId).order("id").limit(2000), [sessionId]);
  const live = useLive<AgentLive>("agent_live", (q) => q.eq("session_id", sessionId).eq("done", false).order("started_at"), [sessionId]);
  const actions = useLive<Action>("actions", (q) => q.eq("case_id", caseId).order("id"), [caseId]);
  const [showRaw, setShowRaw] = useState(false);

  const { items, stats } = useMemo(() => build(events, actions), [events, actions]);
  const pending = items.filter((i) => i.kind === "tool" && i.action?.status === "pending_approval").length;
  const isLive = run?.status === "running" || live.length > 0;

  // Keep the newest activity in view while the user is at the bottom.
  const endRef = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  useEffect(() => {
    const onScroll = () => { stick.current = window.innerHeight + window.scrollY >= document.body.scrollHeight - 120; };
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => { if (stick.current) endRef.current?.scrollIntoView({ block: "end" }); }, [items.length, live]);

  return (
    <>
      <section className="stats">
        <div className={`stat ${isLive ? "hl-live" : ""}`}>
          <div className="stat-v">{isLive ? <><span className="dot" /> live</> : run?.status ?? "—"}</div>
          <div className="muted small">{run?.stop_reason ? `stopped: ${run.stop_reason}` : "status"}</div>
        </div>
        <div className={`stat ${pending ? "hl" : ""}`}><div className="stat-v">{pending}</div><div className="muted small">awaiting approval</div></div>
        <div className="stat"><div className="stat-v">{stats.tools}</div><div className="muted small">tool calls</div></div>
        <div className="stat"><div className="stat-v">{stats.models}</div><div className="muted small">model calls</div></div>
        <div className="stat"><div className="stat-v">{stats.outTokens.toLocaleString()}</div><div className="muted small">output tokens</div></div>
        <div className="stat"><div className="stat-v">${((run?.list_cost_cents ?? 0) / 100).toFixed(2)}</div><div className="muted small">cost</div></div>
      </section>

      <div className="row muted small">
        <span>Session <code>{sessionId}</code>{run?.trace_url && <> · <a href={run.trace_url} target="_blank" rel="noreferrer">open trace in Anthropic Console</a></>}</span>
        <label className="inline"><input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} /> show raw events</label>
      </div>

      <ol className="feed">
        {items.map((it) => <FeedItem key={it.ev.id} item={it} showRaw={showRaw} active={isLive} />)}
        {live.map((l) => (
          <li key={l.event_id} className="fi fi-say fi-live">
            <div className="fi-head"><span className="tag">{l.kind === "agent.thinking" ? "thinking" : "writing"}</span><span className="dot" /></div>
            {l.kind === "agent.thinking" ? <div className="muted">The model is thinking…</div>
              : <div className="fi-body">{l.text}<span className="caret" /></div>}
          </li>
        ))}
        {!items.length && !live.length && <li className="muted">No events yet.</li>}
      </ol>
      <div ref={endRef} />
    </>
  );
}

function build(events: AgentEvent[], actions: Action[]) {
  const results = new Map<string, AgentEvent>();
  const confirms = new Map<string, AgentEvent>();
  const ends = new Map<string, AgentEvent>();
  const byEvent = new Map(actions.filter((a) => a.mcp_event_id).map((a) => [a.mcp_event_id as string, a]));
  for (const e of events) {
    const p = e.payload ?? {};
    if (e.type === "agent.mcp_tool_result" || e.type === "agent.tool_result") {
      const id = p.mcp_tool_use_id ?? p.tool_use_id;
      if (id) results.set(id, e);
    } else if (e.type === "user.tool_confirmation" && p.tool_use_id) confirms.set(p.tool_use_id, e);
    else if (e.type === "span.model_request_end" && p.model_request_start_id) ends.set(p.model_request_start_id, e);
  }
  // The pipeline engine logs tool calls without ids: pair each result with the oldest unanswered call instead.
  const byOrder = new Map<number, AgentEvent>();
  const open: AgentEvent[] = [];
  for (const e of events) {
    if ((e.type === "agent.mcp_tool_use" || e.type === "agent.tool_use") && !e.payload?.id) open.push(e);
    else if ((e.type === "agent.mcp_tool_result" || e.type === "agent.tool_result") && !e.payload?.mcp_tool_use_id
             && !e.payload?.tool_use_id && open.length) byOrder.set(open.shift()!.id, e);
  }
  const paired = new Set([...results.values(), ...byOrder.values()].map((e) => e.id));
  const stats = { tools: 0, models: 0, outTokens: 0 };
  const items: Item[] = [];
  for (const e of events) {
    const p = e.payload ?? {};
    const id = p.id as string | undefined;
    switch (e.type) {
      case "user.message": items.push({ kind: "wake", ev: e, text: textOf(p.content) }); break;
      case "span.model_request_start": stats.models++; items.push({ kind: "model", ev: e, end: id ? ends.get(id) : undefined }); break;
      case "span.model_request_end": stats.outTokens += p.model_usage?.output_tokens ?? 0; break;
      case "agent.thinking": items.push({ kind: "thinking", ev: e }); break;
      case "agent.message": items.push({ kind: "say", ev: e, text: textOf(p.content) }); break;
      case "agent.mcp_tool_use":
      case "agent.tool_use":
        stats.tools++;
        items.push({ kind: "tool", ev: e, result: id ? results.get(id) : byOrder.get(e.id), confirm: id ? confirms.get(id) : undefined,
                     action: id ? byEvent.get(id) : undefined });
        break;
      case "agent.mcp_tool_result":
      case "agent.tool_result": if (!paired.has(e.id)) items.push({ kind: "result", ev: e }); break;
      case "session.status_running": items.push({ kind: "status", ev: e, label: "running" }); break;
      case "session.status_idle": items.push({ kind: "status", ev: e, label: `idle · ${p.stop_reason?.type ?? ""}` }); break;
      case "session.status_terminated": items.push({ kind: "status", ev: e, label: "terminated" }); break;
      case "session.error": items.push({ kind: "error", ev: e }); break;
      case "user.tool_confirmation": case "session.usage": case "session.thread_status_running": case "session.thread_status_idle": break;
      default: items.push({ kind: "other", ev: e });
    }
  }
  return { items, stats };
}

const at = (e: AgentEvent) => e.payload?.processed_at ?? e.created_at;
const secs = (a?: string, b?: string) => (a && b ? (new Date(b).getTime() - new Date(a).getTime()) / 1000 : null);

function FeedItem({ item, showRaw, active }: { item: Item; showRaw: boolean; active: boolean }) {
  const raw = showRaw && <pre className="raw">{JSON.stringify(item.ev.payload, null, 2)}</pre>;
  const when = <span className="muted small right">{fmtTime(at(item.ev))}</span>;
  switch (item.kind) {
    case "wake":
      return <li className="fi fi-wake"><div className="fi-head"><span className="tag">wake-up</span>{when}</div>
        <div className="fi-body">{item.text}</div>{raw}</li>;
    case "model": {
      const u = item.end?.payload?.model_usage;
      const d = secs(at(item.ev), item.end ? at(item.end) : undefined);
      return <li className="fi fi-model"><div className="fi-head"><span className="tag">model</span>
        {item.end ? <span className="muted small">{d != null && `${d.toFixed(1)}s · `}{u ? `${(u.output_tokens ?? 0).toLocaleString()} out · ${(u.cache_read_input_tokens ?? 0).toLocaleString()} cached in` : "done"}
          {item.end.payload?.is_error ? " · error" : ""}</span>
          : <span className="muted small"><span className="dot" /> generating…</span>}{when}</div>{raw}</li>;
    }
    case "thinking":
      return <li className="fi fi-thinking"><div className="fi-head"><span className="tag">thinking</span>
        <span className="muted small">reasoning happened here (content not exposed)</span>{when}</div>{raw}</li>;
    case "say":
      return <li className="fi fi-say"><div className="fi-head"><span className="tag">agent</span>{when}</div>
        <div className="fi-body">{item.text}</div>{raw}</li>;
    case "tool": return <ToolItem item={item} raw={raw} when={when} active={active} />;
    case "result":
      return <li className="fi"><div className="fi-head"><span className="tag">result</span>{when}</div>
        <pre className="fi-pre">{prettyResult(item.ev.payload?.content)}</pre>{raw}</li>;
    case "status":
      return <li className="fi-status"><span>{item.label}</span> <span className="muted small">{fmtTime(at(item.ev))}</span></li>;
    case "error":
      return <li className="fi fi-error"><div className="fi-head"><span className="tag tag-bad">error</span>{when}</div>
        <pre className="fi-pre">{JSON.stringify(item.ev.payload?.error ?? item.ev.payload, null, 2)}</pre></li>;
    default:
      return showRaw ? <li className="fi"><div className="fi-head"><span className="tag">{item.ev.type}</span>{when}</div>{raw}</li> : null;
  }
}

function ToolItem({ item, raw, when, active }: { item: Extract<Item, { kind: "tool" }>; raw: React.ReactNode; when: React.ReactNode; active: boolean }) {
  const p = item.ev.payload ?? {};
  const perm = p.evaluated_permission as string | undefined;
  const resultP = item.result?.payload;
  const waiting = item.action?.status === "pending_approval";
  const state = item.result ? (resultP?.is_error ? "error" : "done")
    : waiting ? "awaiting approval" : item.confirm?.payload?.result === "deny" ? "rejected" : active ? "running" : "no result";
  const [open, setOpen] = useState(false);
  const input = p.input ?? {};
  const headline = input.to_party ? `→ ${input.to_party}${input.channel ? ` via ${input.channel}` : ""}`
    : input.sql ? input.sql : input.case_id && Object.keys(input).length === 1 ? `case ${input.case_id}` : input.summary ?? input.query ?? "";

  return (
    <li className={`fi fi-tool st-${state.replace(" ", "-")}`}>
      <div className="fi-head" onClick={() => setOpen(!open)} style={{ cursor: "pointer" }}>
        <span className="tag">tool</span><strong>{p.name}</strong>
        <span className={`status s-${state === "done" ? "done" : state === "error" || state === "rejected" ? "rejected" : "pending_approval"}`}>{state}</span>
        {perm && perm !== "allow" && <span className="muted small">permission: {perm}</span>}
        <span className="muted small ellipsis">{String(headline).slice(0, 140)}</span>
        {when}
      </div>
      {(open || waiting) && (
        <div className="fi-cols">
          <div><div className="muted small">input</div><pre className="fi-pre">{prettyInput(input)}</pre></div>
          <div><div className="muted small">result</div>
            {item.result ? <pre className="fi-pre">{prettyResult(resultP?.content)}</pre>
              : <div className="muted small">{waiting ? "Waiting for a coordinator." : "No result yet."}</div>}
          </div>
        </div>
      )}
      {item.confirm && <div className="muted small">
        {item.confirm.payload?.result === "allow" ? "Approved" : "Rejected"}{item.action?.decided_by ? ` by ${item.action.decided_by}` : ""}
        {item.confirm.payload?.deny_message ? `: ${item.confirm.payload.deny_message}` : ""}</div>}
      {waiting && item.action && <ApproveBar action={item.action} />}
      {raw}
    </li>
  );
}

function ApproveBar({ action }: { action: Action }) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const decide = async (verb: "approve" | "reject") => {
    setBusy(true); setErr("");
    try { await hub(`/api/actions/${action.id}/${verb}`, { reason }); } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  };
  return (
    <div className="row">
      <input placeholder="Reason (sent to the agent if rejected)" value={reason} onChange={(e) => setReason(e.target.value)} />
      <button className="danger" disabled={busy} onClick={() => decide("reject")}>Reject</button>
      <button className="primary" disabled={busy} onClick={() => decide("approve")}>Approve</button>
      {err && <span className="error small">{err}</span>}
    </div>
  );
}

function prettyInput(input: Record<string, unknown>): string {
  return Object.entries(input).map(([k, v]) => `${k}: ${typeof v === "string" ? v : JSON.stringify(v, null, 2)}`).join("\n");
}

/** MCP results arrive as [{type:'text', text:'{"result":"..."}'}]; unwrap down to readable text/JSON. */
function prettyResult(content: unknown): string {
  let s = textOf(content);
  for (let i = 0; i < 3; i++) {
    try {
      const v = JSON.parse(s);
      if (v && typeof v === "object" && "result" in v && Object.keys(v).length === 1) { s = String((v as any).result); continue; }
      return JSON.stringify(v, null, 2);
    } catch { break; }
  }
  return s;
}
