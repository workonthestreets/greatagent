import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  fmtTime, go, hub, useLive, type Action, type AgentEvent, type AgentLive, type AgentRun, type Case,
} from "./lib";
import { ArrowUpRight } from "./icons";
import { Status } from "./ui";

/** /agents: one row per case the agent has worked, newest activity first; /agents/<case id> opens its live log.
 *  Staff only (agent_events, agent_runs and agent_live are staff-only under RLS). */
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
  // One row per case: its latest run, plus the case's run count and spend across runs.
  const rows = useMemo(() => {
    const seen = new Map<string, { run: AgentRun; runs: number; cents: number }>();
    for (const r of runs) {
      const row = seen.get(r.case_id);
      if (row) { row.runs++; row.cents += r.list_cost_cents ?? 0; }
      else seen.set(r.case_id, { run: r, runs: 1, cents: r.list_cost_cents ?? 0 });
    }
    return [...seen.values()];
  }, [runs]);
  const liveCount = rows.filter((r) => r.run.status === "running").length;
  const totalCost = runs.reduce((s, r) => s + (r.list_cost_cents ?? 0), 0);

  return (
    <main className="view agents" id="top">
      <header className="view-head">
        <h1 className="headline-lg">What the <span className="emphasis">agent</span> is doing.</h1>
        <p className="text-muted body-lg">
          Every wake-up, model call, tool call and approval, as it happens. Pick a case to follow its runs.
        </p>
      </header>

      <dl className="stats">
        <Stat label="Cases worked" value={rows.length} />
        <Stat label="Running now" value={liveCount} highlight={liveCount > 0} />
        <Stat label="Awaiting approval" value={pending.length} highlight={pending.length > 0} />
        <Stat label="Agent runs" value={runs.length} />
        <Stat label="Agent spend" value={`$${(totalCost / 100).toFixed(2)}`} />
      </dl>

      <div className="split">
        <section className="split__list" aria-labelledby="runs-title">
          <h2 className="section-title" id="runs-title">Runs</h2>
          <ul className="case-list">
            {rows.map(({ run, runs: n, cents }) => {
              const c = titles.get(run.case_id);
              const ask = waiting.get(run.case_id) ?? 0;
              const state = run.status === "running" ? "running" : ask ? "awaiting_approval" : stopLabel(run);
              return (
                <li key={run.case_id} className="case-row" aria-current={run.case_id === caseId ? "true" : undefined}
                    onClick={() => go(`/agents/${encodeURIComponent(run.case_id)}`)}>
                  <div className="case-row__top">
                    <span className="case-row__title">#{run.case_id} {c?.title ?? ""}</span>
                    <Status status={state} />
                  </div>
                  <div className="case-row__summary">
                    {fmtTime(run.updated_at)} · {n > 1 ? `${n} runs · ` : ""}${(cents / 100).toFixed(2)}
                    {run.session_id.startsWith("pipeline-") ? " · pipeline" : ""}
                  </div>
                </li>
              );
            })}
            {!rows.length && <li className="empty text-muted">The agent hasn't worked any case yet.</li>}
          </ul>
        </section>
        <section className="split__detail">
          {caseId ? <CaseAgent key={caseId} caseId={caseId} />
            : <p className="text-muted empty">Pick a run to watch what the agent did: wake-ups, model calls, tool calls with
                their results, approvals and its messages, live as they happen.</p>}
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

const STOP: Record<string, string> = { end_turn: "finished", requires_action: "needs_action", budget_reached: "budget_reached" };
const stopLabel = (r: AgentRun) => (r.stop_reason ? STOP[r.stop_reason] ?? r.stop_reason : r.status);

function CaseAgent({ caseId }: { caseId: string }) {
  const [c] = useLive<Case>("cases", (q) => q.eq("id", caseId), [caseId]);
  const runs = useLive<AgentRun>("agent_runs", (q) => q.eq("case_id", caseId).order("created_at", { ascending: false }), [caseId]);
  const [picked, setPicked] = useState<string | null>(null);
  const sessionId = picked ?? c?.session_id ?? runs[0]?.session_id ?? null;
  const run = runs.find((r) => r.session_id === sessionId);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const wake = async () => {
    setBusy(true); setErr("");
    try { await hub(`/api/cases/${caseId}/run`, {}); setPicked(null); } catch (e) { setErr((e as Error).message); }
    setBusy(false);
  };

  return (
    <div className="detail">
      <div className="detail__head">
        <h2 className="headline-md">#{caseId}&nbsp; {c?.title ?? ""}</h2>
        <button className="btn btn--secondary" disabled={busy} onClick={wake}>{busy ? "Waking agent…" : "Ask agent to re-assess"}</button>
      </div>
      {err && <p className="error-text">{err}</p>}
      {runs.length > 1 && (
        <div className="tabs detail__tabs" role="tablist" aria-label="Runs on this case">
          {runs.map((r, i) => (
            <button key={r.session_id} role="tab" className="tab" aria-selected={r.session_id === sessionId}
                    onClick={() => setPicked(r.session_id)}>
              Run {runs.length - i}<span className="tab__count">{fmtTime(r.created_at)}</span>
            </button>
          ))}
        </div>
      )}
      {sessionId ? <SessionLog key={sessionId} caseId={caseId} sessionId={sessionId} run={run} />
        : <p className="text-muted empty">The agent hasn't worked this case yet. Ask it to re-assess to start a run.</p>}
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

const textOf = (content: unknown): string =>
  Array.isArray(content) ? content.map((b) => (typeof b === "string" ? b : b?.text ?? "")).join("\n").trim() : String(content ?? "");

function SessionLog({ caseId, sessionId, run }: { caseId: string; sessionId: string; run?: AgentRun }) {
  const events = useLive<AgentEvent>("agent_events", (q) => q.eq("session_id", sessionId).order("id").limit(2000), [sessionId]);
  const live = useLive<AgentLive>("agent_live", (q) => q.eq("session_id", sessionId).eq("done", false).order("started_at"), [sessionId]);
  const actions = useLive<Action>("actions", (q) => q.eq("case_id", caseId).order("id"), [caseId]);
  const [showRaw, setShowRaw] = useState(false);

  const { items, stats } = useMemo(() => build(events, actions), [events, actions]);
  const isLive = run?.status === "running" || live.length > 0;

  // Keep the newest activity in view while the reader is at the bottom of the page.
  const endRef = useRef<HTMLDivElement>(null);
  const stick = useRef(true);
  useEffect(() => {
    const onScroll = () => { stick.current = window.innerHeight + window.scrollY >= document.body.scrollHeight - 160; };
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => { if (stick.current && isLive) endRef.current?.scrollIntoView({ block: "end" }); }, [items.length, live, isLive]);

  return (
    <>
      <div className="meta">
        <Status status={isLive ? "running" : run ? stopLabel(run) : "idle"} />
        <span>{stats.tools} tool calls</span>
        <span>{stats.models} model calls</span>
        <span>{stats.outTokens.toLocaleString()} output tokens</span>
        {run?.list_cost_cents != null && <span>${(run.list_cost_cents / 100).toFixed(2)}</span>}
        {run?.trace_url && <a className="meta__link" href={run.trace_url} target="_blank" rel="noreferrer">Trace <ArrowUpRight size={14} /></a>}
        <label className="afeed__raw"><input type="checkbox" checked={showRaw} onChange={(e) => setShowRaw(e.target.checked)} /> Raw events</label>
      </div>

      <ol className="afeed">
        {items.map((it) => <FeedItem key={it.ev.id} item={it} showRaw={showRaw} active={isLive} />)}
        {live.map((l) => (
          <li key={l.event_id} className="afeed__item afeed__item--say afeed__item--live">
            <div className="afeed__head">
              <span className="afeed__kind">{l.kind === "agent.thinking" ? "Thinking" : "Writing"}</span>
              <span className="live-dot" aria-label="live" />
            </div>
            {l.kind === "agent.thinking" ? <p className="text-muted body-sm afeed__note">The model is thinking…</p>
              : <div className="afeed__body">{l.text}<span className="afeed__caret" aria-hidden="true" /></div>}
          </li>
        ))}
        {!items.length && !live.length && <li className="empty text-muted">No events yet.</li>}
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
      case "session.status_running": items.push({ kind: "status", ev: e, label: "Running" }); break;
      case "session.status_idle": {
        const why = p.stop_reason?.type as string | undefined;
        items.push({ kind: "status", ev: e, label: why ? `Idle, ${(STOP[why] ?? why).replace(/_/g, " ")}` : "Idle" });
        break;
      }
      case "session.status_terminated": items.push({ kind: "status", ev: e, label: "Session ended" }); break;
      case "session.error": items.push({ kind: "error", ev: e }); break;
      case "user.tool_confirmation": case "session.usage": case "session.thread_status_running": case "session.thread_status_idle": break;
      default: items.push({ kind: "other", ev: e });
    }
  }
  return { items, stats };
}

const at = (e: AgentEvent) => e.payload?.processed_at ?? e.created_at;
const secs = (a?: string, b?: string) => (a && b ? (new Date(b).getTime() - new Date(a).getTime()) / 1000 : null);

function Row({ kind, label, when, extra, children }: { kind: string; label: string; when: string; extra?: ReactNode; children?: ReactNode }) {
  return (
    <li className={`afeed__item afeed__item--${kind}`}>
      <div className="afeed__head">
        <span className="afeed__kind">{label}</span>
        {extra}
        <time className="afeed__time">{fmtTime(when)}</time>
      </div>
      {children}
    </li>
  );
}

function FeedItem({ item, showRaw, active }: { item: Item; showRaw: boolean; active: boolean }) {
  const raw = showRaw && <pre className="afeed__pre afeed__pre--raw">{JSON.stringify(item.ev.payload, null, 2)}</pre>;
  const when = at(item.ev);
  switch (item.kind) {
    case "wake":
      return <Row kind="wake" label="Wake-up" when={when}><div className="afeed__body">{item.text}</div>{raw}</Row>;
    case "model": {
      const u = item.end?.payload?.model_usage;
      const d = secs(at(item.ev), item.end ? at(item.end) : undefined);
      const extra = item.end
        ? <span className="text-muted body-sm">{d != null && `${d.toFixed(1)}s · `}{u ? `${(u.output_tokens ?? 0).toLocaleString()} out · ${(u.cache_read_input_tokens ?? 0).toLocaleString()} cached` : "done"}{item.end.payload?.is_error ? " · error" : ""}</span>
        : <span className="text-muted body-sm"><span className="live-dot" /> generating</span>;
      return <Row kind="model" label="Model" when={when} extra={extra}>{raw}</Row>;
    }
    case "thinking":
      return <Row kind="model" label="Thinking" when={when} extra={<span className="text-muted body-sm">reasoning not exposed</span>}>{raw}</Row>;
    case "say":
      return <Row kind="say" label="Agent" when={when}><div className="afeed__body">{item.text}</div>{raw}</Row>;
    case "tool": return <ToolItem item={item} raw={raw} active={active} />;
    case "result":
      return <Row kind="tool" label="Result" when={when}><pre className="afeed__pre">{prettyResult(item.ev.payload?.content)}</pre>{raw}</Row>;
    case "status":
      return <li className="afeed__status"><span>{item.label}</span> · <time>{fmtTime(when)}</time></li>;
    case "error":
      return <Row kind="error" label="Error" when={when}><pre className="afeed__pre">{JSON.stringify(item.ev.payload?.error ?? item.ev.payload, null, 2)}</pre></Row>;
    default:
      return showRaw ? <Row kind="model" label={item.ev.type} when={when}>{raw}</Row> : null;
  }
}

function ToolItem({ item, raw, active }: { item: Extract<Item, { kind: "tool" }>; raw: ReactNode; active: boolean }) {
  const p = item.ev.payload ?? {};
  const resultP = item.result?.payload;
  const waiting = item.action?.status === "pending_approval";
  const denied = item.confirm?.payload?.result === "deny";
  const state = item.result ? (resultP?.is_error ? "failed" : "done")
    : waiting ? "awaiting_approval" : denied ? "rejected" : active ? "running" : "no_result";
  const [open, setOpen] = useState(false);
  const input = (p.input ?? {}) as Record<string, any>;
  const headline = input.to_party ? `to ${input.to_party}${input.channel ? ` via ${input.channel}` : ""}`
    : input.sql ?? input.summary ?? input.query ?? (input.case_id && Object.keys(input).length === 1 ? `case ${input.case_id}` : "");
  const expanded = open || waiting;

  return (
    <li className={`afeed__item afeed__item--tool ${waiting ? "afeed__item--ask" : ""} ${state === "failed" || state === "rejected" ? "afeed__item--bad" : ""}`}>
      <button className="afeed__head afeed__toggle" aria-expanded={expanded} onClick={() => setOpen(!open)}>
        <span className="afeed__kind">Tool</span>
        <span className="afeed__tool">{p.name}</span>
        <Status status={state} />
        {p.evaluated_permission && p.evaluated_permission !== "allow" && <span className="text-muted body-sm">permission: {p.evaluated_permission}</span>}
        <span className="afeed__headline">{String(headline)}</span>
        <time className="afeed__time">{fmtTime(at(item.ev))}</time>
      </button>
      {expanded && (
        <div className="afeed__cols">
          <div><div className="afeed__label">Input</div><pre className="afeed__pre">{prettyInput(input)}</pre></div>
          <div><div className="afeed__label">Result</div>
            {item.result ? <pre className="afeed__pre">{prettyResult(resultP?.content)}</pre>
              : <p className="text-muted body-sm">{waiting ? "Waiting for a coordinator." : "No result yet."}</p>}
          </div>
        </div>
      )}
      {item.confirm && <p className="text-muted body-sm afeed__note">
        {denied ? "Rejected" : "Approved"}{item.action?.decided_by ? ` by ${item.action.decided_by}` : ""}
        {item.confirm.payload?.deny_message ? `: ${item.confirm.payload.deny_message}` : ""}</p>}
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
    <div className="afeed__approve">
      <label className="sr-only" htmlFor={`reason-${action.id}`}>Reason</label>
      <input id={`reason-${action.id}`} className="input" placeholder="Reason (sent to the agent if rejected)" value={reason}
             onChange={(e) => setReason(e.target.value)} />
      <button className="btn btn--secondary" disabled={busy} onClick={() => decide("reject")}>Reject</button>
      <button className="btn btn--primary" disabled={busy} onClick={() => decide("approve")}>Approve</button>
      {err && <span className="error-text body-sm">{err}</span>}
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
      if (v && typeof v === "object" && "result" in v && Object.keys(v).length === 1) { s = String((v as { result: unknown }).result); continue; }
      return JSON.stringify(v, null, 2);
    } catch { break; }
  }
  return s;
}
