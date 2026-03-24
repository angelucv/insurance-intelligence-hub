# Portal (Reflex)

Interfaz tipo SPA para KPIs y tableros. Reflex genera su propia estructura de proyecto.

## Crear el esqueleto Reflex (cuando vayas a implementarlo)

Desde esta carpeta:

```bash
cd portal-reflex
pip install reflex
reflex init
```

Luego añade llamadas a `backend-compute` vía `httpx` o similar, usando URL base desde variables de entorno.

## Despliegue típico

- Vercel u otro host compatible con Reflex (según versión y guía oficial).

No se incluye el árbol generado por `reflex init` para mantener el repo ligero hasta que decidas la versión de Reflex.
