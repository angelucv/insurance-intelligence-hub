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
COMPUTE_API_URL = "https://insurance-hub-api.onrender.com"
DJANGO_ADMIN_BASE_URL = "https://insurance-hub-admin.onrender.com"
# Tras desplegar Reflex, descomenta y pega la URL que te dé Reflex Cloud:
# PORTAL_REFLEX_URL = "https://tu-app.reflex.run"
```

5. Deploy. **Laboratorio público de referencia:** [insurance-suite.streamlit.app](https://insurance-suite.streamlit.app/). **Sube el CSV** en Django Admin → `/admin/upload-policies/`.

Plantilla local: `lab-streamlit/.streamlit/secrets.toml.example`.

## 3. Reflex (portal)

1. Cuenta en [Reflex Cloud](https://reflex.dev/) y conecta el mismo repo; **root / directorio de la app:** `portal-reflex/` (según el asistente de despliegue de tu versión de Reflex).
2. **Variables de entorno** (sin barra final en las URLs):

| Variable | Valor de referencia (ajusta si tus nombres en Render difieren) |
|----------|----------------------------------------------------------------|
| `COMPUTE_API_URL` | `https://insurance-hub-api.onrender.com` |
| `DJANGO_ADMIN_BASE_URL` | `https://insurance-hub-admin.onrender.com` |
| `STREAMLIT_LAB_URL` | `https://insurance-suite.streamlit.app` |

3. Despliega (`reflex deploy` o botón en Reflex Cloud). Copia la **URL pública del portal**.
4. Vuelve a **Streamlit Cloud → Secrets** y añade (o descomenta):

```toml
PORTAL_REFLEX_URL = "https://LA-URL-QUE-TE-DIO-REFLEX"
```

**Resumen de enlaces cruzados:** Reflex usa `STREAMLIT_LAB_URL` → app Streamlit («Análisis BI detallado»). Streamlit usa `PORTAL_REFLEX_URL` → portal ejecutivo.

## 4. Alternativas gratuitas (opcional)

| Plataforma | Uso típico |
|------------|------------|
| [Railway](https://railway.app) | API / Django con crédito mensual. |
| [Fly.io](https://fly.io) | Contenedores; más setup. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Plan B para demos con Docker. |

## 5. Mensaje para stakeholders

- Excel / Power BI siguen siendo el día a día; el CSV exportable en Streamlit enlaza con ese flujo.
- La **validación** (Pydantic / `hub-contracts`) y la **trazabilidad** de cargas viven en **Django** al subir el archivo; las tablas `upload_batches` / `policies` son la fuente común para la API de KPIs.
