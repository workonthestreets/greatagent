-- Live previews of the agent's text while the model is still generating (Managed Agents event_deltas).
-- The hub's driver writes the running text here every ~0.3s and marks it done when the final agent.message
-- lands in agent_events. Previews are never persisted by the API, so this is the only place they exist.

create table if not exists public.agent_live (
  event_id text primary key,              -- id of the agent.message / agent.thinking being previewed
  session_id text not null,
  case_id text,
  kind text not null,                     -- 'agent.message' or 'agent.thinking'
  text text not null default '',
  done boolean not null default false,
  started_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists agent_live_case_idx on public.agent_live (case_id, started_at);

alter table public.agent_live enable row level security;
drop policy if exists agent_live_read on public.agent_live;
create policy agent_live_read on public.agent_live for select to authenticated using (public.is_staff());
grant select on public.agent_live to authenticated;
grant all on public.agent_live to service_role;

do $$ begin
  if not exists (
    select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'agent_live'
  ) then
    alter publication supabase_realtime add table public.agent_live;
  end if;
end $$;
