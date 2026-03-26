"""Vista demo: explicación del ecosistema IIHub (documentación en pantalla)."""

import reflex as rx

from iihub_portal import copy


def suite_panel() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    copy.SUITE_MAP_HEADING,
                    class_name="text-base font-semibold text-gray-900 mb-2",
                ),
                rx.image(
                    src="/infografia/suite-arquitectura-reflex.png",
                    alt=copy.SUITE_MAP_ALT_REFLEX,
                    class_name=(
                        "w-full max-w-4xl rounded-xl border border-gray-200 "
                        "bg-slate-50/80 shadow-sm object-contain"
                    ),
                ),
                rx.el.p(
                    copy.SUITE_MAP_CAPTION_REFLEX,
                    class_name="text-sm text-gray-600 mt-3 max-w-4xl leading-relaxed",
                ),
                class_name="mb-8 pb-6 border-b border-gray-100",
            ),
            rx.markdown(
                copy.SUITE_ARCHITECTURE_MD,
                class_name=(
                    "text-sm text-gray-700 leading-relaxed max-w-4xl "
                    "[&_h3]:text-base [&_h3]:font-semibold [&_h3]:text-gray-900 [&_h3]:mt-6 [&_h3]:mb-2 [&_h3]:first:mt-0 "
                    "[&_p]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:mb-3 [&_li]:mb-1 "
                    "[&_table]:text-xs [&_table]:w-full [&_th]:text-left [&_th]:py-2 [&_td]:py-1.5 [&_tr]:border-b [&_tr]:border-gray-100 "
                    "[&_code]:text-xs [&_code]:bg-violet-50 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_pre]:bg-slate-900 [&_pre]:text-slate-100 [&_pre]:p-4 [&_pre]:rounded-xl [&_pre]:overflow-x-auto [&_pre]:text-xs"
                ),
            ),
            class_name="rounded-2xl border border-gray-100 bg-white shadow-sm p-5 sm:p-8",
        ),
        class_name="w-full pb-8",
    )
