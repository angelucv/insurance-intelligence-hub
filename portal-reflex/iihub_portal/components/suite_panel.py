"""Vista demo: presentación de la suite (lenguaje claro + infografías)."""

import reflex as rx

from iihub_portal import copy


def _responsive_figure(
    *,
    src: str,
    alt: str,
    heading: str | None = None,
    caption: str | None = None,
    bottom_border: bool = True,
) -> rx.Component:
    """Contenedor con scroll horizontal suave en pantallas estrechas (mapas anchos)."""
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
                    "text-sm text-gray-600 mt-3 max-w-4xl leading-relaxed "
                    "[&_strong]:font-semibold [&_strong]:text-gray-800"
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


def suite_panel() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            _responsive_figure(
                heading=copy.SUITE_MAP_HEADING,
                src="/infografia/suite-arquitectura-reflex.png",
                alt=copy.SUITE_MAP_ALT_REFLEX,
                caption=copy.SUITE_MAP_CAPTION_REFLEX,
                bottom_border=True,
            ),
            _responsive_figure(
                heading=copy.SUITE_COMPARISON_HEADING,
                src="/infografia/suite-comparativa-powerbi.png",
                alt=copy.SUITE_COMPARISON_ALT,
                caption=copy.SUITE_COMPARISON_CAPTION,
                bottom_border=True,
            ),
            _responsive_figure(
                heading=copy.SUITE_HEART_HEADING,
                src="/infografia/suite-corazon-proceso.png",
                alt=copy.SUITE_HEART_ALT,
                caption=copy.SUITE_HEART_CAPTION,
                bottom_border=True,
            ),
            rx.markdown(
                copy.SUITE_ARCHITECTURE_MD,
                class_name=(
                    "text-sm text-gray-700 leading-relaxed max-w-4xl "
                    "[&_h3]:text-base [&_h3]:font-semibold [&_h3]:text-gray-900 [&_h3]:mt-6 [&_h3]:mb-2 [&_h3]:first:mt-0 "
                    "[&_p]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mb-3 [&_li]:mb-1 "
                    "[&_table]:text-xs [&_table]:w-full [&_th]:text-left [&_th]:py-2 [&_td]:py-1.5 [&_tr]:border-b [&_tr]:border-gray-100 "
                    "[&_code]:text-xs [&_code]:bg-violet-50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded"
                ),
            ),
            class_name="rounded-2xl border border-gray-100 bg-white shadow-sm p-4 sm:p-8",
        ),
        class_name="w-full pb-8",
    )
