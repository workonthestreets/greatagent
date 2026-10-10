import { createClient, type Session } from "@supabase/supabase-js";
import { useEffect, useState } from "react";

export const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY);
const HUB = (import.meta.env.VITE_HUB_URL || "http://localhost:8000").replace(/\/$/, "");

export type Role = "admin" | "coordinator" | "customer" | "driver" | "depot" | "merchant";
export type Profile = { id: string; email: string; display_name: string | null; role: Role; party_name: string | null };
export type Case = {
  id: string; title: string; status: string; source_name: string | null; shipment_id: string | null;
  coordinator: string | null; context: string | null; initial_request: string | null; session_id: string | null;
  decision: Record<string, string> | null; decision_summary: string | null; updated_at: string;
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
export type AgentRun = { session_id: string; case_id: string; status: string; stop_reason: string | null; list_cost_cents: number | null; trace_url: string };
export type Shipment = { id: string; case_id: string | null; description: string | null; status: string | null; eta: string | null; depot: string | null; driver_name: string | null };

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

/** Sign out even when the server-side session is already gone (e.g. after a reseed): the client's own
 *  signOut can hang on its refresh lock, so clear the stored session ourselves and reload. */
export async function signOut(): Promise<void> {
  try {
    await Promise.race([supabase.auth.signOut({ scope: "local" }), new Promise((r) => setTimeout(r, 1500))]);
  } finally {
    Object.keys(localStorage).filter((k) => k.startsWith("sb-")).forEach((k) => localStorage.removeItem(k));
    window.location.reload();
  }
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
