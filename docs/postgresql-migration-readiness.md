# PostgreSQL migration and production-readiness runbook

## Purpose

This runbook prepares the MSE Data Intelligence relational foundation for a future managed PostgreSQL deployment. It is a controlled operational checklist, not authorisation to provision a paid database or import MSE data. No production database credentials are currently configured in this repository workflow.

## Release gates

Do not connect a public application route to issuer or market tables until all of these are true:

1. Written source permission and data agreement cover the intended storage, processing, derived metrics, public display, caching and redistribution.
2. A managed PostgreSQL 15+ instance is provisioned with encrypted connections, automated backups and point-in-time recovery.
3. Migrations 001, 002 and 003 have been reviewed and applied in order in a controlled environment.
4. Database roles, grants and row-level security have been tested using the exact application identities.
5. Ingestion retains original source artifacts, SHA-256 checksums, parser versions, dataset IDs, ingestion IDs and source locators.
6. Validation and human publication approval are recorded before any dataset is exposed.

## Migration sequence

Run from a trusted deployment runner with a dedicated migration identity. Do not place database passwords in shell history, source control, CI logs or client-side environment variables.

1. Confirm PostgreSQL server version is 15 or later. Migration 003 uses `security_invoker` view options.
2. Take and verify a restorable backup or create a disposable staging database.
3. Apply `database/migrations/001_initial_data_foundation.sql`.
4. Apply `database/migrations/002_publication_gate.sql`.
5. Apply `database/migrations/003_issuer_research_and_corporate_actions.sql`.
6. Capture migration output, database version, migration checksums and operator/time in the deployment record.
7. Run schema, constraint, trigger, view and privilege verification queries before loading any data.

The migrations are transactional individually. Apply each as a separate reviewed unit; stop on the first error and investigate rather than continuing with a partially understood schema.

## Preflight checks

- Confirm database name, host, TLS requirement, region, retention and recovery objectives.
- Confirm the migration identity can create schema objects but is not used by the web application.
- Confirm the application identity has only the minimum read permissions required for approved views.
- Keep base tables, ingestion metadata, source artifacts and validation issues private.
- Confirm no `anon`, public or broad authenticated role has direct SELECT on raw tables.
- Confirm view ownership and PostgreSQL security-invoker behaviour. The 003 issuer views request `security_invoker = true`; the 002 market-observation view does not. Treat this as a required review item and do not grant public access until its effective privilege behaviour has been tested and hardened.
- Confirm the publication trigger rejects unapproved sources, missing redistribution permission and datasets without `public_display` permission.
- Confirm unapproved, rejected and pending datasets are absent from every approved read view.

## Post-migration verification

At minimum, verify:

- Required tables exist: `data_sources`, `datasets`, `ingestion_runs`, `instruments`, `market_observations`, `validation_issues`, `issuers`, `issuer_profile_versions`, `issuer_financial_periods`, `issuer_financial_facts`, `dividends`, `corporate_actions`, `issuer_announcements`.
- Required views exist: `public_market_observations`, `public_issuer_financial_facts`, `public_issuer_dividends`, `public_issuer_announcements`.
- The `datasets_publication_gate` trigger is enabled.
- Check constraints and unique indexes are present and validated.
- Application read identity can query approved views but cannot query base tables or mutate records.
- A test dataset with no permission cannot be published; a permitted, validated test dataset can pass the gate only when all required source and dataset permissions are explicit.
- The application cannot read pending, rejected, withdrawn or unapproved records.

Use synthetic test data in staging only. Label it clearly and never present it as actual Malawi Stock Exchange information.

## Ingestion and publication controls

1. Store the original file in private object storage before parsing.
2. Compute SHA-256 and create the dataset/ingestion records with source licence metadata.
3. Parse using a versioned, deterministic parser; retain row counts and source locators.
4. Run schema, date, currency, unit, duplicate, range and cross-field validation.
5. Record validation issues and quarantine rejected rows; do not silently coerce missing values.
6. Reconcile parsed totals and sample facts against the original source document.
7. Obtain a human review of source terms, validation results and display scope.
8. Only then set the dataset to `approved_public` where explicit permission allows it.

## Known implementation cautions

- The initial migration's active-symbol unique index is partial and permits historical inactive symbols; symbol changes still require careful effective-dated handling.
- The 003 issuer statement-period uniqueness key includes nullable `fiscal_period`; PostgreSQL unique constraints allow multiple rows when a key component is NULL. Decide whether to normalise missing fiscal-period values or add an appropriate nulls-not-distinct constraint/index before production ingestion.
- The 002 public market view requires a security/privilege review because it is not declared with `security_invoker = true`.
- The issuer views are not an authorisation grant. Their presence does not make them safe to expose without role, ownership and RLS review.
- The development JSONL manifest adapter is not a multi-writer production ingestion mechanism.
- No migrations have been applied to a live database and no real MSE data has been imported.

## Current blockers

- No managed PostgreSQL instance or credentials are provisioned for this project.
- Written MSE data permission and redistribution terms remain outstanding.
- Production object storage, backup policy, migration runner and database role grants remain to be configured.
- No real issuer dataset has completed the ingestion and publication review process.

**Status:** readiness documentation prepared; deployment and data activation remain blocked pending the prerequisites above.
