# Alcance de datos SUDEASEG (referencia de mercado)

Los Excel viven en `Info/data-sudeaseg/xlsx/` (carpeta **local**, ignorada en Git). Este documento fija **qué archivos** usar, **ventana temporal** y **cómo** encajan con el demo operativo (pólizas/siniestros simulados).

## Archivos prioritarios (ventana ~3 años + cierre reciente)

| Archivo | Rol |
|---------|-----|
| `cuadros-de-resultados-2023.xlsx` | Cuadro de resultados **cierre 2023** (12 hojas mensuales; usar **Diciembre** como anual). |
| `Dic%20cuadro-de-resultados-2024.xlsx` | Cuadro de resultados **cierre 2024**. |
| `1_Cuadro_de_Resultados_Dic.xlsx` | Cuadro **diciembre 2025** (acumulado al 31/12/2025 en encabezado) — serie más reciente. |
| `resumen-por-empresa-2023.xlsx` | Resumen por empresa **2023**. |
| `Dic%20resumen-por-empresa-2024.xlsx` | Resumen por empresa **2024**. |
| `2_Resumen_por_Empresa_Dic.xlsx` | Resumen por empresa **diciembre 2025** (acumulado). |

Con esto construyes **series 2023 → 2024 → 2025** (o 2023–2024 + punto 2025) para gráficos históricos.

## Estructura detectada (hoja `Diciembre`)

### `1_Cuadro_de_Resultados_*.xlsx` / `cuadro-de-resultados-*.xlsx`

- Hojas por mes; para **anual** conviene **Diciembre** (acumulado).
- Tabla de datos: filas desde ~12; columnas:
  - `#`, **Empresas de Seguros**
  - Resultado técnico bruto, reaseguro cedido, resultado técnico neto, gestión general, saldo de operaciones (miles de Bs. en el periodo del archivo).

### `2_Resumen_por_Empresa_*.xlsx` / `resumen-por-empresa-*.xlsx`

- Misma lógica de hojas mensuales.
- Encabezado de métricas (fila ~8): **Primas Netas Cobradas (1)**, **Siniestros Pagados (2)**, reservas (3)(4), **Siniestros Totales (5)**, comisiones (6), gastos adquisición (7), administración (8), etc.
- Filas por empresa; en datos recientes aparece **Fe C.A., Seguros** (identificador SUDEASEG para Seguros La Fe en estas tablas).

## Modelo de datos propuesto (Postgres, capa `reference` / `market`)

Objetivo: tablas **largas** fáciles de consultar desde API → Streamlit/Reflex.

### `market_sudeaseg_resumen_empresa`

| Columna | Tipo | Notas |
|---------|------|--------|
| `id` | bigserial | |
| `source_file` | text | Traza de procedencia |
| `period_year` | int | 2023, 2024, 2025 |
| `period_month` | int | 1–12; usar 12 para cierre anual |
| `empresa_rank` | int | Columna # |
| `empresa_nombre` | text | |
| `primas_netas_cobradas` | numeric | Miles Bs. |
| `siniestros_pagados` | numeric | |
| `siniestros_totales` | numeric | Según definición (5) del cuadro |
| `comisiones` | numeric | nullable |
| `gastos_adquisicion` | numeric | nullable |
| `gastos_administracion` | numeric | nullable |
| `ingested_at` | timestamptz | default now() |

### `market_sudeaseg_cuadro_resultados`

| Columna | Tipo |
|---------|------|
| `id` | bigserial |
| `source_file` | text |
| `period_year`, `period_month` | int |
| `empresa_rank` | int |
| `empresa_nombre` | text |
| `primas_netas_cobradas` | numeric nullable (solo algunos cuadros 2023 traen primas en columna extra) |
| `resultado_tecnico_bruto` | numeric |
| `resultado_reaseguro_cedido` | numeric |
| `resultado_tecnico_neto` | numeric |
| `resultado_gestion_general` | numeric |
| `saldo_operaciones` | numeric |

Índices: `(period_year, empresa_nombre)`, `(period_year, period_month)`.

## Coherencia con datos simulados (cartera demo)

1. **Extraer** para **Fe C.A., Seguros** (o la fila que corresponda) las series de **primas** y **siniestros totales** 2023–2025.
2. Calcular ratios agregados del mercado o de esa fila: ej. \( \text{siniestralidad proxy} \approx \text{siniestros totales} / \text{primas} \) (ajustar según definición exacta del cuadro).
3. Al **simular** pólizas/siniestros micro, escalar volúmenes y tasas para que **tendencias YoY** (crecimiento, ratio) no contradigan fuerte las series públicas (demo creíble, no contabilidad auditada).

## ETL (implementado)

1. Aplicar en Supabase/Postgres: `supabase/migrations/002_market_sudeaseg.sql` (después de `001_initial.sql`).
2. Dependencias: `pip install -r scripts/requirements-etl.txt` (o usar el mismo venv que `backend-ingest`).
3. Carga (desde la raíz del repo, con Excel en `Info/data-sudeaseg/xlsx/`):

```bash
set DATABASE_URL=postgresql+psycopg://...
python scripts/etl_sudeaseg.py --data-dir Info/data-sudeaseg/xlsx
```

4. Simulacro sin escribir en BD: `python scripts/etl_sudeaseg.py --data-dir ... --dry-run`

El script borra filas previas con el mismo `source_file` y vuelve a insertar (carga idempotente). Archivos incluidos: los seis xlsx de la tabla del inicio de este documento.

### Si en Windows ves `getaddrinfo failed` (11001) con `db.xxx.supabase.co`

El host **directo** (`db.<ref>.supabase.co`, puerto **5432**) a veces **solo resuelve por IPv6**. Si tu red o PC no tiene IPv6 usable, falla el DNS/conexión.

**Solución:** en Supabase → **Connect** → **Session pooler**: copia la **URI tal cual** (host `*.pooler.supabase.com`, usuario `postgres.<ref>`). El **puerto** lo indica el panel (p. ej. **5432** o **6543** según región/tipo); no lo cambies manualmente. Añade `?sslmode=require` si hace falta. Usa esa cadena como `DATABASE_URL` en el ETL y en Render ([`docs/deploy-free-tier.md`](deploy-free-tier.md)).

## Arquitectura: ¿Django, API o Supabase directo?

En este monorepo la **base de datos única** suele ser **Postgres en Supabase** (`DATABASE_URL` compartida por **Django Admin** y la **API FastAPI**).

| Pregunta | Respuesta práctica |
|----------|-------------------|
| ¿La API lee SUDEASEG “directo a Supabase”? | **Sí para consultas.** La FastAPI ya usa SQLAlchemy contra la misma `DATABASE_URL`; no hace falta “pasar por Django” para **leer** tablas `market_*` una vez cargadas. |
| ¿Hace falta Django para cargar SUDEASEG? | **No obligatoriamente.** El ETL puede ser un `scripts/etl_sudeaseg.py` (cron / GitHub Actions / job en Render) que escribe en Postgres. **Django solo aporta valor** si quieres pantalla de operaciones (subida de Excel, logs, permisos staff) en el mismo Admin donde ya cargas pólizas. |
| ¿Qué implica “luego cambios en Django”? | Si el ETL es **externo**, Django no cambia salvo que quieras **vista o comando** `manage.py ingest_sudeaseg` para operar desde el panel. Si todo es script + API, **cero cambios** en Django para SUDEASEG. |

Resumen: **Supabase = almacén**; **FastAPI = lectura para Streamlit/Reflex**; **Django = opcional para ingesta operativa** (pólizas hoy; SUDEASEG mañana si lo decides).

## Fuentes

- Publicaciones y cuadros de la **Superintendencia de la Actividad Aseguradora** (SUDEASEG).
- Producto alineado narrativamente con [Seguros La Fe — salud / asistencia funeraria](https://seguroslafe.com/salud/).
