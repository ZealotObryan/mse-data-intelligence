# Supabase security baseline

## Provisioned project

- Project: MSE Data Intelligence
- Project ref: `olftvtqbzbheolywnqiz`
- Region: `eu-west-1`
- PostgreSQL: 17
- Initial quoted project cost: $0/month
- Status at provisioning: `ACTIVE_HEALTHY`

## Applied schema migrations

Migrations 001–003 create the data-source, dataset, ingestion, instrument,
market-observation, validation, issuer, financial-statement, dividend,
corporate-action and announcement foundations. No MSE market or issuer data
was seeded.

Migration 004 establishes a deliberate default-deny state:

- RLS enabled on all 13 application tables in `public`.
- No policies yet; absence of policies means ordinary roles cannot access rows.
- `anon` and `authenticated` have no table or publication-view privileges.
- The four publication views are not exposed to browser roles.
- The market publication view uses `security_invoker = true`.
- The publication trigger function is not executable as a client RPC.
- Default privileges keep future tables and functions unexposed for the migration owner.

## Role model and CRUD intent

| Principal | Intended read | Intended create | Intended update | Intended delete |
| --- | --- | --- | --- | --- |
| Anonymous visitor | Approved publication views only | None | None | None |
| Authenticated learner | Own learning progress; approved views | Own progress | Own progress | Own progress |
| Analyst | Assigned internal research and approved views | Analysis artefacts only (future) | Own analysis artefacts (future) | Own analysis artefacts (future) |
| Data steward | Source, dataset and validation scope | Source evidence and ingestion metadata | Staging/validation fields | No evidence deletion |
| Publisher/compliance | Evidence and publication scope | Approval/audit events | Permission/publication decisions | No evidence deletion |
| Platform administrator | Operational scope | Role assignments/audit events | Role assignments/configuration | Controlled break-glass only |
| Ingestion worker | Required source/instrument lookups | Ingestion runs and validated observations | Run status only | None |

These are intended capabilities, not grants or deployed role policies. The
browser roles remain fully blocked until an authenticated identity contract,
trusted role mapping, scoped grants and RLS policies are implemented and
tested. Do not use user-editable Auth metadata for authorisation. Never place a
service-role/secret key in browser code or a `NEXT_PUBLIC_*` variable.

## Verification performed

- Catalog verification: all 13 application tables have RLS enabled.
- Privilege verification: anonymous and authenticated roles cannot SELECT raw
  tables or publication views.
- Publication-gate negative test: a dataset with an unapproved source could not
  be published.
- Publication-gate positive test: a passed synthetic-demo dataset with an
  approved source could be published.
- Both publication tests used a transaction that was rolled back.
- Supabase security advisor reports 13 `rls_enabled_no_policy` informational
  findings. This is expected in this locked state; it is not a request to add
  permissive policies.
- Performance advisor currently reports unindexed foreign keys and unused
  indexes. These should be reviewed after workload and query patterns exist.

## Remaining release gates

1. Choose and implement the app identity contract using Supabase Auth.
2. Add trusted role assignments and scoped data access; do not infer roles from
   user-editable metadata.
3. Create explicit CRUD grants and RLS policies per principal and row scope.
4. Add actual API/view access only after tests prove approved rows are visible
   and pending/restricted rows remain invisible.
5. Review functions/RPCs, Storage buckets, Next.js route handlers, server
   actions and ingestion workers for alternate access paths.
6. Run positive and negative tests using real test identities through both SQL
   and the Data API; record results before enabling any public endpoint.
7. Obtain written permission before importing or publicly displaying actual MSE
   data. Synthetic fixtures must remain clearly labelled.

This baseline is not a completed production authorisation system. It is a
secure, intentionally inaccessible starting point.
