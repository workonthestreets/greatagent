/** Preview-only stand-in for src/lib.ts: same exports, static demo fixtures, no network.
 *  Swapped in by preview/vite.config.ts (alias on "./lib"). All names are fictional. */
import type { Session } from "@supabase/supabase-js";
import type {
  Action, AgentEvent, AgentRun, Case, CaseEvent, Profile, Role, Shipment,
} from "../src/lib";

export type { Action, AgentEvent, AgentRun, Case, CaseEvent, Profile, Role, Shipment };
export type {
  DecisionResponse, DecisionRewards, MedalProgress, MedalRef, MerchantDecision, MerchItem, MerchOrder, RedeemResponse, RewardsMe, TeamRow,
} from "../src/lib";

const view = new URLSearchParams(window.location.search).get("view") ?? "ops";
const isParty = view === "party";

const PROFILES: Record<string, Profile> = {
  coordinator: { id: "u-coord", email: "coordinator@greatagent.demo", display_name: "Mara Quist", role: "coordinator", party_name: null },
  admin: { id: "u-admin", email: "admin@greatagent.demo", display_name: "Oskar Lind", role: "admin", party_name: null },
  customer: { id: "u-cust", email: "customer@greatagent.demo", display_name: "Vessa Lorne", role: "customer", party_name: "Vessa Lorne" },
  driver: { id: "u-driver", email: "driver@greatagent.demo", display_name: "Ilan Brooke", role: "driver", party_name: "Ilan Brooke" },
  depot: { id: "u-depot", email: "depot@greatagent.demo", display_name: "Northgate", role: "depot", party_name: "Northgate" },
  merchant: { id: "u-merchant", email: "merchant@greatagent.demo", display_name: "Halden Home", role: "merchant", party_name: "Halden Home" },
};
const VIEW_PROFILE: Record<string, Profile> = {
  party: PROFILES.customer, driver: PROFILES.driver, depot: PROFILES.depot, merchant: PROFILES.merchant, rewards: PROFILES.admin,
};
const profile = VIEW_PROFILE[view] ?? PROFILES.coordinator;

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
  { id: 44, case_id: "D101", tool: "send_message", status: "pending_approval", decided_by: null, created_at: T("09:50"), result: null,
    args: { to_party: "Vessa Lorne", channel: "sms",
      body: "Hi Vessa, this is the Rivet delivery desk. A coordinator will call you today on the number on your order to confirm the new account before any refund is made. We will not ask for your card or login details." },
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
  { id: "DL-101", case_id: "D101", description: "Standing desk frame", status: "delivered", eta: null, depot: "Eastfield", driver_name: "Sora Venn" },
];

/* ---------- Driver, depot and merchant fixtures (what RLS would hand each party) ---------- */
const PARTY_CASES: Record<string, Case[]> = {
  driver: [
    { ...CASES[0], updated_at: T("09:52") },
    { id: "D105", title: "Side gate locked on DL-112", status: "in_progress", source_name: "Pell Okafor", shipment_id: "DL-112",
      coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d105", decision: null, decision_summary: null,
      updated_at: T("09:30") },
  ],
  depot: [
    { id: "D107", title: "Collection tomorrow morning", status: "waiting", source_name: "Ada Fenn", shipment_id: "DL-110",
      coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d107", decision: null, decision_summary: null,
      updated_at: T("09:38") },
    { ...CASES[0], updated_at: T("09:42") },
  ],
  merchant: [
    { id: "D106", title: "Chair arrived with a split leg", status: "waiting", source_name: "Pell Okafor", shipment_id: "DL-118",
      coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d106", decision: null, decision_summary: null,
      updated_at: T("09:40") },
    { id: "D108", title: "Late handover at the warehouse", status: "resolved", source_name: "Halden Home", shipment_id: "DL-114",
      coordinator: "Mara Quist", context: null, initial_request: null, session_id: "sess-d108", decision: null, decision_summary: null,
      updated_at: T("08:15") },
  ],
};

const ev = (id: number, case_id: string, hhmm: string, author: string, author_role: string, kind: string, body: string,
  extra: Partial<CaseEvent> = {}): CaseEvent =>
  ({ id, case_id, ts: T(hhmm), channel: null, author, author_role, to_party: null, kind, visibility: "party", body, ...extra });

const PARTY_EVENTS: Record<string, CaseEvent[]> = {
  driver: [
    ev(201, "D103", "09:48", "Rivet Desk", "agent", "agent_message",
      "Ilan, dispatch may move DL-103 back to the 14:00 to 16:00 window on route 14. Keep it on your list; we will confirm here before 15:40.",
      { channel: "portal", to_party: "Ilan Brooke" }),
    ev(211, "D105", "09:22", "Pell Okafor", "customer", "message", "The side gate is locked after 17:00. Please use the front door.", { channel: "portal" }),
    ev(212, "D105", "09:30", "Rivet Desk", "agent", "agent_message",
      "Ilan, the customer on DL-112 asks you to use the front door; the side gate is locked after 17:00.",
      { channel: "portal", to_party: "Ilan Brooke" }),
  ],
  depot: [
    ev(221, "D107", "09:31", "Ada Fenn", "customer", "message", "I can only collect DL-110 tomorrow before 10:00. Can it wait at the counter?", { channel: "portal" }),
    ev(222, "D107", "09:38", "Rivet Desk", "agent", "agent_message",
      "Northgate team, the customer for DL-110 will collect tomorrow before 10:00. Please keep it at the counter until then and mark it collected when it goes.",
      { channel: "portal", to_party: "Northgate" }),
    ev(231, "D103", "09:42", "Northgate dispatch", "depot", "message",
      "Route 14 was rebuilt at 08:50. We can try to keep DL-103 before 16:00 if we hear back before the 15:40 cutoff.", { channel: "email" }),
  ],
  merchant: [
    ev(241, "D106", "09:12", "Pell Okafor", "customer", "message",
      "One of the two chairs from order HH-2207 arrived with a split back leg. Photos attached.", { channel: "portal" }),
    ev(242, "D106", "09:40", "Rivet Desk", "agent", "agent_message",
      "Halden Home team, one chair on order HH-2207 (shipment DL-118) arrived with a split leg; the customer's photos are on the case. Can you approve a replacement chair or a refund for it? We will tell the customer as soon as you decide.",
      { channel: "portal", to_party: "Halden Home" }),
    ev(251, "D108", "08:02", "Rivet Desk", "agent", "agent_message",
      "The warehouse handover for DL-114 happened at 07:55. Nothing else is needed from you on this one.",
      { channel: "portal", to_party: "Halden Home" }),
  ],
};

const PARTY_SHIPMENTS: Shipment[] = [
  { id: "DL-107", case_id: null, description: "Bedside table", status: "delivered", eta: "Today, 10:00 to 12:00", depot: "Eastfield", driver_name: "Ilan Brooke" },
  { id: "DL-112", case_id: "D105", description: "Bookshelf, flat pack", status: "out_for_delivery", eta: "Today, 16:00 to 18:00", depot: "Eastfield", driver_name: "Ilan Brooke" },
  { id: "DL-109", case_id: null, description: "Garden bench, 1 crate", status: "arrived_at_depot", eta: "Tomorrow, 08:00 to 12:00", depot: "Northgate", driver_name: null },
  { id: "DL-110", case_id: "D107", description: "Table lamp", status: "ready_for_collection", eta: null, depot: "Northgate", driver_name: null },
];

const PARTY_VIEWS = ["driver", "depot", "merchant"];
const isRole = PARTY_VIEWS.includes(view);

const TABLES: Record<string, any[]> = {
  cases: isRole ? PARTY_CASES[view] : isParty ? CASES.filter((c) => c.id !== "D104") : CASES,
  case_events: isRole ? PARTY_EVENTS[view] : isParty ? EVENTS.filter((e) => e.visibility !== "staff") : EVENTS,
  actions: ACTIONS,
  agent_events: AGENT_EVENTS,
  agent_runs: RUNS,
  shipments: isRole ? [...SHIPMENTS, ...PARTY_SHIPMENTS] : SHIPMENTS,
  profiles: [profile],
};

/* ---------- Rewards fixtures ---------- */
const MEDALS = [
  { id: "first_call", title: "First call", description: "Your first approval or rejection on the desk.", icon: "check", metric: "decisions", threshold: 1 },
  { id: "steady_hand", title: "Steady hand", description: "Ten decisions on the desk.", icon: "check", metric: "decisions", threshold: 10 },
  { id: "desk_veteran", title: "Desk veteran", description: "Fifty decisions on the desk.", icon: "user", metric: "decisions", threshold: 50 },
  { id: "gatekeeper", title: "Gatekeeper", description: "Rejected a draft and told the agent why.", icon: "x", metric: "reasoned_rejections", threshold: 1 },
  { id: "clean_desk", title: "Clean desk", description: "Cleared the approvals queue.", icon: "pause", metric: "queue_cleared", threshold: 1 },
  { id: "early_bird", title: "Early bird", description: "Five decisions within 10 minutes of the draft.", icon: "clock", metric: "fast_decisions", threshold: 5 },
];
const PROGRESS: Record<string, [number, string | null]> = {
  first_call: [1, "2026-10-03T10:12:00"], steady_hand: [7, null], desk_veteran: [7, null],
  gatekeeper: [1, "2026-10-07T15:40:00"], clean_desk: [0, null], early_bird: [3, null],
};
const MERCH = [
  { id: "cap", name: "Rivet cap", description: "Six-panel cotton cap with the Rivet mark.", price_coins: 60, stock: 25 },
  { id: "mug", name: "Desk mug", description: "Stoneware mug for the long shift.", price_coins: 40, stock: 0 },
  { id: "socks", name: "Route socks", description: "Merino socks for days on your feet.", price_coins: 35, stock: 24 },
  { id: "tote", name: "Parcel tote", description: "Heavy canvas tote that fits a laptop.", price_coins: 50, stock: 25 },
  { id: "hoodie", name: "Rivet hoodie", description: "Brushed cotton hoodie with the mark on the chest.", price_coins: 160, stock: 10 },
  { id: "bottle", name: "Steel bottle", description: "Insulated steel bottle, 750 ml.", price_coins: 80, stock: 25 },
];
const rewardsState = {
  balance: 135, earned: 170, decisions: 0,
  orders: [{ id: 1, item_id: "socks", item_name: "Route socks", coins: 35, status: "placed", created_at: "2026-10-08T12:05:00" }],
};
const TEAM = [
  { profile_id: "u-coord", display_name: "Mara Quist", role: "coordinator", balance: 210, medals: 3, decisions: 14 },
  { profile_id: "u-admin", display_name: "Oskar Lind", role: "admin", balance: 135, medals: 2, decisions: 7 },
  { profile_id: "u-coord2", display_name: "Juno Park", role: "coordinator", balance: 95, medals: 1, decisions: 5 },
];

/** Answers the hub endpoints the views call, with the fixtures above. Unknown paths resolve to {}. */
function mockHub(path: string, body?: any): any {
  let m = path.match(/^\/api\/actions\/(\d+)\/(approve|reject)$/);
  if (m) {
    const coins = m[2] === "approve" ? 15 : (body?.reason ?? "").trim() ? 10 : 5;
    rewardsState.decisions += 1;
    rewardsState.balance += coins;
    rewardsState.earned += coins;
    const first = MEDALS[0];
    const new_medals = rewardsState.decisions === 1
      ? [{ id: first.id, title: first.title, description: first.description, icon: first.icon }] : [];
    return { ok: true, rewards: { coins, balance: rewardsState.balance, new_medals } };
  }
  if (path === "/api/rewards/me") {
    return {
      balance: rewardsState.balance, earned_total: rewardsState.earned, orders: [...rewardsState.orders].reverse(),
      medals: MEDALS.map((x) => ({ ...x, progress: PROGRESS[x.id][0], earned_at: PROGRESS[x.id][1] })),
    };
  }
  if (path === "/api/rewards/team") return TEAM;
  if (path === "/api/merch") return MERCH.map((x) => ({ ...x }));
  m = path.match(/^\/api\/merch\/([^/]+)\/redeem$/);
  if (m) {
    const item = MERCH.find((x) => x.id === m![1]);
    if (!item || item.stock <= 0) throw new Error("out of stock");
    if (rewardsState.balance < item.price_coins) throw new Error("not enough coins");
    item.stock -= 1;
    rewardsState.balance -= item.price_coins;
    const id = rewardsState.orders.length + 1;
    rewardsState.orders.push({ id, item_id: item.id, item_name: item.name, coins: item.price_coins, status: "placed", created_at: new Date().toISOString() });
    return { order_id: id, balance: rewardsState.balance, item_name: item.name };
  }
  m = path.match(/^\/api\/shipments\/([^/]+)\/status$/);
  if (m) return { ok: true, status: body?.status };
  if (/^\/api\/cases\/[^/]+\/merchant_decision$/.test(path)) return { ok: true };
  if (path === "/api/cases") return { case_id: "D199" };
  return {};
}

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

export async function hub(path: string, body?: unknown): Promise<any> {
  return mockHub(path, body);
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
