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
    blocks = [
        ("suite-1", copy.SUITE_MD_BLOCK1, 0),
        ("suite-2", copy.SUITE_MD_BLOCK2, 1),
        ("suite-3", copy.SUITE_MD_BLOCK3, 2),
        ("suite-4", copy.SUITE_MD_BLOCK4, 3),
        ("suite-5", copy.SUITE_MD_BLOCK5, 4),
        ("suite-6", copy.SUITE_MD_BLOCK6, 5),
        ("suite-7", copy.SUITE_MD_BLOCK7, 6),
        ("suite-8", copy.SUITE_MD_BLOCK8, 7),
    ]
    return rx.fragment(*[_md_block(a, m, z) for a, m, z in blocks])


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
        _suite_infographics(),
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
