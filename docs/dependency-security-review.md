# Dependency security review

## Current audit snapshot

An isolated audit of the repository lockfile on 18 November 2026 found **14 high-severity development-dependency findings**, with **0 moderate and 0 critical findings** in that audit result. A separate production-only audit (`npm audit --omit=dev`) returned **0 vulnerabilities** across the production dependency graph.

The audit result is a point-in-time snapshot. It should be rerun against the exact lockfile used for each release.

## Affected dependency paths

The remaining high-severity findings are concentrated in the development/lint toolchain, including:

- `eslint-config-next` and `@next/eslint-plugin-next`
- `typescript-eslint` and its parser, plugin, type-utils, utils and typescript-estree packages
- Transitive glob/matching packages including `fast-glob`, `fdir`, `micromatch`, `picomatch` and `tinyglobby`
- `eslint-import-resolver-typescript`

The audit specifically reports a high-severity `picomatch` ReDoS advisory (GHSA-fc5q-39xc-vjpf) in the development dependency tree. The affected paths are used by lint/build tooling; the production-only audit did not report vulnerable production dependencies.

## Remediation attempted

A standard, non-force `npm audit fix` was tested in an isolated sandbox. It updated compatible development transitive dependencies and the local lockfile, but the subsequent audit still reported 14 high-severity findings.

npm's suggested force remediation would downgrade `eslint-config-next` to 14.2.35, a breaking framework/tooling change relative to this project's Next.js 16.4.6 setup. That force fix was deliberately not applied.

No lockfile changes from the isolated experiment were committed or deployed.

## Validation and release implications

- The current PR #13 branch passed GitHub Actions Python analytics tests, ESLint, and a Next.js production build.
- A local isolated lint and production build also passed after the non-force audit fix.
- The isolated sandbox did not have the Python test dependency installed, so Python tests were not re-run there.
- Production dependencies currently audit clean, but the development-toolchain findings remain open and should be tracked.

## Next safe steps

1. Review the exact advisories and patched release compatibility for the Next.js 16 ESLint toolchain.
2. Prefer a compatible patched ESLint/plugin dependency path or a deliberate lint-toolchain migration over a blind force downgrade.
3. Regenerate the lockfile on a dedicated branch and inspect the dependency diff.
4. Run CI, lint, TypeScript/production build and Python tests.
5. Re-run both full and production-only audits against the committed lockfile.
6. Keep the findings open until the full audit is clean or the remaining risk is explicitly accepted and documented.

**Status:** partially investigated; production dependency graph clean in the latest audit, development dependency remediation still open.
