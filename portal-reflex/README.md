# Portal (Reflex)

SPA en Python que consume la API de cómputo (`GET /api/v1/kpi/summary`).

## Configuración

- Variable de entorno **`COMPUTE_API_URL`** (URL pública de `backend-compute`, sin barra final).

## Local

```bash
pip install -r requirements.txt
set COMPUTE_API_URL=http://127.0.0.1:8000
reflex run
```

Requiere **Node/Bun** instalado (Reflex compila el frontend). Si falta, instala según [documentación Reflex](https://reflex.dev/docs/getting-started/installation/).

## Nube

- [Reflex Cloud](https://reflex.dev/) o contenedor propio (Render/Fly) con el mismo comando de arranque que indique la versión de Reflex.

## Estructura

Generada con `reflex init --name iihub_portal --template blank`. Lógica principal en `iihub_portal/iihub_portal.py`.
