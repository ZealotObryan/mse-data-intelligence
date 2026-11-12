# Controlled price-data staging

The `mse_analytics.staging.stage_price_csv` workflow connects the local
immutable archive, CSV parser, non-destructive price validator and provenance
publication gate.

## Processing order

1. Archive the original file by SHA-256 and append an ingestion manifest record.
2. Verify any checksum supplied in provenance metadata against the archived
   bytes.
3. Parse the CSV into a pandas DataFrame.
4. Validate required fields, dates, prices, instrument identifiers, currencies
   and duplicate natural keys.
5. Set provenance validation status from the actual quality report rather than
   trusting an operator-supplied status.
6. Evaluate publication permission using the provenance policy.

## Safety boundaries

- The original file is archived before parsing, including when the data later
  fails validation.
- Failed validation prevents publication.
- External datasets require explicit redistribution permission and
  `public_display` in permitted uses.
- Synthetic demo data is permitted only with visible synthetic/illustrative
  labelling in the consuming interface.
- The staging function does not write to PostgreSQL, expose an API, or publish
  data. Those remain separate integration and operational approval steps.
- The JSONL manifest and local filesystem adapter are development-only; they
  are not a concurrent production ingestion system.
- CSV parsing errors are surfaced to the caller. The original artifact remains
  archived for diagnosis.
