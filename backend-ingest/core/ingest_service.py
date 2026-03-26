"""Ingesta CSV/XLSX → PostgreSQL con validación hub-contracts (Pydantic)."""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
from contracts.claim import ClaimRow
from contracts.policy import PolicyRow
from django.db import connection, transaction


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").removeprefix("\ufeff")
        for c in df.columns
    ]
    required = {"policy_id", "cohort_year", "issue_age", "annual_premium", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    return df


def _read_dataframe(data: bytes, filename: str) -> pd.DataFrame:
    buf = io.BytesIO(data)
    lower = (filename or "").lower()
    if lower.endswith(".csv"):
        return pd.read_csv(buf)
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(buf)
    raise ValueError("Formato no soportado (use .csv, .xlsx, .xls)")


def ingest_policies_file(
    data: bytes,
    filename: str,
    *,
    source: str = "django",
) -> dict[str, Any]:
    df = _read_dataframe(data, filename)
    df = _normalize_columns(df)

    errors: list[dict[str, Any]] = []
    valid_rows: list[PolicyRow] = []
    for idx, row in df.iterrows():
        try:
            raw = {
                "policy_id": row["policy_id"],
                "cohort_year": int(row["cohort_year"]),
                "issue_age": int(row["issue_age"]),
                "annual_premium": float(row["annual_premium"]),
                "status": row["status"],
            }
        except (TypeError, ValueError) as e:
            errors.append({"row": int(idx) + 2, "error": f"celda inválida: {e}"})
            continue
        try:
            valid_rows.append(PolicyRow.model_validate(raw))
        except Exception as e:
            errors.append({"row": int(idx) + 2, "error": str(e)})

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO upload_batches (source, filename, row_count, error_count)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                [
                    source,
                    (filename or "")[:512] or None,
                    len(valid_rows),
                    len(errors),
                ],
            )
            row = cursor.fetchone()
            if not row:
                raise RuntimeError("No se pudo registrar el lote de carga.")
            batch_id = row[0]

            ins = """
                INSERT INTO policies (batch_id, policy_id, cohort_year, issue_age, annual_premium, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (policy_id) DO NOTHING
            """
            inserted = 0
            skipped = 0
            for pr in valid_rows:
                cursor.execute(
                    ins,
                    [
                        batch_id,
                        pr.policy_id,
                        pr.cohort_year,
                        pr.issue_age,
                        pr.annual_premium,
                        pr.status,
                    ],
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1

    return {
        "batch_id": str(batch_id),
        "rows_valid": len(valid_rows),
        "inserted": inserted,
        "skipped_duplicate_policy_id": skipped,
        "errors": errors[:50],
        "error_truncated": len(errors) > 50,
    }


def _normalize_claim_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").removeprefix("\ufeff")
        for c in df.columns
    ]
    required = {"claim_id", "policy_id", "loss_date", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    if "reported_amount_bs" not in df.columns:
        df["reported_amount_bs"] = 0.0
    if "paid_amount_bs" not in df.columns:
        df["paid_amount_bs"] = 0.0
    return df


def _cell_to_date(val: object) -> Any:
    import datetime as dt

    if val is None or (isinstance(val, float) and pd.isna(val)):
        raise ValueError("fecha vacía")
    if isinstance(val, dt.datetime):
        return val.date()
    if isinstance(val, dt.date):
        return val
    if hasattr(val, "to_pydatetime"):
        return val.to_pydatetime().date()
    if isinstance(val, str):
        return dt.datetime.fromisoformat(val.strip()[:10]).date()
    raise ValueError(f"fecha no reconocida: {val!r}")


def ingest_claims_file(
    data: bytes,
    filename: str,
    *,
    source: str = "django",
) -> dict[str, Any]:
    df = _read_dataframe(data, filename)
    df = _normalize_claim_columns(df)

    errors: list[dict[str, Any]] = []
    validated: list[tuple[int, ClaimRow]] = []
    for idx, row in df.iterrows():
        excel_row = int(idx) + 2
        try:
            ld = _cell_to_date(row["loss_date"])
            raw = {
                "claim_id": row["claim_id"],
                "policy_id": row["policy_id"],
                "loss_date": ld,
                "reported_amount_bs": float(row["reported_amount_bs"] or 0),
                "paid_amount_bs": float(row["paid_amount_bs"] or 0),
                "status": row["status"],
            }
        except (TypeError, ValueError) as e:
            errors.append({"row": excel_row, "error": f"celda inválida: {e}"})
            continue
        try:
            validated.append((excel_row, ClaimRow.model_validate(raw)))
        except Exception as e:
            errors.append({"row": excel_row, "error": str(e)})

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO upload_batches (source, filename, row_count, error_count)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                [
                    source,
                    (filename or "")[:512] or None,
                    len(validated),
                    len(errors),
                ],
            )
            row0 = cursor.fetchone()
            if not row0:
                raise RuntimeError("No se pudo registrar el lote de carga.")
            batch_id = row0[0]

            ins = """
                INSERT INTO policy_claims (batch_id, claim_id, policy_id, loss_date, reported_amount_bs, paid_amount_bs, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (claim_id) DO NOTHING
            """
            inserted = 0
            skipped = 0
            for excel_row, cr in validated:
                cursor.execute(
                    "SELECT 1 FROM policies WHERE policy_id = %s LIMIT 1",
                    [cr.policy_id],
                )
                if not cursor.fetchone():
                    errors.append(
                        {
                            "row": excel_row,
                            "error": f"policy_id {cr.policy_id!r} no existe en policies",
                        }
                    )
                    continue
                cursor.execute(
                    ins,
                    [
                        batch_id,
                        cr.claim_id,
                        cr.policy_id,
                        cr.loss_date,
                        cr.reported_amount_bs,
                        cr.paid_amount_bs,
                        cr.status,
                    ],
                )
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1

    return {
        "batch_id": str(batch_id),
        "rows_valid": len(validated),
        "inserted": inserted,
        "skipped_duplicate_or_invalid": skipped,
        "errors": errors[:50],
        "error_truncated": len(errors) > 50,
    }
