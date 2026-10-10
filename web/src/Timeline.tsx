import { useState } from "react";
import { fmtTime, hub, type CaseEvent } from "./lib";

const KIND_LABEL: Record<string, string> = {
  message: "Message", call: "Call", note: "Internal note", system: "System",
  agent_message: "Desk (AI)", decision: "AI decision",
};

export function Timeline({ events }: { events: CaseEvent[] }) {
  if (!events.length) return <p className="muted">No activity yet.</p>;
  return (
    <ol className="timeline">
      {events.map((e) => (
        <li key={e.id} className={`ev ev-${e.kind} ${e.visibility === "staff" ? "ev-staff" : ""}`}>
          <div className="ev-head">
            <span className="tag">{KIND_LABEL[e.kind] ?? e.kind}</span>
            <strong>{e.author || "—"}</strong>
            {e.to_party && <span className="muted">→ {e.to_party}</span>}
            {e.channel && <span className="muted">· {e.channel}</span>}
            <span className="muted right">{fmtTime(e.ts)}</span>
          </div>
          <div className="ev-body">{e.body}</div>
        </li>
      ))}
    </ol>
  );
}

export function Composer({ caseId, placeholder }: { caseId: string; placeholder: string }) {
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const send = async () => {
    if (!body.trim()) return;
    setBusy(true);
    setNote("");
    try {
      await hub(`/api/cases/${caseId}/messages`, { body });
      setBody("");
      setNote("Sent. The desk is looking at it.");
    } catch (err) {
      setNote(String((err as Error).message));
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="composer">
      <textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder={placeholder} rows={3} />
      <div className="row">
        <span className="muted small">{note}</span>
        <button className="primary" disabled={busy || !body.trim()} onClick={send}>{busy ? "Sending…" : "Send"}</button>
      </div>
    </div>
  );
}
