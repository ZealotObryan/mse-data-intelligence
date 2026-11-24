# MSE live-data access assessment and ingestion plan

**Assessment date:** 24 November 2026  
**Project:** MSE Data Intelligence  
**Status:** Research complete; external data ingestion remains disabled pending written clarification from the Malawi Stock Exchange (MSE).

## Executive decision

The project should move from permanently synthetic dashboard fixtures towards a permissioned MSE-source integration. The public MSE website exposes current market snapshots and a Market Reports catalogue, but the reviewed public pages do not expose a documented API, downloadable data schema, feed credentials, or published redistribution terms for a third-party educational website.

MSE's site disclaimer says website and data access is for personal and non-commercial use, identifies MSE as copyright owner unless otherwise stated, and says commercial use requires a data agreement. It also disclaims guarantees of accuracy, timeliness and completeness. The disclaimer does not clearly answer whether a free, publicly accessible independent educational site may automatically retrieve, store, transform and republish the data. Obtain written clarification before automated retrieval or public display.

This is a permission gate, not a conclusion that the project is commercial or that permission is necessarily unavailable.

## Official source inventory

| Source | Publicly visible capability | Current limitation | Proposed use after confirmation |
|---|---|---|---|
| MSE homepage / Market Watch | Main Board and debt security snapshots; update timestamp and market status; Market Watch includes price, change, volume and turnover | No documented public API contract or redistribution licence identified | Market overview and latest published quote snapshot |
| Market Reports | Daily, weekly, monthly, quarterly and annual report catalogue | Report files are downloadable artefacts; automated retrieval, parsing, archival and republication rights need confirmation | Historical observations, trading activity and market research |
| Published Accounts | Issuer financial reports are linked from MSE navigation | Reuse, storage and republication rights and document completeness need confirmation | Issuer fundamentals with direct document attribution |
| Announcements / Corporate Announcements | Public issuer and exchange announcements | No documented feed/API or reuse terms identified | News and corporate-actions timeline |
| Data Portal | Official product page exists | Page currently says “Coming Soon” | Revisit when operational; request access details |
| Website Integration | Official product page exists | Page currently says “Coming soon” | Preferred official web integration route if MSE offers it |
| Real-time Data Feed | Official product page exists | Page currently says “Coming Soon” | Preferred intraday route if access, cost and display rights are offered |
| Fees and Prices | Official product page exists | Page currently says “Coming Soon” | Request current educational/non-commercial pricing or waiver |

## Key source observations

- The MSE disclaimer states that website/data access is for personal and non-commercial use, identifies MSE copyright, and says commercial use requires notifying the Exchange to sign a data agreement.
- The disclaimer says information is provided as-is and may not be accurate, timely or complete.
- The MSE market schedule published on its website lists Pre-Open 09:00–09:30, Open 09:30–14:30, Close 14:30–15:00 and Post Close 15:00–17:00. Treat this as indicative website information and revalidate against official notices/holidays.
- On 24 November 2026, the MSE public snapshot showed an update time of 11:55 and Market Status: Open. This is an example of a published snapshot, not evidence of a documented real-time API.
- The Data Portal, Website Integration, Real-time Data Feed and Fees and Prices pages were reviewed on 24 November 2026; each displayed “Coming Soon” (wording/capitalisation varies).
- The reports catalogue showed a daily report for 23 November 2026 and a sequence of recent daily reports, alongside weekly and monthly/quarterly/annual reports.
- The report catalogue's linked daily report returned an application/octet-stream response to the research browser. This confirms the link points to a downloadable file but does not establish a stable format, extraction contract or right to republish its contents.

## Permission questions to send MSE

Request written answers for a free, independent educational project with no subscriptions, advertising, sponsorship, paid access or investment execution:

1. Does the personal/non-commercial website disclaimer permit an independent, publicly accessible educational website to display MSE market snapshots and derived summaries?
2. Is automated retrieval of the public Market Watch page permitted? If yes, what polling frequency, user-agent identification, rate limits and technical restrictions apply?
3. May daily/weekly/monthly reports be downloaded, parsed into structured observations, retained for historical analysis and displayed as derived charts/tables with attribution and links to original reports?
4. May raw prices, volumes, turnover, index values and derived values be displayed to visitors? Are any fields restricted?
5. Is there an official API, CSV/Excel export, website widget, embeddable integration, or real-time feed available now? If not, is there an expected availability date?
6. What are the data delay, timestamps/timezone, correction policy, market calendar, instrument coverage and data definitions?
7. Are there separate conditions for issuer accounts, announcements, dividends, corporate actions and debt securities?
8. Is there an educational/non-commercial access arrangement, fee waiver or written permission letter that can cover this project?
9. What exact MSE attribution, disclaimer, logo use and link-back wording is required?
10. May the project retain source documents and normalized historical data in a private database for reproducible analysis, and for how long?

## Proposed ingestion architecture

Keep source acquisition separate from parsing, validation, storage and publication. Never let the browser contact MSE directly and never expose provider credentials.

1. **Source registry** — approved source URLs, source owner, access method, permitted fields, allowed retrieval frequency, retention, attribution, redistribution and effective approval dates.
2. **Acquisition adapter** — initially operator-assisted report upload or an MSE-approved integration. Add scheduled retrieval only after written permission and documented limits. No undocumented endpoints, bypasses, CAPTCHA workarounds or aggressive scraping.
3. **Immutable raw archive** — private object storage with content SHA-256, original filename, source URL, retrieval timestamp, content type and uploader/job identity. Do not publicly serve raw source files unless explicitly permitted.
4. **Parser layer** — versioned parsers per source format. Preserve raw text/values and parser version. Reject unexpected layouts rather than guessing columns.
5. **Canonical normalization** — map to instrument, observation date/time, market session, quote/close, change, volume, turnover, index and currency fields. Preserve source precision and nulls.
6. **Validation and reconciliation** — instrument allow-list, date/session checks, decimal-safe numeric parsing, OHLC consistency where OHLC exists, duplicate detection, cross-field checks and comparison with the source document. Quarantine anomalies.
7. **Approval gate** — record source permission, data quality outcome and reviewer approval. Unknown/restricted permission or failed validation blocks public publication.
8. **Database** — private raw/staging tables; role-scoped published read views only after the permission gate is satisfied. RLS must apply to exposed tables/views; use security-invoker views where supported and review all functions/endpoints.
9. **Public API** — read-only server-side endpoints with explicit source, observed-at, retrieved-at, market status, freshness, quality and demo/live labels.
10. **Monitoring** — retrieval failures, report delays, parser drift, missing sessions, stale data, duplicates, source corrections and quota/rate-limit events.

## Canonical observation contract

This is an internal target contract, not a claim about MSE's current response format.

- instrument_code — exact source instrument identifier.
- instrument_type — equity, debt security, index or other confirmed type.
- observation_date — exchange-local trading date.
- observed_at — source observation timestamp with explicit timezone where available.
- market_session — pre-open, open, close, post-close, end-of-day or unknown.
- price_basis — last traded, closing, indicative, bid, ask or other source-defined basis.
- price, change, change_percent — decimal strings; never binary floating point.
- volume, turnover — nullable decimal strings with source units retained.
- currency — only set where confirmed by the source.
- source_id, source_url, source_record_id, raw_artifact_sha256.
- retrieved_at, parser_version, quality_status, permission_status.
- publication_status — blocked, pending_review, approved or withdrawn.

Do not map an MSE displayed number into last_traded_price or closing_price unless the source explicitly defines that basis. Do not treat a zero volume as missing, or missing volume as zero. Keep unadjusted source observations separate from derived/adjusted series.

## Data freshness and UI behaviour

- Label a quote “Live” only if MSE confirms the feed is live and supplies a reliable observation timestamp.
- Otherwise use precise labels such as “MSE website snapshot”, “Latest published close” or “Daily report — 23 Nov 2026”.
- Show “Updated by source” and “Retrieved by this platform” separately.
- Use the exchange's Africa/Blantyre time context; preserve source timezone and raw timestamp.
- When the market is closed, show the latest available observation date, not a live badge.
- On weekends/holidays, do not mark the previous session as stale merely because no new session is expected; use the official market calendar.
- If retrieval fails, retain the last approved observation with a visible stale/unavailable label; never silently replace it with synthetic data.
- Keep synthetic fixtures in a separate namespace and visibly mark them “Demonstration data — not MSE market data”.

## Phased rollout

### Phase 0 — permission and source contract
- Send the clarification request to MSE.
- Obtain written permission or a source agreement covering retrieval, storage, derived analytics, public display, caching and attribution.
- Request sample files/API documentation, rate limits and current fee schedule.
- Keep production synthetic data unchanged until approval.

### Phase 1 — controlled daily report pilot
- Use only an approved daily report source and a small set of fields.
- Operator-assisted upload first if automation is not authorised.
- Archive the original privately, parse into staging, validate and review.
- Compare parsed output to the original report manually before publication.

### Phase 2 — public daily market intelligence
- Publish only fields and derived values explicitly permitted.
- Add provenance and freshness UI.
- Build daily time series from approved reports; no interpolation of missing trading days.
- Add source corrections and withdrawal handling.

### Phase 3 — issuer and corporate intelligence
- Add published accounts, dividends, corporate actions and announcements only under their applicable reuse permissions.
- Keep issuer financial facts linked to original reporting period, units, accounting basis and source page.

### Phase 4 — intraday feed
- Integrate MSE's official real-time feed or website integration only if offered and authorised.
- Do not reverse engineer undocumented endpoints or infer that a visible web quote equals exchange-authorised real-time redistribution.

## Security and governance requirements

- No MSE source credentials, Supabase service-role keys or ingestion secrets in client bundles.
- Separate ingestion identity from public read identity.
- Restrict create/update/delete rights to ingestion service and authorised stewards; ordinary visitors receive read-only access only to approved published data.
- Keep raw source artefacts private.
- Log each import, parse, validation, approval, correction and withdrawal.
- Use test identities and synthetic fixtures to prove allowed and denied database access before enabling publication.
- Review RLS, views, RPC functions, storage policies and server routes together; database RLS alone does not protect data leaked through an unprotected server endpoint.
- No schema migration or production database write is part of this assessment.

## Official links

- MSE homepage and disclaimer: https://mse.co.mw/
- MSE Market Reports: https://mse.co.mw/market/reports
- MSE Data Portal: https://mse.co.mw/service/3
- MSE Website Integration: https://mse.co.mw/service/7
- MSE Real-time Data Feed: https://mse.co.mw/service/4
- MSE Fees and Prices: https://mse.co.mw/service/6
- MSE Contact: https://mse.co.mw/contact

## Contact

The MSE contact page currently lists info@mse.co.mw, telephone +265 884 824 233, and WhatsApp +265 887 249 784. Confirm contact details on the official page before sending.

## Decision log

- 24 Nov 2026: MSE official public sources and service pages reviewed.
- 24 Nov 2026: No documented public API/feed contract or redistribution permission identified.
- 24 Nov 2026: Automated retrieval and public republication remain disabled pending written clarification.
