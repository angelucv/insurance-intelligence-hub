"""Ingesta CSV/XLSX → PostgreSQL con validación hub-contracts (Pydantic)."""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
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
