import { useState } from "react";
import { useLive, type Case, type Profile, type Shipment } from "./lib";
import { CasesSplit, LatestBand, NewRequest, PortalHead } from "./portal";
import { Status } from "./ui";

/** Customers: only their own shipments and cases (enforced by RLS). */
export default function CustomerPortal({ initialCase }: { profile: Profile; initialCase?: string }) {
  const shipments = useLive<Shipment>("shipments", (q) => q.order("updated_at", { ascending: false }));
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const [selected, setSelected] = useState<string | null>(initialCase ?? null);
  const current = selected ?? cases[0]?.id ?? null;

  return (
    <main className="view party" id="top">
      <PortalHead
        title={<>Your deliveries, in one <span className="emphasis">thread</span>.</>}
        sub="Every message from the delivery desk about your parcels lands here, and you can write back at any time." />

      <LatestBand caseId={current} />

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

      <CasesSplit cases={cases} current={current} onSelect={setSelected}
        listFooter={<NewRequest onCreated={setSelected} />} />
    </main>
  );
}
