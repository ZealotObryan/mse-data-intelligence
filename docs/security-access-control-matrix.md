# Security access-control matrix and implementation gate

## Status and scope

This document defines the intended least-privilege access model for the PostgreSQL data foundation. It is a design and deployment gate, **not evidence that these permissions or row-level security policies have already been deployed**.

The repository currently contains migrations 001–003 and a PostgreSQL persistence adapter, but no provisioned production database or connected application authentication layer. Do not expose the raw tables or publication views until the identity provider, role claims, grants, row-level security (RLS), and positive/negative access tests are implemented.

The model is PostgreSQL-first and can be adapted to Supabase. If Supabase is selected, use trusted app metadata or a protected database role mapping for authorization; never use user-editable profile metadata as an authorization source. Never expose a service-role or secret key in browser code or a `NEXT_PUBLIC_*` variable.

## Principals

| Principal | Purpose | Trust boundary |
| --- | --- | --- |
| Anonymous visitor | Read approved public market and issuer views only | No access to raw tables, staging, ingestion, user records or audit logs |
| Authenticated learner | Use learning content and manage only their own learning progress, once persistence is implemented | Cannot access market ingestion or governance data |
| Analyst | Read approved and explicitly authorised internal research data; prepare analysis | Cannot approve source permissions or publish datasets |
| Data steward | Register sources, upload/ingest artifacts, review validation issues and prepare datasets | Cannot grant themselves publication approval |
| Publisher / compliance approver | Review evidence and approve or withdraw publication within delegated scope | Approval actions must be attributable and audited |
| Platform administrator | Manage platform configuration and user-role assignments | No routine direct market-data editing; break-glass access is logged |
| Backend ingestion worker | Write ingestion runs, staging records and validated observations through a server-only credential | Credential never reaches the browser; scoped to required tables/actions |

A single person may hold multiple business roles only through an explicit, audited assignment. The database must enforce the effective permissions; hiding UI controls is not authorization.

## Table-level access matrix

Legend: R = read, C = create, U = update, D = delete, — = no access. “Own” means rows whose owner/user ID matches the authenticated subject. All permissions are subject to row-level policy and column-level restrictions where needed.

| Data object | Anonymous | Learner | Analyst | Data steward | Publisher | Platform admin | Ingestion worker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `data_sources` | — | — | R (approved/internal scope) | R/C/U | R/U (permission decision) | R | R/C/U (ingestion metadata only) |
| `datasets` | — | — | R (authorised scope) | R/C/U | R/U (publication fields) | R | R/C/U (staging fields only) |
| `ingestion_runs` | — | — | R (authorised scope) | R | R | R | R/C/U |
| `instruments` | — | — | R | R/C/U (registry proposals) | R | R | R (no registry administration) |
| `market_observations` | — | — | R (authorised scope) | R | R | R | R/C (validated staging only); no unrestricted U/D |
| `validation_issues` | — | — | R | R/C/U | R | R | R/C/U |
| Issuer profile/financial/dividend/action/announcement raw tables | — | — | R (authorised scope) | R/C/U (source-backed proposals) | R | R | R/C (approved ingestion path) |
| Approved public market/issuer views | R | R | R | R | R | R | R |
| Learner progress (future) | — | R/C/U/D (own) | — | — | — | R (support case only; audited) | — |
| User-role assignments (future) | — | R (own safe profile only) | — | — | — | R/C/U/D | — |
| Audit events (future) | — | — | R (own/relevant scope) | R (relevant scope) | R | R | C (append only) |

### Important qualifications

- The table describes intended capabilities, not current grants. Every raw table remains private until an explicit migration grants the minimum required privileges.
- Anonymous users should receive SELECT only on approved, security-invoker publication views, and only after view-owner, underlying-table grants and RLS behavior are tested. Do not grant anonymous SELECT on raw tables.
- Analyst and steward access must be further scoped by dataset/source assignment and data classification. A generic `authenticated` role is not sufficient.
- Publisher permissions must be separated from ingestion and validation permissions. A worker cannot approve its own data.
- No routine principal receives broad DELETE on source evidence, ingestion history, validation issues or audit records. Use controlled correction/withdrawal workflows and preserve lineage.
- Learner progress, user profiles, role assignments and audit events are future objects; no such tables are implied to exist today.

## Required database controls

1. Enable RLS on every API-exposed table in exposed schemas. Default-deny access; add explicit policies for each principal and operation.
2. Revoke broad default privileges and avoid granting raw-table access to `anon` or ordinary `authenticated` users.
3. Use narrowly scoped database roles for migrations, ingestion, application reads, governance and break-glass administration. Do not run the application as a schema owner.
4. For UPDATE, define both the row visibility predicate (`USING`) and the post-update constraint (`WITH CHECK`). UPDATE generally also requires an applicable SELECT policy.
5. Ensure role assignment is controlled by a trusted server/admin process. Users must not be able to elevate themselves by editing profile metadata.
6. Use security-invoker views (PostgreSQL 15+) and verify the invoking role has only the required underlying table privileges and is still subject to RLS.
7. Avoid SECURITY DEFINER functions. If one is unavoidable, pin a safe search_path, fully qualify objects, validate caller identity/role, revoke default PUBLIC execution and test privilege boundaries.
8. Review RPCs/functions, triggers, storage buckets and policies, API route handlers, server actions, background jobs and logs for alternate paths to the same records.
9. Keep secrets in server-only environment variables or a managed secret store. Rotate credentials and ensure no service credential is included in client bundles, source maps or logs.
10. Record publication, permission, role-assignment, correction and withdrawal events in an append-only audit trail with actor, action, target, timestamp and reason.

## Publication workflow separation

- Data steward registers source metadata and records licence/permission evidence.
- Ingestion worker archives the original artifact, computes its checksum and writes staging/ingestion records.
- Validation process records checks and rejects or flags bad data without silently coercing source values.
- Publisher independently verifies source permission, intended use, validation status and evidence before publication.
- Database publication trigger remains the final guard. A successful import or passing validation does not itself grant redistribution permission.
- Withdrawal must immediately remove the affected records from public views while preserving the evidence and audit trail.

## Required access-control test plan before merge/deployment

Use disposable test data and test identities for every role. Run tests against the actual target PostgreSQL/Supabase version and API path, not only unit tests or mocked policies.

| Test | Expected result |
| --- | --- |
| Anonymous SELECT from each raw table | Denied |
| Anonymous SELECT from approved publication views | Only approved, passed, permitted records returned |
| Anonymous read of pending, rejected, withdrawn or restricted dataset | No rows |
| Learner reads own progress | Allowed |
| Learner reads or modifies another learner's progress | Denied |
| Analyst reads assigned internal dataset | Allowed |
| Analyst writes source permission or publication approval | Denied |
| Data steward creates ingestion/source evidence | Allowed within assigned scope |
| Data steward changes publication status to approved | Denied |
| Ingestion worker writes valid staging/ingestion records | Allowed |
| Ingestion worker changes source licence approval or publishes | Denied |
| Publisher approves eligible dataset with evidence | Allowed and audited |
| Publisher approves dataset with failed validation or missing permission | Rejected by database gate |
| Publisher reads/updates unrelated restricted dataset | Denied |
| Authenticated user changes their own role/privilege | Denied |
| API route, RPC, view, storage or background worker bypass attempt | Denied |
| UPDATE with row ownership/scope changed to an unauthorised value | Denied by WITH CHECK |
| DELETE from immutable evidence/audit history | Denied |

For each test, record the principal, operation, target, expected result, actual result and test fixture ID. Include both successful and denied cases in CI or a repeatable deployment verification script. Run database security advisors/lints where supported.

## Deployment sequence

1. Select and document the identity provider and server-side session/claim contract.
2. Finalise the role-to-dataset scope mapping and confirm which API schemas are exposed.
3. Implement grants, RLS policies and security-invoker views in a reviewed migration.
4. Review functions/RPCs, storage, API routes, server actions and background workers for bypasses.
5. Execute the complete positive/negative test matrix against disposable data.
6. Run database advisors, migration checks, application tests and secret-exposure checks.
7. Only then grant application access and deploy the database connection.
8. Verify production role behavior using non-privileged test identities before any real data is loaded.

## Current known gaps

- No provisioned production PostgreSQL database is connected.
- The existing migrations do not create application roles, grants or RLS policies.
- No connected application authentication/authorization implementation has been verified.
- The PostgreSQL persistence adapter accepts a caller-supplied DB-API connection; it does not establish credentials or a connection pool.
- Learner progress, user-role assignments and audit-event persistence are not yet established by the migrations inspected.
- The existing publication views use `security_invoker = true`, but access remains blocked pending explicit grants/RLS review and role testing.

These gaps are release blockers for exposing database-backed data or administrative workflows. Do not represent this document as a completed security implementation.
