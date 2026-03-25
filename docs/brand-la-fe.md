# Marca Seguros La Fe — demo Insurance Intelligence Hub

Referencia pública del producto funerario: [Asistencia funeraria](https://seguroslafe.com/salud/). Uso **no oficial**: el repositorio es un hub técnico; validar con el cliente antes de publicar.

## Django Admin

El admin usa cabecera morada (`#7029B3`), logo `logo-fe-2` en la barra superior y pie con RIF / SUDEASEG. Los estilos viven en `backend-ingest/core/static/admin/css/la_fe_admin.css` y la plantilla en `backend-ingest/templates/admin/base_site.html`.

## Logos versionados (`static/brand/`)

| Archivo | Uso recomendado |
|---------|-----------------|
| `logo-fe-1.jpg` | Logo base (fondo claro): headers Admin, Streamlit, Reflex en modo claro. |
| `logo-fe-2.jpg` | Variante con **fondo morado**; barras de navegación, hero oscuro, contraste con texto blanco. |
| `logo2.jpg` | Cintillo **60 años (1965–2025)**; landing, pie de campaña o sección “Trayectoria”. |

Copia adicional en `Info/logos/` (local, no versionada) puede usarse solo en tu máquina.

## Paleta (derivada de logo-fe-2 y material gráfico)

Valores orientativos para CSS / temas; ajustar con muestreado fino sobre los JPG si hace falta.

| Token | HEX | Uso |
|-------|-----|-----|
| `--brand-purple` | `#7029B3` | Primario (botones, barras, acentos). |
| `--brand-purple-deep` | `#5a1f94` | Hover, bordes fuertes. |
| `--brand-lavender` | `#C4B5FD` | Fondos suaves, acentos claros (similar al “6” del cintillo). |
| `--brand-lilac` | `#E9D5FF` | Superficies secundarias. |
| `--text-on-dark` | `#FFFFFF` | Texto sobre morado. |
| `--text-default` | `#111827` | Texto sobre fondo claro (equivalente al negro del logotipo). |

Gradiente sugerido (hero / Streamlit cabecera): `#5a1f94` → `#7029B3` → `#8B5CF6`.

## Tipografía

Sans-serif neutra (**Inter**, **Source Sans 3** o sistema): negrita para títulos tipo “La Fe”, peso regular para “Seguros” y cuerpo.

## Pie legal (consistente con logo)

Texto corto para footers de Admin / Streamlit / Reflex (adaptar si Legal indica otro redactado):

- RIF **J-000467382** (confirmar formato con dígito verificador en material oficial del cliente).
- Inscripción **SUDEASEG N.º 62** (según pie de [seguroslafe.com/salud](https://seguroslafe.com/salud/) y logotipos).

## Terminología de producto (demo)

- **Plan de asistencia funeraria** / **asistencia funeraria** (no “seguro de muerte” en titulares de UI).
- Prestaciones alineadas al sitio: traslado, capilla, carroza, trámites, parcela, cremación, etc.
