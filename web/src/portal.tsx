import { useEffect, useRef, useState, type ReactNode } from "react";
import { fmtTime, hub, useLive, type Case, type CaseEvent, type Shipment } from "./lib";
import { Composer, Timeline } from "./Timeline";
import { Bell } from "./icons";
import { Status } from "./ui";

/** Shared pieces of the four party portals (customer, driver, depot, merchant). RLS decides which rows each one sees. */
export { Composer };

export function PortalHead({ title, sub }: { title: ReactNode; sub: string }) {
  return (
    <header className="view-head">
      <h1 className="headline-lg">{title}</h1>
      <p className="text-muted body-lg">{sub}</p>
    </header>
  );
}

/** The one spectrum band of a portal: the desk's latest message on the current case sits over it. */
export function LatestBand({ caseId }: { caseId: string | null }) {
  return (
    <section className="band-block band-block--single" aria-label="Latest from the desk">
      <div className="spectrum-band band--party" aria-hidden="true" />
      <div className="spectrum-cards spectrum-cards--single">
        {caseId ? <LatestFromDesk key={caseId} caseId={caseId} /> : (
          <article className="card-feature">
            <span className="card-feature__icon"><Bell /></span>
            <h2 className="headline-md">Latest from the desk</h2>
            <p className="card-feature__body">Nothing from the desk yet. Messages appear here as soon as they are sent.</p>
          </article>
        )}
      </div>
    </section>
  );
}

/** The hero of a portal: the desk's most recent message on the current case (what the voice line reads out). */
export function LatestFromDesk({ caseId }: { caseId: string }) {
  const events = useLive<CaseEvent>("case_events", (q) => q.eq("case_id", caseId).order("ts").order("id"), [caseId]);
  const fromDesk = events.filter((e) => e.kind === "agent_message" || (e.kind === "message" && e.author_role === "agent"));
  const latest = fromDesk[fromDesk.length - 1] ?? events[events.length - 1];
  const reply = () => {
    const el = document.getElementById(`composer-${caseId}`) as HTMLTextAreaElement | null;
    el?.scrollIntoView({ behavior: "smooth", block: "center" });
    el?.focus({ preventScroll: true });
  };
  return (
    <article className="card-feature latest">
      <span className="card-feature__icon"><Bell /></span>
      <h2 className="headline-md">Latest from the desk</h2>
      <p className="card-feature__body latest__body">{latest ? latest.body : "Nothing from the desk yet on this case."}</p>
      {latest && (
        <p className="latest__meta">
          {fmtTime(latest.ts)}{latest.channel ? `, via ${latest.channel}` : ""} on case #{caseId}
        </p>
      )}
      <button className="btn btn--inverse card-feature__cta" onClick={reply}>Reply</button>
    </article>
  );
}

export function CaseList({ cases, current, onSelect, empty = "No cases yet." }: {
  cases: Case[]; current: string | null; onSelect: (id: string) => void; empty?: string;
}) {
  return (
    <ul className="case-list">
      {cases.map((c) => (
        <li key={c.id} className="case-row" aria-current={c.id === current ? "true" : undefined} onClick={() => onSelect(c.id)}>
          <div className="case-row__top">
            <span className="case-row__title">#{c.id} {c.title}</span>
            <Status status={c.status} />
          </div>
          <div className="case-row__summary">Updated {fmtTime(c.updated_at)}</div>
        </li>
      ))}
      {!cases.length && <li className="empty text-muted">{empty}</li>}
    </ul>
  );
}

/** Case header, timeline and composer. `extra` sits between the timeline and the composer (the merchant's decision panel). */
export function Thread({ caseId, extra }: { caseId: string; extra?: (c: Case) => ReactNode }) {
  const [c] = useLive<Case>("cases", (q) => q.eq("id", caseId), [caseId]);
  const events = useLive<CaseEvent>("case_events", (q) => q.eq("case_id", caseId).order("ts").order("id"), [caseId]);
  if (!c) return <p className="text-muted empty">Loading…</p>;
  return (
    <div className="detail">
      <div className="detail__head">
        <h2 className="headline-md">#{c.id}&nbsp; {c.title}</h2>
      </div>
      <div className="meta"><Status status={c.status} />{c.shipment_id && <span>Shipment {c.shipment_id}</span>}</div>
      <Timeline events={events} />
      {extra?.(c)}
      <Composer caseId={caseId} placeholder="Write to the delivery desk…" />
    </div>
  );
}

/** Cases list on the left, thread on the right. `listFooter` goes under the list (new request form). */
export function CasesSplit({ cases, current, onSelect, listFooter, extra }: {
  cases: Case[]; current: string | null; onSelect: (id: string) => void; listFooter?: ReactNode; extra?: (c: Case) => ReactNode;
}) {
  return (
    <div className="split">
      <section className="split__list" aria-labelledby="party-cases-title">
        <div className="section-head">
          <h2 className="section-title" id="party-cases-title">Cases</h2>
        </div>
        <CaseList cases={cases} current={current} onSelect={onSelect} />
        {listFooter}
      </section>
      <section className="split__detail">
        {current ? <Thread key={current} caseId={current} extra={extra} /> : <p className="text-muted empty">No cases yet.</p>}
      </section>
    </div>
  );
}

/** Opens a case through the hub. `shipment` prefills the reference (driver and depot "Report a problem"). */
export function NewRequest({ onCreated, shipment: prefill, startOpen = false, label = "New request" }: {
  onCreated: (id: string) => void; shipment?: string; startOpen?: boolean; label?: string;
}) {
  const [open, setOpen] = useState(startOpen);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [shipment, setShipment] = useState(prefill ?? "");
  const [err, setErr] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (startOpen) ref.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [startOpen]);
  const submit = async () => {
    setErr("");
    try {
      const r = await hub("/api/cases", { title, body, shipment_id: shipment || null });
      setOpen(false); setTitle(""); setBody(""); setShipment("");
      onCreated(r.case_id);
    } catch (e) { setErr((e as Error).message); }
  };
  if (!open) return <button className="btn btn--primary new-request__open" onClick={() => setOpen(true)}>{label}</button>;
  return (
    <div className="card new-request" ref={ref}>
      <label className="field">
        <span className="field__label">What's it about?</span>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} autoFocus={startOpen} />
      </label>
      <label className="field">
        <span className="field__label">Shipment reference <span className="text-muted">(optional)</span></span>
        <input className="input" placeholder="DL-103" value={shipment} onChange={(e) => setShipment(e.target.value)} />
      </label>
      <label className="field">
        <span className="field__label">Tell us what happened</span>
        <textarea className="input" rows={4} value={body} onChange={(e) => setBody(e.target.value)} />
      </label>
      <div className="new-request__actions">
        <button className="btn btn--secondary" onClick={() => setOpen(false)}>Cancel</button>
        <button className="btn btn--primary" disabled={!title || !body} onClick={submit}>Send</button>
      </div>
      {err && <p className="error-text">{err}</p>}
    </div>
  );
}

export type StatusOption = { status: string; label: string };

/** Driver stops and depot shipments: one row per shipment with its status, a note field and the status pills. */
export function ShipmentStops({ title, shipments, options, empty, onReport, onSelectCase, currentCase }: {
  title: string; shipments: Shipment[]; options: StatusOption[]; empty: string;
  onReport: (shipmentId: string) => void; onSelectCase: (caseId: string) => void; currentCase: string | null;
}) {
  return (
    <section className="shipments" aria-labelledby="stops-title">
      <div className="section-head">
        <h2 className="section-title" id="stops-title">{title}</h2>
        {shipments.length > 0 && <span className="text-muted body-sm">{shipments.length} {shipments.length === 1 ? "shipment" : "shipments"}</span>}
      </div>
      {shipments.length ? (
        <ol className="card stops">
          {shipments.map((s) => (
            <Stop key={s.id} shipment={s} options={options} onReport={() => onReport(s.id)}
              onSelectCase={onSelectCase} isCurrent={!!s.case_id && s.case_id === currentCase} />
          ))}
        </ol>
      ) : <p className="text-muted empty">{empty}</p>}
    </section>
  );
}

function Stop({ shipment: s, options, onReport, onSelectCase, isCurrent }: {
  shipment: Shipment; options: StatusOption[]; onReport: () => void; onSelectCase: (caseId: string) => void; isCurrent: boolean;
}) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [shown, setShown] = useState<string | null>(null);
  const status = shown ?? s.status;
  useEffect(() => setShown(null), [s.status]);
  const set = async (o: StatusOption) => {
    setBusy(o.status);
    setMsg("");
    try {
      const r = await hub(`/api/shipments/${s.id}/status`, { status: o.status, note });
      setShown(r?.status ?? o.status);
      setNote("");
      setMsg(`Marked ${o.label.toLowerCase()}.${s.case_id ? " The desk has it." : ""}`);
    } catch (e) {
      setMsg((e as Error).message);
    }
    setBusy(null);
  };
  return (
    <li className={`stop ${isCurrent ? "is-current" : ""}`}>
      <div className="stop__head">
        <span className="tbl__id">{s.id}</span>
        <span className="stop__what">{s.description ?? "No description"}</span>
        {status ? <Status status={status} /> : <span className="text-muted body-sm">Not set</span>}
      </div>
      <div className="stop__meta">
        <span>{s.eta ? `ETA ${s.eta}` : "ETA not set"}</span>
        {s.case_id && (
          <button className="stop__case" onClick={() => onSelectCase(s.case_id!)}>Case #{s.case_id}</button>
        )}
      </div>
      <div className="stop__actions">
        <label className="sr-only" htmlFor={`note-${s.id}`}>Note for {s.id}</label>
        <input id={`note-${s.id}`} className="input stop__note" placeholder="Note (optional)" value={note}
          onChange={(e) => setNote(e.target.value)} />
        <div className="stop__pills">
          {options.map((o) => (
            <button key={o.status} className="btn btn--secondary btn--sm" disabled={!!busy || status === o.status}
              aria-pressed={status === o.status} onClick={() => set(o)}>
              {busy === o.status ? "Saving…" : o.label}
            </button>
          ))}
          <button className="btn-text btn-text--ink" onClick={onReport}>Report a problem</button>
        </div>
      </div>
      {msg && <p className="stop__msg">{msg}</p>}
    </li>
  );
}

/** Driver and depot portals share this shape: head, band, shipments with status pills, then cases and thread. */
export function ShipmentPortal({ head, sub, stopsTitle, options, column, partyName, empty, initialCase }: {
  head: ReactNode; sub: string; stopsTitle: string; options: StatusOption[]; column: "driver_name" | "depot";
  partyName: string | null; empty: string; initialCase?: string;
}) {
  const shipments = useLive<Shipment>("shipments",
    (q) => (partyName ? q.eq(column, partyName) : q).order("updated_at", { ascending: false }), [partyName]);
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const [selected, setSelected] = useState<string | null>(initialCase ?? null);
  const [report, setReport] = useState<{ shipment: string; key: number } | null>(null);
  const current = selected ?? cases[0]?.id ?? null;
  const created = (id: string) => { setReport(null); setSelected(id); };

  return (
    <main className="view party" id="top">
      <PortalHead title={head} sub={sub} />
      <LatestBand caseId={current} />
      <ShipmentStops title={stopsTitle} shipments={shipments} options={options} empty={empty}
        onReport={(id) => setReport({ shipment: id, key: Date.now() })} onSelectCase={setSelected} currentCase={current} />
      <CasesSplit cases={cases} current={current} onSelect={setSelected}
        listFooter={report
          ? <NewRequest key={report.key} shipment={report.shipment} startOpen onCreated={created} label="Report a problem" />
          : <NewRequest key="idle" onCreated={created} label="Report a problem" />} />
    </main>
  );
}
