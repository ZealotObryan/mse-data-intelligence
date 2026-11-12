"""Dataset provenance contracts and publication permission checks.

This module does not fetch data or grant rights. It enforces metadata and
permission decisions supplied by an authorised operator.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping
from urllib.parse import urlparse


class DataClass(str, Enum):
    SYNTHETIC_DEMO = "synthetic_demo"
    OFFICIAL_PUBLIC = "official_public"
    LICENSED_MARKET = "licensed_market"
    ISSUER_DISCLOSURE = "issuer_disclosure"
    DERIVED = "derived"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    WARNING = "warning"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DatasetProvenance:
    dataset_id: str
    dataset_name: str
    data_class: DataClass
    source_name: str
    collected_at: datetime
    validation_status: ValidationStatus
    source_url: str | None = None
    source_document_id: str | None = None
    published_at: datetime | None = None
    coverage_start: str | None = None
    coverage_end: str | None = None
    licence_name: str | None = None
    licence_reference: str | None = None
    permitted_uses: tuple[str, ...] = ()
    redistribution_allowed: bool | None = None
    attribution_text: str | None = None
    collector_version: str | None = None
    checksum: str | None = None
    notes: str | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "DatasetProvenance":
        """Build a typed record from decoded JSON and reject malformed metadata."""
        required = {
            "dataset_id", "dataset_name", "data_class", "source_name",
            "collected_at", "validation_status",
        }
        missing = sorted(required - payload.keys())
        if missing:
            raise ValueError(f"missing required provenance fields: {', '.join(missing)}")

        def parse_datetime(field: str) -> datetime | None:
            value = payload.get(field)
            if value is None:
                return None
            if not isinstance(value, str):
                raise ValueError(f"{field} must be an ISO-8601 string")
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"{field} must be a valid ISO-8601 datetime") from exc
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError(f"{field} must include a timezone")
            return parsed

        try:
            data_class = DataClass(payload["data_class"])
            status = ValidationStatus(payload["validation_status"])
        except (TypeError, ValueError) as exc:
            raise ValueError("unknown data_class or validation_status") from exc

        for field in ("dataset_id", "dataset_name", "source_name"):
            if not isinstance(payload[field], str) or not payload[field].strip():
                raise ValueError(f"{field} must be a non-empty string")

        permitted = payload.get("permitted_uses", ())
        if not isinstance(permitted, (list, tuple)) or any(
            not isinstance(item, str) or not item.strip() for item in permitted
        ):
            raise ValueError("permitted_uses must be a list of non-empty strings")

        redistribution = payload.get("redistribution_allowed")
        if redistribution is not None and not isinstance(redistribution, bool):
            raise ValueError("redistribution_allowed must be true, false or null")

        checksum = payload.get("checksum")
        if checksum is not None:
            if not isinstance(checksum, str) or len(checksum) != 64:
                raise ValueError("checksum must be a 64-character SHA-256 hex digest")
            try:
                int(checksum, 16)
            except ValueError as exc:
                raise ValueError("checksum must be a 64-character SHA-256 hex digest") from exc

        source_url = payload.get("source_url")
        if source_url is not None:
            parsed_url = urlparse(source_url) if isinstance(source_url, str) else None
            if parsed_url is None or parsed_url.scheme not in {"https", "http"} or not parsed_url.netloc:
                raise ValueError("source_url must be an absolute HTTP(S) URL")

        if data_class == DataClass.SYNTHETIC_DEMO and payload["source_name"] != "Internal synthetic data generator":
            raise ValueError("synthetic_demo source_name must identify the internal generator")

        if data_class in {
            DataClass.OFFICIAL_PUBLIC,
            DataClass.LICENSED_MARKET,
            DataClass.ISSUER_DISCLOSURE,
        }:
            if not source_url or not payload.get("licence_name") or "redistribution_allowed" not in payload:
                raise ValueError("external datasets require source_url, licence_name and a redistribution_allowed field (null means unknown)")

        return cls(
            dataset_id=payload["dataset_id"].strip(),
            dataset_name=payload["dataset_name"].strip(),
            data_class=data_class,
            source_name=payload["source_name"].strip(),
            collected_at=parse_datetime("collected_at"),  # type: ignore[arg-type]
            validation_status=status,
            source_url=source_url,
            source_document_id=payload.get("source_document_id"),
            published_at=parse_datetime("published_at"),
            coverage_start=payload.get("coverage_start"),
            coverage_end=payload.get("coverage_end"),
            licence_name=payload.get("licence_name"),
            licence_reference=payload.get("licence_reference"),
            permitted_uses=tuple(permitted),
            redistribution_allowed=redistribution,
            attribution_text=payload.get("attribution_text"),
            collector_version=payload.get("collector_version"),
            checksum=checksum,
            notes=payload.get("notes"),
        )


def publication_decision(record: DatasetProvenance) -> tuple[bool, str]:
    """Return whether a record may be publicly displayed and the reason.

    Synthetic demonstrations may be displayed only with an explicit
    illustrative label. External and derived data require passed validation,
    explicit redistribution permission and a public-display permission.
    """
    if record.validation_status != ValidationStatus.PASSED:
        return False, f"validation status is {record.validation_status.value}"
    if record.data_class == DataClass.SYNTHETIC_DEMO:
        return True, "allowed only when visibly labelled as synthetic/illustrative"
    if record.redistribution_allowed is not True:
        return False, "redistribution permission is not explicitly granted"
    if "public_display" not in record.permitted_uses:
        return False, "permitted_uses does not include public_display"
    if not record.source_url or not record.licence_name:
        return False, "source and licence metadata are incomplete"
    return True, "publication permission and validation metadata are present"
