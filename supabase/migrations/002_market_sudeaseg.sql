-- Capa de referencia SUDEASEG (mercado). Alimentada por scripts/etl_sudeaseg.py.
-- Ejecutar después de 001_initial.sql en Supabase / Postgres.

-- Resumen por empresa (primas, siniestros, etc.; miles de Bs. según fuente).
create table if not exists public.market_sudeaseg_resumen_empresa (
  id bigserial primary key,
  source_file text not null,
  period_year integer not null,
  period_month integer not null default 12,
  empresa_rank integer not null,
  empresa_nombre text not null,
  primas_netas_cobradas numeric(22, 8),
  siniestros_pagados numeric(22, 8),
  reservas_psp_brutas numeric(22, 8),
  reservas_psp_netas_reaseg numeric(22, 8),
  siniestros_totales numeric(22, 8),
  comisiones numeric(22, 8),
  gastos_adquisicion numeric(22, 8),
  gastos_administracion numeric(22, 8),
  ingested_at timestamptz not null default now(),
  constraint market_resumen_period_chk check (period_month >= 1 and period_month <= 12),
  constraint market_resumen_rank_chk check (empresa_rank >= 0),
  constraint market_resumen_uniq unique (source_file, period_year, period_month, empresa_rank)
);

create index if not exists idx_market_resumen_year on public.market_sudeaseg_resumen_empresa (period_year);
create index if not exists idx_market_resumen_empresa on public.market_sudeaseg_resumen_empresa (empresa_nombre);
create index if not exists idx_market_resumen_year_empresa on public.market_sudeaseg_resumen_empresa (period_year, empresa_nombre);

comment on table public.market_sudeaseg_resumen_empresa is 'Resumen financiero analítico por empresa (SUDEASEG); miles de Bs.';

-- Cuadro de resultados (resultado técnico, saldo operaciones; miles de Bs.).
create table if not exists public.market_sudeaseg_cuadro_resultados (
  id bigserial primary key,
  source_file text not null,
  period_year integer not null,
  period_month integer not null default 12,
  empresa_rank integer not null,
  empresa_nombre text not null,
  primas_netas_cobradas numeric(22, 8),
  resultado_tecnico_bruto numeric(22, 8),
  resultado_reaseguro_cedido numeric(22, 8),
  resultado_tecnico_neto numeric(22, 8),
  resultado_gestion_general numeric(22, 8),
  saldo_operaciones numeric(22, 8),
  ingested_at timestamptz not null default now(),
  constraint market_cuadro_period_chk check (period_month >= 1 and period_month <= 12),
  constraint market_cuadro_rank_chk check (empresa_rank >= 0),
  constraint market_cuadro_uniq unique (source_file, period_year, period_month, empresa_rank)
);

create index if not exists idx_market_cuadro_year on public.market_sudeaseg_cuadro_resultados (period_year);
create index if not exists idx_market_cuadro_empresa on public.market_sudeaseg_cuadro_resultados (empresa_nombre);

comment on table public.market_sudeaseg_cuadro_resultados is 'Cuadro de resultados por empresa (SUDEASEG); miles de Bs.';
