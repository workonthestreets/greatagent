/** Preview-only stand-in for src/lib.ts: same exports, static demo fixtures, no network.
 *  Swapped in by preview/vite.config.ts (alias on "./lib"). All names are fictional. */
import type { Session } from "@supabase/supabase-js";
import type {
  Action, AgentEvent, AgentRun, Case, CaseEvent, Profile, Role, Shipment,
} from "../src/lib";

export type { Action, AgentEvent, AgentRun, Case, CaseEvent, Profile, Role, Shipment };

const view = new URLSearchParams(window.location.search).get("view") ?? "ops";
const isParty = view === "party";

const PROFILES: Record<string, Profile> = {
  coordinator: { id: "u-coord", email: "coordinator@greatagent.demo", display_name: "Mara Quist", role: "coordinator", party_name: null },
  customer: { id: "u-cust", email: "customer@greatagent.demo", display_name: "Vessa Lorne", role: "customer", party_name: "Vessa Lorne" },
};
const profile = isParty ? PROFILES.customer : PROFILES.coordinator;

const T = (hhmm: string) => `2026-10-10T${hhmm}:00`;

const CASES: Case[] = [
  {
    id: "D103", title: "Delivery slot moved?", status: "in_progress", source_name: "Vessa Lorne", shipment_id: "DL-103",
    coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d103",
    decision: {
      decision_type: "act",
      summary: "Ask Northgate dispatch to hold the original 14:00 to 16:00 slot before their 15:40 cutoff, and tell Vessa the new evening slot is not confirmed yet.",
      not_doing: "Not promising the original slot back; not offering compensation.",
      next_trigger: "Dispatch replies, or 15:40 passes without an answer.",
    },
    decision_summary: "Ask dispatch to hold the original slot before the 15:40 cutoff; tell the customer the change is not confirmed yet.",
    updated_at: T("09:46"),
  },
  {
    id: "D101", title: "Refund to new bank details", status: "escalated", source_name: "Vessa Lorne", shipment_id: "DL-101",
    coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d101",
    decision: {
      decision_type: "escalate_to_human",
      summary: "A refund was requested to bank details that differ from the ones on the order. Payment changes need a person to verify the account holder.",
      not_doing: "Not issuing the refund; not confirming the new account.",
      next_trigger: "A coordinator verifies the account holder by phone.",
    },
    decision_summary: "Refund requested to new bank details; handed to a coordinator to verify the account holder.",
    updated_at: T("08:58"),
  },
  {
    id: "D104", title: "Pallet held for inspection", status: "waiting", source_name: "Orrin Freight broker", shipment_id: null,
    coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d104",
    decision: {
      decision_type: "hold_no_action",
      summary: "Broker promised the inspection protocol by 17:00 CEST; nothing new to tell the customer yet",
      not_doing: "Not chasing the broker or the inspector; not giving a delivery hour",
      next_trigger: "Re-check the broker thread at 16:30 CEST or when the protocol arrives",
    },
    decision_summary: "Broker promised the inspection protocol by 17:00 CEST; nothing new to tell the customer yet",
    updated_at: T("08:40"),
  },
];

const EVENTS: CaseEvent[] = [
  { id: 1, case_id: "D103", ts: T("09:12"), channel: "portal", author: "Vessa Lorne", author_role: "customer", to_party: null, kind: "message", visibility: "party",
    body: "My delivery slot for DL-103 moved from the afternoon window to 18:00 to 20:00 on the tracking page. I did not ask for that. Is it real? I am out after 17:00." },
  { id: 2, case_id: "D103", ts: T("09:13"), channel: null, author: "Rivet Desk", author_role: "agent", to_party: null, kind: "system", visibility: "party",
    body: "Case opened from the customer portal." },
  { id: 3, case_id: "D103", ts: T("09:14"), channel: "portal", author: "Rivet Desk", author_role: "agent", to_party: "Vessa Lorne", kind: "agent_message", visibility: "party",
    body: "Thanks, Vessa. We can see the slot change on DL-103 and are checking with dispatch whether it is final. We will not confirm a new time until they reply." },
  { id: 4, case_id: "D103", ts: T("09:20"), channel: "voice", author: "Vessa Lorne", author_role: "customer", to_party: null, kind: "call", visibility: "party",
    body: "Called the voice line to ask if the driver can still come before 16:00. Told her the desk is checking with dispatch and will update the thread." },
  { id: 5, case_id: "D103", ts: T("09:31"), channel: null, author: "Mara Quist", author_role: "coordinator", to_party: null, kind: "note", visibility: "staff",
    body: "Dispatch rebuilt two routes this morning after a road closure. The change is probably real; their cutoff for moving a stop back is 15:40." },
  { id: 6, case_id: "D103", ts: T("09:42"), channel: "email", author: "Northgate dispatch", author_role: "depot", to_party: "Rivet Desk", kind: "message", visibility: "staff",
    body: "Route 14 was rebuilt at 08:50. We can try to keep DL-103 before 16:00 if we hear back before the 15:40 cutoff." },
  { id: 7, case_id: "D103", ts: T("09:45"), channel: null, author: "Rivet Desk", author_role: "agent", to_party: null, kind: "decision", visibility: "staff",
    body: "Acting: ask dispatch to hold the original slot before 15:40; tell the customer the change is not confirmed yet. Two drafts are waiting for approval." },
  { id: 11, case_id: "D101", ts: T("08:51"), channel: "portal", author: "Vessa Lorne", author_role: "customer", to_party: null, kind: "message", visibility: "party",
    body: "The desk frame arrived bent. Please refund it to my new account, details below." },
  { id: 12, case_id: "D101", ts: T("08:53"), channel: "portal", author: "Rivet Desk", author_role: "agent", to_party: "Vessa Lorne", kind: "agent_message", visibility: "party",
    body: "Sorry about the frame. A coordinator will call you to confirm the account before any refund is made." },
  { id: 21, case_id: "D104", ts: T("08:20"), channel: "email", author: "Orrin Freight broker", author_role: "merchant", to_party: "Rivet Desk", kind: "message", visibility: "staff",
    body: "Customs flagged the pallet for inspection. The protocol will follow by 17:00 CEST." },
  { id: 22, case_id: "D104", ts: T("08:40"), channel: null, author: "Rivet Desk", author_role: "agent", to_party: null, kind: "decision", visibility: "staff",
    body: "Holding: nothing new to tell the customer until the protocol arrives." },
];

const ACTIONS: Action[] = [
  { id: 41, case_id: "D103", tool: "send_message", status: "executed", decided_by: "policy (auto)", created_at: T("09:14"), result: null,
    args: { to_party: "Vessa Lorne", channel: "portal", body: "Thanks, Vessa. We can see the slot change on DL-103 and are checking with dispatch whether it is final." },
    policy: [{ level: "WARN", rule: "customer_contact", match: "to_party" }] },
  { id: 42, case_id: "D103", tool: "send_message", status: "pending_approval", decided_by: null, created_at: T("09:45"), result: null,
    args: { to_party: "Northgate dispatch", channel: "email", subject: "DL-103: can you keep the 14:00 to 16:00 slot?",
      body: "Hello Northgate team,\n\nThe customer on DL-103 cannot take the new 18:00 to 20:00 slot. Can you keep the stop in its original 14:00 to 16:00 window on route 14? Please reply before your 15:40 cutoff.\n\nThanks,\nRivet Delivery Desk" },
    policy: [{ level: "WARN", rule: "external_email", match: "channel" }] },
  { id: 43, case_id: "D103", tool: "send_message", status: "pending_approval", decided_by: null, created_at: T("09:46"), result: null,
    args: { to_party: "Vessa Lorne", channel: "portal",
      body: "Hi Vessa, the 18:00 to 20:00 slot you saw is not confirmed yet. We have asked dispatch to keep your original 14:00 to 16:00 window and will tell you here before 16:00 either way." },
    policy: [{ level: "WARN", rule: "customer_contact", match: "to_party" }] },
  { id: 31, case_id: "D101", tool: "issue_refund", status: "blocked", decided_by: "policy", created_at: T("08:55"), result: null,
    args: { amount: "189.00", account: "new" }, policy: [{ level: "BLOCK", rule: "payment_details_change", match: "account" }] },
];

const AGENT_EVENTS: AgentEvent[] = [
  { id: 101, case_id: "D103", session_id: "sess-d103", type: "user.message", created_at: T("09:43"),
    payload: { content: [{ text: "New email from Northgate dispatch on D103." }] } },
  { id: 102, case_id: "D103", session_id: "sess-d103", type: "agent.mcp_tool_use", created_at: T("09:43"),
    payload: { name: "get_shipment", input: { id: "DL-103" } } },
  { id: 103, case_id: "D103", session_id: "sess-d103", type: "agent.mcp_tool_result", created_at: T("09:43"),
    payload: { content: [{ text: "route 14, slot 18:00-20:00, changed 08:50" }] } },
  { id: 104, case_id: "D103", session_id: "sess-d103", type: "agent.message", created_at: T("09:44"),
    payload: { content: [{ text: "Dispatch can still move the stop back before 15:40. Drafting a request to dispatch and an update to the customer." }] } },
  { id: 105, case_id: "D103", session_id: "sess-d103", type: "agent.mcp_tool_use", created_at: T("09:45"),
    payload: { name: "send_message", input: { to_party: "Northgate dispatch", channel: "email" }, evaluated_permission: "ask" } },
  { id: 106, case_id: "D103", session_id: "sess-d103", type: "agent.mcp_tool_use", created_at: T("09:46"),
    payload: { name: "send_message", input: { to_party: "Vessa Lorne", channel: "portal" }, evaluated_permission: "ask" } },
  { id: 107, case_id: "D103", session_id: "sess-d103", type: "session.status_idle", created_at: T("09:46"),
    payload: { stop_reason: { type: "requires_action" } } },
];

const RUNS: AgentRun[] = [
  { session_id: "sess-d103", case_id: "D103", status: "idle", stop_reason: "requires_action", list_cost_cents: 42, trace_url: "#trace-d103" },
];

const SHIPMENTS: Shipment[] = [
  { id: "DL-103", case_id: "D103", description: "Kitchen chairs, 2 boxes", status: "out_for_delivery", eta: "Today, 14:00 to 16:00", depot: "Northgate", driver_name: "Ilan Brooke" },
  { id: "DL-101", case_id: "D101", description: "Standing desk frame", status: "delivered", eta: null, depot: "Northgate", driver_name: "Ilan Brooke" },
];

const TABLES: Record<string, any[]> = {
  cases: isParty ? CASES.filter((c) => c.id !== "D104") : CASES,
  case_events: isParty ? EVENTS.filter((e) => e.visibility !== "staff") : EVENTS,
  actions: ACTIONS,
  agent_events: AGENT_EVENTS,
  agent_runs: RUNS,
  shipments: SHIPMENTS,
  profiles: [profile],
};

/** Tiny chainable query that records eq/order/limit and resolves synchronously. */
class Query {
  private filters: [string, unknown][] = [];
  private sorts: [string, boolean][] = [];
  private max = Infinity;
  constructor(private table: string) {}
  select() { return this; }
  eq(col: string, v: unknown) { this.filters.push([col, v]); return this; }
  order(col: string, opts?: { ascending?: boolean }) { this.sorts.push([col, opts?.ascending ?? true]); return this; }
  limit(n: number) { this.max = n; return this; }
  rows(): any[] {
    let r = (TABLES[this.table] ?? []).filter((row) => this.filters.every(([c, v]) => row[c] === v));
    const [first] = this.sorts;
    if (first) {
      const [col, asc] = first;
      r = [...r].sort((a, b) => (a[col] < b[col] ? -1 : a[col] > b[col] ? 1 : 0) * (asc ? 1 : -1));
    }
    return r.slice(0, this.max);
  }
  single() { return Promise.resolve({ data: this.rows()[0] ?? null, error: null }); }
  then(res: (v: { data: any[]; error: null }) => unknown) { return Promise.resolve({ data: this.rows(), error: null }).then(res); }
}

export const supabase: any = {
  from: (table: string) => new Query(table),
  auth: {
    getSession: async () => ({ data: { session: view === "login" ? null : fakeSession } }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
    signInWithPassword: async () => ({ error: { message: "Preview only: sign-in is disabled." } }),
    signInWithOAuth: async () => ({ error: null }),
    signOut: async () => ({ error: null }),
  },
  channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  removeChannel: () => {},
};

const fakeSession = { user: { id: profile.id, email: profile.email }, access_token: "preview" } as unknown as Session;

export const isStaff = (r?: Role) => r === "admin" || r === "coordinator";

export async function hub(_path: string, _body?: unknown): Promise<any> {
  return {};
}

export function useSession(): Session | null | undefined {
  return view === "login" ? null : fakeSession;
}

export function useLive<T>(table: string, build: (q: any) => any, _deps: unknown[] = []): T[] {
  return (build(new Query(table)) as Query).rows() as T[];
}

export const fmtTime = (ts: string) =>
  new Date(ts).toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

export async function signOut(): Promise<void> {
  window.location.search = "?view=login";
}
