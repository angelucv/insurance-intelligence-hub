# Contratos compartidos (`hub-contracts`)

Paquete instalable (`pyproject.toml`) con modelos **Pydantic v2** usados por `backend-compute` (ingesta).

## Instalación

Desde la raíz del repo o desde `backend-compute`:

```bash
pip install ./shared
# o
pip install ../shared
```

Importación:

```python
from contracts.policy import PolicyRow
```

## Contenido

- `contracts/policy.py` — `PolicyRow` para filas CSV/XLSX de pólizas (edad 0–110, prima &gt; 0, estados `active` / `lapsed`).
