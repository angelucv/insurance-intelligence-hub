"""Tests de validación e ingesta (SQLite en CI; Postgres en despliegue)."""

from __future__ import annotations

from pathlib import Path

import pytest
from contracts.policy import PolicyRow
from django.db import connection

from core.ingest_service import _normalize_columns, _read_dataframe, ingest_policies_file

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_CSV = REPO_ROOT / "docs" / "sample-policies.csv"


def test_sample_csv_parses_and_validates_all_rows():
    raw = SAMPLE_CSV.read_bytes()
    df = _normalize_columns(_read_dataframe(raw, "sample-policies.csv"))
    valid: list[PolicyRow] = []
    for _, row in df.iterrows():
        r = {
            "policy_id": row["policy_id"],
            "cohort_year": int(row["cohort_year"]),
            "issue_age": int(row["issue_age"]),
            "annual_premium": float(row["annual_premium"]),
            "status": row["status"],
        }
        valid.append(PolicyRow.model_validate(r))
    assert len(valid) == 5
    assert {v.policy_id for v in valid} == {
        "DEMO-001",
        "DEMO-002",
        "DEMO-003",
        "DEMO-004",
        "DEMO-005",
    }


def test_normalize_columns_missing_required_raises():
    import pandas as pd

    df = pd.DataFrame({"policy_id": ["x"], "cohort_year": [2022]})
    with pytest.raises(ValueError, match="Faltan columnas"):
        _normalize_columns(df)


@pytest.mark.django_db
def test_ingest_inserts_rows(hub_schema):
    raw = SAMPLE_CSV.read_bytes()
    out = ingest_policies_file(raw, "sample-policies.csv", source="django")
    assert out["rows_valid"] == 5
    assert out["inserted"] == 5
    assert out["skipped_duplicate_policy_id"] == 0
    assert out["errors"] == []
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM policies")
        assert cursor.fetchone()[0] == 5


@pytest.mark.django_db
def test_ingest_second_upload_skips_duplicates(hub_schema):
    raw = SAMPLE_CSV.read_bytes()
    ingest_policies_file(raw, "sample-policies.csv", source="django")
    out2 = ingest_policies_file(raw, "sample-policies.csv", source="django")
    assert out2["inserted"] == 0
    assert out2["skipped_duplicate_policy_id"] == 5
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM policies")
        assert cursor.fetchone()[0] == 5
