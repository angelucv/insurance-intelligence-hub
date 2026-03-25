-- Serie mensual SUDEASEG: YTD en columnas base; incremento mensual en *_mes.
-- Tras aplicar, vuelve a ejecutar scripts/etl_sudeaseg.py (borra por source_file y recarga).

-- La unicidad por empresa no puede depender de empresa_rank (cambia entre hojas).
alter table public.market_sudeaseg_resumen_empresa
  drop constraint if exists market_resumen_uniq;

alter table public.market_sudeaseg_resumen_empresa
  add column if not exists empresa_nombre_norm text;

update public.market_sudeaseg_resumen_empresa
set empresa_nombre_norm = trim(
  regexp_replace(regexp_replace(lower(empresa_nombre), ',|;', ' ', 'g'), '\s+', ' ', 'g')
)
where empresa_nombre_norm is null;

alter table public.market_sudeaseg_resumen_empresa
  add column if not exists primas_netas_cobradas_mes numeric(22, 8),
  add column if not exists siniestros_pagados_mes numeric(22, 8),
  add column if not exists reservas_psp_brutas_mes numeric(22, 8),
  add column if not exists reservas_psp_netas_reaseg_mes numeric(22, 8),
  add column if not exists siniestros_totales_mes numeric(22, 8),
  add column if not exists comisiones_mes numeric(22, 8),
  add column if not exists gastos_adquisicion_mes numeric(22, 8),
  add column if not exists gastos_administracion_mes numeric(22, 8);

alter table public.market_sudeaseg_resumen_empresa
  alter column empresa_nombre_norm set not null;

alter table public.market_sudeaseg_resumen_empresa
  add constraint market_resumen_uniq unique (source_file, period_year, period_month, empresa_nombre_norm);

comment on column public.market_sudeaseg_resumen_empresa.primas_netas_cobradas is 'Acumulado YTD hasta period_month (miles Bs., según SUDEASEG).';
comment on column public.market_sudeaseg_resumen_empresa.primas_netas_cobradas_mes is 'Incremento mensual: YTD(m) - YTD(m_prev), m_prev último mes previo con dato en el año.';

-- Cuadro de resultados
alter table public.market_sudeaseg_cuadro_resultados
  drop constraint if exists market_cuadro_uniq;

alter table public.market_sudeaseg_cuadro_resultados
  add column if not exists empresa_nombre_norm text;

update public.market_sudeaseg_cuadro_resultados
set empresa_nombre_norm = trim(
  regexp_replace(regexp_replace(lower(empresa_nombre), ',|;', ' ', 'g'), '\s+', ' ', 'g')
)
where empresa_nombre_norm is null;

alter table public.market_sudeaseg_cuadro_resultados
  add column if not exists primas_netas_cobradas_mes numeric(22, 8),
  add column if not exists resultado_tecnico_bruto_mes numeric(22, 8),
  add column if not exists resultado_reaseguro_cedido_mes numeric(22, 8),
  add column if not exists resultado_tecnico_neto_mes numeric(22, 8),
  add column if not exists resultado_gestion_general_mes numeric(22, 8),
  add column if not exists saldo_operaciones_mes numeric(22, 8);

alter table public.market_sudeaseg_cuadro_resultados
  alter column empresa_nombre_norm set not null;

alter table public.market_sudeaseg_cuadro_resultados
  add constraint market_cuadro_uniq unique (source_file, period_year, period_month, empresa_nombre_norm);

comment on column public.market_sudeaseg_cuadro_resultados.resultado_tecnico_bruto is 'Acumulado YTD hasta period_month (miles Bs.).';
comment on column public.market_sudeaseg_cuadro_resultados.resultado_tecnico_bruto_mes is 'Incremento mensual vs último mes previo con dato en el año.';

create index if not exists idx_market_resumen_ym on public.market_sudeaseg_resumen_empresa (period_year, period_month);
create index if not exists idx_market_cuadro_ym on public.market_sudeaseg_cuadro_resultados (period_year, period_month);
