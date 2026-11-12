"""Immutable local source-artifact archive and append-only ingestion manifest.

This is a local filesystem adapter for development and controlled ingestion.
Production deployments should replace the storage adapter with access-controlled
object storage while preserving the same checksum and manifest contract.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil


@dataclass(frozen=True)
class IngestionRecord:
    ingestion_id: str
    dataset_id: str
    source_name: str
    collected_at: str
    original_filename: str
    archive_path: str
    checksum_sha256: str
    bytes_received: int
    parser_version: str
    status: str = "received"


def _sha256(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def archive_source_artifact(
    source_path: str | Path,
    archive_dir: str | Path,
    manifest_path: str | Path,
    *,
    dataset_id: str,
    source_name: str,
    parser_version: str,
    collected_at: datetime | None = None,
) -> IngestionRecord:
    """Archive a source file by content hash and append an ingestion record.

    Repeating the same dataset/checksum pair is idempotent and returns the
    existing record. Existing archived bytes are never overwritten.
    """
    source = Path(source_path)
    archive_root = Path(archive_dir)
    manifest = Path(manifest_path)

    if not source.is_file():
        raise FileNotFoundError(f"source artifact does not exist: {source}")
    for field, value in (
        ("dataset_id", dataset_id),
        ("source_name", source_name),
        ("parser_version", parser_version),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    timestamp = collected_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("collected_at must include a timezone")

    checksum, byte_count = _sha256(source)
    archive_root.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    suffix = source.suffix.lower()[:16]
    archived = archive_root / f"{checksum}{suffix}"
    if archived.exists():
        existing_hash, existing_size = _sha256(archived)
        if existing_hash != checksum or existing_size != byte_count:
            raise RuntimeError("archive integrity conflict; refusing to overwrite artifact")
    else:
        temporary = archive_root / f".{checksum}.tmp"
        try:
            with source.open("rb") as src, temporary.open("xb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
                dst.flush()
                os.fsync(dst.fileno())
            copied_hash, copied_size = _sha256(temporary)
            if copied_hash != checksum or copied_size != byte_count:
                raise RuntimeError("source changed during archive copy; artifact not committed")
            try:
                temporary.rename(archived)
            except FileExistsError:
                # A concurrent identical ingestion won the archive race.
                temporary.unlink(missing_ok=True)
        finally:
            temporary.unlink(missing_ok=True)

    if not archived.is_file():
        raise RuntimeError("archive artifact was not committed")

    if manifest.exists():
        with manifest.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                previous = json.loads(line)
                if previous.get("dataset_id") == dataset_id and previous.get("checksum_sha256") == checksum:
                    return IngestionRecord(**previous)

    record = IngestionRecord(
        ingestion_id=f"{dataset_id}:{checksum[:16]}",
        dataset_id=dataset_id,
        source_name=source_name,
        collected_at=timestamp.isoformat(),
        original_filename=source.name,
        archive_path=str(archived),
        checksum_sha256=checksum,
        bytes_received=byte_count,
        parser_version=parser_version,
    )
    with manifest.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return record
