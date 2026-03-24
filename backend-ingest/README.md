# Backend — Ingesta y administración (Django)

## Rol

- **Usuarios y sesiones** vía Django Admin (`/admin/`).
- **Listado de pólizas** (modelo no gestionado sobre la tabla `policies` creada en Supabase).
- **Carga de CSV/XLSX** en `/admin/upload-policies/`: el archivo se reenvía a **FastAPI** `POST /api/v1/ingest/policies` para reutilizar la validación **Pydantic** (`hub-contracts`).

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Misma base PostgreSQL que la API (Supabase). |
| `COMPUTE_API_URL` | URL base de `backend-compute` (p. ej. `https://...onrender.com`). |
| `INGEST_API_KEY` | Opcional pero recomendado en público; debe coincidir con la API. |
| `DJANGO_SECRET_KEY` | Secreto de Django. |
| `DEBUG` | `false` en producción. |
| `ALLOWED_HOSTS` | Hosts permitidos (p. ej. `.onrender.com`). |

## Local

```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql://...
set COMPUTE_API_URL=http://127.0.0.1:8000
set INGEST_API_KEY=tu-clave
set DJANGO_SECRET_KEY=dev
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8080
```

**Nota:** el modelo `Policy` es `managed = False`. La tabla debe existir (script SQL en `../supabase/migrations/`). Sin esa tabla, el listado de pólizas en Admin fallará.

## Despliegue

Ver [`../docs/deploy-free-tier.md`](../docs/deploy-free-tier.md) y el servicio `insurance-hub-admin` en [`../render.yaml`](../render.yaml).
