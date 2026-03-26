"""Textos de interfaz del portal — tono ejecutivo."""

# Acciones
BTN_CARGA_POLIZAS = "Carga de pólizas"
BTN_CARGA_SINIESTROS = "Carga de siniestros"
LINK_ANALISIS_BI_DETALLADO = "Análisis BI detallado"

# Sidebar
SIDEBAR_BRAND_TITLE = "Portal BI Ejecutivo"
SIDEBAR_BRAND_SHORT = "IIH"
SIDEBAR_BRAND_LONG = "Insurance Intelligence Hub"
SIDEBAR_SECTION_VIEWS = "Vistas"
SIDEBAR_SECTION_OPS = "Operaciones"
SIDEBAR_AUTHOR_LABEL = "Elaborado por"
AUTHOR_NAME = "Prof. Angel Colmenares"
AUTHOR_EMAIL = "angelc.ucv@gmail.com"

# Sugerencias visuales (panel Mercado — bloque colapsable)
VISUAL_SUGGESTIONS_TITLE = "Sugerencias visuales y rendimiento"
VISUAL_SUGGESTIONS_MD = """
**Gráficos que suelen funcionar bien en paneles ejecutivos**

- **Área bajo la línea** (como en primas): refuerza tendencia sin saturar.
- **Doble eje** para series con escala distinta (La Fe vs mercado): evita distorsionar la lectura.
- **Barras apiladas o agrupadas** por ramo o canal: útiles para cuota y composición.
- **Donut o barra horizontal** para participación de mercado en un solo período.
- **Mapa de calor** (mes × métrica) para estacionalidad y picos.
- **Sparklines** junto a KPIs en tablas resumen (tendencia en una línea).
- **Tacómetros (gauge)** con Plotly `go.Indicator`: persistencia, ratios o participación en un vistazo.
- **Donut** (`go.Pie` con `hole`): composición (p. ej. activas vs lapsos).
- **Mapa de calor** (`go.Heatmap`): matriz período × métrica para ver picos y estacionalidad.

**Más ideas (cuando haya más dimensiones en datos)**

- **Treemap / sunburst**: jerarquía ramo → producto → canal.
- **Waterfall**: puente de prima o resultado de un periodo a otro.
- **Sankey**: flujo primas → siniestros → resultado (requiere agregados por etapa).
- **Barras apiladas al 100 %**: mix temporal de estados o ramos.
- **Violin / box** por cohorte o edad actuarial (dispersión de prima).

**Rendimiento**

- Cargar datos en **paralelo** (series y snapshot) y **mostrar estado de carga** mientras llega la API.
- En el futuro: **paginar** series largas, **reducir puntos** (muestreo) o **cachear** respuestas en servidor.
"""

# Cabecera de página (área principal)
HEADER_GREETING = "Panel ejecutivo"
HEADER_SUB_MERCADO = "Referencia SUDEASEG · último cierre y series La Fe vs mercado"
HEADER_SUB_CARTERA = "Indicadores de cartera · lectura rápida y cargas en Admin"

# Bloque introductorio (se puede ocultar con el botón)
PORTAL_INTRO_TITLE = "Acerca de este portal"
PORTAL_INTRO_MD = """
**Qué es.** Vista de lectura de KPI y visualizaciones de cartera y mercado. Los datos provienen del **API de cómputo** (FastAPI) sobre **PostgreSQL**; si no hay filas para un año, el resumen puede ser sintético o demostrativo según indiquen los avisos azules.

**Mi cartera.** Tacómetros, cifras, donut y gráficos avanzados (sunburst, treemap, waterfall, Sankey, etc.). El **año** del filtro corresponde a la **cohorte** consultada por la API. La **carga de pólizas y siniestros** no se hace aquí: use los enlaces del menú lateral hacia **Django Admin**.

**Mercado SUDEASEG.** Series de referencia pública (La Fe frente al mercado total), mapas de calor y comparativas YoY según los selectores. No sustituye los informes regulatorios oficiales.

**Análisis BI detallado.** Abre el **laboratorio Streamlit** para exploración interactiva adicional (misma línea de datos vía API, distinta experiencia).
"""
PORTAL_INTRO_DISMISS = "Ocultar"

# Mercado
MERCADO_PARAMS_TITLE = "Series SUDEASEG"
MERCADO_PARAMS_BODY = (
    "Rango temporal, modo y años A/B para la comparativa YoY. "
    "Un solo «Actualizar» aplica series del rango y la comparativa. "
    "Exportaciones detalladas: «Análisis BI detallado»."
)
MERCADO_YOY_A = "YoY A"
MERCADO_YOY_B = "YoY B"
MERCADO_SNAPSHOT_TITLE = "Último cierre La Fe (YTD)"
MERCADO_SNAPSHOT_HINT = "Miles de Bs. · ratios en fracción"
MERCADO_CHART_PRIM_TITLE = "Primas netas · La Fe vs mercado total"
MERCADO_CHART_PRIM_SUB = "Miles de bolívares · doble eje"
MERCADO_CHART_LR_TITLE = "Loss ratio proxy (siniestros / primas)"
MERCADO_CHART_LR_SUB = "La Fe y mercado total · fracción"
MERCADO_HEATMAP_TITLE = "Intensidad por período (cuatro métricas)"
MERCADO_HEATMAP_SUB = (
    "Cada fila se escala de forma independiente (0 = mínimo del rango, 1 = máximo). "
    "Así se comparan patrones temporales entre primas y loss ratio. Valor real en el hover."
)

# Cartera
CARTERA_PAGE_HEADING = "Resumen de cartera"
CARTERA_LEAD = "KPI por API · BD o sintético según carga."
CARTERA_HERO_TITLE = "Referencia"
CARTERA_PARAMS_TITLE = "Filtro"
CARTERA_PARAMS_BODY = "Año = cartera API · mes = etiqueta visual."
CARTERA_GAUGE_TITLE = "Indicadores clave"
CARTERA_GAUGE_SUB = (
    "Delta vs referencia (85 % persistencia, 80 % share). Umbrales en verde/teal. "
    "Ratio técnico: franja demo; línea roja = zona de alerta."
)
CARTERA_METRICS_TITLE = "Cifras"
CARTERA_DONUT_TITLE = "Composición de la cartera"
CARTERA_DONUT_SUB = "Distribución entre pólizas activas y lapsos"

PORTFOLIO_SECTION_TITLE = "Análisis de cartera (base de datos)"
PORTFOLIO_SECTION_LEAD = (
    "Sunburst, treemap, waterfall, Sankey y demás vistas usan el detalle en PostgreSQL; "
    "si no hay filas para el año, se muestran gráficos demostrativos alineados al KPI."
)
PORTFOLIO_SUNBURST_T = "Sunburst"
PORTFOLIO_SUNBURST_S = "Jerarquía cartera → estado → tramo de edad al emitir"
PORTFOLIO_TREEMAP_T = "Treemap"
PORTFOLIO_TREEMAP_S = "Misma jerarquía en formato treemap (áreas proporcionales)"
PORTFOLIO_WATERFALL_T = "Waterfall · emisión mensual"
PORTFOLIO_WATERFALL_S = "Contribución acumulada de prima anual por mes de emisión"
PORTFOLIO_SANKEY_T = "Sankey · prima vs siniestros"
PORTFOLIO_SANKEY_S = "Flujo desde prima emitida hacia pagado y saldo no reclamado como siniestro"
PORTFOLIO_STACKED_T = "Barras apiladas al 100 %"
PORTFOLIO_STACKED_S = "Mix de estados por tramo de edad (normalizado al 100 % por columna)"
PORTFOLIO_VIOLIN_T = "Violín · prima por edad"
PORTFOLIO_VIOLIN_S = "Distribución de prima anual por tramo (muestra hasta 500 pólizas por tramo)"
PORTFOLIO_BOX_T = "Cajas · prima por estado"
PORTFOLIO_BOX_S = "Box plot de prima según estado de la póliza"

# Años para selector (emisión de cartera y mercado)
CARTERA_YEAR_OPTIONS = [str(y) for y in range(2015, 2032)]
MERCADO_YEAR_OPTIONS = CARTERA_YEAR_OPTIONS
CARTERA_MONTH_OPTIONS = [f"{m:02d}" for m in range(1, 13)]

# Pestañas / títulos cortos (sidebar + mobile) — cartera primero en el menú
TAB_CARTERA = "Mi cartera"
TAB_MERCADO = "Mercado SUDEASEG"
TAB_SUITE = "La suite"

# Vista documentación / demo (mapa del ecosistema)
SUITE_PAGE_HEADING = "Mapa de la suite"
# Infografía contextual (variante Reflex: resaltado portal ejecutivo)
SUITE_MAP_HEADING = "Tu lugar en la suite"
SUITE_MAP_ALT_REFLEX = (
    "Diagrama de la arquitectura IIHub; resaltado: portal ejecutivo de BI (Reflex)."
)
SUITE_MAP_CAPTION_REFLEX = (
    "Estás en el portal ejecutivo de BI: KPI, cartera y mercado en lectura vía API. "
    "La carga manual de pólizas y siniestros (CSV/Excel) se hace en el panel de operaciones."
)
HEADER_SUB_SUITE = (
    "Núcleo: Postgres + carga manual (CSV/Excel) y API de cómputo; Reflex y Streamlit leen vía HTTPS, no SQL desde el navegador."
)
SUITE_ARCHITECTURE_MD = """
### Idea central

**PostgreSQL** es el **núcleo persistente**: tablas de pólizas, lotes de carga y (según migraciones) mercado SUDEASEG. El **API de cómputo** (FastAPI en `backend-compute`) **lee** esa base para KPI, cohortes y series; **escribe** en ella cuando entra una ingesta por API. Las pantallas **no** abren conexión SQL directa: **Reflex** y **Streamlit** llaman al mismo **API HTTP** (`COMPUTE_API_URL`).

### Núcleo ampliado: carga → base → API → UIs

**1. Carga manual de información (operativa típica)**  
En **Django Admin** (`backend-ingest`) los formularios *Carga de pólizas* y *Carga de siniestros* aceptan **CSV** y **Excel** (`.xlsx` / `.xls`). Los datos se validan con **Pydantic** (contratos compartidos) y se insertan en Postgres (p. ej. `policies`, `claims`, lotes en `upload_batches`). Es el camino habitual en demo: subir fichero → ver KPI en Reflex/Streamlit tras refrescar.

**2. Ingesta alternativa por API (automatización / integraciones)**  
El mismo servicio FastAPI expone **`POST /api/v1/ingest/policies`** (multipart con fichero `.csv` / `.xlsx`), protegido con cabecera **`X-API-Key`**. Escribe en las **mismas tablas** que la carga manual; el núcleo sigue siendo la misma base.

**3. API que alimenta la lectura (desde la base hacia las apps)**  
`backend-compute` consulta Postgres (SELECT y agregados; DuckDB donde aplica) y publica endpoints REST: **`/api/v1/kpi/...`**, mercado SUDEASEG, etc. Esa es la **puerta de lectura** que usan el portal y el laboratorio en la arquitectura recomendada.

**4. De la base de datos a Reflex y a Streamlit**  
- **Reflex** (este portal) y **Streamlit** (`lab-streamlit`) son clientes **HTTPS** contra **`COMPUTE_API_URL`**.  
- Enlaces opcionales: `STREAMLIT_LAB_URL` en Reflex, `PORTAL_REFLEX_URL` en Streamlit, `DJANGO_ADMIN_BASE_URL` para ir a la carga.  
- No hace falta “conectar la BD” en el front: basta con la URL pública del API y, para carga, la del Admin.

### Cómo nombrar herramientas (recomendación para demos)

- **En diagramas ejecutivos:** nombra **capas y productos** que despliegas (**PostgreSQL**, **FastAPI**, **Django Admin**, **Reflex**, **Streamlit**). Responde “qué piezas existen” sin saturar.
- **Evita** en la infografía principal una lista larga de librerías (Plotly, pandas, httpx…): mejor en README o documentación técnica.
- **Versiones** de runtime: en guías de despliegue, no en el dibujo de negocio.
- Si la audiencia es **no técnica**, prioriza **roles** (“carga de datos”, “portal ejecutivo”, “laboratorio BI”) y deja marcas en segundo plano o en un pie.

### Flujo de datos (resumen)

1. **Ingesta** — Admin (CSV/XLSX) **o** `POST /api/v1/ingest/policies` → Postgres.
2. **Cómputo** — FastAPI expone KPI, cohortes y mercado SUDEASEG (cuando hay datos y migraciones).
3. **Consumo** — Reflex y Streamlit consumen **el API** por HTTPS; misma línea de datos, distinta UX.

### Dónde “arranca” cada rol

| Rol | Punto de entrada natural |
|-----|---------------------------|
| **Carga de datos** | Django Admin → *Carga de pólizas / siniestros* (CSV/Excel) |
| **Ingesta por integración** | `POST /api/v1/ingest/policies` + API key (misma BD) |
| **Lectura ejecutiva (esta demo)** | **Reflex** → *Mi cartera* / *Mercado* |
| **Análisis exploratorio** | Streamlit (*Análisis BI detallado* en el menú) |

No hay una única URL obligatoria: la suite es **un core de datos** con **varias aplicaciones** alrededor.

### Diagrama lógico (Mermaid)

Si tu visor Markdown renderiza Mermaid (p. ej. GitHub, VS Code), verás el diagrama; si no, copia el bloque a [mermaid.live](https://mermaid.live).

```mermaid
flowchart TB
  subgraph entrada["Hacia PostgreSQL"]
    DJ["Django Admin · CSV / XLSX"]
    ING["POST /api/v1/ingest/policies · X-API-Key"]
  end
  PG[("PostgreSQL · núcleo")]
  DJ -->|INSERT validado| PG
  ING -->|INSERT validado| PG
  API["FastAPI · KPI / mercado / cohortes"]
  PG -->|SELECT| API
  RF["Portal Reflex · HTTPS"]
  ST["Streamlit · HTTPS"]
  API -->|COMPUTE_API_URL| RF
  API -->|COMPUTE_API_URL| ST
```

### Componentes del repositorio (monorepo)

- **`backend-ingest`** — Django: formularios de carga manual, listados de solo lectura.
- **`backend-compute`** — FastAPI: `/api/v1/kpi/...`, mercado SUDEASEG, ingest `/api/v1/ingest/policies`.
- **`portal-reflex`** — Este portal (KPI, Plotly, series).
- **`lab-streamlit`** — Laboratorio exploratorio vía mismo API.
- **`shared`** — Contratos Pydantic compartidos entre ingesta y API.

### Variables de entorno típicas

- **`DATABASE_URL`** — Postgres (compartida por Django y API de cómputo).
- **`COMPUTE_API_URL`** — Base del API; Reflex y Streamlit la usan para leer datos.
- **`INGEST_API_KEY`** (servidor) — Protege el endpoint de ingestión por API.
- Enlaces a **Admin** y **Streamlit** se resuelven en runtime (`DJANGO_ADMIN_BASE_URL`, `STREAMLIT_LAB_URL`, etc.).

*Texto orientado a demo académica; validar siempre cifras operativas en sistemas oficiales.*
"""

# Pie
FOOTER_LEGAL = "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62"
