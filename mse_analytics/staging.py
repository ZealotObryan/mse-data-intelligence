"""Controlled CSV staging workflow for price observations.

The workflow preserves every received source artifact, validates a parsed copy,
and evaluates publication permission. It deliberately does not publish data or
write to a production database.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from mse_analytics.data_quality import QualityReport, validate_price_observations
from mse_analytics.ingestion import IngestionRecord, archive_source_artifact
from mse_analytics.provenance import DatasetProvenance, publication_decision


@dataclass(frozen=True)
class PriceCsvStageResult:
    ingestion: IngestionRecord
    provenance: DatasetProvenance
    quality: QualityReport
    publication_allowed: bool
    publication_reason: str


def stage_price_csv(
    source_path: str | Path,
    archive_dir: str | Path,
    manifest_path: str | Path,
    *,
    provenance: Mapping[str, Any],
    parser_version: str = "price-csv-v1",
) -> PriceCsvStageResult:
    """Archive, parse, validate and permission-check one price CSV file.

    The original bytes are archived before parsing so malformed files remain
    available for audit. A dataset is never automatically inserted into a
    database or exposed publicly by this function.
    """
    metadata = dict(provenance)
    for field in ("dataset_id", "source_name"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise ValueError(f"provenance.{field} must be a non-empty string")

    ingestion = archive_source_artifact(
        source_path,
        archive_dir,
        manifest_path,
        dataset_id=metadata["dataset_id"],
        source_name=metadata["source_name"],
        parser_version=parser_version,
    )

    supplied_checksum = metadata.get("checksum")
    if supplied_checksum is not None and supplied_checksum != ingestion.checksum_sha256:
        raise ValueError("provenance checksum does not match the archived source artifact")
    metadata["checksum"] = ingestion.checksum_sha256

    frame = pd.read_csv(source_path)
    quality = validate_price_observations(frame)
    metadata["validation_status"] = quality.status
    parsed_provenance = DatasetProvenance.from_mapping(metadata)
    allowed, reason = publication_decision(parsed_provenance)

    return PriceCsvStageResult(
        ingestion=ingestion,
        provenance=parsed_provenance,
        quality=quality,
        publication_allowed=allowed,
        publication_reason=reason,
    )
