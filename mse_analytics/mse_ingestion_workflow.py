"""Controlled, operator-assisted MSE CSV ingestion workflow.

This workflow accepts a file supplied by an operator. It does not download,
scrape, publish, or write to a database. Permission metadata is evaluated by
the existing provenance gate; unknown or restricted permissions block public
eligibility.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping

from mse_analytics.staging import stage_price_csv


def run_controlled_ingestion(
    source_path: str | Path,
    *,
    archive_dir: str | Path,
    manifest_path: str | Path,
    provenance_path: str | Path,
    report_path: str | Path,
) -> dict[str, Any]:
    """Archive and validate an operator-provided CSV, then write a report.

    Metadata is loaded from a JSON file, so source permission decisions are
    reviewable and auditable. The report intentionally excludes data rows.
    """
    metadata_file = Path(provenance_path)
    with metadata_file.open("r", encoding="utf-8") as stream:
        metadata = json.load(stream)
    if not isinstance(metadata, dict):
        raise ValueError("provenance JSON must contain an object")

    result = stage_price_csv(
        source_path,
        archive_dir,
        manifest_path,
        provenance=metadata,
        parser_version="controlled-mse-csv-v1",
    )

    report: dict[str, Any] = {
        "workflow": "controlled_operator_csv_ingestion",
        "source_filename": result.ingestion.original_filename,
        "dataset_id": result.ingestion.dataset_id,
        "checksum_sha256": result.ingestion.checksum_sha256,
        "bytes_received": result.ingestion.bytes_received,
        "collected_at": result.ingestion.collected_at,
        "parser_version": result.ingestion.parser_version,
        "validation": {
            "status": result.quality.status,
            "rows_received": result.quality.rows_received,
            "rows_checked": result.quality.rows_checked,
            "issues": [asdict(issue) for issue in result.quality.issues],
        },
        "permission": {
            "data_class": result.provenance.data_class.value,
            "redistribution_allowed": result.provenance.redistribution_allowed,
            "permitted_uses": list(result.provenance.permitted_uses),
            "publication_allowed": result.publication_allowed,
            "decision": result.publication_reason,
        },
        "publication_status": "eligible_for_review" if result.publication_allowed else "blocked",
        "note": "This workflow stages and validates only; it never publishes or writes to a database.",
    }

    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive, validate and permission-check an operator-provided market CSV."
    )
    parser.add_argument("--source", required=True, help="Path to the supplied CSV file")
    parser.add_argument("--provenance", required=True, help="JSON provenance/permission metadata")
    parser.add_argument("--archive", required=True, help="Private archive directory")
    parser.add_argument("--manifest", required=True, help="Append-only ingestion JSONL manifest")
    parser.add_argument("--report", required=True, help="Output validation report JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        report = run_controlled_ingestion(
            args.source,
            archive_dir=args.archive,
            manifest_path=args.manifest,
            provenance_path=args.provenance,
            report_path=args.report,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Ingestion failed: {exc}")
        return 2

    print(json.dumps({
        "dataset_id": report["dataset_id"],
        "checksum_sha256": report["checksum_sha256"],
        "validation_status": report["validation"]["status"],
        "publication_status": report["publication_status"],
        "report_path": str(args.report),
    }, indent=2))
    return 0 if report["validation"]["status"] == "passed" else 3


if __name__ == "__main__":
    raise SystemExit(main())
