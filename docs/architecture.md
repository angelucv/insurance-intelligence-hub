# Arquitectura (vista neutra)

Implementación actual del demo y conexión entre servicios: [`ecosystem.md`](ecosystem.md).

Tabla de referencia para alinear **componente**, **herramienta típica** y **dónde suele desplegarse**. Ajusta celdas a tu proveedor real; los nombres aquí son orientativos.

| Capa / componente | Herramienta (referencia) | Despliegue típico | Valor (genérico) |
|--------------------|---------------------------|-------------------|------------------|
| Ingesta y administración | Framework admin + auth | Servicio web (PaaS) | Usuarios, permisos y carga de maestros con trazabilidad. |
| Base de datos | PostgreSQL compatible | Nube gestionada | Persistencia relacional, backups y políticas de acceso. |
| Validación de datos | Pydantic v2 | En backend | Contratos de entrada; rechazo temprano de datos inválidos. |
| Motor analítico | DuckDB | Proceso embebido en API | Consultas analíticas rápidas sobre volúmenes grandes en fichero o memoria. |
| API actuarial / negocio | FastAPI | Contenedor / PaaS | Endpoints de baja latencia para cálculos y orquestación. |
| Observabilidad | Log estructurado + APM | SaaS de errores / trazas | Alertas, trazas y contexto para incidentes. |
| Portal ejecutivo / KPIs | Framework SPA (p. ej. Reflex) | CDN / serverless front | Visualización para dirección y operaciones. |
| Laboratorio | Streamlit u homólogo | Entorno de demos | Experimentos, curvas y sensibilidades sin pasar por producción. |

## Flujo de datos (alto nivel)

1. **Ingesta**: carga validada contra contratos compartidos (`shared/contracts`).
2. **Persistencia**: almacenamiento principal en BD relacional; opcionalmente ficheros parquet/csv para laboratorio.
3. **Cómputo**: DuckDB (u otro motor) dentro de `backend-compute` para agregaciones y escenarios.
4. **Exposición**: FastAPI sirve resultados a `portal-reflex` y a integraciones externas.
5. **Exploración**: `lab-streamlit` consume la misma API o snapshots de datos anonimizados.

## Decisiones a documentar más adelante

- Estrategia de autenticación entre portal y API (JWT, cookies, API keys).
- Esquema de entornos (dev / staging / prod) y secretos.
- Enlaces desde propiedades digitales corporativas (solo documentación y URL; sin dependencia de código en este repo).
