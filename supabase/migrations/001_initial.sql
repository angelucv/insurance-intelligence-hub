-- Insurance Intelligence Hub — esquema inicial (PostgreSQL / Supabase).
-- Ejecutar en SQL Editor de Supabase o con psql contra DATABASE_URL.

create extension if not exists "pgcrypto";

create table if not exists public.upload_batches (
  id uuid primary key default gen_random_uuid(),
  source text not null default 'api',
  filename text,
  row_count integer not null default 0,
  error_count integer not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.policies (
  id bigserial primary key,
  batch_id uuid references public.upload_batches (id) on delete set null,
  policy_id text not null,
  cohort_year integer not null,
  issue_age integer not null,
  annual_premium numeric(14, 2) not null,
  status text not null,
  created_at timestamptz not null default now(),
  constraint policies_age_chk check (issue_age >= 0 and issue_age <= 110),
  constraint policies_premium_chk check (annual_premium > 0),
  constraint policies_status_chk check (status in ('active', 'lapsed')),
  constraint policies_policy_id_uniq unique (policy_id)
);

create index if not exists idx_policies_cohort on public.policies (cohort_year);
create index if not exists idx_policies_status on public.policies (status);

comment on table public.policies is 'Maestro demo de pólizas; alimentado por Django Admin (ingesta) u opcionalmente POST API.';
comment on table public.upload_batches is 'Trazabilidad de cargas (archivo / origen).';
