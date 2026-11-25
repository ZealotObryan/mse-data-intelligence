import json
from pathlib import Path

import pandas as pd
import pytest

from mse_analytics.mse_ingestion_workflow import run_controlled_ingestion


def provenance(**overrides):
    data = {
        "dataset_id": "mse-report-pilot-001",
        "dataset_name": "Operator-provided market report pilot",
        "data_class": "official_public",
        "source_name": "Malawi Stock Exchange",
        "source_url": "https://mse.co.mw/market/reports",
        "collected_at": "2026-11-25T09:00:00+02:00",
        "validation_status": "pending",
        "licence_name": "Permission pending",
        "redistribution_allowed": None,
        "permitted_uses": ["internal_research"],
        "notes": "Test fixture only; no live MSE data.",
    }
    data.update(overrides)
    return data


def write_csv(path: Path, rows=None):
    rows = rows or [
        ["MSE-TEST", "2026-11-24", "123.45", "MWK"],
        ["MSE-TEST", "2026-11-25", "124.00", "MWK"],
    ]
    path.write_text(
        "instrument_id,observation_date,price,currency\n"
        + "\n".join(",".join(row) for row in rows)
        + "\n",
        encoding="utf-8",
    )


def setup_files(tmp_path, metadata):
    source = tmp_path / "operator-supplied.csv"
    write_csv(source)
    metadata_path = tmp_path / "provenance.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    return source, metadata_path


def run(tmp_path, source, metadata_path):
    return run_controlled_ingestion(
        source,
        archive_dir=tmp_path / "private-archive",
        manifest_path=tmp_path / "manifest.jsonl",
        provenance_path=metadata_path,
        report_path=tmp_path / "validation-report.json",
    )


def test_permission_unknown_blocks_publication_but_stage_is_auditable(tmp_path):
    source, metadata_path = setup_files(tmp_path, provenance())
    report = run(tmp_path, source, metadata_path)
    assert report["validation"]["status"] == "passed"
    assert report["permission"]["publication_allowed"] is False
    assert report["publication_status"] == "blocked"
    assert report["checksum_sha256"]
    assert (tmp_path / "validation-report.json").exists()
    assert (tmp_path / "private-archive" / f'{report["checksum_sha256"]}.csv').exists()


def test_explicit_permission_and_valid_rows_only_mark_eligible_for_review(tmp_path):
    source, metadata_path = setup_files(tmp_path, provenance(
        licence_name="Written educational permission",
        licence_reference="permission-letter-TEST",
        redistribution_allowed=True,
        permitted_uses=["internal_research", "public_display"],
        validation_status="pending",
    ))
    report = run(tmp_path, source, metadata_path)
    assert report["validation"]["status"] == "passed"
    assert report["permission"]["publication_allowed"] is True
    assert report["publication_status"] == "eligible_for_review"
    assert "never publishes or writes to a database" in report["note"]


def test_quality_failure_stays_blocked(tmp_path):
    source, metadata_path = setup_files(tmp_path, provenance())
    write_csv(source, [["MSE-TEST", "bad-date", "-1", "MWK"]])
    report = run(tmp_path, source, metadata_path)
    assert report["validation"]["status"] == "rejected"
    assert report["publication_status"] == "blocked"
    assert report["permission"]["publication_allowed"] is False


def test_metadata_must_be_json_object(tmp_path):
    source = tmp_path / "file.csv"
    write_csv(source)
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="object"):
        run(tmp_path, source, metadata_path)


def test_report_does_not_include_market_rows(tmp_path):
    source, metadata_path = setup_files(tmp_path, provenance())
    report = run(tmp_path, source, metadata_path)
    output = (tmp_path / "validation-report.json").read_text(encoding="utf-8")
    assert "123.45" not in output
    assert report["validation"]["rows_received"] == 2
