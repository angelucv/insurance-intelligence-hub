# Catálogo de métricas, gráficos y reparto Reflex / Streamlit

Referencia para diseñar **endpoints**, **contratos JSON** y **pantallas** sin duplicar lógica incoherente. Los datos SUDEASEG están en `market_sudeaseg_*` (miles de Bs. según fuente); la cartera demo en `policies` + KPI sintético vía API actual.

---

## 1. Inventario de datos útiles

### Resumen por empresa (`market_sudeaseg_resumen_empresa`)

| Campo base (YTD en cada `period_month`) | Campo incremental (`*_mes`) |
|----------------------------------------|----------------------------|
| `primas_netas_cobradas` | `primas_netas_cobradas_mes` |
| `siniestros_pagados` | `siniestros_pagados_mes` |
| `reservas_psp_brutas` | `reservas_psp_brutas_mes` |
| `reservas_psp_netas_reaseg` | `reservas_psp_netas_reaseg_mes` |
| `siniestros_totales` | `siniestros_totales_mes` |
| `comisiones` | `comisiones_mes` |
| `gastos_adquisicion` | `gastos_adquisicion_mes` |
| `gastos_administracion` | `gastos_administracion_mes` |

**Derivadas recomendadas (API o vista materializada):**

- `loss_ratio_proxy_ytd` = `siniestros_totales / nullif(primas_netas_cobradas, 0)` (misma ventana YTD).
- `loss_ratio_proxy_mes` = `siniestros_totales_mes / nullif(primas_netas_cobradas_mes, 0)` (cuidado con meses con primas muy bajas).
- `comision_ratio_ytd` = `comisiones / nullif(primas_netas_cobradas, 0)`.
- `gasto_adm_ratio_ytd` = `gastos_administracion / nullif(primas_netas_cobradas, 0)`.
- `crecimiento_ytd_yoy` = comparar YTD del mismo `period_month` entre años (ej. sep 2024 vs sep 2023).
- `crecimiento_mes_mom` o comparación del mismo mes año anterior.
- **Cuota de mercado (primas YTD):** `primas_empresa / primas_mercado` para un mes dado (suma de todas las filas del mismo `source_file`, `period_year`, `period_month`).

### Cuadro de resultados (`market_sudeaseg_cuadro_resultados`)

| YTD | Mes |
|-----|-----|
| `primas_netas_cobradas` (cuando existe) | `primas_netas_cobradas_mes` |
| `resultado_tecnico_bruto` | `resultado_tecnico_bruto_mes` |
| `resultado_reaseguro_cedido` | `resultado_reaseguro_cedido_mes` |
| `resultado_tecnico_neto` | `resultado_tecnico_neto_mes` |
| `resultado_gestion_general` | `resultado_gestion_general_mes` |
| `saldo_operaciones` | `saldo_operaciones_mes` |

**Derivadas:**

- Margen / resultado sobre primas (YTD): `resultado_tecnico_neto / nullif(primas, 0)` si hay primas en cuadro; si no, solo series absolutas.
- Evolución de `saldo_operaciones` (YTD) como “trayectoria anual” acumulada.

### Cartera demo (API `/kpi/summary` + `policies`)

- Persistencia, activas, lapsos, prima media, ratio técnico demo (sintético / proxy).

---

## 2. Lista extensa de indicadores (por tema)

### A. Volumen y crecimiento (mercado / La Fe)

1. Primas netas cobradas (YTD mensual — escalón por mes).
2. Primas netas cobradas (flujo `*_mes`) — línea temporal.
3. Variación % YoY del YTD (mismo mes, distinto año).
4. Variación % del flujo mensual vs mismo mes año anterior.
5. Índice encadenado (base ene=100 o dic año-1=100).
6. Cuota de mercado primas (La Fe vs total) por cierre mensual.
7. Ranking por primas YTD (tabla o top-N).

### B. Siniestralidad y reservas

8. Siniestros totales YTD y `*_mes`.
9. Siniestros pagados YTD y `*_mes`.
10. Reservas PSP brutas / netas (YTD y mes).
11. Ratio siniestros totales / primas (YTD y mes).
12. Ratio siniestros pagados / primas.
13. “Combined ratio” aproximado (si se define numerador común con gastos + siniestros; documentar fórmula explícita).

### C. Eficiencia y estructura de gastos

14. Comisiones / primas (YTD).
15. Gastos administración / primas (YTD).
16. Gastos adquisición / primas (YTD).
17. Composición apilada (comisiones + gastos adm + adq) en % de primas o absoluto mensual.
18. Evolución mensual de cada gasto (`*_mes`).

### D. Resultados (cuadro — más técnico-contable)

19. Resultado técnico bruto YTD y mensual.
20. Resultado reaseguro cedido YTD y mensual.
21. Resultado técnico neto YTD y mensual.
22. Resultado gestión general YTD y mensual.
23. Saldo de operaciones YTD (y opcionalmente flujo mensual).
24. Waterfall simplificado (bruto → reaseguro → neto → gestión → saldo) para un cierre elegido.

### E. Comparación y contexto de mercado

25. Curva de Lorenz / concentración (opcional avanzado): primas acumuladas por empresas ordenadas.
26. Posición de La Fe en ranking (percentil o puesto).
27. Brecha La Fe vs mediana del mercado en ratio o primas.
28. Mapa de calor: mes × año × métrica (una empresa).

### F. Operativo demo (pólizas)

29. KPI cohorte (existentes) por año.
30. Puente “demo vs referencia SUDEASEG”: texto o gauge que compare orden de magnitud (sin afirmar igualdad contable).

---

## 3. Gráficos sugeridos (tipo × métrica)

| Tipo | Indicadores adecuados |
|------|------------------------|
| **Línea temporal** | Primas `_mes`, siniestros `_mes`, comisiones `_mes`, ratios mensuales (con umbral de aviso si denominador pequeño). |
| **Área / línea YTD** | Primas YTD, siniestros totales YTD (escalón creciente en el año). |
| **Barras agrupadas** | Mismo mes, varias métricas; o La Fe vs mercado (total). |
| **Barras apiladas** | Gastos + comisiones vs primas (estructura). |
| **Donut / torta** | Cuota de mercado en un punto de tiempo (uso moderado). |
| **Tabla + sparkline** | Ranking empresas con mini-serie. |
| **Scatter** | Primas YTD vs ratio (cada punto una empresa en un mes). |
| **Waterfall** | Resultados cuadro para un mes. |
| **Banda / ribbon** | Percentiles mercado con línea La Fe superpuesta. |
| **Gauge** | Solo para KPI demo o ratios con objetivo declarado “ilustrativo”. |

---

## 4. Cómo separar Reflex y Streamlit (principios)

- **Una sola fuente de verdad:** Postgres + **API FastAPI** que exponga DTOs estables (`MarketLaFeSeries`, `MarketBenchmark`, `CohortKpiSummary`, …). Reflex y Streamlit solo consumen HTTP; no duplican SQL ni fórmulas críticas en el cliente salvo formateo.
- **Contratos compartidos:** Definir schemas en `shared/` (Pydantic) o OpenAPI generado por FastAPI para que ambos portales usen los mismos nombres de campo y semántica (YTD vs `flow_month`).
- **Semántica explícita en payload:** Cada serie debe llevar `granularity` (`ytd_eom` | `monthly_flow`), `unit` (`thousands_bs`), `source` (`sudeaseg`).

### Opción recomendada: **Reflex = ejecutivo / Streamlit = laboratorio**

| Plataforma | Rol | Contenido típico |
|------------|-----|-------------------|
| **Reflex** | Portal ejecutivo, primera impresión, móvil OK | Pocos KPIs, **La Fe** en foco: primas y siniestralidad proxy (YTD + últimos meses), cuota simple, enlace a laboratorio y admin. Opcional: **tarjetas** de resultado (solo último cierre) sin waterfall pesado. |
| **Streamlit** | Exploración, comparaciones, exportación | **Todas** las series anteriores: multi-selector empresa, mercado, años; tablas ranking; ratios; cuadro de resultados; cruce demo vs SUDEASEG; descarga CSV. |

**Ventajas:** Reflex no se satura; Streamlit ya es el “lab” en el README; la audiencia ejecutiva no necesita 20 gráficos en la home.

### Opción alternativa: **Reflex = macro de todo / Streamlit = detalle de todo**

| Plataforma | Rol |
|------------|-----|
| **Reflex** | Dashboard “panorama”: mismas familias de indicadores (volumen, siniestralidad, gastos, resultado) pero **versión resumida** (un gráfico por familia + KPIs). |
| **Streamlit** | Misma taxonomía de familias pero **filtros finos**, más gráficos por página, tablas drill-down y export. |

**Ventaja:** coherencia mental “misma estructura de menú” en ambos sitios. **Riesgo:** Reflex puede volverse pesado si se copian demasiadas vistas.

---

## 5. Ruta por plataforma (checklist de implementación)

### API (previo o en paralelo)

- [x] `GET /api/v1/market/la-fe/resumen-series` — `mode` (`ytd` | `monthly_flow`), `from_year`, `to_year`, `empresa_norm_fragment`.
- [x] `GET /api/v1/market/resumen/totals-series` — suma mercado (misma granularidad).
- [ ] `GET /api/v1/market/benchmarks` — mediana / ranking La Fe (opcional).
- [x] `GET /api/v1/market/la-fe/resumen-extended` — resumen completo La Fe (YTD / flujo mensual).
- [x] `GET /api/v1/market/resumen/totals-extended` — suma mercado (mismas magnitudes).
- [x] `GET /api/v1/market/la-fe/cuadro-series` y `GET /api/v1/market/cuadro/totals-series` — cuadro de resultados.
- [x] `GET /api/v1/market/la-fe/snapshot-latest` — último cierre YTD + cuota primas.
- [ ] Reutilizar `/api/v1/kpi/summary` para demo; opcional `GET .../bridge` que devuelva texto comparativo parametrizado.

### Reflex (fase 1)

- [x] Bloque “Referencia SUDEASEG — La Fe”: primas mensuales (eje dual) + líneas de loss ratio La Fe vs mercado.
- [x] Tarjetas último cierre (`snapshot-latest`): primas, siniestros, ratios, cuota, comisiones, gasto adm.
- [x] Enlace a carga de siniestros (Admin) + laboratorio; KPI cohorte (existente).

### Streamlit (fase 1)

- [x] Pestaña “Mercado SUDEASEG” con subpestañas: primas vs mercado, último cierre, métricas resumen extendidas, cuadro de resultados + CSV/JSON.
- [ ] Waterfall cuadro para un mes puntual (pendiente).
- [x] Pestaña “Cohorte demo” (actual) + nota metodológica vía `data_note` API.

### Fase 2 (según prioridad)

- [ ] Ranking y percentiles; heatmap; scatter mercado.
- [ ] Exportaciones programáticas; caché en API.

---

## 6. Resumen de decisión sugerida

- **Sí:** definir primero el **conjunto de métricas** y **por endpoint**; luego gráficos.
- **Separación recomendada:** **Reflex = financiero/mercado en modo ejecutivo (La Fe + pocos KPIs)** + **Streamlit = detalle técnico y exploración de todo el catálogo**; la **cartera demo** puede vivir en ambos pero con **menos peso en Reflex**.
- Si preferís **paridad de familias** en ambos portales, usar la **opción alternativa** manteniendo siempre **menos densidad** en Reflex.

Este documento puede actualizarse cuando cierren la lista mínima v1 de endpoints.
