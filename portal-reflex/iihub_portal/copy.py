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

# Pie
FOOTER_LEGAL = "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62"
