# Backend — Ingesta y administración (Django)

## Rol

- **Usuarios y sesiones** vía Django Admin (`/admin/`).
- **Listado de pólizas** (modelo no gestionado sobre la tabla `policies` creada en Supabase).
- **Carga de CSV/XLSX** en `/admin/upload-policies/`: validación con **hub-contracts** (`PolicyRow`, Pydantic) e inserción en PostgreSQL **desde este proceso** (sin reenviar a FastAPI).

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | Misma base PostgreSQL que la API (Supabase). |
| `DJANGO_SECRET_KEY` | Secreto de Django. |
| `DEBUG` | `false` en producción. |
| `ALLOWED_HOSTS` | Hosts permitidos (p. ej. `.onrender.com`). |

## Local

```bash
pip install ../shared
pip install -r requirements.txt
set DATABASE_URL=postgresql://...
set DJANGO_SECRET_KEY=dev
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8080
```

**Nota:** el modelo `Policy` es `managed = False`. La tabla debe existir (script SQL en `../supabase/migrations/`). Sin esa tabla, el listado de pólizas en Admin y la carga fallarán.

## Tests (local y CI)

```bash
pip install ../shared
pip install -r requirements.txt -r requirements-dev.txt
set DJANGO_SECRET_KEY=dev
pytest -q
```

GitHub Actions ejecuta el mismo `pytest` en cada push/PR (workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).

## Despliegue

El build en Render debe instalar contratos: `pip install ../shared` (ver [`../render.yaml`](../render.yaml)). Guía: [`../docs/deploy-free-tier.md`](../docs/deploy-free-tier.md).
