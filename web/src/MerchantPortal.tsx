import { useState } from "react";
import { hub, useLive, type Case, type MerchantDecision, type Profile } from "./lib";
import { CasesSplit, LatestBand, PortalHead } from "./portal";

const DECISIONS: { id: MerchantDecision; label: string }[] = [
  { id: "approve_replacement", label: "Approve replacement" },
  { id: "approve_refund", label: "Approve refund" },
  { id: "decline", label: "Decline" },
];

/** Merchants and partners: cases on their orders, the thread, and a decision panel the desk acts on. */
export default function MerchantPortal({ initialCase }: { profile: Profile; initialCase?: string }) {
  const cases = useLive<Case>("cases", (q) => q.order("updated_at", { ascending: false }));
  const [selected, setSelected] = useState<string | null>(initialCase ?? null);
  const current = selected ?? cases[0]?.id ?? null;

  return (
    <main className="view party" id="top">
      <PortalHead
        title={<>Cases on your <span className="emphasis">orders</span>.</>}
        sub="Delivery cases raised on your orders and where the desk has got to with each one." />
      <LatestBand caseId={current} />
      <CasesSplit cases={cases} current={current} onSelect={setSelected}
        extra={(c) => <DecisionPanel key={c.id} caseId={c.id} />} />
    </main>
  );
}

function DecisionPanel({ caseId }: { caseId: string }) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const send = async (decision: MerchantDecision) => {
    setBusy(true);
    setMsg("");
    try {
      await hub(`/api/cases/${caseId}/merchant_decision`, { decision, note });
      setNote("");
      setMsg("Sent. The desk is looking at it.");
    } catch (e) {
      setMsg((e as Error).message);
    }
    setBusy(false);
  };
  return (
    <section className="card merchant-decision" aria-labelledby={`md-${caseId}`}>
      <h3 className="section-title" id={`md-${caseId}`}>Your decision</h3>
      <p className="text-muted body-sm">The desk tells the customer and arranges the next step.</p>
      <label className="sr-only" htmlFor={`md-note-${caseId}`}>Note</label>
      <input id={`md-note-${caseId}`} className="input" placeholder="Note for the desk (optional)" value={note}
        onChange={(e) => setNote(e.target.value)} />
      <div className="merchant-decision__row">
        {DECISIONS.map((d) => (
          <button key={d.id} className="btn btn--secondary btn--sm" disabled={busy} onClick={() => send(d.id)}>{d.label}</button>
        ))}
      </div>
      {msg && <p className="composer__note">{msg}</p>}
    </section>
  );
}
