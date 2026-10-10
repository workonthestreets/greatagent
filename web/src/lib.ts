import { createClient, type Session } from "@supabase/supabase-js";
import { useEffect, useState, useSyncExternalStore } from "react";

export const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);
const HUB = (import.meta.env.VITE_HUB_URL || "http://localhost:8000").replace(/\/$/, "");

export type Role = "admin" | "coordinator" | "customer" | "driver" | "depot" | "merchant";
export type Profile = { id: string; email: string; display_name: string | null; role: Role; party_name: string | null };
export type Case = {
  id: string; title: string; status: string; source_name: string | null; shipment_id: string | null;
  coordinator: string | null; context: string | null; initial_request: string | null; session_id: string | null;
  decision: Record<string, string> | null; decision_summary: string | null; updated_at: string;
  ref?: string | null; source?: string | null; legacy_ref?: string | null;
};
export type CaseEvent = {
  id: number; case_id: string; ts: string; channel: string | null; author: string | null; author_role: string | null;
  to_party: string | null; kind: string; visibility: string; body: string;
};
export type Action = {
  id: number; case_id: string; tool: string; args: Record<string, unknown>; status: string;
  policy: { level: string; rule: string; match: string; negated_context?: boolean }[]; result: unknown;
  decided_by: string | null; created_at: string; mcp_event_id: string | null; session_id: string | null;
};
export type AgentEvent = { id: number; case_id: string; session_id: string; type: string; payload: any; created_at: string };
export type AgentRun = {
  session_id: string; case_id: string; status: string; stop_reason: string | null; list_cost_cents: number | null; trace_url: string;
  created_at: string; updated_at: string;
};
export type Shipment = {
  id: string; case_id: string | null; description: string | null; status: string | null; eta: string | null; depot: string | null;
  driver_name: string | null; tracking_ref?: string | null;
};

/** Rewards (staff only). Shapes follow the hub contract for /api/rewards, /api/merch and decision responses. */
export type MedalRef = { id: string; title: string; description: string; icon: string };
export type DecisionRewards = { coins: number; balance: number; new_medals: MedalRef[] } | null;
export type DecisionResponse = { rewards?: DecisionRewards } & Record<string, unknown>;
export type MedalProgress = MedalRef & { threshold: number; metric: string; progress: number; earned_at: string | null };
export type MerchOrder = { id: number; item_id: string; item_name: string; coins: number; status: string; created_at: string };
export type RewardsMe = { balance: number; earned_total: number; medals: MedalProgress[]; orders: MerchOrder[] };
export type MerchItem = { id: string; name: string; description: string; price_coins: number; stock: number };
export type TeamRow = { profile_id: string; display_name: string; role: Role; balance: number; medals: number; decisions: number };
export type RedeemResponse = { order_id: number; balance: number; item_name: string };
export type MerchantDecision = "approve_replacement" | "approve_refund" | "decline";

export const isStaff = (r?: Role) => r === "admin" || r === "coordinator";

export async function hub(path: string, body?: unknown): Promise<any> {
  const { data } = await supabase.auth.getSession();
  const res = await fetch(`${HUB}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${data.session?.access_token ?? ""}` },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.detail || `request failed (${res.status})`);
  return json;
}

export function useSession(): Session | null | undefined {
  const [session, setSession] = useState<Session | null | undefined>(undefined);
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_e, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);
  return session;
}

/** Rows of a table, kept live with Supabase Realtime. RLS decides what this user gets. */
export function useLive<T>(table: string, build: (q: any) => any, deps: unknown[] = []): T[] {
  const [rows, setRows] = useState<T[]>([]);
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      const { data, error } = await build(supabase.from(table).select("*"));
      if (!cancelled && !error) setRows((data ?? []) as T[]);
    };
    load();
    const channel = supabase
      .channel(`${table}-${Math.random().toString(36).slice(2)}`)
      .on("postgres_changes", { event: "*", schema: "public", table }, () => load())
      .subscribe();
    return () => { cancelled = true; supabase.removeChannel(channel); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return rows;
}

export const fmtTime = (ts: string) =>
  new Date(ts).toLocaleString(undefined, { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });

export const DEMO_PASSWORD: string = import.meta.env.VITE_DEMO_PASSWORD || "greatagent-demo";
export const DEMO_ROLES: Role[] = ["coordinator", "customer", "admin", "driver", "depot", "merchant"];
export const demoEmail = (role: Role) => `${role}@greatagent.demo`;

/** Forget the current session on this device even when the server-side session is already gone (e.g. after a
 *  reseed): the client's own signOut can hang on its refresh lock, so cap it and clear the stored session ourselves. */
async function forgetSession(): Promise<void> {
  try {
    await Promise.race([supabase.auth.signOut({ scope: "local" }), new Promise((r) => setTimeout(r, 1500))]);
  } catch { /* already signed out, or the server rejected the token */ }
  for (const store of [localStorage, sessionStorage]) {
    try { Object.keys(store).filter((k) => k.startsWith("sb-")).forEach((k) => store.removeItem(k)); } catch { /* storage unavailable */ }
  }
}

/** Sign out and land on the login page: a full navigation to "/" also drops any OAuth hash or deep link. */
export async function signOut(): Promise<void> {
  await forgetSession();
  window.location.replace("/");
}

/** Sign out and sign in as another demo account in one step, without a reload. Returns an error message or null. */
export async function switchAccount(role: Role): Promise<string | null> {
  await forgetSession();
  const { error } = await supabase.auth.signInWithPassword({ email: demoEmail(role), password: DEMO_PASSWORD });
  if (error) return error.message;
  if (window.location.pathname !== "/") go("/");
  window.scrollTo({ top: 0 });
  return null;
}

/** Minimal client-side routing: the current path, and go() to change it without a reload. */
export function usePath(): string {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  return path;
}

export function go(path: string): void {
  if (path === window.location.pathname) return;
  window.history.pushState(null, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}

export type AgentLive = { event_id: string; session_id: string; case_id: string; kind: string; text: string; done: boolean; started_at: string };

// ---------------------------------------------------------------- public references (db/migrations/004_refs.sql)
/** What people see and say: a case's reference (C-10009) and a shipment's tracking number (DL-4829137). Before the
 *  migration these columns don't exist and every lookup falls back to the internal id. */
export const caseLabel = (c: Pick<Case, "id" | "ref">) => c.ref || c.id;
export const shipmentLabel = (s: Pick<Shipment, "id" | "tracking_ref">) => s.tracking_ref || s.id;

type Refs = { cases: Map<string, string>; shipments: Map<string, string> };
let refs: Refs = { cases: new Map(), shipments: new Map() };
const refListeners = new Set<() => void>();
let refsStarted = false;

async function loadRefs() {
  const [c, sh] = await Promise.all([
    supabase.from("cases").select("id,ref"),
    supabase.from("shipments").select("id,tracking_ref"),
  ]);
  refs = {
    cases: new Map((c.error ? [] : (c.data as { id: string; ref: string | null }[])).filter((r) => r.ref).map((r) => [r.id, r.ref!])),
    shipments: new Map((sh.error ? [] : (sh.data as { id: string; tracking_ref: string | null }[]))
      .filter((r) => r.tracking_ref).map((r) => [r.id, r.tracking_ref!])),
  };
  refListeners.forEach((f) => f());
}

function startRefs() {
  if (refsStarted) return;
  refsStarted = true;
  loadRefs();
  supabase.auth.onAuthStateChange(() => { loadRefs(); });   // what RLS lets this user see changes with the session
  supabase.channel("refs")
    .on("postgres_changes", { event: "INSERT", schema: "public", table: "cases" }, () => loadRefs())
    .on("postgres_changes", { event: "INSERT", schema: "public", table: "shipments" }, () => loadRefs())
    .subscribe();
}

/** id -> reference lookups for places that only hold an id (an action's case_id, a case's shipment_id). */
export function useRefs() {
  startRefs();
  const current = useSyncExternalStore((f) => { refListeners.add(f); return () => refListeners.delete(f); }, () => refs);
  return {
    caseRef: (id: string) => current.cases.get(id) ?? id,
    shipmentRef: (id: string) => current.shipments.get(id) ?? id,
    /** Internal case id for a reference or id (URLs carry the reference). */
    caseIdFor: (refOrId: string) => {
      for (const [id, ref] of current.cases) if (ref === refOrId) return id;
      return refOrId;
    },
  };
}
