-- greatagent schema: cases, shipments, timeline, agent actions/events, accounts with role-based access.
-- Works on Supabase as-is. Locally, run db/local_bootstrap.sql first (db/migrate.py does this).
-- All writes go through the hub (service connection); the web app only reads, under RLS.

create extension if not exists pgcrypto;

-- ------------------------------------------------------------------ accounts
create table if not exists public.admin_emails (
  email text primary key
);

create table if not exists public.profiles (
  id uuid primary key,
  email text unique,
  display_name text,
  role text not null default 'customer'
    check (role in ('admin', 'coordinator', 'customer', 'driver', 'depot', 'merchant')),
  party_name text,          -- links the account to the name used in case records
  phone text,               -- maps voice callers to the account
  created_at timestamptz not null default now()
);
create index if not exists profiles_party_idx on public.profiles (party_name);
create index if not exists profiles_phone_idx on public.profiles (phone);

-- New sign-ups (Google or email) get a profile; listed admin emails become admins.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, display_name, role)
  values (
    new.id, new.email,
    coalesce(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    case when exists (select 1 from public.admin_emails a where lower(a.email) = lower(new.email))
         then 'admin' else 'customer' end
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ------------------------------------------------------------------ domain
create table if not exists public.cases (
  id text primary key,
  title text not null,
  track text not null default 'Delivery & Logistics',
  status text not null default 'open'
    check (status in ('open', 'in_progress', 'waiting', 'escalated', 'resolved', 'closed')),
  source_name text,
  source_role text,
  coordinator text,
  shipment_id text,
  context text,
  initial_request text,
  session_id text,          -- the Managed Agents session that owns this case
  decision jsonb,           -- latest submit_decision payload
  decision_summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.case_parties (
  case_id text not null references public.cases (id) on delete cascade,
  party_name text not null,
  role text,
  primary key (case_id, party_name)
);
create index if not exists case_parties_party_idx on public.case_parties (party_name);

create table if not exists public.shipments (
  id text primary key,
  case_id text references public.cases (id) on delete set null,
  description text,
  status text,
  recipient_name text,
  merchant text,
  depot text,
  driver_name text,
  eta text,
  updated_at timestamptz not null default now()
);

create table if not exists public.case_events (
  id bigserial primary key,
  case_id text not null references public.cases (id) on delete cascade,
  ts timestamptz not null default now(),
  channel text,
  author text,
  author_role text,
  to_party text,
  kind text not null default 'message'
    check (kind in ('message', 'call', 'note', 'system', 'agent_message', 'decision')),
  visibility text not null default 'all' check (visibility in ('all', 'staff')),
  body text not null,
  meta jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists case_events_case_idx on public.case_events (case_id, ts);

-- ------------------------------------------------------------------ agent
create table if not exists public.actions (
  id bigserial primary key,
  case_id text references public.cases (id) on delete cascade,
  session_id text,
  tool text not null,
  args jsonb not null default '{}'::jsonb,
  status text not null
    check (status in ('pending_approval', 'approved', 'rejected', 'done', 'blocked', 'failed')),
  policy jsonb not null default '[]'::jsonb,   -- findings from deskagent.policy
  result jsonb,
  mcp_event_id text unique,                    -- the sevt_ id to confirm/deny
  decided_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists actions_case_idx on public.actions (case_id, created_at);

create table if not exists public.agent_events (
  id bigserial primary key,
  event_id text unique not null,
  session_id text not null,
  case_id text,
  type text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);
create index if not exists agent_events_case_idx on public.agent_events (case_id, id);

create table if not exists public.agent_runs (
  session_id text primary key,
  case_id text references public.cases (id) on delete cascade,
  status text,
  stop_reason text,
  list_cost_cents integer,
  trace_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ------------------------------------------------------------------ access helpers
create or replace function public.my_role() returns text
language sql stable security definer set search_path = public as $$
  select role from public.profiles where id = auth.uid()
$$;

create or replace function public.my_party() returns text
language sql stable security definer set search_path = public as $$
  select party_name from public.profiles where id = auth.uid()
$$;

create or replace function public.is_staff() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(public.my_role() in ('admin', 'coordinator'), false)
$$;

create or replace function public.can_see_case(cid text) returns boolean
language sql stable security definer set search_path = public as $$
  select public.is_staff() or exists (
    select 1 from public.case_parties p where p.case_id = cid and p.party_name = public.my_party()
  )
$$;

-- ------------------------------------------------------------------ RLS
alter table public.profiles enable row level security;
alter table public.admin_emails enable row level security;
alter table public.cases enable row level security;
alter table public.case_parties enable row level security;
alter table public.shipments enable row level security;
alter table public.case_events enable row level security;
alter table public.actions enable row level security;
alter table public.agent_events enable row level security;
alter table public.agent_runs enable row level security;

drop policy if exists profiles_read on public.profiles;
create policy profiles_read on public.profiles for select to authenticated
  using (id = auth.uid() or public.is_staff());

drop policy if exists cases_read on public.cases;
create policy cases_read on public.cases for select to authenticated
  using (public.can_see_case(id));

drop policy if exists case_parties_read on public.case_parties;
create policy case_parties_read on public.case_parties for select to authenticated
  using (public.can_see_case(case_id));

drop policy if exists shipments_read on public.shipments;
create policy shipments_read on public.shipments for select to authenticated
  using (public.can_see_case(case_id) or driver_name = public.my_party() or depot = public.my_party());

-- Parties see the shared timeline of their cases, never staff-only notes.
drop policy if exists case_events_read on public.case_events;
create policy case_events_read on public.case_events for select to authenticated
  using (public.can_see_case(case_id) and (public.is_staff() or visibility = 'all'));

drop policy if exists actions_read on public.actions;
create policy actions_read on public.actions for select to authenticated using (public.is_staff());

drop policy if exists agent_events_read on public.agent_events;
create policy agent_events_read on public.agent_events for select to authenticated using (public.is_staff());

drop policy if exists agent_runs_read on public.agent_runs;
create policy agent_runs_read on public.agent_runs for select to authenticated using (public.is_staff());

grant usage on schema public to anon, authenticated, service_role;
grant select on all tables in schema public to authenticated;
grant all on all tables in schema public to service_role;
grant usage, select on all sequences in schema public to service_role;
grant execute on function public.my_role(), public.my_party(), public.is_staff(), public.can_see_case(text) to authenticated;

-- ------------------------------------------------------------------ agent read-only role
-- The hub runs the agent's read_sql inside a read-only transaction under this role.
-- No access to profiles (emails/phones) or the auth schema.
do $$ begin
  if not exists (select from pg_roles where rolname = 'agent_ro') then create role agent_ro nologin; end if;
end $$;
do $$ begin
  execute format('grant agent_ro to %I', current_user);
exception when others then null;  -- already a member
end $$;
grant usage on schema public to agent_ro;
grant select on public.cases, public.case_parties, public.shipments, public.case_events, public.actions to agent_ro;
do $$
declare t text;
begin
  foreach t in array array['cases', 'case_parties', 'shipments', 'case_events', 'actions'] loop
    execute format('drop policy if exists agent_ro_read on public.%I', t);
    execute format('create policy agent_ro_read on public.%I for select to agent_ro using (true)', t);
  end loop;
end $$;
alter role agent_ro set statement_timeout = '5s';

-- ------------------------------------------------------------------ realtime
do $$
declare t text;
begin
  foreach t in array array['cases', 'case_events', 'shipments', 'actions', 'agent_events', 'agent_runs'] loop
    if not exists (
      select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t
    ) then
      execute format('alter publication supabase_realtime add table public.%I', t);
    end if;
  end loop;
end $$;
