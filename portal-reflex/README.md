# Portal (Reflex)

SPA en Python que consume la API de cómputo (`GET /api/v1/kpi/summary`).

## Configuración

- **`COMPUTE_API_URL`**: URL pública de `backend-compute` (sin barra final).
- **`DJANGO_ADMIN_BASE_URL`**: URL pública del Django Admin (sin barra final), para el botón “Carga de pólizas”. Si no está definida, el enlace por defecto apunta a `http://127.0.0.1:8080` (solo útil en local).

## Local

```bash
pip install -r requirements.txt
set COMPUTE_API_URL=http://127.0.0.1:8000
set DJANGO_ADMIN_BASE_URL=http://127.0.0.1:8080
reflex run
```

Requiere **Node/Bun** instalado (Reflex compila el frontend). Si falta, instala según [documentación Reflex](https://reflex.dev/docs/getting-started/installation/).

## Nube

- [Reflex Cloud](https://reflex.dev/) o contenedor propio (Render/Fly) con el mismo comando de arranque que indique la versión de Reflex.

## Estructura

Generada con `reflex init --name iihub_portal --template blank`. Lógica principal en `iihub_portal/iihub_portal.py`.
