-- Fecha de emisión para análisis temporal (además de cohort_year).
-- Coherente con siniestros: loss_date suele ser >= issue_date.

alter table public.policies
  add column if not exists issue_date date;

update public.policies
set issue_date = make_date(cohort_year, 6, 15)
where issue_date is null;

alter table public.policies
  alter column issue_date set not null;

alter table public.policies
  add constraint policies_issue_year_chk
  check (extract(year from issue_date)::int = cohort_year);

create index if not exists idx_policies_issue_date on public.policies (issue_date);

comment on column public.policies.issue_date is 'Fecha de emisión (demo); mismo año calendario que cohort_year.';
