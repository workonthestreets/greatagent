import { useState } from "react";
import { fmtTime, hub, type CaseEvent } from "./lib";

const KIND_LABEL: Record<string, string> = {
  message: "Message", call: "Call", note: "Internal note", system: "System",
  agent_message: "Desk (AI)", decision: "AI decision",
};

const DESK_ROLES = new Set(["agent", "desk", "coordinator", "admin"]);

/** Desk / agent events get the ink dot; system errors the brick dot; everyone else a muted dot. */
function tone(e: CaseEvent): "desk" | "alert" | "other" {
  if (e.kind === "system" && /error/i.test(e.body)) return "alert";
  if (e.kind === "agent_message" || e.kind === "decision" || DESK_ROLES.has(e.author_role ?? "")) return "desk";
  return "other";
}

const isAI = (e: CaseEvent) => e.kind === "agent_message" || e.kind === "decision" || e.author_role === "agent";

export function Timeline({ events }: { events: CaseEvent[] }) {
  if (!events.length) return <p className="text-muted empty">No activity yet.</p>;
  return (
    <ol className="timeline">
      {events.map((e) => {
        const label = isAI(e) ? "Desk (AI)"
          : e.kind !== "message" ? (KIND_LABEL[e.kind] ?? e.kind) : null;
        return (
          <li key={e.id} className={`ev ev--${tone(e)} ${e.visibility === "staff" ? "ev--staff" : ""}`}>
            <span className="ev__dot" aria-hidden="true" />
            <div className="ev__head">
              <span className="ev__who">
                <span className="ev__author">{e.author || "Unknown"}</span>
                {label && <span className={`ev__kind ${isAI(e) ? "ev__kind--ai" : ""}`}>{label}</span>}
                {e.to_party && <span className="text-muted">to {e.to_party}</span>}
                {e.channel && <span className="text-muted">via {e.channel}</span>}
                {e.visibility === "staff" && <span className="ev__internal">internal</span>}
              </span>
              <time className="ev__time">{fmtTime(e.ts)}</time>
            </div>
            <div className="ev__body">{e.body}</div>
          </li>
        );
      })}
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
      <label className="sr-only" htmlFor={`composer-${caseId}`}>Message</label>
      <textarea id={`composer-${caseId}`} className="input" value={body} onChange={(e) => setBody(e.target.value)}
        placeholder={placeholder} rows={3} />
      <div className="composer__row">
        <span className="composer__note">{note}</span>
        <button className="btn btn--primary" disabled={busy || !body.trim()} onClick={send}>{busy ? "Sending…" : "Send"}</button>
      </div>
    </div>
  );
}
