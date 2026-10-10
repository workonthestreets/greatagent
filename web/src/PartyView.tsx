import { useState, type ReactNode } from "react";
import { fmtTime, hub, useLive, type Case, type CaseEvent, type Profile, type Shipment } from "./lib";
import { Composer, Timeline } from "./Timeline";
import { Bell } from "./icons";
import { Status } from "./ui";

const HEADLINES: Record<string, { title: ReactNode; sub: string }> = {
  customer: {
    title: <>Your deliveries, in one <span className="emphasis">thread</span>.</>,
    sub: "Every message from the delivery desk about your parcels lands here, and you can write back at any time.",
  },
  driver: {
    title: <>Stops on your <span className="emphasis">route</span>.</>,
    sub: "The shipments you are carrying and the cases the desk has opened about them.",
  },
  depot: {
    title: <>Shipments at your <span className="emphasis">site</span>.</>,
    sub: "Parcels held or passing through your site, and what the desk needs from you.",
  },
  merchant: {
    title: <>Cases on your <span className="emphasis">orders</span>.</>,
    sub: "Delivery cases raised on your orders and where the desk has got to with each one.",
  },
};

/** Customers, drivers, depots and merchants: only their own shipments and cases (enforced by RLS). */
export default function PartyView({ profile, initialCase }: { profile: Profile; initialCase?: string }) {
  const shipments = useLive<Shipment>("shipments", (q) => q.order("updated_at", { ascending: false }));
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const [selected, setSelected] = useState<string | null>(initialCase ?? null);
  const current = selected ?? cases[0]?.id ?? null;
  const head = HEADLINES[profile.role] ?? HEADLINES.customer;

  return (
    <main className="view party" id="top">
      <header className="view-head">
        <h1 className="headline-lg">{head.title}</h1>
        <p className="text-muted body-lg">{head.sub}</p>
      </header>

      <section className="band-block band-block--single" aria-label="Latest from the desk">
        <div className="spectrum-band band--party" aria-hidden="true" />
        <div className="spectrum-cards spectrum-cards--single">
          {current ? <LatestFromDesk key={current} caseId={current} /> : (
            <article className="card-feature">
              <span className="card-feature__icon"><Bell /></span>
              <h2 className="headline-md">Latest from the desk</h2>
              <p className="card-feature__body">Nothing from the desk yet. Messages appear here as soon as they are sent.</p>
            </article>
          )}
        </div>
      </section>

      <section className="shipments" aria-labelledby="shipments-title">
        <h2 className="section-title" id="shipments-title">Shipments</h2>
        {shipments.length ? (
          <div className="card card--table">
            <table className="tbl tbl--stack">
              <thead><tr><th>Shipment</th><th>What</th><th>Status</th><th>ETA</th></tr></thead>
              <tbody>
                {shipments.map((s) => (
                  <tr key={s.id} onClick={() => s.case_id && setSelected(s.case_id)}
                    className={`clickable ${s.case_id && s.case_id === current ? "is-current" : ""}`}>
                    <td className="tbl__id">{s.id}</td>
                    <td>{s.description}</td>
                    <td>{s.status ? <Status status={s.status} /> : <span className="text-muted">Not set</span>}</td>
                    <td className="tbl__eta">{s.eta ?? <span className="text-muted">Not set</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="text-muted empty">Nothing here yet.</p>}
      </section>

      <div className="split">
        <section className="split__list" aria-labelledby="party-cases-title">
          <div className="section-head">
            <h2 className="section-title" id="party-cases-title">Cases</h2>
          </div>
          <ul className="case-list">
            {cases.map((c) => (
              <li key={c.id} className="case-row" aria-current={c.id === current ? "true" : undefined} onClick={() => setSelected(c.id)}>
                <div className="case-row__top">
                  <span className="case-row__title">#{c.id} {c.title}</span>
                  <Status status={c.status} />
                </div>
                <div className="case-row__summary">Updated {fmtTime(c.updated_at)}</div>
              </li>
            ))}
            {!cases.length && <li className="empty text-muted">No cases yet.</li>}
          </ul>
          {profile.role === "customer" && <NewRequest onCreated={setSelected} />}
        </section>
        <section className="split__detail">
          {current ? <Thread key={current} caseId={current} /> : <p className="text-muted empty">No cases yet.</p>}
        </section>
      </div>
    </main>
  );
}

/** The hero of the customer side: the desk's most recent message on the current case (what the voice line reads out). */
function LatestFromDesk({ caseId }: { caseId: string }) {
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

function Thread({ caseId }: { caseId: string }) {
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
      <Composer caseId={caseId} placeholder="Write to the delivery desk…" />
    </div>
  );
}

function NewRequest({ onCreated }: { onCreated: (id: string) => void }) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [shipment, setShipment] = useState("");
  const [err, setErr] = useState("");
  const submit = async () => {
    setErr("");
    try {
      const r = await hub("/api/cases", { title, body, shipment_id: shipment || null });
      setOpen(false); setTitle(""); setBody(""); setShipment("");
      onCreated(r.case_id);
    } catch (e) { setErr((e as Error).message); }
  };
  if (!open) return <button className="btn btn--primary new-request__open" onClick={() => setOpen(true)}>New request</button>;
  return (
    <div className="card new-request">
      <label className="field">
        <span className="field__label">What's it about?</span>
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
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
