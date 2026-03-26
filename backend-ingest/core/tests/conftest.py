"""Esquema mínimo SQLite para probar ingest_service (Postgres en producción)."""

from __future__ import annotations

import pytest
from django.db import connection

_HUB_DDL = """
DROP TABLE IF EXISTS policy_claims;
DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS upload_batches;
CREATE TABLE upload_batches (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  source TEXT NOT NULL DEFAULT 'django',
  filename TEXT,
  row_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE policies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT REFERENCES upload_batches(id) ON DELETE SET NULL,
  policy_id TEXT NOT NULL UNIQUE,
  cohort_year INTEGER NOT NULL,
  issue_age INTEGER NOT NULL,
  annual_premium REAL NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CHECK (issue_age >= 0 AND issue_age <= 110),
  CHECK (annual_premium > 0),
  CHECK (status IN ('active', 'lapsed'))
);
CREATE TABLE policy_claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  batch_id TEXT REFERENCES upload_batches(id) ON DELETE SET NULL,
  claim_id TEXT NOT NULL UNIQUE,
  policy_id TEXT NOT NULL REFERENCES policies(policy_id),
  loss_date TEXT NOT NULL,
  reported_amount_bs REAL NOT NULL DEFAULT 0,
  paid_amount_bs REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  CHECK (status IN ('reported', 'adjusted', 'paid', 'closed', 'rejected')),
  CHECK (reported_amount_bs >= 0 AND paid_amount_bs >= 0)
);
"""


@pytest.fixture
def hub_schema(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.executescript(_HUB_DDL)
    yield
