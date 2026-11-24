# Authentication foundation and access boundaries

## Scope

This change adds cookie-based Supabase Auth plumbing for the Next.js App Router. It does not make the public demonstration dashboard private, create users, assign application roles, grant database permissions, or connect production environment variables.

The dashboard remains public and visibly marked as synthetic demo data. Sign-in is an entry point for future authenticated workflows, not proof that a user is authorised to access a dataset.

## Identity and session handling

- Use `@supabase/ssr` with `@supabase/supabase-js` for cookie-backed Next.js sessions.
- Browser-visible configuration is limited to `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`.
- The root Next.js `proxy.ts` refreshes sessions using `supabase.auth.getClaims()`.
- Server-side clients are request-scoped and use the cookie store.
- Never use `getSession()` as server-side proof of identity or authorisation.
- No service-role or secret key is used by this application code.
- Redirect destinations are restricted to local absolute paths to prevent open redirects.
- Missing environment configuration is handled without breaking the public demo.

## Data access matrix

These are the intended application permissions. Database RLS remains the enforcement layer; UI visibility is not a security boundary.

| Identity / role | Read private datasets | Create / update data | Delete data |
|---|---|---|---|
| Anonymous visitor | No | No | No |
| Authenticated user without an app role or dataset scope | No | No | No |
| Analyst | Read only assigned datasets | No direct browser writes | No |
| Data steward | Read assigned datasets and validation metadata | Through controlled ingestion workflow only | No direct browser deletes |
| Publisher | Read assigned datasets and publication metadata | Through approved publication workflow only | No direct browser deletes |
| Platform administrator | Operational access through trusted server-side administration | Explicitly authorised administrative workflows | Explicitly authorised administrative workflows |

## Existing database baseline

The Supabase project already has RLS enabled on the 16 application tables, with role and dataset-scope checks established in migrations 001–006. Browser clients must not write role assignments, dataset scopes, or audit events. No new database policy or schema change is made in this PR.

Before any future write endpoint is introduced, review the endpoint, its caller-scoped database client, views, functions, storage policies and any service credential use. Test both permitted and denied cases with synthetic identities before merge.

## Deployment prerequisites

The following variables are configured only for the `feat/supabase-auth-foundation` Vercel Preview branch. They are not configured for Production:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

Before testing sign-in, configure Supabase Dashboard → Authentication → URL Configuration:

- Site URL: `https://mse-data-intelligence.vercel.app`
- Local callback: `http://localhost:3000/auth/callback`
- Stable Vercel branch callback: `https://mse-data-intelligence-git-feat-supaba-0d1b14-obriensibande-7013.vercel.app/auth/callback`
- For unique Vercel preview deployment URLs, use a project-scoped wildcard such as `https://mse-data-intelligence-*-obriensibande-7013.vercel.app/auth/callback`; remove it when preview testing is complete. The exact stable branch alias above is preferable when possible.

Create test-only identities through the project owner/admin workflow; do not use a personal or production identity as a test account. Test successful sign-in, invalid credentials, callback exchange, session refresh, sign-out, and denied database access using synthetic test identities.

The login page shows an explicit setup-pending notice when its required environment variables are absent. With the branch-scoped preview variables present, it displays the email/password sign-in form. The public dashboard remains available in either state.
