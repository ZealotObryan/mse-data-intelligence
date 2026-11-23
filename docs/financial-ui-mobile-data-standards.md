# Financial UI, charting and mobile-data implementation standards

This document turns the supplied library/API recommendations into project-specific implementation guidance. It complements `AGENTS.md`; it does not authorise any real market-data integration.

## Current repository baseline

- Next.js 16.4.6, React 19.3.0, Tailwind CSS 4.3.3, TypeScript 5.
- Recharts 3.10.1 and Lucide are already installed.
- The dashboard is built around the existing main page and global stylesheet; do not assume a separate market route exists.
- Market figures are synthetic illustrative data. No market provider is connected or approved.
- A dedicated Supabase project exists, but the web app is not yet connected to it. Database RLS does not replace server-side session and endpoint authorisation.

## Library selection

| Need | Preferred approach | Decision |
|---|---|---|
| OHLC/candlestick and dense time series | TradingView Lightweight Charts | Add when instrument detail/time-series view is implemented. Client-only; responsive sizing and cleanup required. |
| Existing dashboard plots | Recharts | Keep for simple overview plots until there is a measurable reason to replace them. |
| KPI cards, sparklines, dashboard blocks | Tremor Raw | Reuse selectively; current docs target React 18.2+ and Tailwind CSS 4+, aligned with this repository's major versions. Avoid creating a second design system. |
| Accessible table controls and data grids | shadcn/ui patterns + TanStack Table | Build a project-owned screener/watchlist table. Fetch rows server-side; use client components for table interactions. Confirm TanStack version/API before installing. |
| Mobile filters/details | Vaul with shadcn/ui | Optional for filter/detail workflows that benefit from swipe-dismiss. |
| Financial math | decimal.js | Use for monetary and ratio calculations, with explicit rounding and precision policy. |
| Technical indicators | technicalindicators or existing tested Python analytics | Add only when needed; specify period, warm-up, missing data and adjustment basis. |

## Chart implementation contract

For Lightweight Charts:
1. Keep chart creation in a client-only component; do not execute during server rendering.
2. Size to the parent using `ResizeObserver` or supported `autoSize`; avoid fixed desktop widths.
3. Remove chart instances, observers and subscriptions during cleanup.
4. Validate strictly increasing unique timestamps and define handling for invalid or missing candles.
5. Treat volume as optional; null volume must not crash rendering.
6. Show empty/insufficient-history, stale-data, market-closed/holiday and source/as-of states.
7. Configure mobile scroll/scale gestures so chart interaction does not block vertical page scrolling.
8. Include the Lightweight Charts NOTICE attribution and TradingView link on a public page.

## Provider evaluation: do not pick a global-market API by default

Finnhub, Alpha Vantage and Polygon/Massive may be useful provider examples or for non-MSE demonstrations, but their availability does not establish Malawi Stock Exchange coverage or rights to redistribute MSE data.

Before selecting a provider, create a written coverage and licensing matrix for:
- exact MSE symbols and instrument types;
- exchange and trading venue coverage;
- daily OHLCV, quotes, corporate actions, issuer fundamentals and announcements;
- data delay and timestamp/timezone;
- free-tier quotas and rate limits;
- commercial use, public display, caching and redistribution rights;
- correction policy, reliability and service-level terms.

Alpha Vantage's published free service currently states 25 requests/day for most datasets, with separate terms for verified open-source/educational projects. Its docs describe daily global-equity series, but some intraday and realtime entitlements are premium and commercial use requires contacting sales. Do not treat the free tier as a production MSE feed.

No provider is approved by this document. Continue using clearly labelled synthetic fixtures until written data rights and exact MSE coverage are verified.

## Canonical market data shape

This is the project's normalized internal contract, not a claim about any provider's JSON response:

```ts
type MarketBar = {
  instrumentId: string;
  sourceId: string;
  sourceRecordId: string;
  timestamp: string;          // ISO-8601 with explicit timezone
  currency: "MWK" | string;   // only as confirmed by source
  interval: "1d" | "1w" | "1m" | string;
  open: string | null;        // decimal string, never binary float
  high: string | null;
  low: string | null;
  close: string | null;
  volume: string | null;
  adjustmentBasis: "raw" | "split_adjusted" | "total_return" | "unknown";
  marketStatus: "open" | "closed" | "holiday" | "unknown";
  retrievedAt: string;
  permissionStatus: "approved" | "restricted" | "unknown";
  dataQualityStatus: "passed" | "warning" | "failed" | "unverified";
};
```

Validate external JSON at the server boundary. Map provider-specific keys into this shape only after validating an actual response fixture. Never put API secrets in client code.

## API caching and Malawi data-lite mode

- Route external requests through a backend adapter; never fetch a provider from a chart component.
- Respect provider quotas and licence terms. Cache keys include provider, symbol, interval, adjustment basis and query range.
- Return `source`, `asOf`, `retrievedAt`, `isStale`, `cacheAgeSeconds` and `marketStatus` with UI payloads.
- Cache only where provider terms permit. For daily closing data, prefer a cache refreshed after a verified market close rather than repeated polling.
- Pause refresh while the page is hidden; use bounded backoff after 429/5xx responses.
- Cache only non-sensitive, permitted public data and preferences in browser storage. Never store tokens, secrets, personal records or authorization state in localStorage.
- Provide low-data mode: load compact summaries first, defer chart history until requested, avoid autoplay/background polling.

## Mobile market workspace specification

Target 375px first; verify 360px, 375px, 390px, 768px and desktop.

### Navigation
- Desktop may retain sidebar/header.
- Mobile should use fixed bottom thumb-zone navigation for Market, Watchlist, Indices and News only once those destinations are implemented.
- Respect `env(safe-area-inset-bottom)`; reserve page padding so content is never hidden behind navigation.
- Use `100dvh`/Tailwind `min-h-dvh` for viewport shells.

### Quotes and screeners
- Below 768px, render compact cards instead of squeezing the wide desktop quote table.
- Each card shows symbol, last traded/closing price with MWK label, percentage change and a mini trend line when history exists.
- Put secondary OHLCV details in a disclosure or bottom sheet.
- Desktop retains full sortable/filterable table. On medium widths, allow column visibility and horizontal table scrolling inside a labelled, keyboard-focusable container.
- Minimum touch target: 44x44 CSS pixels for timeframe controls, filters, row actions and bottom navigation.

### Charts
- Charts fit parent width and never cause page-level horizontal overflow.
- Timeframe controls wrap or scroll inside their own control group.
- Avoid touch drag/wheel settings that trap vertical page scrolling.
- Show skeleton, empty, stale, error and closed-market states explicitly.

## Financial correctness guardrails

- Use decimal-safe arithmetic for MWK amounts, price changes, percentages, yields, P/E and financial aggregation.
- State exact formula, denominator and price/date basis for each derived metric.
- Distinguish percentage points from percent change.
- A missing/zero denominator yields an unavailable result with a reason, not Infinity/NaN or an invented zero.
- Technical indicators disclose period and price basis, including split/dividend adjustments.
- Use chronological validation for time series; do not randomly shuffle observations.
- Preserve raw source values; do not overwrite them with adjusted or derived values.

## Suggested implementation sequence

1. **Market data contract and chart foundation:** validate canonical bar schema, build a client-only responsive Lightweight Charts component using synthetic fixture data clearly labelled, add chart empty/stale/closed states and TradingView attribution.
2. **Mobile market workspace:** responsive quote cards, fixed bottom nav for existing routes, safe-area handling, 44px controls and low-data loading.
3. **Screener/watchlist table:** shadcn-style primitives and TanStack Table, sorting/filtering/visibility, mobile card transformation.
4. **Financial calculation hardening:** decimal.js wrappers and tests for price/return/ratio calculations.
5. **Provider adapter evaluation:** only after coverage and licensing evidence; add one provider behind server-side proxy/cache with exact response fixtures.
6. **End-to-end verification:** 360–390px mobile tests, keyboard/touch accessibility, API quota tests, hidden-tab polling tests, empty/market-closed/error states and database role access tests.

## Official references

- TradingView Lightweight Charts: https://www.tradingview.com/lightweight-charts/
- Lightweight Charts setup and licence/attribution: https://github.com/tradingview/lightweight-charts/blob/master/website/docs/intro.mdx
- Lightweight Charts chart sizing: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ChartOptionsImpl
- Tremor Raw installation: https://www.tremor.so/docs/getting-started/installation
- Tremor components: https://npm.tremor.so/components
- shadcn/ui data table: https://ui.shadcn.com/docs/components/radix/data-table
- Tailwind responsive design: https://tailwindcss.com/docs/responsive-design
- Vaul: https://docs.vaul.emilkowalski.sk/getting-started
- Alpha Vantage API docs: https://www.alphavantage.co/documentation/
- Alpha Vantage API usage limits: https://www.alphavantage.co/support/api-key/

References checked 23 November 2026. Recheck docs, pricing, API limits and terms before implementation or provider selection.
