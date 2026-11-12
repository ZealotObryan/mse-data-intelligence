from datetime import datetime

import pytest

from mse_analytics.provenance import (
    DataClass,
    DatasetProvenance,
    ValidationStatus,
    publication_decision,
)


def base_record(**updates):
    record = {
        "dataset_id": "demo-prices-v1",
        "dataset_name": "Illustrative price series",
        "data_class": "synthetic_demo",
        "source_name": "Internal synthetic data generator",
        "collected_at": "2026-11-12T08:00:00+02:00",
        "validation_status": "passed",
        "permitted_uses": ["public_display"],
    }
    record.update(updates)
    return record


def test_parse_synthetic_provenance_and_allow_labelled_display():
    record = DatasetProvenance.from_mapping(base_record())
    assert record.data_class == DataClass.SYNTHETIC_DEMO
    assert publication_decision(record) == (
        True,
        "allowed only when visibly labelled as synthetic/illustrative",
    )


def test_external_data_requires_explicit_licence_and_redistribution_status():
    payload = base_record(
        data_class="licensed_market",
        source_name="Market data provider",
    )
    with pytest.raises(ValueError, match="source_url"):
        DatasetProvenance.from_mapping(payload)


def test_external_data_without_public_display_permission_is_blocked():
    record = DatasetProvenance.from_mapping(base_record(
        data_class="licensed_market",
        source_name="Market data provider",
        source_url="https://provider.example/data",
        licence_name="Research licence",
        redistribution_allowed=True,
        permitted_uses=["internal_research"],
    ))
    allowed, reason = publication_decision(record)
    assert not allowed
    assert "public_display" in reason


def test_external_data_with_explicit_permission_and_passed_validation_is_allowed():
    record = DatasetProvenance.from_mapping(base_record(
        data_class="licensed_market",
        source_name="Market data provider",
        source_url="https://provider.example/data",
        licence_name="Display licence",
        redistribution_allowed=True,
        permitted_uses=["internal_research", "public_display"],
    ))
    assert publication_decision(record)[0] is True


@pytest.mark.parametrize("status", ["pending", "warning", "rejected"])
def test_unpassed_validation_blocks_publication(status):
    record = DatasetProvenance.from_mapping(base_record(validation_status=status))
    assert publication_decision(record)[0] is False


def test_unknown_redistribution_permission_blocks_publication():
    record = DatasetProvenance.from_mapping(base_record(
        data_class="issuer_disclosure",
        source_name="Issuer",
        source_url="https://issuer.example/report",
        licence_name="Terms to review",
        redistribution_allowed=None,
    ))
    assert publication_decision(record)[0] is False


def test_naive_collection_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        DatasetProvenance.from_mapping(base_record(collected_at="2026-11-12T08:00:00"))


def test_invalid_checksum_is_rejected():
    with pytest.raises(ValueError, match="SHA-256"):
        DatasetProvenance.from_mapping(base_record(checksum="not-a-hash"))


def test_invalid_source_url_is_rejected():
    with pytest.raises(ValueError, match="HTTP"):
        DatasetProvenance.from_mapping(base_record(
            data_class="licensed_market",
            source_name="Provider",
            source_url="file:///tmp/data.csv",
            licence_name="Licence",
            redistribution_allowed=False,
        ))


def test_record_is_immutable():
    record = DatasetProvenance.from_mapping(base_record())
    assert record.validation_status == ValidationStatus.PASSED
    assert isinstance(record.collected_at, datetime)
    assert record.collected_at.utcoffset() is not None
