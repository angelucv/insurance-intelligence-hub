# Hoja de ruta

- [x] Contrato `PolicyRow` en paquete `hub-contracts` (`shared/`).
- [x] Esquema Postgres inicial (`supabase/migrations/001_initial.sql`).
- [x] API: ingestión CSV/XLSX, KPIs desde BD + DuckDB, fallback sintético, Loguru/Sentry opcional.
- [x] Django Admin + vista de carga hacia la API.
- [x] Streamlit: dashboard + pestaña de carga.
- [x] Reflex: portal KPI (plantilla `reflex init`).
- [x] Blueprint Render: API + Django (`render.yaml`).
- [ ] Row Level Security y Supabase Auth enlazados a la API.
- [ ] Endpoints actuariales (`/pricing`, reservas / chainladder).
- [ ] Tests automatizados (ingesta, KPI, contratos).

## Integración externa

Documentar URLs públicas de demos en README o propiedad digital del cliente; el código sigue neutro por configuración.
