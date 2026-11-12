# Data provenance, validation and governance

## Purpose

Every market observation used by MSE Data Intelligence must be traceable to an identified source, a defined collection event and a documented validation process. Provenance is a product requirement, not optional metadata.

The current public dashboard uses synthetic illustrative data only. These records must remain visibly distinct from real observations and must never be presented as MSE-listed issuers, prices, market capitalisation, index values or trading activity.

## Data classes

Use an explicit `data_class` on every dataset and record:

- `synthetic_demo`: fictional values created for interface demonstrations, examples or tests.
- `official_public`: information published by an official source for a use that is permitted by its terms.
- `licensed_market`: market information obtained under a written data agreement.
- `issuer_disclosure`: company announcements, annual reports or other issuer-originated disclosures.
- `derived`: calculated values whose complete input lineage is retained.

Do not silently merge classes. Any derived output must inherit the restrictive permissions of its inputs.

## Required dataset metadata

Each dataset registration must capture:

| Field | Meaning |
| --- | --- |
| dataset_id | Stable internal identifier |
| dataset_name | Human-readable name |
| data_class | One of the classes above |
| source_name | Publisher, issuer or internal generator |
| source_url | Exact source location, where applicable |
| source_document_id | Report, file or release identifier, if available |
| collected_at | UTC timestamp when the platform retrieved or received it |
| published_at | Source publication timestamp, if known |
| coverage_start / coverage_end | Observation period represented |
| licence_name | Licence or agreement name |
| licence_reference | URL or internal agreement reference |
| permitted_uses | Explicitly approved purposes |
| redistribution_allowed | Boolean; unknown must not be treated as true |
| attribution_text | Required source attribution |
| collector_version | Ingestion job or parser version |
| checksum | Content hash of the received source artifact |
| validation_status | pending, passed, warning or rejected |
| notes | Limitations, caveats and manual review notes |

Unknown values should be null/unknown, not guessed.

## Required observation lineage

Every imported or calculated observation should retain:

- dataset_id and source record identifier;
- instrument/issuer identifier where verified;
- field name and value, with currency and unit where relevant;
- observation date or reporting period;
- source page, table, row or document locator where possible;
- ingestion timestamp and transformation version;
- validation outcome and any warning codes;
- for derived values, the input observation identifiers and calculation method/version.

Never use a company name alone as a permanent security identifier. Maintain a controlled issuer/instrument registry with effective dates and source evidence.

## Permission gate

The Malawi Stock Exchange website states that website/data use is for personal and non-commercial purposes and that commercial use requires notifying the Exchange and signing a data agreement. This project must not assume that public visibility grants redistribution rights.

Before collecting, storing, displaying, caching, or redistributing real MSE market data, record written permission and the agreed scope. If the permission status is absent, expired or unclear, block public publication. Public issuer reports and announcements also require source-specific terms and attribution review.

Primary source: https://www.mse.co.mw/
Market reports: https://www.mse.co.mw/market/reports

## Validation pipeline

1. **Register** the source, data class, licence and permitted uses before ingestion.
2. **Acquire** the original artifact without overwriting it; compute a checksum and record collection time.
3. **Parse** into a staging area, retaining original values and source locators.
4. **Validate schema**: required fields, types, units, currency, date formats and identifier mapping.
5. **Validate content**: nulls, duplicates, impossible values, inconsistent units, out-of-period observations and suspicious discontinuities.
6. **Reconcile** totals and reported figures against the source document where possible.
7. **Review** warnings and rejected records; never silently coerce or discard material errors.
8. **Publish** only records that pass the permission gate and required validation rules.
9. **Monitor** freshness, source changes, failed imports and data-quality drift.

## Validation outcomes

- `passed`: all mandatory checks pass and publication permissions are confirmed.
- `warning`: data may be usable for a restricted internal purpose, but a disclosed issue remains; public display requires an explicit policy decision.
- `rejected`: malformed, contradictory, untraceable or unauthorised data; do not publish.
- `pending`: not yet reviewed; do not publish as verified data.

A successful technical import is not evidence that the source is accurate or that reuse is licensed.

## Quality checks

At minimum, implement checks for:

- missing required values and unexpected null rates;
- duplicate natural keys (instrument, observation date, field);
- invalid or non-monotonic dates;
- invalid prices (non-numeric, zero or negative where a positive price is required);
- currency/unit mismatches;
- stale observations relative to the source's publication cadence;
- unexpected jumps and outliers, flagged for review rather than automatically deleted;
- corporate actions and adjusted/unadjusted price distinctions;
- consistency between reported totals and component values;
- issuer/instrument mappings with effective dates.

Thresholds must be source- and field-specific, documented, and tested. Do not invent a universal price-change threshold.

## Display rules

- Label synthetic values at the point of use, not only in a footer.
- Show source, as-of date, reporting period and freshness for real data.
- Distinguish reported facts, calculated metrics, model estimates and interpretation.
- Show calculation method and key assumptions for derived metrics.
- Surface stale, incomplete or warning-state data clearly.
- Never imply causation from correlation or a price movement alone.
- Never convert an automated metric into a buy/sell instruction.

## Operational controls

- Keep raw source artifacts immutable and access-controlled.
- Store secrets and licence documents outside the public repository.
- Log ingestion runs, parser versions, checksums, validation results and publication decisions.
- Make ingestion idempotent and safe to retry.
- Version schemas and transformations; retain reproducible lineage.
- Provide a process to withdraw data when permissions change or errors are discovered.
- Keep synthetic fixtures in a separate namespace from production market datasets.

## Implementation sequence

1. Add typed dataset and observation contracts based on the accompanying JSON Schema.
2. Implement a source registry and permission gate.
3. Build immutable raw-file storage and ingestion run logs.
4. Add staging tables and validation reports.
5. Add approved publication views consumed by the dashboard.
6. Add freshness and quality monitoring.
7. Integrate real MSE data only after written permission and a tested data agreement workflow.

## Acceptance criteria

- Every displayed real figure can be traced to its source and reporting period.
- Every dataset has a recorded data class and licence/permission state.
- Unknown redistribution rights block public publication.
- Synthetic and real datasets cannot be confused in storage or UI.
- Failed validation is visible and prevents publication.
- Derived metrics retain input lineage and method version.
- A source artifact can be reprocessed reproducibly from its checksum and parser version.
