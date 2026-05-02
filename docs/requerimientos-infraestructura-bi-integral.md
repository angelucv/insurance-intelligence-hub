# Requerimientos integrales de infraestructura de BI — Cobranza (La Fe)

**Fecha:** 14/04/2026 · **Versión:** 1.1 · **Elaborado por:** Angel Colmenares · **Cargo:** Coordinador Estadístico · **Estado:** propuesta para validación por sistemas

**Versión ejecutiva (PDF):** portada con logo, márgenes amplios, glosario para lectores no técnicos y texto ampliado de solicitud/justificación — generar con `python scripts/generar_pdf_requerimientos_bi.py` a partir de `docs/pdf/requerimientos-infraestructura-bi-integral.html` (salida: `docs/pdf/infra-bi-la-fe.pdf`).

---

Documento único para alinear **área de tecnología**, **negocio** y **desarrollo**. **Fase inicial:** BI orientado al **seguimiento de cobranza** sobre la cartera vigente (**funerario, vida AP, RCV**). **Etapas posteriores:** BI en **otras áreas** de forma escalonada; la infraestructura debe contemplar ese crecimiento.

---

## 1. Objetivo

Disponer de un entorno **estable, seguro y escalable** para:

- Tableros y análisis con **Streamlit** (propuesta de este documento). Cualquier otro front o marco equivalente sería **cambio explícito** acordado con el área de tecnología. **Énfasis inicial en cobranza** y posibilidad de ampliar a otras áreas según roadmap.
- **API en Python** (p. ej. FastAPI) como capa de métricas y reglas de negocio frente a los datos.
- **No impactar** el sistema transaccional del core (Sirweb): la lectura operativa de datos sensibles se hará por canales definidos por tecnología.
- **Infraestructura** preparada para **crecer** con el volumen de datos y la **concurrencia de acceso**, y para **incorporar en fases posteriores** BI en otras áreas sin rediseñar desde cero.

---

## 2. Principios de arquitectura

| Principio | Descripción |
|-----------|-------------|
| Separación lectura/escritura del core | Las consultas de BI **no** deben ejecutarse contra el OLTP de producción en horarios o modos que afecten operación. |
| Solo lectura hacia el origen corporativo | Acceso a datos maestros vía **réplica**, **vistas** o **esquema analítico** provisto por sistemas. |
| Escritura solo en capa analítica propia | Tablas intermedias, agregados y caches viven en un **destino con escritura** bajo control del proyecto BI (ver sección 6). |
| Contenedores para aplicación | Despliegue con **Docker** (Compose u homólogo) sobre **Ubuntu Server LTS**. |
| Secretos y configuración | Variables por entorno; **sin** credenciales en repositorio; integración con estándar de la empresa. |
| Evolución por fases | La arquitectura debe permitir **ampliar el BI** a otras áreas y fuentes **de forma escalonada**, con gobierno del dato y capacidad acordadas con tecnología. |

---

## 3. Alcance funcional (fase inicial)

- **Contexto de cartera:** la oferta comercial actual se centra en **funerario**, **vida AP** y **RCV**; los indicadores de cobranza deben alinearse a esas líneas.
- **Área y enfoque inicial:** **seguimiento de la cobranza** (indicadores a definir con negocio: mora, vencimientos, cartera, cumplimiento, etc.).
- **Roadmap:** en **etapas posteriores** se incorporará BI para **otras áreas** de manera escalada; la infraestructura debe contemplar ese crecimiento (capacidad, red, entornos o esquemas según política).
- **Tipo de uso:** principalmente **lectura y visualización**; cualquier escritura hacia sistemas corporativos queda **fuera de alcance** salvo acuerdo explícito posterior.

---

## 4. Arquitectura lógica objetivo

```
[ Usuarios autorizados ]
         │
         ▼
[ HTTPS / DNS interno ] ──► [ Reverse proxy ]
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
 [ Streamlit ]             [ API Python ]          (opcional futuro)
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         [ Base analítica con ESCRITURA ]
         (tablas intermedias, agregados, índices)
                     │
                     ▲
                     │  ETL / jobs programados (solo lectura en origen)
                     │
         [ Réplica / vistas / esquema de lectura ]
                     │
                     ▼
              [ Core / origen datos ]
              (Sirweb — gestionado por tecnología)
```

---

## 5. Infraestructura de aplicaciones (servidor de apps)

### 5.1 Sistema operativo

- **Ubuntu Server 22.04 LTS** (64 bits), actualizado según política de parches de la empresa.

### 5.2 Hardware orientativo (VM o físico dedicado)

| Recurso | Mínimo (piloto) | Recomendado |
|---------|-----------------|-------------|
| CPU | 4 vCPU | **8 vCPU** |
| RAM | 16 GB | **32 GB** |
| Disco | SSD **200 GB** | SSD **≥ 500 GB** |
| Red | 1 Gbps, IP fija en VLAN acordada | Igual |

*Justificación disco:* SO, Docker, imágenes, entornos Python, logs, espacio para cachés locales si aplica política; margen de crecimiento.

### 5.3 Software base en el servidor de apps

| Componente | Uso |
|------------|-----|
| **Docker** + Docker Compose (o runtime equivalente aprobado) | Contenedores de Streamlit, API y procesos batch si se empaquetan así. |
| **Python 3.11+** | Runtime alineado con imágenes base o venv si algún componente corre fuera de contenedor. |
| **Reverse proxy** (p. ej. **nginx**) | Terminación TLS, enrutamiento a servicios, límites de tamaño de cuerpo. |
| **Certificados TLS** | Certificado corporativo / CA interna (no autofirmado en producción sin excepción documentada). |

### 5.4 Instalación de dependencias y actualizaciones

- El área de tecnología debe definir **un único mecanismo**, acorde a la política de La Fe, para que el servidor obtenga **paquetes Python** e **imágenes Docker** de forma controlada (habitualmente **salida vía proxy corporativo** gestionado por sistemas). Si no hubiera salida a Internet, se aplicará el **procedimiento acordado** de importación de artefactos (entorno restringido o importación manual documentada, p. ej. air-gap). No se detallan aquí marcas o productos de repositorio: basta con que exista **una vía clara y soportada** por la empresa.

### 5.5 Operación

- Servicios con **arranque automático** y **reinicio** ante fallo.
- **Logs** con rotación; preferible integración con centralización de logs si existe.
- **Backups:** al menos configuración de despliegue y definiciones versionadas en Git; política de backup de volúmenes Docker acordada con sistemas.

### 5.6 Monitoreo y alertas

- Además de logs y rotación, se requiere **visibilidad proactiva** antes de que el fallo se note al **abrir el tablero**: **health checks** sobre la API (Python), el front (Streamlit) y, si aplica, la ejecución de jobs ETL (última corrida, duración anómala, errores).
- Si un servicio no responde o un job crítico no corrió, debe poder **notificarse** al **equipo de desarrollo BI** (y a sistemas si aplica). Como mínimo suele bastar **correo** hacia una **lista de destinatarios definida**. La herramienta concreta la define tecnología con seguridad.

### 5.7 Continuidad operativa ante incidentes (RTO y RPO)

- **RTO** (*Recovery Time Objective*): tiempo máximo aceptable para restaurar tablero y API tras una caída; orienta si basta una VM o se requiere alta disponibilidad respecto a decisiones de cobranza.
- **RPO** (*Recovery Point Objective*): antigüedad máxima aceptable de los datos recuperados; se alinea con frecuencia de backup de la capa analítica.
- Los valores concretos se negocian con tecnología y se revisan al crecer el **uso** y la criticidad.

---

## 6. Base de datos y datos

### 6.1 Lectura desde el entorno corporativo

- **Réplica de solo lectura**, **vistas** publicadas por sistemas, o **esquema analítico** alimentado por ellos.
- Credenciales **dedicadas** al proyecto BI, **mínimo privilegio** (idealmente solo `SELECT` sobre objetos acordados).
- Conectividad desde el servidor de apps (o desde el host de ETL) según reglas de firewall.

### 6.2 Escritura para tablas intermedias (obligatorio para modelo analítico)

La réplica **no** admite creación de tablas propias del proyecto. Por tanto:

**Opción preferida (recomendada):**

- **Instancia PostgreSQL (u homólogo aprobado)** con **escritura** en esquema dedicado a BI (mismo centro de datos, idealmente **servidor separado** del servidor de aplicaciones para no competir por CPU/RAM/I/O).

**Opción alternativa (piloto / volúmenes controlados):**

- **DuckDB / SQLite / Parquet** en volumen persistente Docker, alimentados por jobs ETL.
- Requiere acuerdo explícito sobre **backup, tamaño máximo y concurrencia**.

Los jobs **leen** el origen de solo lectura y **escriben** en la capa analítica con escritura.

Ante el volumen histórico potencial de datos de cobranza, el paso a **PostgreSQL dedicado** debe basarse en **criterios de salida del piloto** acordados (umbrales **X** e **Y** a fijar en el proyecto), por ejemplo:

- Tamaño de la capa analítica o indisponibilidad de rendimiento (p. ej. superar **X GB**).
- Concurrencia (accesos simultáneos al tablero y a la API): más de **Y** o picos sostenidos que degraden tiempos de respuesta.
- Necesidades de integridad concurrente, auditoría o backups en caliente que el esquema de archivos no cubra bien.

### 6.3 Separación app vs datos

| Escenario | Cuándo |
|-----------|--------|
| **Mismo host:** app Docker + motor analítico en contenedor | Piloto pequeño, baja concurrencia; debe revisarse al crecer datos o la carga de accesos. |
| **Hosts separados:** apps en un servidor, BD analítica en otro | **Escenario ideal** para producción y crecimiento. |

---

## 7. Aplicación (stack de desarrollo)

| Capa | Tecnología propuesta |
|------|----------------------|
| Interfaz BI | **Streamlit** |
| API de métricas / negocio | **FastAPI** (Python), consumida por Streamlit y futuros clientes |
| Validación y contratos | Pydantic / paquetes compartidos en repositorio |
| Orquestación de ETL ligero | Cron, systemd timers, o herramienta que apruebe sistemas |

*Evolución futura:* otro front (p. ej. React) puede consumir la **misma API** sin cambiar el modelo de datos.

**Streamlit como capa de presentación:** es la opción planteada en este documento para el tablero en Python. El **framework Streamlit no incluye de serie** un modelo multiusuario corporativo (cuentas, roles o perfiles de aplicación); **implementarlo sería desarrollo adicional** sobre el marco. En esta fase el **acceso** a la URL se **restringe por red, proxy y políticas** (sección 8), sin asumir ese módulo dentro de la app.

---

## 8. Desarrollo, repositorio e integración continua

**Git** (p. ej. GitHub u otra forja aprobada) aporta **control de versiones** (historial, ramas, revisiones), **trabajo colaborativo** e **integración/despliegue automatizado**. No sustituye el almacén de datos de la empresa: solo concentra **código** y definición técnica del despliegue.

El desarrollo se realiza en **estaciones de trabajo** (equipo de escritorio o portátil con capacidad equivalente; ver sección 10). El código se centraliza en un **repositorio privado** en la **forja Git autorizada por la empresa** (creado y mantenido por **desarrollo BI**, con **accesos y política** acordados con tecnología): API (FastAPI), tableros (Streamlit), contenedores y pruebas.

### 8.1 Qué sí y qué no debe vivir en el repositorio

- **No** deben residir ahí **datos sensibles de negocio**, **volcados de bases de datos** ni **credenciales** en claro; eso queda en servidores/bases autorizados o **gestores de secretos** (sección 9).
- El repo guarda código, plantillas de configuración **sin** secretos, Dockerfile, compose y documentación — en línea con política de seguridad de La Fe.

### 8.2 Contenido mínimo esperado en el repositorio

- **Dockerfile** (por servicio o los que aplique).
- **docker-compose.yml** (u homólogo) para orquestar app, API, motor analítico piloto, etc.
- **.gitignore** para no versionar secretos ni credenciales.
- Código `.py`, `requirements.txt` (o equivalente) y documentación breve de despliegue.

### 8.3 Despliegue automatizado (p. ej. GitHub Actions)

- **GitHub Actions** (o pipeline equivalente) puede ejecutar pruebas, construcción de imágenes y despliegue ante cambios en la rama acordada, **según política de La Fe**.
- Si no se autoriza ejecución desde la nube hacia la red interna, se usará variante aprobada (agente *self-hosted*, artefactos y despliegue supervisado, etc.).

---

## 9. Red y seguridad

| Tema | Requerimiento |
|------|----------------|
| Exposición | **Sin** publicación abierta a Internet para datos reales; acceso **intranet y/o VPN** según política. |
| Autenticación | Integración con **SSO / directorio / política corporativa** (Azure AD, LDAP, etc.) o modelo acordado (proxy con auth). |
| Firewall | Reglas explícitas: tráfico desde **redes o equipos autorizados** → proxy → apps; salida apps → BD lectura y BD analítica. |
| Cuentas de servicio | Usuario de ejecución **sin** privilegios de administrador en el SO. |
| Secretos | Almacenamiento seguro (vault, secretos del orquestador, o mecanismo que use La Fe). |

---

## 10. Entornos

| Entorno | Propósito |
|---------|-----------|
| **Desarrollo** | Estación de trabajo del desarrollador: **equipo asignado** (PC Core i7, 16 GB RAM) **u ordenador portátil equivalente** (p. ej. Intel Core i9-13900H, 16 GB RAM) para el mismo fin. |
| **Integración / pruebas** | Servidor o VM con datos **anonimizados o subset** cuando sea posible. |
| **Producción** | Servidor(es) descritos en este documento, datos reales, cambios controlados. |

---

## 11. Roles y responsabilidades

| Área | Responsabilidad |
|------|-----------------|
| **Tecnología / sistemas** | VMs, red, firewall, TLS, réplica o acceso lectura, provisión de BD analítica con escritura, identidad, backups, monitoreo/alertas acordados, y **política única** de obtención de paquetes e imágenes (sección 5.4). |
| **Desarrollo BI** | Diseño de aplicación, API, ETL hacia capa analítica, repositorio, documentación de despliegue, no hardcodear secretos. |
| **Negocio / cobranza** | Definición de KPIs, validación funcional, uso autorizado. |

---

## 12. Entregables esperados del área de tecnología (checklist)

- [ ] VM(s) o servidor(es) con especificaciones de la sección 5.2, **Ubuntu 22.04 LTS**.
- [ ] **Docker** y mecanismo de despliegue acordado.
- [ ] **Proxy inverso + HTTPS** con certificado válido en el entorno corporativo.
- [ ] Acceso **lectura** a datos de cobranza vía réplica/vistas/esquema (credenciales y firewall).
- [ ] **Base de datos con escritura** para esquema BI (preferible servidor dedicado) o aprobación explícita de alternativa DuckDB/Parquet con política de backup.
- [ ] **Política definida** para obtener paquetes Python e imágenes Docker (p. ej. proxy corporativo o, si no hay salida, procedimiento de importación acordado —sección 5.4).
- [ ] Definición de **autenticación / control de acceso** al tablero (p. ej. SSO o proxy; ver sección 8).
- [ ] **DNS interno** para el servicio (nombre estable).
- [ ] **Monitoreo y alertas:** health checks (API, Streamlit, ETL según diseño) y notificación proactiva (p. ej. correo a destinatarios acordados).
- [ ] **RTO y RPO** documentados con negocio (continuidad del tablero ante incidentes).
- [ ] **Forja Git autorizada por la empresa** con **repositorio privado del proyecto** (**creado y mantenido por desarrollo BI**; tecnología facilita **accesos y política**). Lo que corre en el **servidor** debe ser la **réplica completa** del desarrollo desplegado; el repo es el canal para **cambios ágiles** y versionado, permitiendo publicar mejoras **en cualquier momento** (ramas y política acordadas). Incluye Dockerfile, docker-compose (o equivalente), `.gitignore` y pipeline CI/CD acordado (p. ej. GitHub Actions o alternativa interna).

---

## 13. Supuestos y puntos abiertos

- El modelo exacto de datos de cobranza y nombres de tablas/vistas lo define **negocio + tecnología** con el core Sirweb, alineado a las líneas **funerario, vida AP y RCV**.
- La ampliación del BI a **otras áreas** y el calendario por fases lo acuerdan **negocio y tecnología**; la infraestructura debe poder **soportar esa evolución** sin partir de cero en cada etapa.
- El dimensionamiento fino puede ajustarse tras un **piloto de carga** y al incorporar nuevas áreas o mayor uso concurrente.
- Cualquier cambio que implique **escritura en sistemas transaccionales** del core queda **fuera** de este documento hasta nuevo acuerdo.

---

## 14. Planificación indicativa (un recurso a tiempo parcial) y fases posteriores

**Advertencia:** de **carácter meramente orientativo**. Lo que más condiciona el calendario suele ser **infraestructura, datos y aprobaciones**. El alcance del proyecto incluye **desarrollar las consultas** al origen de datos autorizado y los **procesos ETL** hacia la capa analítica (sección 6).

**Supuesto:** **un recurso a tiempo parcial** asignado al proyecto; piloto acotado (cobranza; líneas funerario, vida AP y RCV); y colaboración oportuna del área de tecnología en accesos y despliegue. Un orden de magnitud razonable:

- **~1,5–2,5 meses:** primer entregable en **integración / pruebas** (API + tablero inicial + ETL mínimo).
- **~3–5 meses:** **piloto en producción** con valor para el **área de negocio** (despliegue estable, alertas básicas; revisar sección 6.2).
- Si sistemas o seguridad alargan trámites, el calendario se desplaza **sin relación** con la dedicación del recurso.

Definir por escrito un **MVP** del piloto (pantallas e indicadores) y la fecha objetivo de disponibilidad de datos ayuda a acotar estos plazos.

### 14.1 Fases posteriores (solo esquema; sin fechas)

- **Fase posterior 1 — Consolidación de cobranza:** más KPIs y mayor uso del tablero, monitoreo y backups; motor analítico dedicado cuando proceda (sección 6.2).
- **Fase posterior 2 — Otras áreas de BI:** nuevos tableros y fuentes, mismo esquema técnico, gobierno del dato por ámbito.
- **Fase posterior 3 — Madurez:** autenticación corporativa si aplica; capacidad y continuidad según criticidad y RTO/RPO.

### 14.2 Seguimiento de avances (orientativo)

Conviene acordar una **cadencia de seguimiento** entre desarrollo BI, tecnología y, cuando aplique, negocio; lo siguiente es **meramente orientativo** y no sustituye el calendario oficial de la empresa:

- **Arranque** (infra y datos): **sincronización semanal breve** (p. ej. 15–30 min) o **informe escrito** (hecho / siguiente / bloqueos).
- **Revisión** con logros o demo corta aproximadamente cada **dos semanas**.
- **Mensual** con dirección o negocio para **alcance y prioridades**, no para cada detalle técnico.
- Si no hay novedades, la semanal puede **cancelarse** o ser **asíncrona**.

---

## 15. Contacto y aprobaciones

| Rol | Nombre | Firma / Fecha |
|-----|--------|----------------|
| Solicitante (desarrollo BI) | | |
| Tecnología / infraestructura | | |
| Seguridad / CISO (si aplica) | | |
| Área de negocio (cobranza) | | |

---

*Documento generado para uso interno La Fe — puede incorporarse al expediente del proyecto y actualizarse por versiones.*
