# Insurance Intelligence Hub

Arquitectura por capas: **ingesta (Django)**, **PostgreSQL (Supabase)**, **validación (Pydantic en `hub-contracts`)**, **API (FastAPI + DuckDB)**, **portal (Reflex)** y **laboratorio (Streamlit)**. Vista del flujo: [`docs/ecosystem.md`](docs/ecosystem.md).

## Mapa del repositorio

| Capa | Carpeta | Rol |
|------|---------|-----|
| Ingesta y administración | `backend-ingest/` | Django Admin, usuarios, **carga CSV/XLSX en Postgres** (Pydantic en Django). |
| API y cómputo | `backend-compute/` | KPIs (DuckDB + SQL), `POST /ingest/policies` opcional para scripts; Loguru/Sentry opcional. |
| Base de datos (SQL) | `supabase/migrations/` | Script inicial para Postgres/Supabase. |
| Contratos | `shared/` | Paquete instalable `hub-contracts` (`PolicyRow`, etc.). |
| Portal | `portal-reflex/` | KPIs vía `COMPUTE_API_URL`. |
| Laboratorio | `lab-streamlit/` | Dashboard KPI vía API; enlace a la carga en Django Admin. |
| ETL SUDEASEG | `scripts/etl_sudeaseg.py` | Carga tablas `market_sudeaseg_*` desde Excel local (`docs/sudeaseg-data-scope.md`). |

## Requisitos

- Python 3.11+.
- Proyecto **Supabase** (gratis) o cualquier Postgres con el SQL aplicado.
- Cuentas **Render** / **Streamlit Cloud** / **Reflex Cloud** (u homólogos) para demo pública.

## Arranque local rápido

### 1. Base de datos

Ejecuta `supabase/migrations/001_initial.sql` en tu instancia. Copia `DATABASE_URL`.

### 2. API (`backend-compute`)

```bash
cd backend-compute
python -m venv .venv
.venv\Scripts\activate
pip install ..\shared
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg://...   # o postgresql:// (se normaliza)
set INGEST_API_KEY=tu-clave   # opcional en local
uvicorn app.main:app --reload --port 8000
```

- `GET /health`, `GET /api/v1/health/db`
- `GET /api/v1/kpi/summary?cohort_year=2022&use_db=true`
- `GET /api/v1/kpi/cohort-bundle?cohort_year=2022&use_db=true` — KPI + cartera en una respuesta (usa el portal Reflex)
- `POST /api/v1/ingest/policies` (multipart `file`) + `X-API-Key` si configuraste clave

### 3. Django Admin (`backend-ingest`)

```bash
cd backend-ingest
python -m venv .venv
.venv\Scripts\activate
pip install ..\shared
pip install -r requirements.txt
set DATABASE_URL=postgresql://...   # misma BD que la API
set DJANGO_SECRET_KEY=dev
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8080
```

- Admin: `http://127.0.0.1:8080/admin/`
- Carga: `http://127.0.0.1:8080/admin/upload-policies/`
- Opcional (enlaces en el panel): `REFLEX_PORTAL_URL` (por defecto `https://insurance-suite.reflex.run`), `STREAMLIT_LAB_URL`, `COMPUTE_API_PUBLIC_HINT` (texto informativo, sin secretos).

### 4. Streamlit

```bash
cd lab-streamlit
pip install -r requirements.txt
streamlit run app.py
```

### 5. Reflex

```bash
cd portal-reflex
pip install -r requirements.txt
reflex run
```

Define `COMPUTE_API_URL` en el entorno del proceso.

## Datos de ejemplo

CSV de prueba: [`docs/sample-policies.csv`](docs/sample-policies.csv).

## Demo en la nube (gratis)

- **[`docs/deploy-free-tier.md`](docs/deploy-free-tier.md)** — Render (API + Django), Streamlit Cloud, Reflex, variables y orden de despliegue.
- Blueprint: [`render.yaml`](render.yaml) (dos servicios web).
- Laboratorio Streamlit (ejemplo): [insurance-suite.streamlit.app](https://insurance-suite.streamlit.app).

## Tests (CI)

- **`backend-ingest`:** `pytest` (validación CSV + ingesta sobre SQLite de prueba). Ver `backend-ingest/README.md`.
- **GitHub Actions:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) en cada push y pull request.

## Documentación

- [`docs/architecture.md`](docs/architecture.md) — vista neutra por componente.
- [`docs/ecosystem.md`](docs/ecosystem.md) — cómo se conectan Django, API, Supabase, Reflex y Streamlit.
- [`docs/sudeaseg-data-scope.md`](docs/sudeaseg-data-scope.md) — mercado SUDEASEG, migración `002` y comando ETL.
- [`docs/metrics-and-portals.md`](docs/metrics-and-portals.md) — catálogo de indicadores, gráficos y reparto Reflex / Streamlit.

## Relación con marca / cliente

Configuración y narrativa comercial fuera del código; este repo permanece reutilizable y configurable por entorno.
