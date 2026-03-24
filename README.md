# Insurance Intelligence Hub

Demo de referencia **neutra**: arquitectura por capas para ingestión, validación, cómputo actuarial, APIs y portales. Los despliegues y nombres comerciales se configuran por entorno (véase `.env.example`).

## Mapa del repositorio

| Capa | Carpeta | Rol |
|------|---------|-----|
| Ingesta y administración | `backend-ingest/` | Admin, usuarios, carga de maestros (p. ej. Django). |
| API y cómputo | `backend-compute/` | Validación (Pydantic), análisis rápido (DuckDB), endpoints (FastAPI). |
| Laboratorio exploratorio | `lab-streamlit/` | Prototipos e interactivos para equipos técnicos. |
| Portal analítico | `portal-reflex/` | UI tipo SPA para KPIs y tableros (Reflex). |
| Contratos compartidos | `shared/` | Esquemas y tipos reutilizables entre servicios. |

Detalle de despliegue sugerido y decisiones de diseño: [`docs/architecture.md`](docs/architecture.md).

## Requisitos previos

- Python 3.11+ (por servicio; ver `requirements.txt` en cada carpeta).
- Cuentas y proyectos según destino (p. ej. base de datos gestionada, hosting de API y front).

## Arranque rápido (API de ejemplo)

```bash
cd backend-compute
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Abrir `http://127.0.0.1:8000/health` y `http://127.0.0.1:8000/api/v1/kpi/summary`.

**Laboratorio Streamlit** (requiere API en marcha):

```bash
cd lab-streamlit
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Opcional: en `lab-streamlit/.streamlit/secrets.toml` define `COMPUTE_API_URL` si la API no está en localhost.

## Demo en vivo (gratis)

Guía paso a paso: **[`docs/deploy-free-tier.md`](docs/deploy-free-tier.md)** — API en **Render** + tablero en **Streamlit Community Cloud**.

## Próximos pasos

1. Definir variables en `.env` (copiar desde `.env.example`).
2. Implementar modelos en `shared/contracts/` y consumirlos desde ingest y compute.
3. Conectar base de datos y observabilidad según `docs/architecture.md`.

## Relación futura con otros productos

Este repo puede enlazarse desde sitios o suites corporativas (p. ej. documentación o demos públicas) sin acoplar el código a una marca concreta: usar configuración y documentación externa para el relato comercial.
