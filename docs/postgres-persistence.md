# PostgreSQL persistence adapter

`mse_analytics.postgres_repository.persist_price_stage` writes a completed
`PriceCsvStageResult` to the PostgreSQL schema created by migrations 001 and
002. It accepts a psycopg-compatible DB-API connection supplied by the caller;
it does not create connections, read credentials, or contact a database at
module import time.

## Transaction contents

- Upsert source identity and permission metadata.
- Upsert dataset provenance, validation state and publication state.
- Record the ingestion run and archived artifact checksum.
- Replace validation issue rows for the idempotent ingestion record.
- Insert price observations only when the full quality report has status
  `passed`. Instrument identifiers must already exist in the registry.
- Rely on the database publication trigger as the final publication authority.

All writes execute in one database transaction. A missing instrument, invalid
foreign key, failed constraint or publication-trigger rejection rolls back the
whole operation.

## Operational prerequisites and limits

1. Apply migrations 001 and 002 to a PostgreSQL 15+ database.
2. Supply a least-privilege connection from the deployment environment.
3. Register instrument identifiers before importing their observations.
4. Review source class, licence and permission status with an authorised
   operator. Never set permission to approved based only on a public URL.
5. Keep raw tables private. Review view ownership, grants and RLS before
   exposing `public_market_observations`.
6. Configure backups, connection pooling, secret rotation and monitoring.

This adapter is implemented but **not connected to a provisioned database**.
No PostgreSQL credentials or live MSE data have been added. The local archive
remains a development adapter and should move to controlled object storage for
production.
