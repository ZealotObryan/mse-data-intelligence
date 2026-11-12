# Database publication gate

Migration `002_publication_gate.sql` adds a database-enforced publication
check and a narrow view for approved observations.

## Publication checks

A dataset can move to `approved_public` only when its validation status is
`passed` and its source has `permission_status = approved`. Non-synthetic
datasets additionally require explicit redistribution permission and
`public_display` permission at both dataset and source level.

## Public read surface

The `public_market_observations` view exposes only observations whose dataset
is approved for public publication, whose source is approved, and whose own
validation status is passed. Raw tables remain private.

## Deployment cautions

This migration does not create roles, enable row-level security, or grant API
access. Review view ownership and PostgreSQL security-invoker behavior for the
target server version before granting access. Apply migrations in order and
test with restricted database roles before exposing the view.
