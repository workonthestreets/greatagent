export type EventRow = { event_no: string; timestamp: string; channel: string; from: string; to: string; body: string };
export type To = { role: string; name: string | null; team: string | null; org: string | null };
export type Response = {
  decision: "send_message" | "ask_clarification" | "escalate_to_human";
  to: To; channel: string; intent: string; body: string | null; references: string[];
  claims_made: { claim: string; source: string }[]; claims_avoided: string[];
  calculations: { expression: string; result: string }[]; evidence_refs: string[];
  rationale: string; confidence: "high" | "medium" | "low";
  handover: { summary: string; open_questions: string[]; not_done: string[]; risk_flags: string[] } | null;
  flags: { safety: boolean; injection_suspected: boolean; authority_boundary: boolean; out_of_scope_items: string[] };
};
export type Check = { id: string; label: string; status: "pass" | "warn" | "fail" | "na"; detail: string };
export type Flag = { p: number; threshold: number; fired: boolean };
export type Pre = {
  case?: string; status: string; error?: string; needs_human_review: boolean; review_reasons: string[];
  request?: { intent: string; confidence: number; margin: number; low_margin: boolean; alternatives: { intent: string; p: number }[] };
  flags?: Record<string, Flag>;
  routing?: {
    party: string; missing_information: boolean; never_customer: boolean;
    team: { id: string | null; label: string | null; org_role: string | null; p: number | null; candidates: { id: string; label: string }[] | null };
    required_info: { id: string; question: string; p_present: number; present: boolean }[];
    target: { kind: string; label?: string; org_role?: string; note?: string };
  };
  channel?: { kind: string; basis: string; generator_alternate: { channel: string; use_when: string; otherwise: string } | null };
  guardrails?: string[];
  usage?: { calls: number; input_tokens: number; cost_usd: number; provider: string };
};
export type Run = {
  case: string; events: EventRow[]; preprocess: Pre;
  classifier_raw: Record<string, { choice: string; probabilities: Record<string, number> }>;
  response: Response | null; checks: Check[]; error: string | null;
  meta: { model?: string; latency_s?: number; total_s?: number; stop_reason?: string; error?: string;
    usage?: { input_tokens: number; output_tokens: number; cache_read_input_tokens: number } };
};
export type Spec = {
  classifications: { id: string; purpose: string; instructions: string; options?: Record<string, string> }[];
  routing_rules: string[];
  routing_map: { parties: Record<string, string>; intents: Record<string, { teams: { id: string; label: string; pick_when?: string }[] }> };
  channel_rules: { rules: string[] };
};

const TOKEN = import.meta.env.VITE_V2_API_TOKEN as string | undefined;

async function call<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api/v2${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json", ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((json as { detail?: string }).detail || `request failed (${res.status})`);
  return json as T;
}

export type Ticket = { id: string; timestamp: string; stage: string; channel: string; from: string; to: string; body: string };
export type CaseItem = { id: string; title: string; preview: string; events: Ticket[] };
export const listCases = () => call<CaseItem[]>("/cases");
export const runNamedCase = (id: string) => call<Run>(`/cases/${encodeURIComponent(id)}/run`, {});
export const getSpec = () => call<Spec>("/spec");

export const nice = (s: string) => { const t = s.replace(/_/g, " "); return t.charAt(0).toUpperCase() + t.slice(1); };
export const pct = (p: number) => (p >= 0.995 ? "100%" : p < 0.001 ? "<0.1%" : `${(p * 100).toFixed(p < 0.1 ? 1 : 0)}%`);
