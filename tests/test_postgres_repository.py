from __future__ import annotations

from contextlib import contextmanager

import pandas as pd
import pytest

from mse_analytics.postgres_repository import persist_price_stage
from mse_analytics.staging import stage_price_csv


class FakeCursor:
    def __init__(self):
        self.statements = []
        self.returned = None
        self._returning = iter([(11,), (22,)])
    def execute(self, query, params=None):
        self.statements.append((query, params))
        if "RETURNING source_id" in query:
            self.returned = (11,)
        elif "RETURNING ingestion_id" in query:
            self.returned = (22,)
        else:
            self.returned = None
    def fetchone(self):
        return self.returned


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.committed = False
        self.rolled_back = False
    @contextmanager
    def transaction(self):
        try:
            yield
            self.committed = True
        except Exception:
            self.rolled_back = True
            raise
    @contextmanager
    def cursor(self):
        yield self.fake_cursor


def make_stage(tmp_path, *, invalid=False):
    source = tmp_path / "prices.csv"
    frame = pd.DataFrame({
        "instrument_id": ["DEMO-001"],
        "observation_date": ["2026-01-02"],
        "price": [-2 if invalid else 100],
        "currency": ["MWK"],
    })
    frame.to_csv(source, index=False)
    provenance = {
        "dataset_id": "demo-prices-v1",
        "dataset_name": "Illustrative prices",
        "data_class": "synthetic_demo",
        "source_name": "Internal synthetic data generator",
        "collected_at": "2026-11-12T08:00:00+02:00",
        "validation_status": "pending",
        "permitted_uses": ["public_display"],
        "redistribution_allowed": True,
    }
    return stage_price_csv(
        source, tmp_path / "archive", tmp_path / "manifest.jsonl",
        provenance=provenance,
    )


def test_persist_stage_records_source_dataset_ingestion_and_observation(tmp_path):
    result = make_stage(tmp_path)
    connection = FakeConnection()

    persisted = persist_price_stage(
        connection, result, source_key="synthetic-generator-v1",
        source_class="synthetic_demo", permission_status="approved",
    )

    sql = "\n".join(query for query, _ in connection.fake_cursor.statements)
    assert persisted.dataset_id == "demo-prices-v1"
    assert persisted.ingestion_id == 22
    assert persisted.rows_received == 1
    assert persisted.rows_persisted == 1
    assert persisted.validation_issues_persisted == 0
    assert persisted.publication_status == "approved_public"
    assert "INSERT INTO data_sources" in sql
    assert "INSERT INTO datasets" in sql
    assert "INSERT INTO ingestion_runs" in sql
    assert "INSERT INTO market_observations" in sql
    assert connection.committed is True


def test_rejected_stage_persists_audit_trail_without_observations(tmp_path):
    result = make_stage(tmp_path, invalid=True)
    connection = FakeConnection()

    persisted = persist_price_stage(
        connection, result, source_key="synthetic-generator-v1",
        source_class="synthetic_demo", permission_status="approved",
    )

    sql = "\n".join(query for query, _ in connection.fake_cursor.statements)
    assert persisted.publication_status == "blocked"
    assert persisted.rows_persisted == 0
    assert "INSERT INTO validation_issues" in sql
    assert "INSERT INTO market_observations" not in sql
    assert connection.committed is True


def test_invalid_permission_status_is_rejected_before_database_write(tmp_path):
    result = make_stage(tmp_path)
    connection = FakeConnection()
    with pytest.raises(ValueError, match="permission_status"):
        persist_price_stage(
            connection, result, source_key="synthetic-generator-v1",
            source_class="synthetic_demo", permission_status="public",
        )
    assert connection.fake_cursor.statements == []
