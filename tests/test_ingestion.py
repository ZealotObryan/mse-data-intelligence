import json
from datetime import datetime, timezone

import pytest

from mse_analytics.ingestion import archive_source_artifact


def test_archives_source_with_checksum_and_manifest(tmp_path):
    source = tmp_path / "market-report.csv"
    source.write_text("date,price\n2026-01-01,100\n", encoding="utf-8")
    archive = tmp_path / "raw"
    manifest = tmp_path / "logs" / "ingestion.jsonl"

    record = archive_source_artifact(
        source, archive, manifest,
        dataset_id="demo-dataset",
        source_name="Approved test fixture",
        parser_version="csv-v1",
        collected_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )

    assert record.bytes_received == source.stat().st_size
    assert len(record.checksum_sha256) == 64
    assert (archive / f"{record.checksum_sha256}.csv").read_bytes() == source.read_bytes()
    stored = json.loads(manifest.read_text(encoding="utf-8").strip())
    assert stored["checksum_sha256"] == record.checksum_sha256


def test_repeated_same_dataset_and_content_is_idempotent(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("unchanged", encoding="utf-8")
    manifest = tmp_path / "ingestion.jsonl"
    kwargs = dict(
        dataset_id="dataset-1",
        source_name="Test source",
        parser_version="v1",
    )
    first = archive_source_artifact(source, tmp_path / "raw", manifest, **kwargs)
    second = archive_source_artifact(source, tmp_path / "raw", manifest, **kwargs)
    assert first == second
    assert len(manifest.read_text(encoding="utf-8").splitlines()) == 1


def test_changed_content_creates_new_immutable_artifact(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("a,b\n1,2", encoding="utf-8")
    archive = tmp_path / "raw"
    manifest = tmp_path / "manifest.jsonl"
    kwargs = dict(dataset_id="dataset-1", source_name="Source", parser_version="v1")
    first = archive_source_artifact(source, archive, manifest, **kwargs)
    source.write_text("a,b\n1,3", encoding="utf-8")
    second = archive_source_artifact(source, archive, manifest, **kwargs)
    assert first.checksum_sha256 != second.checksum_sha256
    assert (archive / f"{first.checksum_sha256}.csv").exists()
    assert (archive / f"{second.checksum_sha256}.csv").exists()
    assert len(manifest.read_text(encoding="utf-8").splitlines()) == 2


def test_missing_source_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        archive_source_artifact(
            tmp_path / "missing.csv", tmp_path / "raw", tmp_path / "manifest.jsonl",
            dataset_id="dataset", source_name="Source", parser_version="v1",
        )


def test_naive_timestamp_is_rejected(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="timezone"):
        archive_source_artifact(
            source, tmp_path / "raw", tmp_path / "manifest.jsonl",
            dataset_id="dataset", source_name="Source", parser_version="v1",
            collected_at=datetime(2026, 1, 1),
        )


@pytest.mark.parametrize("field", ["dataset_id", "source_name", "parser_version"])
def test_empty_metadata_is_rejected(tmp_path, field):
    source = tmp_path / "source.csv"
    source.write_text("x", encoding="utf-8")
    kwargs = dict(dataset_id="dataset", source_name="Source", parser_version="v1")
    kwargs[field] = " "
    with pytest.raises(ValueError, match=field):
        archive_source_artifact(source, tmp_path / "raw", tmp_path / "manifest.jsonl", **kwargs)
