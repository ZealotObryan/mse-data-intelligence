# Market data provider integration plan

## Objective

Connect MSE Data Intelligence to an authorised market-data source without coupling the analytics platform to one vendor. The first supported input remains the reviewed CSV staging workflow. An API adapter may be added when a provider's coverage, schema, licence and credentials have been verified.

## Provider onboarding gate

Do not activate a provider until an operator has recorded and reviewed:

- Legal provider identity and the underlying source of its Malawi Stock Exchange data.
- Written permission and licence terms for storage, historical analysis, public display and commercial redistribution (each assessed separately).
- Instruments and asset classes covered, including equities and debt securities where offered.
- Historical depth, update frequency, timezone, trading calendar and correction policy.
- Field definitions, currency/unit conventions, corporate-action adjustments and treatment of suspended or delisted instruments.
- API authentication, rate limits, service availability, support contact and pricing.
- Sample payloads for normal trading days, no-trade days, missing values, corrections and corporate actions.

A provider's claim of MSE coverage is not proof of exchange-originated data or redistribution rights.

## Canonical observation contract

All provider adapters must map source records into the existing staged observation grain:

| Field | Meaning |
|---|---|
| instrument_id | Stable internal instrument identifier resolved through the instrument registry |
| observation_date | Exchange-local trading date, retained as a date rather than inferred from server time |
| price | Numeric quoted price with the provider's price type documented |
| currency | ISO 4217 currency code |
| metric_key | Explicit metric name for non-price observations in future extensions |
| source timestamp | Original provider publication/observation timestamp retained in provenance or raw payload metadata |

Never infer missing prices, convert currencies silently, or treat absent records as zero. Preserve the original response or file, checksum it, and retain the parser/adapter version.

## Adapter boundary

Implement each source as a separate adapter that:

1. Fetches only documented endpoints or supplied files using approved credentials.
2. Stores the untouched response in the controlled raw archive.
3. Maps the response to the canonical schema without silently dropping source fields.
4. Runs schema, instrument mapping, date, currency, duplicate and numeric validation.
5. Creates dataset provenance containing provider, endpoint/dataset identifier, retrieval timestamp, coverage, licence reference, permitted uses and checksum.
6. Submits the staged result to the existing persistence workflow.
7. Records request identifiers, pagination, response status and retry history without logging secrets.

The dashboard and analytics modules must consume canonical persisted observations, not vendor-specific payloads.

## Reliability and reconciliation

- Use pagination and bounded date windows; persist cursors only after a successful archive and validation.
- Make retries idempotent using provider record identifiers where available, otherwise dataset checksum and natural observation key.
- Detect corrections to previously published observations and retain the superseded value and lineage rather than overwriting history without an audit record.
- Monitor freshness against the provider's stated publication schedule; show the last successful update and stale-data warning.
- Reconcile daily record counts, instrument coverage and aggregate totals against the provider's official report where available.
- Keep failed, incomplete or warning datasets out of public market views until reviewed.

## Security and deployment

- Store API credentials only in server-side environment secrets or a managed secret store. Never use `NEXT_PUBLIC_` variables for private credentials.
- Apply least-privilege database roles and keep raw ingestion tables private.
- Rate-limit ingestion, use bounded timeouts, validate response size/content type and avoid logging authorization headers.
- Keep provider access disabled by default until licence and configuration are approved.
- Do not scrape pages or bypass access controls as a substitute for an authorised feed.

## Initial rollout

1. Obtain MSE response and, if offered, official sample files/feed specification.
2. Evaluate third-party provider samples against the same checklist and confirm underlying provenance and licence.
3. Select one source for a limited historical pilot.
4. Run the pilot in a non-public staging environment; compare samples to MSE-published reports.
5. Obtain explicit approval for public display before enabling the public observation view.
6. Enable scheduled updates with freshness monitoring and an operational correction process.

## Current status

The CSV archive, provenance, quality validation, staging and PostgreSQL persistence components exist. No provider has been approved or connected, no credentials are configured, and no live MSE market data is present. Dashboard sample values must continue to be labelled illustrative until verified source data is lawfully integrated.
