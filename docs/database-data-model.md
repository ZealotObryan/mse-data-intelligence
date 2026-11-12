# PostgreSQL data model

## Purpose and scope

This is the first relational foundation for MSE Data Intelligence. The migration in `database/migrations/001_initial_data_foundation.sql` creates metadata and observation tables only. It does not connect to MSE, download reports, seed securities or publish market observations.

## Entity grain

| Table | Grain | Responsibility |
|---|---|---|
| `data_sources` | One source identity and its terms | Source ownership, URL, licence and permission review |
| `datasets` | One named dataset/version | Classification, coverage, validation and publication decision |
| `ingestion_runs` | One received source artifact per dataset/checksum | Parser version, archive URI, checksum, row counts and processing outcome |
| `instruments` | One instrument identity | Issuer, exchange symbol, type, sector, currency and listing dates |
| `market_observations` | One metric for one instrument on one date in one dataset | Numeric observation with dataset and ingestion lineage |
| `validation_issues` | One finding raised during an ingestion run | Severity, issue code, message and row locator |

## Relationships

- A source can supply multiple datasets.
- A dataset belongs to one source and can have multiple ingestion runs.
- An ingestion run can produce multiple validation issues and observations.
- Each observation belongs to one dataset and one instrument; its ingestion run is retained when known.
- The observation uniqueness key is dataset + instrument + date + metric. Multiple datasets may preserve separate source vintages without overwriting history.

## Publication controls

The default dataset publication state is `blocked`. External data can be marked `approved_public` only when validation has passed, redistribution permission is explicitly true and `public_display` is included in permitted uses. Synthetic demo datasets still require visible illustrative labelling in the application. Database constraints provide a backstop, not a substitute for the Python publication gate or a human review of licence terms.

The MSE website states that its website/data use is personal and non-commercial and that commercial use requires a data agreement. Obtain written permission and confirm storage, caching, display and redistribution scope before importing or publicly displaying actual MSE data.

## Operational safeguards before production

1. Use a managed PostgreSQL service with encrypted connections, backups and point-in-time recovery.
2. Keep raw source artifacts in private, access-controlled object storage; store stable object URIs and SHA-256 checksums in ingestion records.
3. Apply least-privilege roles. Enable row-level security if data is exposed through a client-facing API; public clients must not be able to query raw datasets or unapproved observations.
4. Make ingestion state changes transactional. Use a queue/worker and database transactions rather than concurrent JSONL manifest writes.
5. Add issuer/instrument effective-dated history before modelling symbol changes, corporate actions or delistings.
6. Add audited approval events for changes to licences, permitted uses and publication status.
7. Add retention and deletion policies that respect provider agreements.

## Current limitations

- No production database has been provisioned or connected.
- No MSE data has been imported.
- Instrument identifiers are internal stable IDs; exchange symbol history and corporate actions need a later migration.
- Observation values are generic numeric measures; metric-specific units and validation rules will be added with the first permissioned dataset.
- The local JSONL ingestion adapter is for development only and is not safe as a multi-writer production manifest.
