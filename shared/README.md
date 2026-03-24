# Contratos compartidos

Aquí viven **modelos Pydantic**, **enums** y definiciones de columnas que deben coincidir entre:

- `backend-ingest` (validación al cargar),
- `backend-compute` (entrada/salida de API),
- opcionalmente clientes en `lab-streamlit` y `portal-reflex`.

## Uso

1. Crear un paquete instalable (`pyproject.toml` en `shared/`) **o**
2. Añadir `shared` al `PYTHONPATH` en desarrollo **o**
3. Publicar un paquete interno privado.

Ejemplo de evolución: `shared/contracts/policy_master.py` con modelos de póliza maestra neutros.
