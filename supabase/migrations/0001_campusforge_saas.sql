create extension if not exists "pgcrypto";

create type public.account_role as enum ('user', 'admin');
create type public.account_status as enum ('active', 'suspended', 'deleted');
create type public.workspace_role as enum ('owner', 'admin', 'member');
create type public.ai_task_status as enum ('queued', 'running', 'completed', 'failed', 'cancelled');
create type public.subscription_status as enum ('trialing', 'active', 'past_due', 'cancelled', 'incomplete', 'unpaid');
create type public.credit_transaction_type as enum ('grant', 'purchase', 'reserve', 'consume', 'refund', 'expire', 'adjust');

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text,
  avatar_url text,
  role public.account_role not null default 'user',
  account_status public.account_status not null default 'active',
  locale text not null default 'zh-CN',
  timezone text not null default 'Asia/Shanghai',
  accepted_terms_version text,
  accepted_terms_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.workspaces (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.workspace_members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  role public.workspace_role not null default 'member',
  created_at timestamptz not null default now(),
  primary key (workspace_id, user_id)
);

create table public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  workspace_id uuid references public.workspaces(id) on delete cascade,
  name text not null,
  study_goal text not null default 'balanced',
  exam_type text not null default 'unknown',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table public.uploaded_files (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  project_id uuid references public.projects(id) on delete cascade,
  storage_bucket text not null,
  storage_path text not null,
  original_filename text not null,
  content_type text,
  size_bytes bigint not null default 0,
  file_hash text,
  created_at timestamptz not null default now()
);

create table public.ai_tasks (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  project_id uuid references public.projects(id) on delete cascade,
  status public.ai_task_status not null default 'queued',
  provider text,
  model text,
  idempotency_key text not null,
  input_bytes bigint not null default 0,
  prompt_chars bigint not null default 0,
  output_chars bigint not null default 0,
  error_code text,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_id, idempotency_key)
);

create table public.ai_task_results (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  task_id uuid not null references public.ai_tasks(id) on delete cascade,
  storage_bucket text,
  storage_path text,
  result_json jsonb not null default '{}'::jsonb,
  markdown text,
  created_at timestamptz not null default now()
);

create table public.plans (
  id text primary key,
  name text not null,
  monthly_price_cents integer not null default 0,
  included_credits integer not null default 0,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table public.payment_customers (
  owner_id uuid primary key references public.profiles(id) on delete cascade,
  stripe_customer_id text unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  plan_id text references public.plans(id),
  stripe_subscription_id text unique,
  status public.subscription_status not null,
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.credit_wallets (
  owner_id uuid primary key references public.profiles(id) on delete cascade,
  balance integer not null default 0 check (balance >= 0),
  updated_at timestamptz not null default now()
);

create table public.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  task_id uuid references public.ai_tasks(id) on delete set null,
  payment_event_id text,
  type public.credit_transaction_type not null,
  amount integer not null,
  balance_after integer not null check (balance_after >= 0),
  idempotency_key text not null,
  created_at timestamptz not null default now(),
  unique (owner_id, idempotency_key)
);

create table public.usage_events (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  task_id uuid references public.ai_tasks(id) on delete set null,
  provider text,
  model text,
  credits integer not null default 0,
  input_chars integer not null default 0,
  output_chars integer not null default 0,
  created_at timestamptz not null default now()
);

create table public.payment_events (
  id text primary key,
  provider text not null default 'stripe',
  event_type text not null,
  payload jsonb not null,
  processed_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references public.profiles(id) on delete set null,
  action text not null,
  target_type text,
  target_id text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index on public.projects(owner_id);
create index on public.uploaded_files(owner_id, project_id);
create index on public.ai_tasks(owner_id, project_id, status);
create index on public.ai_task_results(owner_id, task_id);
create index on public.usage_events(owner_id, created_at);
create index on public.credit_transactions(owner_id, created_at);

alter table public.profiles enable row level security;
alter table public.workspaces enable row level security;
alter table public.workspace_members enable row level security;
alter table public.projects enable row level security;
alter table public.uploaded_files enable row level security;
alter table public.ai_tasks enable row level security;
alter table public.ai_task_results enable row level security;
alter table public.payment_customers enable row level security;
alter table public.subscriptions enable row level security;
alter table public.credit_wallets enable row level security;
alter table public.credit_transactions enable row level security;
alter table public.usage_events enable row level security;
alter table public.payment_events enable row level security;
alter table public.audit_logs enable row level security;

create policy "users read own profile" on public.profiles for select using (auth.uid() = id);
create policy "users update own profile" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

create policy "users read own workspaces" on public.workspaces for select using (
  owner_id = auth.uid() or exists (
    select 1 from public.workspace_members wm where wm.workspace_id = id and wm.user_id = auth.uid()
  )
);

create policy "users read own projects" on public.projects for select using (owner_id = auth.uid());
create policy "users insert own projects" on public.projects for insert with check (owner_id = auth.uid());
create policy "users update own projects" on public.projects for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());

create policy "users read own files" on public.uploaded_files for select using (owner_id = auth.uid());
create policy "users insert own files" on public.uploaded_files for insert with check (owner_id = auth.uid());

create policy "users read own tasks" on public.ai_tasks for select using (owner_id = auth.uid());
create policy "users insert own tasks" on public.ai_tasks for insert with check (owner_id = auth.uid());

create policy "users read own task results" on public.ai_task_results for select using (owner_id = auth.uid());
create policy "users read own payment customer" on public.payment_customers for select using (owner_id = auth.uid());
create policy "users read own subscriptions" on public.subscriptions for select using (owner_id = auth.uid());
create policy "users read own wallet" on public.credit_wallets for select using (owner_id = auth.uid());
create policy "users read own credit transactions" on public.credit_transactions for select using (owner_id = auth.uid());
create policy "users read own usage" on public.usage_events for select using (owner_id = auth.uid());

insert into public.plans (id, name, monthly_price_cents, included_credits)
values
  ('free', 'Free', 0, 20),
  ('student_plus', 'Student Plus', 900, 500),
  ('credit_pack_1000', 'Credit Pack 1000', 1200, 1000)
on conflict (id) do update set
  name = excluded.name,
  monthly_price_cents = excluded.monthly_price_cents,
  included_credits = excluded.included_credits;
