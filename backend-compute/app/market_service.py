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
