# Supabase security baseline

## Provisioned backend

- MSE Data Intelligence Supabase project: `olftvtqbzbheolywnqiz`
- PostgreSQL 17, region `eu-west-1`
- Project was provisioned on the zero-monthly-cost plan at setup.
- Migrations 001–006 are applied to this project.
- No market or issuer records were imported.

## Role and scope model

| Principal | Read | Create | Update | Delete |
|---|---|---|---|---|
| Anonymous visitor | None | None | None | None |
| Authenticated learner | Own role/scope records only; learner progress schema is not yet implemented | None | None | None |
| Analyst | Assigned dataset and related evidence | None through browser | None through browser | None |
| Data steward | Assigned stewardship datasets, source metadata and validation issues | None through browser | None through browser | None |
| Publisher/compliance | Assigned publication datasets and evidence | None through browser | None through browser | None |
| Platform administrator | Assigned/administrative data via trusted backend workflow | None through browser | None through browser | None |
| Ingestion worker | Server-side ingestion workflow only | Server-side only | Server-side only | None |

The browser is intentionally read-only. Write operations, role assignment, dataset-scope grants,
ingestion and publication approvals must be implemented as authenticated server-side workflows
with explicit validation and audit events. No browser user can grant themselves a role or dataset
scope. No learner-progress tables have been created yet.

## Applied database controls

- RLS is enabled on all 16 application tables in the `public` schema.
- Anonymous role has no SELECT on raw tables or publication views.
- Authenticated role has scoped SELECT privileges on application tables, constrained by RLS.
- Authenticated users can read only their own role and dataset assignment records.
- Dataset visibility is controlled by trusted `app_user_roles` and `dataset_access` rows.
- Analysts need a `read` assignment; data stewards need `steward` or `publish`; publishers need `publish`.
- Platform administrators can read the application dataset scope but cannot mutate assignments from the browser.
- Audit events are append-only from the application perspective; browser clients have no write grants.
- Role/scope helper functions are in the unexposed `private` schema, return booleans only, use pinned search paths, and are not exposed as public RPC functions.
- The market publication view uses `security_invoker=true`; all public publication views remain ungranted until the public data contract is approved.
- The dataset publication trigger rejects datasets with failed validation or missing source permission and public-display rights.

## Verification completed

- Supabase migration history: migrations 001–006 applied.
- Catalog: 16/16 application tables have RLS enabled.
- Catalog: 16 policies exist across the application tables.
- Privileges: `anon` cannot SELECT datasets.
- Privileges: `authenticated` has SELECT but no INSERT on role assignments.
- Runtime SQL as `anon`: direct dataset SELECT denied with permission error.
- Runtime SQL as `authenticated` without an identity claim: dataset SELECT returned zero rows.
- Runtime SQL as `authenticated`: attempt to INSERT a platform-admin role was denied.
- Supabase security advisor after moving helpers to the private schema: no findings.
- The project currently has zero Auth users. Therefore positive/negative tests with real authenticated identities and assigned scopes have not yet been run.
- Earlier publication-gate positive/negative tests used synthetic fixtures inside a rolled-back transaction.

## Explicit remaining launch gates

1. Configure Supabase Auth sign-up/invitation and password-reset policy.
2. Add the Supabase project URL and publishable key to Vercel as environment variables. The Vercel project currently has no environment variables configured.
3. Implement Next.js server/client Supabase clients and server-side session handling.
4. Build trusted admin workflows to assign roles and dataset access; no browser endpoint may accept self-assigned roles.
5. Implement audited server-side ingestion, validation and publication operations.
6. Add disposable Auth test users for each role and verify allowed and denied operations through the Supabase Data API.
7. Review Storage buckets, API routes, server actions, Edge Functions and service credentials before exposing upload or write workflows.
8. Grant public SELECT only to approved publication views after source rights and the public-data release decision are recorded.
9. Obtain written permission before importing or displaying actual Malawi Stock Exchange data.

This is a secure database access baseline, not a finished production login/application integration.
Do not remove the launch gates or call the system production-authenticated until they pass.
