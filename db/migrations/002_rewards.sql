-- greatagent rewards: coins and medals for desk staff (admins, coordinators), and a small fictional merch shop.
-- Idempotent: re-running keeps balances, medals, orders and stock; the catalogues are refreshed.
-- Writes go through the hub (hub/rewards.py); the web app only reads, under RLS.

-- ------------------------------------------------------------------ medals
create table if not exists public.medals (
  id text primary key,
  title text not null,
  description text,
  icon text,
  metric text not null
    check (metric in ('decisions', 'reasoned_rejections', 'queue_cleared', 'fast_decisions')),
  threshold int not null default 1,
  sort int not null default 0
);

insert into public.medals (id, title, description, icon, metric, threshold, sort) values
  ('first_call',   'First call',   'Your first approval or rejection on the desk.',     'check', 'decisions',           1,  10),
  ('steady_hand',  'Steady hand',  'Ten approvals or rejections on the desk.',          'check', 'decisions',           10, 20),
  ('desk_veteran', 'Desk veteran', 'Fifty approvals or rejections on the desk.',        'user',  'decisions',           50, 30),
  ('gatekeeper',   'Gatekeeper',   'Rejected a draft and told the agent why.',          'x',     'reasoned_rejections', 1,  40),
  ('clean_desk',   'Clean desk',   'Cleared the approvals queue.',                      'pause', 'queue_cleared',       1,  50),
  ('early_bird',   'Early bird',   'Five decisions within 10 minutes of the draft.',    'clock', 'fast_decisions',      5,  60)
on conflict (id) do update set
  title = excluded.title, description = excluded.description, icon = excluded.icon,
  metric = excluded.metric, threshold = excluded.threshold, sort = excluded.sort;

create table if not exists public.profile_medals (
  profile_id uuid not null references public.profiles (id) on delete cascade,
  medal_id text not null references public.medals (id),
  awarded_at timestamptz not null default now(),
  primary key (profile_id, medal_id)
);

-- ------------------------------------------------------------------ coins
create table if not exists public.coin_ledger (
  id bigserial primary key,
  profile_id uuid not null references public.profiles (id) on delete cascade,
  delta int not null,
  reason text not null,          -- approve | reject | redeem | welcome
  ref text,                      -- action:<id> | order:<id>
  created_at timestamptz not null default now()
);
create index if not exists coin_ledger_profile_idx on public.coin_ledger (profile_id, created_at);

-- security_invoker: the view reads coin_ledger under the caller's RLS, not the owner's.
create or replace view public.coin_balances with (security_invoker = true) as
  select profile_id, coalesce(sum(delta), 0)::int as balance
  from public.coin_ledger
  group by profile_id;

-- ------------------------------------------------------------------ merch
create table if not exists public.merch_items (
  id text primary key,
  name text not null,
  description text,
  price_coins int not null check (price_coins > 0),
  stock int not null default 0 check (stock >= 0),
  sort int not null default 0
);

-- Stock is only set on first insert, so re-running the migration never refills the shelves.
insert into public.merch_items (id, name, description, price_coins, stock, sort) values
  ('cap',    'Rivet cap',    'Charcoal cap with the Rivet mark stitched in ink.',      60,  25, 10),
  ('mug',    'Desk mug',     'Enamel mug for the long shift on the approvals queue.',  40,  25, 20),
  ('socks',  'Route socks',  'A pair of socks printed with a delivery route map.',     35,  25, 30),
  ('tote',   'Parcel tote',  'Heavy canvas tote, sized for a parcel or two.',          50,  25, 40),
  ('hoodie', 'Rivet hoodie', 'Heavyweight hoodie with the Rivet Delivery Desk crest.', 160, 10, 50),
  ('bottle', 'Steel bottle', 'Insulated steel bottle for depot runs.',                 80,  25, 60)
on conflict (id) do update set
  name = excluded.name, description = excluded.description, price_coins = excluded.price_coins, sort = excluded.sort;

create table if not exists public.merch_orders (
  id bigserial primary key,
  profile_id uuid not null references public.profiles (id) on delete cascade,
  item_id text not null references public.merch_items (id),
  coins int not null,
  status text not null default 'placed',
  created_at timestamptz not null default now()
);
create index if not exists merch_orders_profile_idx on public.merch_orders (profile_id, created_at);

-- Medal metrics count decisions per speaker name.
create index if not exists actions_decided_by_idx on public.actions (decided_by);

-- ------------------------------------------------------------------ RLS
alter table public.medals enable row level security;
alter table public.profile_medals enable row level security;
alter table public.coin_ledger enable row level security;
alter table public.merch_items enable row level security;
alter table public.merch_orders enable row level security;

drop policy if exists medals_read on public.medals;
create policy medals_read on public.medals for select to authenticated using (true);

drop policy if exists merch_items_read on public.merch_items;
create policy merch_items_read on public.merch_items for select to authenticated using (true);

drop policy if exists profile_medals_read on public.profile_medals;
create policy profile_medals_read on public.profile_medals for select to authenticated
  using (profile_id = auth.uid() or public.is_staff());

drop policy if exists coin_ledger_read on public.coin_ledger;
create policy coin_ledger_read on public.coin_ledger for select to authenticated
  using (profile_id = auth.uid() or public.is_staff());

drop policy if exists merch_orders_read on public.merch_orders;
create policy merch_orders_read on public.merch_orders for select to authenticated
  using (profile_id = auth.uid() or public.is_staff());

grant select on public.medals, public.profile_medals, public.coin_ledger, public.coin_balances,
  public.merch_items, public.merch_orders to authenticated;
grant all on public.medals, public.profile_medals, public.coin_ledger, public.coin_balances,
  public.merch_items, public.merch_orders to service_role;
grant usage, select on all sequences in schema public to service_role;

-- ------------------------------------------------------------------ realtime
do $$
declare t text;
begin
  foreach t in array array['profile_medals', 'coin_ledger', 'merch_orders', 'merch_items'] loop
    if not exists (
      select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t
    ) then
      execute format('alter publication supabase_realtime add table public.%I', t);
    end if;
  end loop;
end $$;
