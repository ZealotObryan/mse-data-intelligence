from __future__ import annotations

import pandas as pd
import pytest

from mse_analytics.staging import stage_price_csv


def metadata(**updates):
    result = {
        "dataset_id": "demo-prices-v1",
        "dataset_name": "Illustrative prices",
        "data_class": "synthetic_demo",
        "source_name": "Internal synthetic data generator",
        "collected_at": "2026-11-12T08:00:00+02:00",
        "validation_status": "pending",
        "permitted_uses": ["public_display"],
    }
    result.update(updates)
    return result


def test_stage_archives_valid_csv_and_returns_permission_decision(tmp_path):
    source = tmp_path / "prices.csv"
    pd.DataFrame({
        "instrument_id": ["DEMO-001", "DEMO-001"],
        "observation_date": ["2026-01-02", "2026-01-03"],
        "price": [100.0, 101.0],
        "currency": ["MWK", "MWK"],
    }).to_csv(source, index=False)

    result = stage_price_csv(
        source, tmp_path / "archive", tmp_path / "manifest.jsonl",
        provenance=metadata(),
    )

    assert result.quality.status == "passed"
    assert result.ingestion.checksum_sha256 == result.provenance.checksum
    assert result.publication_allowed is True
    assert "synthetic" in result.publication_reason
    assert (tmp_path / "archive" / f"{result.ingestion.checksum_sha256}.csv").exists()


def test_stage_rejects_bad_rows_and_never_allows_publication(tmp_path):
    source = tmp_path / "prices.csv"
    pd.DataFrame({
        "instrument_id": ["DEMO-001"],
        "observation_date": ["not-a-date"],
        "price": [-1],
        "currency": ["MWK"],
    }).to_csv(source, index=False)

    result = stage_price_csv(
        source, tmp_path / "archive", tmp_path / "manifest.jsonl",
        provenance=metadata(),
    )

    assert result.quality.status == "rejected"
    assert result.publication_allowed is False
    assert result.provenance.validation_status.value == "rejected"
    assert (tmp_path / "archive" / f"{result.ingestion.checksum_sha256}.csv").exists()


def test_stage_blocks_external_dataset_without_display_permission(tmp_path):
    source = tmp_path / "prices.csv"
    pd.DataFrame({
        "instrument_id": ["EXT-001"],
        "observation_date": ["2026-01-02"],
        "price": [100.0],
        "currency": ["MWK"],
    }).to_csv(source, index=False)

    external = metadata(
        data_class="licensed_market",
        source_name="Approved provider",
        source_url="https://provider.example/prices.csv",
        licence_name="Internal research only",
        redistribution_allowed=False,
        permitted_uses=["internal_research"],
    )
    result = stage_price_csv(
        source, tmp_path / "archive", tmp_path / "manifest.jsonl",
        provenance=external,
    )

    assert result.quality.status == "passed"
    assert result.publication_allowed is False
    assert "redistribution" in result.publication_reason


def test_stage_rejects_mismatched_supplied_checksum(tmp_path):
    source = tmp_path / "prices.csv"
    source.write_text(
        "instrument_id,observation_date,price,currency\nDEMO-001,2026-01-02,100,MWK\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not match"):
        stage_price_csv(
            source, tmp_path / "archive", tmp_path / "manifest.jsonl",
            provenance=metadata(checksum="0" * 64),
        )
