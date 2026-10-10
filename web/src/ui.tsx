/** Meridian has no status palette: statuses are Inter medium text with a small dot.
 *  Ink = active, muted = waiting or done, brick = escalated / blocked / rejected / failed. */
const ALERT = new Set(["escalated", "blocked", "rejected", "failed", "error", "cancelled"]);
const QUIET = new Set([
  "waiting", "resolved", "done", "closed", "delivered", "executed", "approved", "sent", "idle", "terminated", "complete", "completed",
]);

export function statusTone(status: string): "alert" | "quiet" | "live" {
  const s = status.toLowerCase();
  if (ALERT.has(s)) return "alert";
  if (QUIET.has(s)) return "quiet";
  return "live";
}

export const statusText = (status: string) => {
  const t = status.replace(/_/g, " ");
  return t.charAt(0).toUpperCase() + t.slice(1);
};

export function Status({ status }: { status: string }) {
  return (
    <span className={`status status--${statusTone(status)}`}>
      <span className="status__dot" aria-hidden="true" />
      {statusText(status)}
    </span>
  );
}
