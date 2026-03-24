# Backend — API y cómputo

Responsabilidad: **endpoints REST**, validación con **Pydantic**, análisis con **DuckDB** (u otro motor embebido).

## Arranque local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- `GET /health` — comprobación de vida.
- `GET /api/v1/info` — metadatos neutros del servicio.

## Próximo paso

- Añadir rutas bajo `app/routers/` y modelos Pydantic importados desde `shared/contracts`.
