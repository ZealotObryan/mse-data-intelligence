<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->


## MSE Data Intelligence: domain and data integrity rules

- Never invent, infer, interpolate, or silently fill actual MSE prices, indices, volumes, market capitalisation, issuer financials, dividends, announcements, trading dates, or forecasts.
- Keep synthetic/demo data explicitly labelled in UI, API payloads, fixtures, screenshots and tests. Never mix demo and approved production datasets in the same series or KPI.
- Preserve source ID, source record ID, retrieval timestamp, currency, unit, exchange/session context, adjustment basis, licence/permission status and data quality status with every canonical observation.
- Do not connect a market-data provider, scrape the MSE website, cache or redistribute MSE content, or enable public display until written permission and provider terms explicitly cover intended use, storage, caching and redistribution.
- A provider's coverage of US/global equities is not evidence that it covers Malawi Stock Exchange listings. Verify exact symbols, exchange coverage, timestamps, corporate actions and licensing before adapter implementation.
- Show currency and units explicitly. Use MWK only when the source confirms that currency. Never assume a provider's default currency.
- Distinguish last close, delayed quote, indicative value and real-time quote. Show source and "as of" time; never label stale/last-close data as live.

## Financial calculations and chart rules

- Use decimal-safe arithmetic (prefer `decimal.js`) for money, prices, percentages, ratios and financial aggregation. Do not use raw JavaScript floating-point arithmetic for financial values. Define rounding, precision, sign, missing-value and denominator-zero behavior in tested domain functions.
- Use a dedicated, tested indicator implementation (for example `technicalindicators`) only where needed. Document input window, warm-up/null periods, price basis and adjustment assumptions. Do not silently replace missing candles.
- Chart components must handle empty data, a single point, out-of-order timestamps, duplicate timestamps, null/missing OHLCV fields, stale series, market holidays, weekends and closed-market states without throwing.
- Use TradingView Lightweight Charts for candlestick/OHLCV or high-density time-series needs; keep it in a Next.js Client Component, dynamically loaded where required. Use container measurement/ResizeObserver or supported auto-sizing, clean up chart instances/subscriptions, and preserve accessible labels and keyboard alternatives.
- Include the Lightweight Charts NOTICE attribution and a TradingView link on a public page when the library is used, as required by its licence.
- Retain Recharts for simple dashboard plots where it already works well. Do not replace a working chart library without a concrete product or performance reason.
- Prefer shadcn/ui patterns for accessible controls and tables. For interactive tables, use TanStack Table with server-side sorting/filtering/pagination for large datasets. Keep table state and row actions accessible.
- Tremor Raw components are optional building blocks, not a mandatory wholesale framework. Check compatibility with the repository's current React and Tailwind versions before adding packages.

## Data-provider and backend rules

- Never call external market-data APIs directly from browser components. Use a server-side provider adapter/proxy with schema validation, timeout, retry/backoff, rate limiting, cache policy, provenance and safe error handling.
- Keep API keys and service credentials server-side only. Never expose secrets in NEXT_PUBLIC variables, client bundles, source maps, logs or committed fixtures.
- Keep provider-neutral canonical schemas and validate exact provider JSON examples before mapping fields. Preserve raw response metadata and provider error/rate-limit responses.
- Cache only where provider terms permit it. Cache keys include provider, symbol, interval, adjustment basis and query parameters. Return cached/stale status and source timestamps to the UI.
- Do not poll continuously. Pause or slow refresh when the page is hidden, respect verified market sessions and provider quotas, and use bounded retries. Do not infer Malawi market hours from another exchange's calendar.
- A free tier is not an unlimited production entitlement. Verify current quotas, exchange coverage, delayed/realtime entitlements and commercial terms before selecting a provider.

## Mobile-first financial UX rules

- Design and test at 375px width first; progressively enhance at larger breakpoints using Tailwind's mobile-first semantics (unprefixed styles are mobile; `sm:`, `md:`, `lg:` apply at minimum widths).
- Every interactive control should have at least a 44px by 44px touch target where practical, clear focus states and accessible names.
- Use `min-height: 100dvh` / `min-h-dvh` for viewport-bound shells and account for safe-area insets.
- On narrow screens, transform dense quote/screener tables into compact ticker cards showing symbol, last price with MWK label, percentage move, and sparkline. Keep the full data table for larger screens; do not simply squeeze all columns.
- Provide fixed bottom navigation for Market, Watchlist, Indices and News only if those routes/actions exist. Respect safe-area insets and ensure content is not obscured.
- Use mobile bottom sheets/drawers for filters and detail panels where appropriate (Vaul may be used with shadcn/ui); preserve keyboard, focus, escape, swipe and reduced-motion behavior.
- Financial charts must resize to their parent container. Avoid page-level horizontal overflow. Do not hijack vertical page scrolling with chart wheel/touch gestures; configure chart interaction on touch devices.
- Provide a data-lite experience: cache only permitted public data with source and freshness metadata, avoid heavy polling and large payloads, and pause background work when the tab is hidden. Use localStorage/IndexedDB only for non-sensitive cache/preferences, never as an authorization source.
- Test 360px, 375px, 390px, 768px and desktop layouts, keyboard navigation, touch scrolling, loading/empty/error/stale/closed-market states, and reduced-motion preferences before calling mobile work complete.

## Engineering and release gates

- Read relevant current Next.js documentation in the installed package before implementing framework APIs.
- Inspect existing components and design tokens before adding dependencies. Prefer small, targeted components over a wholesale UI rewrite.
- For every Supabase change, define CRUD access by role, enable RLS on API-exposed tables, inspect views/functions/storage/server endpoints, and test allowed and denied access with disposable identities before merge.
- Add unit tests for financial arithmetic and data normalization; add integration tests for provider adapters and access control. Never mark a check as passed unless it ran and its result was observed.
- Keep synthetic data visually and technically separate from approved real data. Do not merge or deploy changes that accidentally turn demo figures into apparent live market data.
