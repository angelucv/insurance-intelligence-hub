"""Ingesta CSV/XLSX validada con Pydantic → PostgreSQL."""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
from contracts.policy import PolicyRow
from sqlalchemy import text
from sqlalchemy.orm import Session


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


def ingest_policies_bytes(
    session: Session,
    data: bytes,
    filename: str,
    *,
    source: str = "api",
) -> dict[str, Any]:
    buf = io.BytesIO(data)
    lower = filename.lower()
    if lower.endswith(".csv"):
        df = pd.read_csv(buf)
    elif lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(buf)
    else:
        raise ValueError("Formato no soportado (use .csv, .xlsx)")

    df = _normalize_columns(df)

    errors: list[dict[str, Any]] = []
    valid_rows: list[PolicyRow] = []
    for idx, row in df.iterrows():
        try:
            raw: dict[str, Any] = {
                "policy_id": row["policy_id"],
                "cohort_year": int(row["cohort_year"]),
                "issue_age": int(row["issue_age"]),
                "annual_premium": float(row["annual_premium"]),
                "status": row["status"],
            }
            if "issue_date" in df.columns:
                v = row["issue_date"]
                if pd.notna(v):
                    ts = pd.to_datetime(v, errors="coerce")
                    if pd.notna(ts):
                        raw["issue_date"] = ts.date()
        except (TypeError, ValueError) as e:
            errors.append({"row": int(idx) + 2, "error": f"celda inválida: {e}"})
            continue
        try:
            valid_rows.append(PolicyRow.model_validate(raw))
        except Exception as e:
            errors.append({"row": int(idx) + 2, "error": str(e)})

    batch_row = session.execute(
        text(
            """
            INSERT INTO upload_batches (source, filename, row_count, error_count)
            VALUES (:source, :filename, :row_count, :error_count)
            RETURNING id
            """
        ),
        {
            "source": source,
            "filename": filename[:512] if filename else None,
            "row_count": len(valid_rows),
            "error_count": len(errors),
        },
    )
    batch_id = batch_row.scalar_one()

    ins = text(
        """
        INSERT INTO policies (batch_id, policy_id, cohort_year, issue_age, annual_premium, status, issue_date)
        VALUES (:batch_id, :policy_id, :cohort_year, :issue_age, :annual_premium, :status, :issue_date)
        ON CONFLICT (policy_id) DO NOTHING
        """
    )
    inserted = 0
    skipped = 0
    for pr in valid_rows:
        res = session.execute(
            ins,
            {
                "batch_id": str(batch_id),
                "policy_id": pr.policy_id,
                "cohort_year": pr.cohort_year,
                "issue_age": pr.issue_age,
                "annual_premium": pr.annual_premium,
                "status": pr.status,
                "issue_date": pr.issue_date,
            },
        )
        if res.rowcount:
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
