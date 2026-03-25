# Despliegue en tier gratuito (demo completa)

Objetivo: **Supabase (Postgres)** + **API (Render)** + **Django Admin (Render)** + **Streamlit Cloud** + (opcional) **Reflex Cloud**, con el flujo carga → BD → KPIs.

Resumen del encaje entre piezas: [`ecosystem.md`](ecosystem.md).

## 0. Supabase

1. Crea un proyecto en [Supabase](https://supabase.com).
2. **SQL Editor** → pega y ejecuta `supabase/migrations/001_initial.sql`.
3. En **Connect → Connection string** elige **Session pooler** (no “Direct”) para **Render**: la conexión directa suele usar **solo IPv6** y en Render verás `Network is unreachable` / IPv6 en el log. Copia la **URI** del *Session pooler* y úsala como `DATABASE_URL` en **API y Admin**. Si falla SSL, prueba a añadir al final: `?sslmode=require`.

### Si ya usaste “Direct” y falla en Render

Síntoma en logs: `connection to server at "2600:..."` (IPv6) y **Network is unreachable**. Solución: sustituir `DATABASE_URL` en ambos servicios por la cadena del **Session pooler** desde Supabase **Connect**.

## 1. API y Django en Render (Blueprint)

1. [Render](https://render.com) → **New** → **Blueprint** → conecta el repo y el archivo [`render.yaml`](../render.yaml).
2. Al crear el blueprint, Render pedirá valores para variables con `sync: false`:
   - **`DATABASE_URL`**: la misma en **insurance-hub-api** e **insurance-hub-admin** (Django escribe las cargas directamente en Postgres).
   - **`INGEST_API_KEY`** (solo API, opcional): si la defines, el endpoint `POST /api/v1/ingest/policies` sigue disponible para scripts; la **carga operativa** es en Django Admin.
   - **`SENTRY_DSN`** (opcional, solo API).

3. Orden práctico: despliega **API** y **Admin** en paralelo o primero la API si quieres probar KPIs antes del superusuario.

4. **Admin (Django)** tras el primer arranque: en el shell de Render o local con las mismas variables, ejecuta `python manage.py createsuperuser` (o usa la consola de Render → Shell).

**Nota:** el tier gratuito **duerme**; la primera petición puede tardar ~30–60 s.

Comprobaciones API:

- `GET .../health`
- `GET .../api/v1/health/db` → `database_configured: true`
- `GET .../api/v1/kpi/summary?cohort_year=2022`
- Tras subir CSV: mismos KPI con `use_db=true` deben reflejar tus filas.

## 2. Streamlit Community Cloud

1. [Streamlit Community Cloud](https://streamlit.io/cloud) → **New app**.
2. **Main file path**: `lab-streamlit/app.py`
3. **Requirements**: `lab-streamlit/requirements.txt`
4. **Secrets**:

```toml
COMPUTE_API_URL = "https://TU-API.onrender.com"
# DJANGO_ADMIN_BASE_URL = "https://TU-ADMIN.onrender.com"
# Tras desplegar Reflex, añade la URL pública del portal:
# PORTAL_REFLEX_URL = "https://tu-app.reflex.run"
```

5. Deploy. **Sube el CSV** en Django Admin → `/admin/upload-policies/`. Opcional: botón al portal Reflex con `PORTAL_REFLEX_URL`.

Plantilla local: `lab-streamlit/.streamlit/secrets.toml.example`.

## 3. Reflex (portal)

1. Cuenta en [Reflex Cloud](https://reflex.dev/) o despliega `portal-reflex/` (Node/Bun según la guía de tu versión).
2. Variables de entorno:
   - **`COMPUTE_API_URL`**: API pública.
   - **`DJANGO_ADMIN_BASE_URL`**: Admin público (botón carga).
   - **`STREAMLIT_LAB_URL`**: tras tener Streamlit en la nube, URL del lab (botón “Abrir laboratorio”).
3. `pip install -r requirements.txt` y `reflex deploy` (o el flujo que indique Reflex Cloud).

**Orden práctico para enlaces cruzados:** despliega Streamlit y copia su URL → configúrala en Reflex como `STREAMLIT_LAB_URL`. Despliega Reflex y copia su URL → configúrala en Streamlit como `PORTAL_REFLEX_URL`.

## 4. Alternativas gratuitas (opcional)

| Plataforma | Uso típico |
|------------|------------|
| [Railway](https://railway.app) | API / Django con crédito mensual. |
| [Fly.io](https://fly.io) | Contenedores; más setup. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Plan B para demos con Docker. |

## 5. Mensaje para stakeholders

- Excel / Power BI siguen siendo el día a día; el CSV exportable en Streamlit enlaza con ese flujo.
- La **validación** (Pydantic / `hub-contracts`) y la **trazabilidad** de cargas viven en **Django** al subir el archivo; las tablas `upload_batches` / `policies` son la fuente común para la API de KPIs.
