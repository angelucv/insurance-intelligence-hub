# Portal (Reflex)

SPA en Python que consume la API de cómputo (FastAPI). Endpoints usados:

- `GET /api/v1/kpi/cohort-bundle` (con `include_portfolio=false` en la primera carga y `cohort-portfolio` después).
- `GET /api/v1/market/portal-bundle` (vista Mercado SUDEASEG: snapshot + series + YoY en una petición).

## Configuración

- **`COMPUTE_API_URL`**: URL pública de `backend-compute` (sin barra final).
- **`DJANGO_ADMIN_BASE_URL`**: URL pública del Django Admin (sin barra final), botón “Carga de pólizas”. Por defecto local: `http://127.0.0.1:8080`.
- **`STREAMLIT_LAB_URL`**: URL pública del app Streamlit (sin barra final), botón **«Análisis BI detallado»** en la barra superior. Por defecto local: `http://127.0.0.1:8501`.

## Local

```bash
pip install -r requirements.txt
set COMPUTE_API_URL=http://127.0.0.1:8000
set DJANGO_ADMIN_BASE_URL=http://127.0.0.1:8080
set STREAMLIT_LAB_URL=http://127.0.0.1:8501
reflex run
```

Requiere **Node/Bun** instalado (Reflex compila el frontend). Si falta, instala según [documentación Reflex](https://reflex.dev/docs/getting-started/installation/).

## Nube

- [Reflex Cloud](https://reflex.dev/) o contenedor propio (Render/Fly) con el comando que indique tu versión de Reflex.

### Variables para desplegar (referencia demo)

Sin barra final:

| Variable | Ejemplo |
|----------|---------|
| `COMPUTE_API_URL` | `https://insurance-hub-api.onrender.com` |
| `DJANGO_ADMIN_BASE_URL` | `https://insurance-hub-admin.onrender.com` |
| `STREAMLIT_LAB_URL` | `https://insurance-suite.streamlit.app` |

Tras el deploy, añade en **Streamlit Secrets** `PORTAL_REFLEX_URL` con la URL que te asigne Reflex Cloud.

## Estructura

- `iihub_portal/iihub_portal.py` — app, tema e página principal.
- `iihub_portal/state.py` — estado (API, KPIs, gráficos).
- `iihub_portal/copy.py` — textos de interfaz.
- `iihub_portal/theme.py` — colores marca.
- `iihub_portal/components/` — layout tipo dashboard (`sidebar`, `layout`, `dashboard_header`, `panels`).

Inspiración de layout: [Broker-CRM-Dashboard](https://github.com/angelucv/Broker-CRM-Dashboard) (sidebar + contenido principal + tarjetas).
