"""Vista demo: documentación de la suite (índice, modo resumen/completo, glosario)."""

import reflex as rx

from iihub_portal import copy
from iihub_portal.state import State

_MD_PROSE = (
    "text-sm text-gray-800 leading-relaxed max-w-4xl "
    "[&_h3]:text-base [&_h3]:font-semibold [&_h3]:text-gray-900 [&_h3]:mt-0 [&_h3]:mb-2 [&_h3]:scroll-mt-24 "
    "[&_p]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mb-3 [&_li]:mb-1 "
    "[&_table]:text-xs [&_table]:w-full [&_th]:text-left [&_th]:py-2 [&_th]:text-gray-900 [&_td]:py-1.5 "
    "[&_tr]:border-b [&_tr]:border-gray-100 "
    "[&_code]:text-xs [&_code]:bg-violet-50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded "
    "[&_strong]:text-gray-900 [&_a]:text-violet-700 [&_a]:underline"
)


def _responsive_figure(
    *,
    src: str,
    alt: str,
    heading: str | None = None,
    caption: str | None = None,
    bottom_border: bool = True,
    loading: str = "lazy",
) -> rx.Component:
    inner: list[rx.Component] = []
    if heading:
        inner.append(
            rx.el.h3(
                heading,
                class_name="text-base font-semibold text-gray-900 mb-2",
            )
        )
    inner.append(
        rx.el.div(
            rx.image(
                src=src,
                alt=alt,
                loading=loading,
                class_name="w-full min-w-0 max-h-[min(70vh,520px)] sm:max-h-none object-contain rounded-xl border border-gray-200 bg-slate-50/80 shadow-sm",
            ),
            class_name="w-full max-w-full overflow-x-auto overflow-y-hidden -mx-1 px-1 sm:mx-0 sm:px-0 [scrollbar-width:thin]",
        )
    )
    if caption:
        inner.append(
            rx.markdown(
                caption,
                class_name=(
                    "text-sm text-gray-700 mt-3 max-w-4xl leading-relaxed "
                    "[&_strong]:font-semibold [&_strong]:text-gray-900"
                ),
            )
        )
    return rx.el.div(
        *inner,
        class_name=(
            "mb-8 pb-6 "
            + ("border-b border-gray-100 " if bottom_border else "")
        ).strip(),
    )


def _suite_pair_section(
    anchor: str,
    heading: str,
    src: str,
    alt: str,
    body_md: str,
    zebra: int,
    loading: str = "lazy",
) -> rx.Component:
    """Una infografía y el texto relacionado, en dos columnas en pantallas anchas."""
    bg = (
        "rounded-xl p-4 sm:p-5 mb-4 border bg-slate-50/90 border-slate-100/90"
        if zebra % 2 == 0
        else "rounded-xl p-4 sm:p-5 mb-4 border bg-white border-gray-100/90"
    )
    return rx.el.div(
        rx.el.h3(
            heading,
            class_name="text-base font-semibold text-gray-900 mb-4 scroll-mt-24",
        ),
        rx.el.div(
            rx.el.div(
                rx.image(
                    src=src,
                    alt=alt,
                    loading=loading,
                    class_name=(
                        "w-full min-w-0 max-h-[min(55vh,440px)] xl:max-h-[min(72vh,560px)] "
                        "object-contain rounded-xl border border-gray-200 bg-slate-50/80 shadow-sm"
                    ),
                ),
                class_name="w-full overflow-x-auto [scrollbar-width:thin] xl:sticky xl:top-24",
            ),
            rx.markdown(body_md.strip(), class_name=_MD_PROSE + " min-w-0"),
            class_name="grid grid-cols-1 xl:grid-cols-2 gap-6 xl:gap-8 items-start",
        ),
        id=anchor,
        class_name=bg,
    )


def _md_block(anchor: str, md: str, zebra: int) -> rx.Component:
    bg = (
        "rounded-xl p-4 sm:p-5 mb-4 border bg-slate-50/90 border-slate-100/90"
        if zebra % 2 == 0
        else "rounded-xl p-4 sm:p-5 mb-4 border bg-white border-gray-100/90"
    )
    return rx.el.div(
        rx.markdown(md.strip(), class_name=_MD_PROSE),
        id=anchor,
        class_name=bg,
    )


def _suite_block3_with_figure() -> rx.Component:
    """Bloque Acsel/x–Rector con dos figuras: coexistencia con core y evolución sin core."""
    zebra = 3
    bg = (
        "rounded-xl p-4 sm:p-5 mb-4 border bg-slate-50/90 border-slate-100/90"
        if zebra % 2 == 0
        else "rounded-xl p-4 sm:p-5 mb-4 border bg-white border-gray-100/90"
    )
    img_cls = (
        "w-full min-w-0 max-h-[min(52vh,400px)] lg:max-h-[min(62vh,480px)] object-contain "
        "rounded-lg border border-gray-200 bg-white shadow-sm"
    )
    col = (
        "flex flex-col min-w-0 gap-2 p-2 sm:p-3 rounded-xl bg-white/60 border border-gray-100/90 "
    )
    return rx.el.div(
        rx.markdown(copy.SUITE_MD_BLOCK3.strip(), class_name=_MD_PROSE),
        rx.markdown(
            copy.SUITE_CORE_FIG_PAIR_INTRO.strip(),
            class_name=_MD_PROSE + " mt-5",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    copy.SUITE_CORE_FIG_COL_TITLE,
                    class_name="text-xs font-semibold text-gray-600 text-center mb-1",
                ),
                rx.el.div(
                    rx.image(
                        src="/infografia/suite-core-coexistencia.png",
                        alt=copy.SUITE_CORE_FIG_ALT,
                        loading="lazy",
                        class_name=img_cls,
                    ),
                    class_name="w-full overflow-x-auto [scrollbar-width:thin]",
                ),
                rx.markdown(
                    copy.SUITE_CORE_FIG_COL_CAPTION,
                    class_name=_MD_PROSE + " text-sm",
                ),
                class_name=col,
            ),
            rx.el.div(
                rx.el.p(
                    copy.SUITE_NO_CORE_FIG_COL_TITLE,
                    class_name="text-xs font-semibold text-gray-600 text-center mb-1",
                ),
                rx.el.div(
                    rx.image(
                        src="/infografia/suite-sin-core-evolucion.png",
                        alt=copy.SUITE_NO_CORE_FIG_ALT,
                        loading="lazy",
                        class_name=img_cls,
                    ),
                    class_name="w-full overflow-x-auto [scrollbar-width:thin]",
                ),
                rx.markdown(
                    copy.SUITE_NO_CORE_FIG_COL_CAPTION,
                    class_name=_MD_PROSE + " text-sm",
                ),
                class_name=col,
            ),
            class_name=(
                "mt-4 grid grid-cols-1 lg:grid-cols-2 gap-5 lg:gap-6 "
                "items-stretch w-full"
            ),
        ),
        id="suite-cores",
        class_name=bg,
    )


def _suite_toc() -> rx.Component:
    links: list[rx.Component] = []
    for anchor, label in copy.SUITE_TOC_ENTRIES:
        links.append(
            rx.link(
                label,
                href=f"#{anchor}",
                class_name=(
                    "text-sm text-violet-700 hover:text-violet-900 underline underline-offset-2 "
                    "decoration-violet-300"
                ),
            )
        )
    return rx.el.nav(
        rx.el.p(
            copy.SUITE_UI_TOC_TITLE,
            class_name="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2",
        ),
        rx.hstack(
            *links,
            spacing="3",
            flex_wrap="wrap",
            align_items="center",
        ),
        class_name="mb-6 p-3 rounded-xl bg-violet-50/50 border border-violet-100/80",
        aria_label=copy.SUITE_UI_TOC_TITLE,
    )


def _suite_glossary() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            copy.SUITE_UI_GLOSSARY_TITLE,
            class_name="text-sm font-semibold text-gray-900 mb-2",
        ),
        rx.markdown(copy.SUITE_GLOSSARY_MD.strip(), class_name=_MD_PROSE),
        class_name="mt-8 pt-6 border-t border-gray-200",
    )


def _suite_infographics() -> rx.Component:
    return rx.fragment(
        _responsive_figure(
            heading=copy.SUITE_MAP_HEADING,
            src="/infografia/suite-arquitectura-reflex.png",
            alt=copy.SUITE_MAP_ALT_REFLEX,
            caption=copy.SUITE_MAP_CAPTION_REFLEX,
            bottom_border=True,
            loading="eager",
        ),
        _responsive_figure(
            heading=copy.SUITE_COMPARISON_HEADING,
            src="/infografia/suite-comparativa-powerbi.png",
            alt=copy.SUITE_COMPARISON_ALT,
            caption=copy.SUITE_COMPARISON_CAPTION,
            bottom_border=True,
            loading="lazy",
        ),
        _responsive_figure(
            heading=copy.SUITE_HEART_HEADING,
            src="/infografia/suite-corazon-proceso.png",
            alt=copy.SUITE_HEART_ALT,
            caption=copy.SUITE_HEART_CAPTION,
            bottom_border=True,
            loading="lazy",
        ),
    )


def _suite_doc_blocks_full() -> rx.Component:
    """Documentación completa: cada infografía principal va con su texto; luego cores y roles."""
    return rx.fragment(
        _suite_pair_section(
            "suite-1",
            copy.SUITE_MAP_HEADING,
            "/infografia/suite-arquitectura-reflex.png",
            copy.SUITE_MAP_ALT_REFLEX,
            copy.SUITE_PAIR1_MD,
            0,
            loading="eager",
        ),
        _suite_pair_section(
            "suite-2",
            copy.SUITE_COMPARISON_HEADING,
            "/infografia/suite-comparativa-powerbi.png",
            copy.SUITE_COMPARISON_ALT,
            copy.SUITE_MD_BLOCK7,
            1,
            loading="lazy",
        ),
        _suite_pair_section(
            "suite-3",
            copy.SUITE_HEART_HEADING,
            "/infografia/suite-corazon-proceso.png",
            copy.SUITE_HEART_ALT,
            copy.SUITE_PAIR3_MD,
            2,
            loading="lazy",
        ),
        _suite_block3_with_figure(),
        _md_block("suite-roles", copy.SUITE_MD_BLOCK8, 4),
    )


def _suite_toolbar() -> rx.Component:
    return rx.hstack(
        rx.button(
            copy.SUITE_UI_DOCS_SUMMARY,
            on_click=State.set_suite_docs_summary,
            size="2",
            variant="outline",
            color_scheme="gray",
            class_name=rx.cond(
                State.suite_docs_mode == "summary",
                "border-violet-500 text-violet-800 bg-violet-50",
                "",
            ),
        ),
        rx.button(
            copy.SUITE_UI_DOCS_FULL,
            on_click=State.set_suite_docs_full,
            size="2",
            variant="outline",
            color_scheme="gray",
            class_name=rx.cond(
                State.suite_docs_mode == "full",
                "border-violet-500 text-violet-800 bg-violet-50",
                "",
            ),
        ),
        spacing="3",
        class_name="mb-6 flex-wrap",
    )


def suite_panel() -> rx.Component:
    summary_column = rx.el.div(
        _suite_toolbar(),
        _suite_infographics(),
        rx.markdown(
            copy.SUITE_PRESENTATION_SUMMARY_MD.strip(),
            class_name=_MD_PROSE,
        ),
        _suite_glossary(),
        class_name="space-y-0",
    )

    full_column = rx.el.div(
        _suite_toolbar(),
        _suite_toc(),
        _suite_doc_blocks_full(),
        _suite_glossary(),
        class_name="space-y-0",
    )

    return rx.el.section(
        rx.el.div(
            rx.cond(State.suite_docs_mode == "summary", summary_column, full_column),
            class_name="rounded-2xl border border-gray-100 bg-white shadow-sm p-4 sm:p-8",
        ),
        class_name="w-full pb-8",
    )
