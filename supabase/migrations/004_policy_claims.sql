-- Siniestros demo alineados a pólizas (maestro `policies.policy_id`).
-- Carga vía Django Admin /admin/upload-claims/ (CSV/XLSX).

create table if not exists public.policy_claims (
  id bigserial primary key,
  batch_id uuid references public.upload_batches (id) on delete set null,
  claim_id text not null,
  policy_id text not null references public.policies (policy_id) on delete restrict,
  loss_date date not null,
  reported_amount_bs numeric(14, 2) not null default 0,
  paid_amount_bs numeric(14, 2) not null default 0,
  status text not null,
  created_at timestamptz not null default now(),
  constraint policy_claims_claim_id_uniq unique (claim_id),
  constraint policy_claims_status_chk check (status in ('reported', 'adjusted', 'paid', 'closed', 'rejected')),
  constraint policy_claims_amounts_chk check (reported_amount_bs >= 0 and paid_amount_bs >= 0)
);

create index if not exists idx_policy_claims_policy on public.policy_claims (policy_id);
create index if not exists idx_policy_claims_loss_date on public.policy_claims (loss_date);

comment on table public.policy_claims is 'Siniestros operativos demo; policy_id debe existir en policies.';
