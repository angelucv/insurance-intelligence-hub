# Backend — Ingesta y administración

Responsabilidad: **usuarios**, **autenticación/autorización** y **carga de maestros** (pólizas, productos, tablas de referencia) hacia la base de datos.

## Stack sugerido

- Django + Django Admin (o alternativa equivalente).
- Despliegue: servicio web persistente (p. ej. Render, Fly, Railway).

## Integración

- Validar payloads con esquemas alineados a `../shared/contracts/` (importar como paquete local o publicar paquete interno).
- Escribir en la misma base PostgreSQL que consuma `backend-compute` (o vía API interna, según diseño).

## Inicialización (cuando implementes Django)

```bash
django-admin startproject config .
python manage.py startapp core
```

Añadir aquí `requirements.txt` y `Dockerfile` cuando definas versiones.
