import { useState } from "react";
import { fmtTime, hub, useLive, type Case, type CaseEvent, type Profile, type Shipment } from "./lib";
import { Composer, Timeline } from "./Timeline";

const TITLES: Record<string, string> = {
  customer: "My deliveries", driver: "My stops", depot: "Shipments at my site", merchant: "Cases on my orders",
};

/** Customers, drivers, depots and merchants: only their own shipments and cases (enforced by RLS). */
export default function PartyView({ profile }: { profile: Profile }) {
  const shipments = useLive<Shipment>("shipments", (q) => q.order("updated_at", { ascending: false }));
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const [selected, setSelected] = useState<string | null>(null);
  const current = selected ?? cases[0]?.id ?? null;

  return (
    <main className="party">
      <section className="card">
        <h2>{TITLES[profile.role]}</h2>
        {shipments.length ? (
          <table className="tbl">
            <thead><tr><th>Shipment</th><th>What</th><th>Status</th><th>ETA</th></tr></thead>
            <tbody>
              {shipments.map((s) => (
                <tr key={s.id} onClick={() => s.case_id && setSelected(s.case_id)} className="clickable">
                  <td>{s.id}</td><td>{s.description}</td><td>{s.status?.replace("_", " ")}</td><td>{s.eta ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="muted">Nothing here yet.</p>}
      </section>

      <div className="split">
        <section className="card list">
          <h2>Cases</h2>
          <ul className="cases">
            {cases.map((c) => (
              <li key={c.id} className={c.id === current ? "active" : ""} onClick={() => setSelected(c.id)}>
                <div className="row"><strong>#{c.id}</strong><span className={`status s-${c.status}`}>{c.status.replace("_", " ")}</span></div>
                <div>{c.title}</div>
                <div className="muted small">Updated {fmtTime(c.updated_at)}</div>
              </li>
            ))}
          </ul>
          {profile.role === "customer" && <NewRequest onCreated={setSelected} />}
        </section>
        <section className="card detail">
          {current ? <Thread key={current} caseId={current} /> : <p className="muted">No cases yet.</p>}
        </section>
      </div>
    </main>
  );
}

function Thread({ caseId }: { caseId: string }) {
  const [c] = useLive<Case>("cases", (q) => q.eq("id", caseId), [caseId]);
  const events = useLive<CaseEvent>("case_events", (q) => q.eq("case_id", caseId).order("ts").order("id"), [caseId]);
  if (!c) return <p className="muted">Loading…</p>;
  return (
    <div>
      <h2>#{c.id} {c.title}</h2>
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
  if (!open) return <button className="primary wide" onClick={() => setOpen(true)}>New request</button>;
  return (
    <div className="stack">
      <input placeholder="What's it about?" value={title} onChange={(e) => setTitle(e.target.value)} />
      <input placeholder="Shipment reference (optional)" value={shipment} onChange={(e) => setShipment(e.target.value)} />
      <textarea placeholder="Tell us what happened" rows={4} value={body} onChange={(e) => setBody(e.target.value)} />
      <div className="row">
        <button className="ghost" onClick={() => setOpen(false)}>Cancel</button>
        <button className="primary" disabled={!title || !body} onClick={submit}>Send</button>
      </div>
      {err && <p className="error">{err}</p>}
    </div>
  );
}
