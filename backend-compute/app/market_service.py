"""Consultas mercado SUDEASEG (tablas market_sudeaseg_*)."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

Mode = Literal["ytd", "monthly_flow"]


def sanitize_empresa_norm_fragment(s: str) -> str:
    t = re.sub(r"[^a-z0-9.\s]", "", s.lower().strip())[:60]
    return t or "fe c.a."


def _ratio(num: Decimal | None, den: Decimal | None) -> float | None:
    if num is None or den is None:
        return None
    if den == 0:
        return None
    return float(num / den)


def la_fe_resumen_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
    empresa_norm_fragment: str = "fe c.a.",
) -> list[dict[str, Any]]:
    """
    Serie La Fe desde market_sudeaseg_resumen_empresa.
    Filtra por nombre normalizado (fragmento + 'seguros').
    """
    frag = sanitize_empresa_norm_fragment(empresa_norm_fragment)

    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas,
                   siniestros_totales
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
        pat = f"%{frag}%"
    else:
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas_mes as primas_netas_cobradas,
                   siniestros_totales_mes as siniestros_totales
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
        pat = f"%{frag}%"

    rows = db.execute(sql, {"fy": from_year, "ty": to_year, "pat": pat}).mappings().all()
    out: list[dict[str, Any]] = []
    for r in rows:
        p = r["primas_netas_cobradas"]
        s = r["siniestros_totales"]
        p_d = Decimal(str(p)) if p is not None else None
        s_d = Decimal(str(s)) if s is not None else None
        out.append(
            {
                "period_year": int(r["period_year"]),
                "period_month": int(r["period_month"]),
                "primas_netas_thousands_bs": float(p_d) if p_d is not None else None,
                "siniestros_totales_thousands_bs": float(s_d) if s_d is not None else None,
                "loss_ratio_proxy": _ratio(s_d, p_d),
            }
        )
    return out


def market_resumen_totals_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
) -> list[dict[str, Any]]:
    """Suma todas las empresas por (año, mes) — referencia de mercado."""
    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas) as primas_netas_cobradas,
                   sum(siniestros_totales) as siniestros_totales
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )
    else:
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas_mes) as primas_netas_cobradas,
                   sum(siniestros_totales_mes) as siniestros_totales
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )

    rows = db.execute(sql, {"fy": from_year, "ty": to_year}).mappings().all()
    out: list[dict[str, Any]] = []
    for r in rows:
        p = r["primas_netas_cobradas"]
        s = r["siniestros_totales"]
        p_d = Decimal(str(p)) if p is not None else None
        s_d = Decimal(str(s)) if s is not None else None
        out.append(
            {
                "period_year": int(r["period_year"]),
                "period_month": int(r["period_month"]),
                "primas_netas_thousands_bs": float(p_d) if p_d is not None else None,
                "siniestros_totales_thousands_bs": float(s_d) if s_d is not None else None,
                "loss_ratio_proxy": _ratio(s_d, p_d),
            }
        )
    return out


def _dec(v: Any) -> Decimal | None:
    if v is None:
        return None
    return Decimal(str(v))


def _row_to_extended_dict(r: Any) -> dict[str, Any]:
    p = _dec(r["primas_netas_cobradas"])
    spag = _dec(r["siniestros_pagados"])
    rb = _dec(r["reservas_psp_brutas"])
    rn = _dec(r["reservas_psp_netas_reaseg"])
    st = _dec(r["siniestros_totales"])
    com = _dec(r["comisiones"])
    gaq = _dec(r["gastos_adquisicion"])
    gad = _dec(r["gastos_administracion"])
    return {
        "period_year": int(r["period_year"]),
        "period_month": int(r["period_month"]),
        "primas_netas_thousands_bs": float(p) if p is not None else None,
        "siniestros_pagados_thousands_bs": float(spag) if spag is not None else None,
        "reservas_psp_brutas_thousands_bs": float(rb) if rb is not None else None,
        "reservas_psp_netas_reaseg_thousands_bs": float(rn) if rn is not None else None,
        "siniestros_totales_thousands_bs": float(st) if st is not None else None,
        "comisiones_thousands_bs": float(com) if com is not None else None,
        "gastos_adquisicion_thousands_bs": float(gaq) if gaq is not None else None,
        "gastos_administracion_thousands_bs": float(gad) if gad is not None else None,
        "loss_ratio_proxy": _ratio(st, p),
        "comision_ratio_proxy": _ratio(com, p),
        "gasto_adm_ratio_proxy": _ratio(gad, p),
    }


def la_fe_resumen_extended_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
    empresa_norm_fragment: str = "fe c.a.",
) -> list[dict[str, Any]]:
    frag = sanitize_empresa_norm_fragment(empresa_norm_fragment)
    pat = f"%{frag}%"
    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas, siniestros_pagados, reservas_psp_brutas, reservas_psp_netas_reaseg,
                   siniestros_totales, comisiones, gastos_adquisicion, gastos_administracion
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
    else:
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas_mes as primas_netas_cobradas,
                   siniestros_pagados_mes as siniestros_pagados,
                   reservas_psp_brutas_mes as reservas_psp_brutas,
                   reservas_psp_netas_reaseg_mes as reservas_psp_netas_reaseg,
                   siniestros_totales_mes as siniestros_totales,
                   comisiones_mes as comisiones,
                   gastos_adquisicion_mes as gastos_adquisicion,
                   gastos_administracion_mes as gastos_administracion
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
    rows = db.execute(sql, {"fy": from_year, "ty": to_year, "pat": pat}).mappings().all()
    return [_row_to_extended_dict(r) for r in rows]


def market_resumen_totals_extended_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
) -> list[dict[str, Any]]:
    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas) as primas_netas_cobradas,
                   sum(siniestros_pagados) as siniestros_pagados,
                   sum(reservas_psp_brutas) as reservas_psp_brutas,
                   sum(reservas_psp_netas_reaseg) as reservas_psp_netas_reaseg,
                   sum(siniestros_totales) as siniestros_totales,
                   sum(comisiones) as comisiones,
                   sum(gastos_adquisicion) as gastos_adquisicion,
                   sum(gastos_administracion) as gastos_administracion
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )
    else:
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas_mes) as primas_netas_cobradas,
                   sum(siniestros_pagados_mes) as siniestros_pagados,
                   sum(reservas_psp_brutas_mes) as reservas_psp_brutas,
                   sum(reservas_psp_netas_reaseg_mes) as reservas_psp_netas_reaseg,
                   sum(siniestros_totales_mes) as siniestros_totales,
                   sum(comisiones_mes) as comisiones,
                   sum(gastos_adquisicion_mes) as gastos_adquisicion,
                   sum(gastos_administracion_mes) as gastos_administracion
            from public.market_sudeaseg_resumen_empresa
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )
    rows = db.execute(sql, {"fy": from_year, "ty": to_year}).mappings().all()
    return [_row_to_extended_dict(r) for r in rows]


def _row_to_cuadro_dict(r: Any) -> dict[str, Any]:
    p = _dec(r["primas_netas_cobradas"])
    rtb = _dec(r["resultado_tecnico_bruto"])
    rrc = _dec(r["resultado_reaseguro_cedido"])
    rtn = _dec(r["resultado_tecnico_neto"])
    rgg = _dec(r["resultado_gestion_general"])
    so = _dec(r["saldo_operaciones"])
    return {
        "period_year": int(r["period_year"]),
        "period_month": int(r["period_month"]),
        "primas_netas_thousands_bs": float(p) if p is not None else None,
        "resultado_tecnico_bruto_thousands_bs": float(rtb) if rtb is not None else None,
        "resultado_reaseguro_cedido_thousands_bs": float(rrc) if rrc is not None else None,
        "resultado_tecnico_neto_thousands_bs": float(rtn) if rtn is not None else None,
        "resultado_gestion_general_thousands_bs": float(rgg) if rgg is not None else None,
        "saldo_operaciones_thousands_bs": float(so) if so is not None else None,
    }


def la_fe_cuadro_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
    empresa_norm_fragment: str = "fe c.a.",
) -> list[dict[str, Any]]:
    frag = sanitize_empresa_norm_fragment(empresa_norm_fragment)
    pat = f"%{frag}%"
    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas, resultado_tecnico_bruto, resultado_reaseguro_cedido,
                   resultado_tecnico_neto, resultado_gestion_general, saldo_operaciones
            from public.market_sudeaseg_cuadro_resultados
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
    else:
        sql = text(
            """
            select period_year, period_month,
                   primas_netas_cobradas_mes as primas_netas_cobradas,
                   resultado_tecnico_bruto_mes as resultado_tecnico_bruto,
                   resultado_reaseguro_cedido_mes as resultado_reaseguro_cedido,
                   resultado_tecnico_neto_mes as resultado_tecnico_neto,
                   resultado_gestion_general_mes as resultado_gestion_general,
                   saldo_operaciones_mes as saldo_operaciones
            from public.market_sudeaseg_cuadro_resultados
            where period_year between :fy and :ty
              and empresa_nombre_norm like :pat
              and empresa_nombre_norm like '%seguros%'
            order by period_year, period_month
            """
        )
    rows = db.execute(sql, {"fy": from_year, "ty": to_year, "pat": pat}).mappings().all()
    return [_row_to_cuadro_dict(r) for r in rows]


def market_cuadro_totals_series(
    db: Session,
    *,
    from_year: int,
    to_year: int,
    mode: Mode,
) -> list[dict[str, Any]]:
    if mode == "ytd":
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas) as primas_netas_cobradas,
                   sum(resultado_tecnico_bruto) as resultado_tecnico_bruto,
                   sum(resultado_reaseguro_cedido) as resultado_reaseguro_cedido,
                   sum(resultado_tecnico_neto) as resultado_tecnico_neto,
                   sum(resultado_gestion_general) as resultado_gestion_general,
                   sum(saldo_operaciones) as saldo_operaciones
            from public.market_sudeaseg_cuadro_resultados
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )
    else:
        sql = text(
            """
            select period_year, period_month,
                   sum(primas_netas_cobradas_mes) as primas_netas_cobradas,
                   sum(resultado_tecnico_bruto_mes) as resultado_tecnico_bruto,
                   sum(resultado_reaseguro_cedido_mes) as resultado_reaseguro_cedido,
                   sum(resultado_tecnico_neto_mes) as resultado_tecnico_neto,
                   sum(resultado_gestion_general_mes) as resultado_gestion_general,
                   sum(saldo_operaciones_mes) as saldo_operaciones
            from public.market_sudeaseg_cuadro_resultados
            where period_year between :fy and :ty
            group by period_year, period_month
            order by period_year, period_month
            """
        )
    rows = db.execute(sql, {"fy": from_year, "ty": to_year}).mappings().all()
    return [_row_to_cuadro_dict(r) for r in rows]


def la_fe_market_snapshot_latest(
    db: Session,
    *,
    empresa_norm_fragment: str = "fe c.a.",
) -> dict[str, Any] | None:
    """Último (año, mes) con dato La Fe; YTD y ratios a ese cierre + totales mercado."""
    frag = sanitize_empresa_norm_fragment(empresa_norm_fragment)
    pat = f"%{frag}%"
    sql_lf = text(
        """
        select period_year, period_month,
               primas_netas_cobradas, siniestros_totales, siniestros_pagados,
               comisiones, gastos_administracion
        from public.market_sudeaseg_resumen_empresa
        where empresa_nombre_norm like :pat
          and empresa_nombre_norm like '%seguros%'
        order by period_year desc, period_month desc
        limit 1
        """
    )
    row = db.execute(sql_lf, {"pat": pat}).mappings().first()
    if not row:
        return None
    y, m = int(row["period_year"]), int(row["period_month"])
    p = _dec(row["primas_netas_cobradas"])
    st = _dec(row["siniestros_totales"])
    sp = _dec(row["siniestros_pagados"])
    com = _dec(row["comisiones"])
    gad = _dec(row["gastos_administracion"])

    sql_mk = text(
        """
        select coalesce(sum(primas_netas_cobradas), 0) as primas,
               coalesce(sum(siniestros_totales), 0) as sini
        from public.market_sudeaseg_resumen_empresa
        where period_year = :y and period_month = :m
        """
    )
    mk = db.execute(sql_mk, {"y": y, "m": m}).mappings().first()
    mp = _dec(mk["primas"]) if mk else None
    ms = _dec(mk["sini"]) if mk else None

    cuota: float | None = None
    if p is not None and mp is not None and mp != 0:
        cuota = float((p / mp) * Decimal("100"))

    note = (
        "empresa_nombre_norm LIKE '%…%' AND '%seguros%' (fragmento: "
        f"{frag!r}); YTD a cierre {y}-{m:02d}."
    )
    return {
        "period_year": y,
        "period_month": m,
        "la_fe": {
            "primas_ytd": float(p) if p is not None else None,
            "siniestros_totales_ytd": float(st) if st is not None else None,
            "siniestros_pagados_ytd": float(sp) if sp is not None else None,
            "comisiones_ytd": float(com) if com is not None else None,
            "gastos_admin_ytd": float(gad) if gad is not None else None,
            "loss_ratio_ytd": _ratio(st, p),
        },
        "mercado_total": {
            "primas_ytd": float(mp) if mp is not None else None,
            "siniestros_totales_ytd": float(ms) if ms is not None else None,
            "loss_ratio_ytd": _ratio(ms, mp),
        },
        "cuota_mercado_primas_pct": cuota,
        "empresa_filter_note": note,
    }
