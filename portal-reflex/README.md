# Portal (Reflex)

SPA en Python que consume la API de cómputo (`GET /api/v1/kpi/summary`).

## Configuración

- **`COMPUTE_API_URL`**: URL pública de `backend-compute` (sin barra final).
- **`DJANGO_ADMIN_BASE_URL`**: URL pública del Django Admin (sin barra final), botón “Carga de pólizas”. Por defecto local: `http://127.0.0.1:8080`.
- **`STREAMLIT_LAB_URL`**: URL pública del app Streamlit (sin barra final), botón “Abrir laboratorio”. Por defecto local: `http://127.0.0.1:8501`.

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

- [Reflex Cloud](https://reflex.dev/) o contenedor propio (Render/Fly) con el mismo comando de arranque que indique la versión de Reflex.

## Estructura

Generada con `reflex init --name iihub_portal --template blank`. Lógica principal en `iihub_portal/iihub_portal.py`.
