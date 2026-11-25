# Controlled operator-assisted market CSV ingestion

This pilot tool prepares **operator-supplied** market CSV files. It does not fetch MSE data, scrape pages, write to the database or publish the dataset.

## Current permission status

MSE permission for automated acquisition and public display remains unconfirmed. Therefore use a provenance file with `redistribution_allowed: null` and permitted uses limited to internal review. The publication decision will be blocked. This is the expected current result.

## Input CSV contract

The staging validator now requires currency values to be exactly three uppercase alphabetic characters (no surrounding whitespace). This is a format check, not a complete ISO 4217 membership check. Invalid values are rejected, not silently normalized.

The current staging adapter expects these columns:

```csv
instrument_id,observation_date,price,currency
MSE-TEST,2026-11-24,123.45,MWK
```

This is an illustrative test fixture, **not real MSE data**. Before using an official report, verify its column definitions and map the file into the staging contract without guessing. Preserve the untouched original artifact. The current contract does not yet encode quote type (e.g., closing, last-traded, bid/ask), adjustment status, or source-specific units; those must be established from the source specification before mapping or analysis.

## Provenance metadata example

Save as `provenance.json` beside your files. This example intentionally has unknown redistribution permission:

```json
{
  "dataset_id": "mse-daily-report-pilot",
  "dataset_name": "Operator-provided MSE report pilot",
  "data_class": "official_public",
  "source_name": "Malawi Stock Exchange",
  "source_url": "https://mse.co.mw/market/reports",
  "collected_at": "2026-11-25T09:00:00+02:00",
  "validation_status": "pending",
  "licence_name": "Permission pending",
  "redistribution_allowed": null,
  "permitted_uses": ["internal_research"],
  "notes": "Permission not yet confirmed; staging only."
}
```

The metadata file should reflect the actual source artifact, collection time and permission decision. Do not use a template timestamp as the real retrieval time.

## Run

From the repository root, after installing Python requirements:

```bash
python -m mse_analytics.mse_ingestion_workflow \
  --source ./input/market-report.csv \
  --provenance ./input/provenance.json \
  --archive ./private-data/raw \
  --manifest ./private-data/ingestion.jsonl \
  --report ./private-data/reports/stage-report.json
```

## Outputs

- **Raw archive:** source artifact stored by SHA-256 checksum; existing artifacts are not overwritten.
- **Manifest:** append-only JSONL ingestion record with source metadata and checksum.
- **Validation report:** dataset identity, checksum, row counts, validation issues and permission decision. It deliberately excludes market-data rows.
- **Exit code:** 0 if data quality passes (even when publication permission is blocked); 3 if data validation rejects the rows; 2 for file/metadata/workflow errors.

## Gate semantics

`eligible_for_review` is **not publication**. It means explicit permission metadata and data-quality checks passed. A human must still review source and data, then use the approved publication process. The CLI itself has no publication or database-write capability.
