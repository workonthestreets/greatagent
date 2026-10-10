import { useCallback, useEffect, useRef, useState, type CSSProperties, type PointerEvent as RPointerEvent } from "react";
import { fmtTime, hub, useRefs, type Action, type DecisionResponse, type MedalRef } from "./lib";
import { Award, Check, Coins, Mail, Send, X } from "./icons";
import { statusText } from "./ui";

const THRESHOLD = 120;
const FLY_MS = 240;

const CHANNEL_LABEL: Record<string, string> = {
  portal: "Customer portal", email: "Email", sms: "SMS", voice: "Voice line", phone: "Phone", whatsapp: "WhatsApp",
};
const channelLabel = (c?: string) => (c ? CHANNEL_LABEL[c] ?? statusText(c) : "");

type Verb = "approve" | "reject";

/** Pending drafts as a stack of charcoal cards over the band. Drag the top card right to approve, left to reject;
 *  the buttons under the deck and the arrow keys do the same. Rows leave the deck when they leave pending_approval. */
export default function SwipeDeck({ pending, onOpen }: { pending: Action[]; onOpen: (caseId: string) => void }) {
  const [gone, setGone] = useState<Set<number>>(new Set());
  const [reasons, setReasons] = useState<Record<number, string>>({});
  const [dx, setDx] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [flying, setFlying] = useState<Verb | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [toast, setToast] = useState<{ key: number; text: string } | null>(null);
  const [medals, setMedals] = useState<MedalRef[]>([]);
  const start = useRef<{ x: number; y: number; id: number } | null>(null);

  const deck = pending.filter((a) => !gone.has(a.id));
  const top = deck[0];

  // Forget local decisions once realtime has caught up (the row left pending), so the set stays small.
  useEffect(() => {
    setGone((g) => {
      const ids = new Set(pending.map((a) => a.id));
      const next = new Set([...g].filter((id) => ids.has(id)));
      return next.size === g.size ? g : next;
    });
  }, [pending]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 2600);
    return () => clearTimeout(t);
  }, [toast]);

  const decide = useCallback(async (verb: Verb) => {
    if (!top || busy) return;
    const action = top;
    const reason = (reasons[action.id] ?? "").trim();
    setBusy(true);
    setErr("");
    setFlying(verb);
    setDx(verb === "approve" ? 1 : -1);
    await new Promise((r) => setTimeout(r, FLY_MS));
    setGone((g) => new Set(g).add(action.id));
    setFlying(null);
    setDx(0);
    try {
      const res = (await hub(`/api/actions/${action.id}/${verb}`, { reason })) as DecisionResponse;
      const rw = res?.rewards;
      if (rw && rw.coins) setToast({ key: Date.now(), text: `+${rw.coins} coins` });
      if (rw?.new_medals?.length) setMedals((m) => [...m, ...rw.new_medals]);
    } catch (e) {
      // Put the card back on top so the decision can be retried.
      setGone((g) => { const n = new Set(g); n.delete(action.id); return n; });
      setErr((e as Error).message);
    }
    setBusy(false);
  }, [top, busy, reasons]);

  // Arrow keys decide on the top card, unless the user is typing.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      if (medals.length) return;
      if (e.key === "ArrowRight") { e.preventDefault(); decide("approve"); }
      if (e.key === "ArrowLeft") { e.preventDefault(); decide("reject"); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [decide, medals.length]);

  const onDown = (e: RPointerEvent<HTMLElement>) => {
    if (busy || e.button !== 0) return;
    if ((e.target as HTMLElement).closest("input, textarea, button, a")) return;
    start.current = { x: e.clientX, y: e.clientY, id: e.pointerId };
  };
  const onMove = (e: RPointerEvent<HTMLElement>) => {
    const s = start.current;
    if (!s || s.id !== e.pointerId) return;
    const mx = e.clientX - s.x;
    if (!dragging) {
      // Vertical movement first means the user is scrolling the draft: let it go.
      if (Math.abs(e.clientY - s.y) > 8 && Math.abs(mx) < 8) { start.current = null; return; }
      if (Math.abs(mx) < 6) return;
      setDragging(true);
      try { e.currentTarget.setPointerCapture(e.pointerId); } catch { /* pointer already gone */ }
    }
    setDx(mx);
  };
  const onUp = () => {
    if (!start.current) return;
    start.current = null;
    if (!dragging) return;
    setDragging(false);
    if (dx > THRESHOLD) decide("approve");
    else if (dx < -THRESHOLD) decide("reject");
    else setDx(0);
  };

  if (!deck.length && !medals.length && !toast) return null;

  const intent: Verb | null = flying ?? (dx > 24 ? "approve" : dx < -24 ? "reject" : null);
  const strength = flying ? 1 : Math.min(1, Math.abs(dx) / THRESHOLD);
  const topStyle = flying
    ? { transform: `translateX(${flying === "approve" ? 140 : -140}%) rotate(${flying === "approve" ? 14 : -14}deg)`, opacity: 0 }
    : { transform: `translateX(${dx}px) rotate(${dx / 22}deg)` };

  return (
    <>
      {deck.length > 0 && (
        <section className="approvals" aria-labelledby="approvals-title">
          <div className="section-head">
            <h2 className="section-title" id="approvals-title">Waiting for your approval</h2>
            <span className="text-muted body-sm">{deck.length} {deck.length === 1 ? "draft" : "drafts"} left</span>
          </div>
          <div className="band-block">
            <div className="spectrum-band band--desk" aria-hidden="true" />
            <div className="deck" aria-live="polite">
              {deck.slice(0, 3).map((a, i) => (
                <DraftCard key={a.id} action={a} depth={i}
                  style={i === 0 ? topStyle : undefined}
                  className={i === 0 ? `deck__card--top ${dragging ? "is-dragging" : ""}` : ""}
                  intent={i === 0 ? intent : null} strength={strength}
                  reason={reasons[a.id] ?? ""} onReason={(v) => setReasons((r) => ({ ...r, [a.id]: v }))}
                  onOpen={() => onOpen(a.case_id)}
                  pointer={i === 0 ? { onPointerDown: onDown, onPointerMove: onMove, onPointerUp: onUp, onPointerCancel: onUp } : undefined} />
              ))}
            </div>
          </div>
          <div className="deck__controls">
            <button className="btn btn--icon deck__btn" aria-label="Reject draft" disabled={busy} onClick={() => decide("reject")}>
              <X />
            </button>
            <span className="deck__hint">Drag the card, or use the arrow keys</span>
            <button className="btn btn--icon deck__btn" aria-label="Approve draft" disabled={busy} onClick={() => decide("approve")}>
              <Check />
            </button>
          </div>
          {err && <p className="error-text deck__error" role="alert">{err}</p>}
        </section>
      )}

      {toast && (
        <div key={toast.key} className="toast" role="status">
          <Coins size={16} />
          <span>{toast.text}</span>
        </div>
      )}

      {medals.length > 0 && <MedalUnlock medal={medals[0]} onClose={() => setMedals((m) => m.slice(1))} />}
    </>
  );
}

type PointerHandlers = {
  onPointerDown: (e: RPointerEvent<HTMLElement>) => void;
  onPointerMove: (e: RPointerEvent<HTMLElement>) => void;
  onPointerUp: () => void;
  onPointerCancel: () => void;
};

function DraftCard({ action, depth, style, className, intent, strength, reason, onReason, onOpen, pointer }: {
  action: Action; depth: number; style?: CSSProperties; className: string; intent: Verb | null; strength: number;
  reason: string; onReason: (v: string) => void; onOpen: () => void; pointer?: PointerHandlers;
}) {
  const { caseRef } = useRefs();
  const a = action.args as Record<string, string>;
  // Fade the bottom of a long draft while more of it is hidden below, so the cut reads as a scroll.
  const draftRef = useRef<HTMLDivElement>(null);
  const [moreBelow, setMoreBelow] = useState(false);
  const checkMore = () => {
    const el = draftRef.current;
    if (el) setMoreBelow(el.scrollTop + el.clientHeight < el.scrollHeight - 2);
  };
  useEffect(checkMore, [a.body, a.subject]);
  const isTop = depth === 0;
  return (
    <article className={`card-feature approval deck__card deck__card--d${depth} ${className}`} style={style}
      aria-hidden={isTop ? undefined : true} {...pointer}>
      {isTop && intent && (
        <span className={`deck__stamp deck__stamp--${intent}`} style={{ opacity: Math.min(1, strength * 1.5) }} aria-hidden="true">
          {intent === "approve" ? "Approve" : "Reject"}
        </span>
      )}
      <div className="approval__top">
        <span className="card-feature__icon">{a.channel === "email" ? <Mail /> : <Send />}</span>
        <span className="approval__meta">
          <button className="approval__case" onClick={onOpen} tabIndex={isTop ? 0 : -1}>Case {caseRef(action.case_id)}</button>
          <span>{fmtTime(action.created_at)}</span>
        </span>
      </div>
      <h3 className="headline-md">
        {a.to_party ? `To ${a.to_party}${a.channel ? `, ${channelLabel(a.channel)}` : ""}` : action.tool}
      </h3>
      <div className={`approval__draft-wrap ${moreBelow ? "has-more" : ""}`}>
        <div className="approval__draft deck__draft" ref={draftRef} onScroll={checkMore}>
          {a.subject && <p className="approval__subject">{a.subject}</p>}
          <div className="approval__body">{a.body ?? JSON.stringify(action.args, null, 2)}</div>
        </div>
      </div>
      <div className="approval__actions">
        <input className="input input--dark" aria-label="Reason" placeholder="Reason, sent to the agent if rejected"
          value={reason} onChange={(e) => onReason(e.target.value)} tabIndex={isTop ? 0 : -1} />
      </div>
    </article>
  );
}

function MedalUnlock({ medal, onClose }: { medal: MedalRef; onClose: () => void }) {
  const btn = useRef<HTMLButtonElement>(null);
  useEffect(() => { btn.current?.focus({ preventScroll: true }); }, [medal.id]);
  return (
    <div className="unlock" role="dialog" aria-modal="true" aria-labelledby="unlock-title"
      onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <article className="card-feature unlock__card">
        <span className="unlock__icon"><Award size={24} /></span>
        <p className="unlock__kicker">Medal unlocked</p>
        <h2 className="headline-md" id="unlock-title">{medal.title}</h2>
        <p className="card-feature__body">{medal.description}</p>
        <button ref={btn} className="btn btn--inverse card-feature__cta" onClick={onClose}>Nice</button>
      </article>
    </div>
  );
}
