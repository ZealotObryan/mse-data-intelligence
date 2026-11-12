"""DB-API persistence for reviewed price CSV staging results.

Accepts a psycopg-compatible PostgreSQL connection. The caller owns connection
creation and credentials. All writes happen in one transaction; no database
connection is opened at import time.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

import pandas as pd

from mse_analytics.staging import PriceCsvStageResult


class CursorLike(Protocol):
    def execute(self, query: str, params: Sequence[Any] | None = None) -> Any: ...
    def fetchone(self) -> Any: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def transaction(self) -> Any: ...


@dataclass(frozen=True)
class PersistenceResult:
    dataset_id: str
    ingestion_id: int
    rows_received: int
    rows_persisted: int
    validation_issues_persisted: int
    publication_status: str


def persist_price_stage(
    connection: ConnectionLike,
    result: PriceCsvStageResult,
    *,
    source_key: str,
    source_class: str,
    permission_status: str,
    source_url: str | None = None,
    licence_name: str | None = None,
    licence_reference: str | None = None,
    attribution_text: str | None = None,
    terms_reviewed_at: Any = None,
) -> PersistenceResult:
    """Persist one staged price CSV and its audit trail atomically.

    Instruments must already exist in the instruments registry. The database
    migration's publication trigger remains the final permission authority.
    """
    provenance = result.provenance
    ingestion = result.ingestion
    quality = result.quality
    if not source_key.strip():
        raise ValueError("source_key must be non-empty")
    if permission_status not in {"unknown", "pending_review", "approved", "restricted", "revoked"}:
        raise ValueError("invalid source permission_status")

    publication_status = (
        "approved_public" if result.publication_allowed and quality.status == "passed"
        else "internal_only" if quality.status in {"passed", "warning"}
        else "blocked"
    )
    rows_persisted = 0
    issue_count = len(quality.issues)

    # psycopg's transaction context commits on success and rolls back on error.
    with connection.transaction():
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO data_sources (
                    source_key, source_name, source_url, source_class, licence_name,
                    licence_reference, permission_status, permitted_uses,
                    redistribution_allowed, attribution_text, terms_reviewed_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (source_key) DO UPDATE SET
                    source_name=EXCLUDED.source_name,
                    source_url=EXCLUDED.source_url,
                    source_class=EXCLUDED.source_class,
                    licence_name=EXCLUDED.licence_name,
                    licence_reference=EXCLUDED.licence_reference,
                    permission_status=EXCLUDED.permission_status,
                    permitted_uses=EXCLUDED.permitted_uses,
                    redistribution_allowed=EXCLUDED.redistribution_allowed,
                    attribution_text=EXCLUDED.attribution_text,
                    terms_reviewed_at=EXCLUDED.terms_reviewed_at
                RETURNING source_id
                """,
                (
                    source_key, provenance.source_name, source_url or provenance.source_url, source_class,
                    licence_name or provenance.licence_name, licence_reference or provenance.licence_reference, permission_status,
                    list(provenance.permitted_uses),
                    getattr(provenance, "redistribution_allowed", None),
                    attribution_text, terms_reviewed_at,
                ),
            )
            source_row = cursor.fetchone()
            if not source_row:
                raise RuntimeError("database did not return source_id")
            source_id = source_row[0]

            cursor.execute(
                """
                INSERT INTO datasets (
                    dataset_id, source_id, dataset_name, data_class, source_document_id,
                    published_at, collected_at, coverage_start, coverage_end,
                    validation_status, publication_status, permitted_uses,
                    redistribution_allowed, attribution_text, collector_version,
                    checksum_sha256, notes
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (dataset_id) DO UPDATE SET
                    source_id=EXCLUDED.source_id,
                    dataset_name=EXCLUDED.dataset_name,
                    validation_status=EXCLUDED.validation_status,
                    publication_status=EXCLUDED.publication_status,
                    checksum_sha256=EXCLUDED.checksum_sha256,
                    notes=EXCLUDED.notes
                """,
                (
                    provenance.dataset_id, source_id, provenance.dataset_name,
                    provenance.data_class.value, provenance.source_document_id,
                    provenance.published_at, provenance.collected_at,
                    provenance.coverage_start, provenance.coverage_end,
                    provenance.validation_status.value, publication_status,
                    list(provenance.permitted_uses),
                    getattr(provenance, "redistribution_allowed", None),
                    getattr(provenance, "attribution_text", None),
                    ingestion.parser_version, ingestion.checksum_sha256,
                    result.publication_reason,
                ),
            )

            cursor.execute(
                """
                INSERT INTO ingestion_runs (
                    dataset_id, source_name, completed_at, run_status, parser_version,
                    checksum_sha256, artifact_uri, original_filename, bytes_received,
                    rows_received, rows_accepted, rows_rejected, error_summary
                ) VALUES (%s,%s,now(),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (dataset_id, checksum_sha256) DO UPDATE SET
                    completed_at=EXCLUDED.completed_at,
                    run_status=EXCLUDED.run_status,
                    rows_received=EXCLUDED.rows_received,
                    rows_accepted=EXCLUDED.rows_accepted,
                    rows_rejected=EXCLUDED.rows_rejected,
                    error_summary=EXCLUDED.error_summary
                RETURNING ingestion_id
                """,
                (
                    ingestion.dataset_id, ingestion.source_name,
                    "succeeded" if quality.status == "passed" else
                    "warning" if quality.status == "warning" else "rejected",
                    ingestion.parser_version, ingestion.checksum_sha256,
                    ingestion.archive_path, ingestion.original_filename,
                    ingestion.bytes_received, quality.rows_received,
                    quality.rows_checked if quality.status != "rejected" else 0,
                    max(0, quality.rows_received - quality.rows_checked),
                    "; ".join(issue.message for issue in quality.issues) or None,
                ),
            )
            ingestion_row = cursor.fetchone()
            if not ingestion_row:
                raise RuntimeError("database did not return ingestion_id")
            ingestion_id = ingestion_row[0]

            cursor.execute("DELETE FROM validation_issues WHERE ingestion_id = %s", (ingestion_id,))
            for issue in quality.issues:
                locators = issue.row_indices or (None,)
                for locator in locators:
                    cursor.execute(
                        """
                        INSERT INTO validation_issues
                            (ingestion_id, severity, issue_code, message, row_locator)
                        VALUES (%s,%s,%s,%s,%s)
                        """,
                        (ingestion_id, issue.severity, issue.code, issue.message,
                         None if locator is None else str(locator)),
                    )

            if quality.status == "passed":
                frame = pd.read_csv(ingestion.archive_path)
                for row in frame.itertuples(index=False):
                    values = row._asdict()
                    cursor.execute(
                        """
                        INSERT INTO market_observations (
                            dataset_id, ingestion_id, instrument_id, observation_date,
                            metric_key, numeric_value, currency, validation_status
                        ) VALUES (%s,%s,%s,%s,'price',%s,%s,'passed')
                        ON CONFLICT (dataset_id, instrument_id, observation_date, metric_key)
                        DO UPDATE SET
                            ingestion_id=EXCLUDED.ingestion_id,
                            numeric_value=EXCLUDED.numeric_value,
                            currency=EXCLUDED.currency,
                            validation_status='passed'
                        """,
                        (
                            provenance.dataset_id, ingestion_id,
                            str(values["instrument_id"]),
                            pd.Timestamp(values["observation_date"]).date(),
                            float(values["price"]), str(values["currency"]).upper(),
                        ),
                    )
                    rows_persisted += 1

    return PersistenceResult(
        dataset_id=provenance.dataset_id,
        ingestion_id=ingestion_id,
        rows_received=quality.rows_received,
        rows_persisted=rows_persisted,
        validation_issues_persisted=issue_count,
        publication_status=publication_status,
    )
