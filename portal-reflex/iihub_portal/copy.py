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

# Vista documentación / demo (tono ejecutivo-formal)
SUITE_PAGE_HEADING = "Demostración · documentación de la suite"
# Infografía 1: mapa (variante Reflex resaltada)
SUITE_MAP_HEADING = "1. Ubicación actual (este portal)"
SUITE_MAP_ALT_REFLEX = "Mapa de la arquitectura; resaltado: portal ejecutivo de consulta de indicadores."
SUITE_MAP_CAPTION_REFLEX = (
    "La vista actual corresponde al **portal ejecutivo**: módulos **Mi cartera** y **Mercado** con representaciones gráficas e indicadores. "
    "Los datos se obtienen mediante un **servicio de datos** cifrado (HTTPS); la **carga de ficheros** (pólizas y siniestros) se realiza en el **panel de operaciones**."
)
# Infografía 2 y 3: argumentario para presentación
SUITE_COMPARISON_HEADING = "2. Enfoque basado en tablero frente a suite integral"
SUITE_COMPARISON_ALT = "Comparación entre un enfoque centrado en tableros y una suite con ingesta, almacén y servicio de datos."
SUITE_COMPARISON_CAPTION = (
    "**Microsoft Power BI** y soluciones afines destacan en **visualización y autoservicio** sobre información previamente preparada. "
    "**La presente suite** incorpora el **proceso de extremo a extremo**: ingesta validada, **almacén unificado**, **motor de cálculo de indicadores** y **dos capas de presentación analítica**. "
    "Ambos enfoques no son excluyentes: numerosas organizaciones combinan **suite de datos** y **tablero corporativo**."
)
SUITE_HEART_HEADING = "3. Proceso de datos previo a la capa gráfica"
SUITE_HEART_ALT = "Secuencia: ingesta, almacén, cómputo y aplicaciones Reflex y Streamlit."
SUITE_HEART_CAPTION = (
    "Sin **ingesta ordenada**, **repositorio único** y **reglas de cálculo centralizadas**, el cuadro de mando carece de sustento consistente. "
    "La **visualización** constituye la capa final; el **proceso de datos** es el que garantiza **coherencia numérica** entre usuarios."
)
HEADER_SUB_SUITE = (
    "Núcleo actuarial integrado: operaciones con control de acceso, almacén PostgreSQL, servicio de indicadores y analítica "
    "(portal ejecutivo y laboratorio). Despliegue demostrativo en nube; arquitectura adaptable a entorno on-premise."
)

# UI — La suite (índice, modos, glosario)
SUITE_UI_TOC_TITLE = "Índice de contenidos"
SUITE_UI_DOCS_FULL = "Documentación completa"
SUITE_UI_DOCS_SUMMARY = "Vista resumida"
SUITE_UI_GLOSSARY_TITLE = "Términos empleados en esta vista"
SUITE_PRESENTATION_SUMMARY_MD = """
**Síntesis.** La suite integra **ingesta validada**, **PostgreSQL** como repositorio, un **servicio único de indicadores** y **dos capas de consulta** (portal ejecutivo y laboratorio). Se diferencia de un despliegue basado solo en tableros (p. ej. Power BI) por el **proceso completo** desde el dato hasta la visualización. Los sistemas **Acsel/x** y **Rector** representan el **core operativo** habitual; esta solución se orienta a la **capa analítica** y a sustituir el **paralelo informal en hojas de cálculo**, no a reemplazar dichos cores en su integridad.
"""
SUITE_GLOSSARY_MD = """
| Término | Significado en este portal |
|---------|----------------------------|
| **Portal ejecutivo** | Vista actual (Reflex): **Mi cartera** y **Mercado**, lectura de KPI y series. |
| **Laboratorio analítico** | Aplicación complementaria (Streamlit): exploración ampliada y lienzo tipo autoservicio sobre los mismos datos. |
| **Panel de operaciones** | Django Admin: usuarios autorizados, carga de pólizas/siniestros y consultas con filtros. |
| **Servicio de datos (API)** | Punto único HTTPS donde las aplicaciones solicitan indicadores ya calculados; no sustituye el gobierno del dato maestro en el core asegurador. |
| **Core tradicional** | P. ej. **Acsel/x** (Consis) o **Rector** (Indra): registro operativo de pólizas y siniestros en producción. |
"""

# Bloques de documentación (índice anclado + fondos alternos en `suite_panel`)
SUITE_MD_BLOCK1 = """
### Contenido de esta sección

El texto que sigue tiene carácter de **documentación ejecutiva** para la demostración: describe el alcance de la suite, define el **servicio de datos (interfaz de programación de aplicaciones, API)** en formulación comprensible para el negocio y establece el **posicionamiento** frente a una solución limitada a cuadros de mando (p. ej. **Microsoft Power BI**).
"""

SUITE_MD_BLOCK2 = """
### Definición sintética del “core actuarial”

Constituye un **conjunto integrado y escalable**: se **ingieren y consolidan** datos (pólizas, siniestros y, según el caso, series de mercado); un **servicio centralizado** calcula y expone **indicadores homogéneos**; a continuación, **dos aplicaciones web** —portal ejecutivo y laboratorio analítico— **consultan dichos resultados** mediante canales seguros. El modelo permite **incrementar volumen y reglas** sin dispersar la lógica crítica en ficheros locales.

La **arquitectura de software** es **parametrizable** según organización (reglas, textos, despliegue). Buena parte de los componentes de referencia son de **código abierto** y admiten despliegue en **entornos de nube de coste contenido**, en función del proveedor y del volumen transaccional.
"""

SUITE_MD_BLOCK3 = """
### Cores tradicionales en seguros (Acsel/x, Rector) y aportación de la presente suite

En **Latinoamérica** y en **Venezuela**, muchas aseguradoras trabajan con **sistemas centrales de gestión** muy completos. Dos nombres que suelen citarse son:

- **Acsel/x** (Consis International): cubre pólizas, siniestros, cobranzas, canales, contabilidad y más; está muy extendido en la región.
- **Rector** (Indra): también orientado a la administración de seguros (emisión, reservas, reaseguro, entre otros), con presencia en Venezuela y el entorno regional.

Esos sistemas son, en la práctica, **donde la compañía “oficializa” la operación** (pólizas, siniestros, etc.). **Esta demostración no pretende reemplazar por completo un despliegue como Acsel/x o Rector.** Lo que sí busca sustituir es el **trabajo paralelo en Excel, bases sueltas y reportes armados a mano** —el típico “mundo aparte” junto al sistema grande—, que suele generar **cifras distintas según quien calcule**.

**Qué ofrece la suite aquí presentada:** **carga de datos con validación**, una **base de datos única (PostgreSQL)** para analítica, **un solo punto** donde las aplicaciones piden **indicadores ya calculados**, y **pantallas de consulta** (portal ejecutivo y laboratorio). Puede **convivir** con el sistema que la empresa ya tenga (por ejemplo cargando ficheros o enlazando después) o usarse como **capa de datos** según convenga.

**Poca escala, huecos o tareas fuera del sistema grande.** En compañías con **menos movimiento de operaciones**, o cuando el sistema central **no llega** a un área, deja un proceso fuera o obliga a reportes paralelos, esta línea de trabajo puede **ir tomando**, paso a paso, la **carga ordenada de información**, las **reglas de los indicadores** y las **consultas** sobre una **misma base**, siempre **acotando** cada fase: no se promete desde el día uno el mismo alcance que un **paquete completo** de los grandes proveedores.

**Cuando no hay aún un “cerebro” único.** Si la organización **no cuenta** con un sistema central fuerte, el mismo conjunto (**panel de operaciones**, **base de datos**, **servicio que entrega indicadores**, portal y laboratorio) puede, **con un plan claro por etapas**, **crecer** hacia un **núcleo propio de datos y reglas** alineado al negocio. No es una **caja cerrada** que solo el proveedor entiende: se puede **revisar y adaptar** con mayor libertad —reglas claras para todos, **tecnología abierta** y ajustes de productos, informes o enlaces **sin depender solo** de filas largas de soporte ante un único fabricante.
"""

SUITE_MD_BLOCK4 = """
### Funcionalidades objeto de la demostración

| Área | Alcance |
|------|---------|
| **Panel de operaciones** (personal autorizado) | **Autenticación** y administración de acceso; **ingesta** de pólizas y siniestros (CSV/Excel) con validación y **lotes trazables**; **consultas en solo lectura** con **criterios de búsqueda, filtrado y ordenación** para revisión de casos (año, estado, fechas, entre otros). El diseño apunta a **sustituir el entorno paralelo Excel/Access** junto al núcleo operativo (p. ej. coexistiendo con **Acsel/x** o **Rector**), no a replicar la totalidad del core tradicional en una única interfaz. |
| **Almacén de datos** | **PostgreSQL** como motor principal (en el escenario demostrativo, habitualmente **en nube**, p. ej. Supabase u homólogo); el esquema puede desplegarse en **infraestructura local** si la política corporativa lo requiere. **Historización única** de maestros; coherencia entre indicadores y origen. |
| **Servicio de datos** (“API”) | Componente que **atiende solicitudes** con KPI, cohortes y series de mercado **precalculados**. Las aplicaciones cliente **no acceden directamente** al motor de base de datos: **interrogan únicamente** al servicio mediante **HTTPS**. |
| **Este portal** | **Mi cartera**: indicadores, métricas y gráficos de composición. **Mercado SUDEASEG**: series y comparativas con referencia pública. Orientado a **consulta ejecutiva expedita** (incluido acceso móvil). |
| **Laboratorio analítico** (enlace en el menú) | Además de visualizaciones y tabulados predefinidos, incorpora un módulo de **exploración tipo lienzo** que permite **definir dimensiones, filtros y vistas** en modalidad análoga al **autoservicio** de Power BI, sobre la misma información servida por la API (sin dependencia de ficheros Excel externos). **Consistencia numérica** con el portal ejecutivo. |
"""

SUITE_MD_BLOCK5 = """
### El servicio de datos (API) en términos de negocio

Puede conceptualizarse como un **punto único de solicitud** de información: ante una petición del tipo «resumen de cartera del año X», el servidor devuelve un conjunto de datos **homogéneo y validado**, evitando divergencias de cálculo entre aplicaciones. En términos técnicos se implementa como **API REST** sobre **HTTPS**; desde la perspectiva de negocio constituye la **interfaz oficial** para indicadores y series.
"""

SUITE_MD_BLOCK6 = """
### Despliegue: entornos en nube y on-premise

La **demostración** se exhibe habitualmente **en infraestructura de nube** (coste y despliegue acotados). La arquitectura admite **traslado a instalación local** o nube privada: mismos componentes (panel de operaciones, PostgreSQL, servicio de datos, aplicaciones de presentación), con políticas de red, seguridad y respaldo acordes al entorno.
"""

SUITE_MD_BLOCK7 = """
### Diferenciación frente a una solución exclusivamente orientada a tableros

**Microsoft Power BI** constituye un referente en **visualización y autoservicio de inteligencia de negocio** sobre datos conectados o previamente modelados; en numerosas organizaciones desempeña la función de **capa de presentación** corporativa.

La **presentación demostrativa** incorpora, además, **ingesta controlada**, **repositorio unificado**, **cálculo centralizado** y **dos modalidades de análisis**. Las figuras precedentes ilustran la **comparación de enfoques** y la **secuencia previa a la visualización**.

**Sobre estética y autoservicio.** **Microsoft Power BI** admite **personalización visual** amplia (temas de informe, formato de objetos visuales y, en muchos despliegues, **exploración por parte del negocio** sin depender del desarrollador). **No** se pretende aquí afirmar que esta suite «supera» al tablero por defecto en belleza de gráficos o en rapidez de maquetar un informe. El valor diferencial de la presentación demostrativa es otro: **experiencia de producto integrada** (portal ejecutivo y laboratorio) y **gobernanza del dato de extremo a extremo** —ingesta, almacén, reglas de indicadores y consulta— como **complemento** habitual al **cuadro de mando corporativo** cuando ambos conviven.

**Ventajas recurrentes frente a una arquitectura basada únicamente en tableros** (sin menoscabar el valor de Power BI):

- **Trazabilidad**: cada ingesta genera **lote** y registro de auditoría; no únicamente una actualización de informe sin trazabilidad del fichero fuente.
- **Fuente única de verdad** para los indicadores servidos; reducción del riesgo de **discrepancias entre cuadros de mando homólogos**.
- **Coste y soberanía tecnológica**: ecosistema abierto y despliegues accesibles; las soluciones propietarias habituales implican **licenciamiento y gobierno** (enfoques complementarios, no excluyentes).
- **Control del proceso**: reglas y validaciones **previas** a la materialización gráfica.
- **Gobernanza frente al uso paralelo de herramientas ofimáticas**: menor exposición cuando los indicadores residen en **Excel** desarticulados del **core** (**Acsel/x**, **Rector** u otro).

**Ventajas complementarias del enfoque “core actuarial”** frente a cadenas exclusivamente ofimáticas adyacentes al core:

- **Reproducibilidad**: reglas homogéneas en servidor para **ingesta, cómputo y consulta**; independiente del usuario que mantenga abierto un determinado fichero `.xlsx`.
- **Canal único para aplicaciones**: portal ejecutivo, laboratorio y consumidores futuros acceden al **mismo servicio de datos**, no a réplicas inconsistentes.
- **Escalabilidad técnica**: PostgreSQL y servicios sin estado de sesión escalan con la organización; sin la limitación inherente a ficheros compartidos o bases de escritorio.
- **Menor acoplamiento a un único proveedor de visualización**: la capa gráfica resulta **sustituible**; el activo reside en **datos y reglas centralizadas**.

**Coexistencia con Power BI**: es frecuente alimentar el tablero corporativo desde el **mismo almacén o canal de datos** que una suite de este tipo.
"""

SUITE_MD_BLOCK8 = """
### Ubicación por rol

| Rol | Punto de acceso |
|-----|-----------------|
| **Ingesta y revisión de casos** | Panel de operaciones → carga de pólizas / siniestros; listados filtrados |
| **Lectura ejecutiva** | Este portal → **Mi cartera** / **Mercado** |
| **Análisis exploratorio y autoservicio tipo lienzo** | **Análisis BI detallado** (laboratorio), menú principal |

*Las cifras operativas deben contrastarse siempre con los sistemas oficiales de registro.*
"""

SUITE_ARCHITECTURE_MD = "\n\n".join(
    [
        SUITE_MD_BLOCK1,
        SUITE_MD_BLOCK2,
        SUITE_MD_BLOCK3,
        SUITE_MD_BLOCK4,
        SUITE_MD_BLOCK5,
        SUITE_MD_BLOCK6,
        SUITE_MD_BLOCK7,
        SUITE_MD_BLOCK8,
    ]
)

# Índice: ancla → etiqueta (misma numeración que bloques)
SUITE_TOC_ENTRIES: list[tuple[str, str]] = [
    ("suite-1", "Contenido"),
    ("suite-2", "Core actuarial"),
    ("suite-3", "Acsel/x y Rector"),
    ("suite-4", "Funcionalidades"),
    ("suite-5", "Servicio de datos (API)"),
    ("suite-6", "Despliegue"),
    ("suite-7", "Diferenciación vs tableros"),
    ("suite-8", "Roles"),
]

# Errores API — cartera / mercado
CARTERA_API_ERROR_ACTION = "Reintentar"
CARTERA_API_ERROR_LINK = "Abrir carga de pólizas (panel de operaciones)"
MERCADO_API_ERROR_ACTION = "Reintentar carga de series"
MERCADO_API_ERROR_LINK = "Abrir carga de pólizas (panel de operaciones)"

# Pie
FOOTER_LEGAL = "Seguros La Fe · RIF J-000467382 · SUDEASEG N.º 62"
