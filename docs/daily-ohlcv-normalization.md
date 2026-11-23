# Daily OHLCV normalization contract

The helper `normalizeDailyBars(records, { expectedSessions })` validates and normalizes daily candles without creating synthetic observations.

- Dates must be real `YYYY-MM-DD` calendar dates; bars are sorted ascending.
- OHLC values are required finite positive decimals. Volume may be `null`; when present it must be non-negative.
- High/low and open/close relationships are validated. Incomplete/invalid bars are returned in `rejected`, never filled with guessed prices.
- Duplicate dates are counted; the last valid input record wins. Invalid later duplicates do not erase earlier valid bars.
- Weekends and holidays are not inferred. Missing sessions are reported only when the caller supplies an authoritative exchange calendar; otherwise `missingSessions` is `null`.
- This helper does not establish source permission, freshness, instrument identity, adjustment basis or market status. Those remain server-boundary responsibilities.
- Never use this contract to imply synthetic fixtures are real MSE prices.

Return shape: `{ bars, rejected, duplicates, missingSessions }`.
