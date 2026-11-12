# Dependency security review

## Finding

The Vercel production build for the forest-green UI deployment completed successfully but printed an npm audit summary of **8 moderate severity vulnerabilities** during `npm ci`.

## What is known

- The build log did not include the advisory IDs, affected dependency paths, patched versions or whether the findings are direct or transitive dependencies.
- The current manifest pins Next.js and eslint-config-next to 16.4.6 and React/React DOM to 19.3.0, with several other packages using semver ranges.
- A production build succeeding does not mean the dependency tree is free of known vulnerabilities.

## Remediation decision

No blind `npm audit fix --force` or major-version upgrade has been applied. That could introduce breaking changes in Next.js, React, Tailwind or the charting stack without knowing which package paths are affected.

## Next safe review

1. Run `npm audit --json` against the exact lockfile and retain the full report as a CI artifact.
2. Classify each advisory by package path, severity, exploitability and whether it is in the production dependency graph.
3. Apply non-breaking patched versions and regenerate `package-lock.json`.
4. Run lint, TypeScript/production build and the Python test suite.
5. Recheck the audit report and deploy only after reviewing the resulting diff.

**Status:** open; exact advisory details still need to be retrieved.