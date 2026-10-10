-- Normalized public references (see user/andrey/drafts/naming.md).
--
-- Every entity a person sees, says or types gets one typed reference: a prefix, digits only, and a final check digit
-- (Luhn), so a misheard number on a phone call is rejected instead of matching the wrong record.
--
--   case      C-<n><check>      sequential from 1000      C-10009
--   shipment  DL-<6 random><check>  not sequential (it unlocks status lookups)   DL-4829137
--   party     P-<n><check>      person or team              P-1003
--   org       O-<n><check>      merchant, carrier, desk...  O-1005
--   run       R-<n><check>      one agent run (managed session or pipeline run)
--   action    A-<n><check>      what the agent did or proposed
--
-- Additive and idempotent: existing ids keep working (they become aliases), nothing is dropped. Triggers give every
-- new row its reference whichever code path inserts it, and link parties by name until the code passes party ids.

-- ------------------------------------------------------------------ reference helpers
create or replace function public.luhn_digit(digits text) returns int
language sql immutable as $$
  -- Luhn check digit for a string of digits (the digit to append).
  select (10 - (sum(case when (length(digits) - i) % 2 = 0
                         then (case when d * 2 > 9 then d * 2 - 9 else d * 2 end)
                         else d end) % 10)) % 10
  from (select i, substr(digits, i, 1)::int as d from generate_series(1, length(digits)) as i) s
$$;

create or replace function public.make_ref(prefix text, n bigint) returns text
language sql immutable as $$
  select prefix || '-' || n::text || public.luhn_digit(n::text)::text
$$;

-- True when the text is a well-formed reference whose check digit matches.
create or replace function public.ref_valid(ref text) returns boolean
language sql immutable as $$
  -- CASE, not AND: the digit cast must only run once the shape is known to be right.
  select case
    when coalesce(upper(ref), '') !~ '^[A-Z]{1,3}-[0-9]{2,}$' then false
    else right(ref, 1)::int = public.luhn_digit(left(split_part(ref, '-', 2), -1))
  end
$$;

create sequence if not exists public.case_ref_seq start 1000;
create sequence if not exists public.party_ref_seq start 1000;
create sequence if not exists public.org_ref_seq start 1000;
create sequence if not exists public.run_ref_seq start 1000;
create sequence if not exists public.action_ref_seq start 1000;

create or replace function public.next_ref(kind text) returns text
language plpgsql volatile as $$
begin
  return case kind
    when 'case' then public.make_ref('C', nextval('public.case_ref_seq'))
    when 'party' then public.make_ref('P', nextval('public.party_ref_seq'))
    when 'org' then public.make_ref('O', nextval('public.org_ref_seq'))
    when 'run' then public.make_ref('R', nextval('public.run_ref_seq'))
    when 'action' then public.make_ref('A', nextval('public.action_ref_seq'))
  end;
end $$;

-- Tracking numbers are random so they can't be enumerated; retried until unused.
create or replace function public.new_tracking_ref() returns text
language plpgsql volatile as $$
declare candidate text;
begin
  loop
    candidate := public.make_ref('DL', 100000 + floor(random() * 900000)::bigint);
    exit when not exists (select 1 from public.shipments where tracking_ref = candidate);
  end loop;
  return candidate;
end $$;

-- ------------------------------------------------------------------ new tables
create table if not exists public.orgs (
  id bigint generated always as identity primary key,
  ref text unique not null default public.next_ref('org'),
  name text unique not null,
  kind text not null default 'partner'
    check (kind in ('desk', 'merchant', 'carrier', 'broker', 'business', 'partner')),
  created_at timestamptz not null default now()
);

create table if not exists public.parties (
  id bigint generated always as identity primary key,
  ref text unique not null default public.next_ref('party'),
  display_name text not null,              -- "Vessa Lorne" or "Dispatch"
  role text,                               -- customer / driver / depot / merchant / coordinator
  org_id bigint references public.orgs (id),
  legacy_name text unique not null,        -- the exact string case records used: "Dispatch, Plover Arc Logistics"
  created_at timestamptz not null default now()
);

-- Old and alternative spellings that still resolve: legacy case ids (001, D101, C-C0F654), old shipment ids (DL-001).
create table if not exists public.ref_aliases (
  kind text not null check (kind in ('case', 'shipment', 'party')),
  alias text not null,                     -- stored upper-case
  target_ref text not null,
  primary key (kind, alias)
);

-- ------------------------------------------------------------------ new columns
alter table public.cases add column if not exists ref text unique;
alter table public.cases add column if not exists source text
  check (source in ('public', 'demo', 'portal', 'voice', 'email', 'staff', 'unknown'));
alter table public.cases add column if not exists legacy_ref text;
alter table public.shipments add column if not exists tracking_ref text unique;
alter table public.case_parties add column if not exists party_id bigint references public.parties (id);
alter table public.profiles add column if not exists party_id bigint references public.parties (id);
alter table public.agent_runs add column if not exists ref text unique;
alter table public.agent_runs add column if not exists engine text;
alter table public.actions add column if not exists ref text unique;
create index if not exists case_parties_party_id_idx on public.case_parties (party_id);
create index if not exists profiles_party_id_idx on public.profiles (party_id);

-- ------------------------------------------------------------------ party / org parsing
-- "Name, Org" where Org is a business; "Name, recipient" where the tail is a role word, not an org.
create or replace function public.party_org_name(legacy text) returns text
language sql immutable as $$
  select case
    when position(', ' in legacy) = 0 then null
    -- never mint an org from an email-style sender (e.g. a spoofed "Refunds team <x@y>")
    when legacy ~ '[<>@"]' then null
    when lower(regexp_replace(legacy, '^.*, ', '')) ~
         '^(intended |reporting |original |new |appointed )?(recipient|customer|resident|household|sender|neighbou?r|consignee|caller|customs broker|broker)$' then null
    -- "Rellin Vos, Vellum Rack receiving coordinator": strip the job title to get the business
    else nullif(btrim(regexp_replace(regexp_replace(legacy, '^.*, ', ''),
           '\s+(receiving|shipping|finance|returns|operations|accounts|logistics)?\s*(coordinator|manager|lead|team|desk lead|supervisor)$', '', 'i')), '')
  end
$$;

create or replace function public.party_display_name(legacy text) returns text
language sql immutable as $$
  select btrim(split_part(legacy, ',', 1), ' "''')
$$;

create or replace function public.org_kind(org_name text) returns text
language sql immutable as $$
  select case
    when org_name ~* 'delivery desk' then 'desk'
    when org_name ~* '(logistics|carrier|freight|courier|transport)' then 'carrier'
    when org_name ~* '(customs|broker|trade desk)' then 'broker'
    when org_name ~* '(goods|pantry|store|shop|homewares|studio|press|loom|rack)' then 'merchant'
    else 'partner'
  end
$$;

-- Find or create the party for a legacy name; returns its id.
create or replace function public.ensure_party(legacy text, party_role text default null) returns bigint
language plpgsql volatile security definer set search_path = public as $$
declare pid bigint; oname text; oid bigint;
begin
  if legacy is null or btrim(legacy) = '' then return null; end if;
  select id into pid from public.parties where legacy_name = legacy;
  if pid is not null then return pid; end if;
  oname := public.party_org_name(legacy);
  if oname is not null then
    -- look up first so an existing org doesn't burn a reference number
    select id into oid from public.orgs where name = oname;
    if oid is null then
      insert into public.orgs (name, kind) values (oname, public.org_kind(oname)) on conflict (name) do nothing;
      select id into oid from public.orgs where name = oname;
    end if;
  end if;
  insert into public.parties (display_name, role, org_id, legacy_name)
  values (public.party_display_name(legacy), party_role, oid, legacy)
  on conflict (legacy_name) do nothing;
  select id into pid from public.parties where legacy_name = legacy;
  return pid;
end $$;

-- ------------------------------------------------------------------ triggers: every new row gets its reference
create or replace function public.cases_set_ref() returns trigger
language plpgsql as $$
begin
  if new.ref is null then
    -- New-style ids (C-10009) are their own reference; anything else gets the next one.
    new.ref := case when new.id ~ '^C-[0-9]+$' and public.ref_valid(new.id) then new.id else public.next_ref('case') end;
  end if;
  if new.source is null or new.source = 'unknown' then   -- the column default fills 'unknown' before this runs
    new.source := case
      when new.id ~ '^[0-9]{3}$' then 'public'
      when new.id ~ '^D[0-9]+$' then 'demo'
      else 'unknown' end;
  end if;
  if new.legacy_ref is null and new.id <> new.ref then new.legacy_ref := new.id; end if;
  return new;
end $$;
drop trigger if exists cases_set_ref on public.cases;
create trigger cases_set_ref before insert on public.cases for each row execute function public.cases_set_ref();

create or replace function public.cases_alias_legacy() returns trigger
language plpgsql as $$
begin
  if new.legacy_ref is not null then
    insert into public.ref_aliases (kind, alias, target_ref) values ('case', upper(new.legacy_ref), new.ref)
    on conflict do nothing;
  end if;
  return new;
end $$;
drop trigger if exists cases_alias_legacy on public.cases;
create trigger cases_alias_legacy after insert on public.cases for each row execute function public.cases_alias_legacy();

create or replace function public.shipments_set_ref() returns trigger
language plpgsql as $$
begin
  if new.tracking_ref is null then new.tracking_ref := public.new_tracking_ref(); end if;
  return new;
end $$;
drop trigger if exists shipments_set_ref on public.shipments;
create trigger shipments_set_ref before insert on public.shipments for each row execute function public.shipments_set_ref();

create or replace function public.shipments_alias_legacy() returns trigger
language plpgsql as $$
begin
  insert into public.ref_aliases (kind, alias, target_ref) values ('shipment', upper(new.id), new.tracking_ref)
  on conflict do nothing;
  return new;
end $$;
drop trigger if exists shipments_alias_legacy on public.shipments;
create trigger shipments_alias_legacy after insert on public.shipments for each row execute function public.shipments_alias_legacy();

create or replace function public.case_parties_set_party() returns trigger
language plpgsql as $$
begin
  if new.party_id is null then new.party_id := public.ensure_party(new.party_name, new.role); end if;
  return new;
end $$;
drop trigger if exists case_parties_set_party on public.case_parties;
create trigger case_parties_set_party before insert or update of party_name on public.case_parties
  for each row execute function public.case_parties_set_party();

create or replace function public.profiles_set_party() returns trigger
language plpgsql as $$
begin
  if new.party_name is not null and (tg_op = 'INSERT' or new.party_name is distinct from old.party_name or new.party_id is null) then
    new.party_id := public.ensure_party(new.party_name, new.role);
  end if;
  return new;
end $$;
drop trigger if exists profiles_set_party on public.profiles;
create trigger profiles_set_party before insert or update of party_name on public.profiles
  for each row execute function public.profiles_set_party();

create or replace function public.agent_runs_set_ref() returns trigger
language plpgsql as $$
begin
  if new.ref is null then new.ref := public.next_ref('run'); end if;
  if new.engine is null then new.engine := case when new.session_id like 'pipeline-%' then 'pipeline' else 'managed' end; end if;
  return new;
end $$;
drop trigger if exists agent_runs_set_ref on public.agent_runs;
create trigger agent_runs_set_ref before insert on public.agent_runs for each row execute function public.agent_runs_set_ref();

create or replace function public.actions_set_ref() returns trigger
language plpgsql as $$
begin
  if new.ref is null then new.ref := public.next_ref('action'); end if;
  return new;
end $$;
drop trigger if exists actions_set_ref on public.actions;
create trigger actions_set_ref before insert on public.actions for each row execute function public.actions_set_ref();

-- ------------------------------------------------------------------ backfill existing rows (oldest first)
do $$
declare r record;
begin
  for r in select id from public.cases where ref is null order by created_at, id loop
    update public.cases set
      ref = public.next_ref('case'),
      legacy_ref = coalesce(legacy_ref, id),
      source = coalesce(source, case
        when id ~ '^[0-9]{3}$' then 'public'
        when id ~ '^D[0-9]+$' then 'demo'
        when exists (select 1 from public.case_events e where e.case_id = cases.id and e.kind = 'call') then 'voice'
        else 'portal' end)
    where id = r.id;
  end loop;
  for r in select id from public.shipments where tracking_ref is null order by id loop
    update public.shipments set tracking_ref = public.new_tracking_ref() where id = r.id;
  end loop;
  for r in select session_id from public.agent_runs where ref is null order by created_at loop
    update public.agent_runs set ref = public.next_ref('run'),
      engine = coalesce(engine, case when session_id like 'pipeline-%' then 'pipeline' else 'managed' end)
    where session_id = r.session_id;
  end loop;
  for r in select id from public.actions where ref is null order by id loop
    update public.actions set ref = public.next_ref('action') where id = r.id;
  end loop;
end $$;

update public.case_parties set party_id = public.ensure_party(party_name, role) where party_id is null;
update public.profiles set party_id = public.ensure_party(party_name, role) where party_id is null and party_name is not null;

insert into public.ref_aliases (kind, alias, target_ref)
  select 'case', upper(legacy_ref), ref from public.cases where legacy_ref is not null
  on conflict do nothing;
insert into public.ref_aliases (kind, alias, target_ref)
  select 'shipment', upper(id), tracking_ref from public.shipments where tracking_ref is not null
  on conflict do nothing;

alter table public.cases alter column ref set not null;
alter table public.cases alter column source set default 'unknown';
alter table public.shipments alter column tracking_ref set not null;
alter table public.agent_runs alter column ref set not null;
alter table public.actions alter column ref set not null;

-- ------------------------------------------------------------------ resolving what a person typed or said
-- Accepts a case ref (C-10009), a legacy case id (001, D101, C-C0F654), a shipment tracking ref (DL-4829137) or an
-- old shipment id (DL-001), in any case and with spaces; returns the case id or null. Open cases win ties.
create or replace function public.resolve_case(input text) returns text
language sql stable security definer set search_path = public as $$
  -- Spoken refs arrive without punctuation ("DL 103", "c 10009"): try the text as given and with a hyphen after
  -- the letter prefix. Both forms are needed: legacy ids like D101 have no hyphen.
  with raw as (select upper(regexp_replace(coalesce(input, ''), '[\s.]+', '', 'g')) as v),
  q as (select v from raw union select regexp_replace(v, '^([A-Z]+)-?([0-9]+)$', '\1-\2') from raw)
  select c.id from public.cases c
  where exists (select 1 from q where
        upper(c.ref) = q.v
     or upper(c.id) = q.v
     or c.ref in (select target_ref from public.ref_aliases where kind = 'case' and alias = q.v)
     or c.id in (select s.case_id from public.shipments s
                 where upper(s.tracking_ref) = q.v or upper(s.id) = q.v
                    or s.tracking_ref in (select target_ref from public.ref_aliases where kind = 'shipment' and alias = q.v))
     or upper(c.shipment_id) = q.v)
  order by (c.status in ('resolved', 'closed')), c.updated_at desc
  limit 1
$$;

-- ------------------------------------------------------------------ access
create or replace function public.my_party_id() returns bigint
language sql stable security definer set search_path = public as $$
  select party_id from public.profiles where id = auth.uid()
$$;

-- Same rule as before, now also by party id (names keep working until every row carries one).
create or replace function public.can_see_case(cid text) returns boolean
language sql stable security definer set search_path = public as $$
  select public.is_staff() or exists (
    select 1 from public.case_parties p
    where p.case_id = cid and (p.party_id = public.my_party_id() or p.party_name = public.my_party())
  )
$$;

alter table public.orgs enable row level security;
alter table public.parties enable row level security;
alter table public.ref_aliases enable row level security;
drop policy if exists orgs_read on public.orgs;
create policy orgs_read on public.orgs for select to authenticated using (true);
drop policy if exists parties_read on public.parties;
create policy parties_read on public.parties for select to authenticated
  using (public.is_staff() or id = public.my_party_id());
drop policy if exists ref_aliases_read on public.ref_aliases;
create policy ref_aliases_read on public.ref_aliases for select to authenticated using (public.is_staff());

grant select on public.orgs, public.parties, public.ref_aliases to authenticated;
grant all on public.orgs, public.parties, public.ref_aliases to service_role;
grant usage, select on all sequences in schema public to service_role;
grant execute on function public.my_party_id(), public.ref_valid(text), public.resolve_case(text) to authenticated;

grant select on public.orgs, public.parties, public.ref_aliases to agent_ro;
do $$
declare t text;
begin
  foreach t in array array['orgs', 'parties', 'ref_aliases'] loop
    execute format('drop policy if exists agent_ro_read on public.%I', t);
    execute format('create policy agent_ro_read on public.%I for select to agent_ro using (true)', t);
  end loop;
end $$;
