"""Textos de interfaz del portal — tono ejecutivo."""

# Acciones
BTN_CARGA_POLIZAS = "Carga de pólizas"
BTN_CARGA_SINIESTROS = "Carga de siniestros"
LINK_ANALISIS_BI_DETALLADO = "Análisis BI detallado"

# Sidebar
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

**Rendimiento**

- Cargar datos en **paralelo** (series y snapshot) y **mostrar estado de carga** mientras llega la API.
- En el futuro: **paginar** series largas, **reducir puntos** (muestreo) o **cachear** respuestas en servidor.
"""

# Cabecera de página (área principal)
HEADER_GREETING = "Panel ejecutivo"
HEADER_SUB_MERCADO = "Referencia SUDEASEG · último cierre y series La Fe vs mercado"
HEADER_SUB_COHORTE = "KPIs de cohorte operativa · alineado con cargas en Admin"

# Mercado
MERCADO_PARAMS_TITLE = "Parámetros de las series"
MERCADO_PARAMS_BODY = (
    "Ajuste rango y modo temporal. Para exportaciones y cortes adicionales use «Análisis BI detallado» en Operaciones."
)
MERCADO_SNAPSHOT_TITLE = "Último cierre La Fe (YTD)"
MERCADO_SNAPSHOT_HINT = "Miles de Bs. · ratios en fracción"
MERCADO_CHART_PRIM_TITLE = "Primas netas · La Fe vs mercado total"
MERCADO_CHART_PRIM_SUB = "Miles de bolívares · doble eje"
MERCADO_CHART_LR_TITLE = "Loss ratio proxy (siniestros / primas)"
MERCADO_CHART_LR_SUB = "La Fe y mercado total · fracción"

# Cartera
COHORT_PAGE_HEADING = "Resumen de cohorte"
COHORT_LEAD = (
    "Indicadores vía API de cómputo. Datos reales en BD o respaldo sintético según carga."
)

# Pestañas / títulos cortos (sidebar + mobile)
TAB_MERCADO = "Mercado SUDEASEG"
TAB_COHORTE = "Cartera cohorte"

# Pie
FOOTER_LEGAL = "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62"
