# Issuer research and corporate actions data model

## Scope

Migration `003_issuer_research_and_corporate_actions.sql` adds a source-backed foundation for company research. It creates structure only; it does not seed issuer profiles, financial statements, dividends, corporate actions or announcements.

## Tables and grain

| Table | Grain | Purpose |
|---|---|---|
| `issuers` | One issuer identity | Stable issuer key and basic legal/display identity |
| `issuer_profile_versions` | One effective-dated profile version per dataset | Historical issuer facts without overwriting earlier disclosures |
| `issuer_financial_periods` | One issuer statement and reporting period per dataset | Statement type, period, fiscal labels, audit basis and publication metadata |
| `issuer_financial_facts` | One metric fact per statement period/comparative period | Normalised numeric facts with explicit currency/unit |
| `dividends` | One issuer/instrument dividend event per dataset | Declaration, ex-dividend, record and payment dates; amount and status |
| `corporate_actions` | One issuer/instrument action per dataset | Splits, consolidations, rights/bonus issues, mergers, suspensions and other events |
| `issuer_announcements` | One issuer announcement per dataset | Headline, summary, timestamp and document/source locator |

Every sourced record links to a dataset and, where available, an ingestion run. The dataset links to its source, licence metadata, checksum and publication decision. The public read views only include records whose dataset is approved for public display and whose source is approved.

## Data handling rules

- Treat issuer disclosures as source documents; retain original files and checksums before parsing.
- Preserve the reported metric label, normalised metric code, original unit, currency, reporting period and comparative period.
- Do not mix audited and unaudited statements without a visible distinction.
- Do not annualise partial periods or derive ratios when required inputs are absent.
- Dividend dates are separate events: declaration, ex-dividend, record and payment dates must not be substituted for one another.
- Corporate actions must be applied to price histories only when the event terms and adjustment methodology are verified. Preserve unadjusted observations.
- Announcement summaries must be traceable to the original document; do not generate unsupported interpretations.
- Corrections and restatements should arrive as new source datasets/versions so historical lineage is retained.
- Do not infer missing figures, dates, share counts or statuses.

## Research metrics to calculate after data is available

- Revenue and earnings growth using comparable periods and consistent reporting basis.
- Gross, operating and net margins when the statement provides the required components.
- Current ratio and debt/equity only when definitions and inputs are available and comparable.
- Earnings per share and P/E only with valid share-count/price alignment and compatible reporting periods.
- Dividend per share and dividend yield only with verified dividend events and a clearly stated price reference date.
- Market capitalisation only with a verified price and shares outstanding on the relevant date.

Every calculated metric should retain formula/version, input fact identifiers, period, currency, assumptions and missing-data notes. These are research measures, not buy/sell recommendations.

## Security and publication

The migration creates public read views as a convenience, not an authorisation grant. Keep base tables private. Review view ownership, PostgreSQL security-invoker behaviour, grants and row-level security before exposing any view through an API. Apply the same data licensing gate as market observations. A company report being publicly downloadable does not automatically grant redistribution rights.

## Current status

This migration has not been applied to a live database. There is no provisioned MSE database, no real issuer dataset has been imported and no provider credentials are configured. The current website remains an illustrative prototype until verified, permissioned data is integrated.


## Approved-view read adapter

`mse_analytics.issuer_repository.fetch_published_issuer_period` reads one issuer and reporting period from `public_issuer_financial_facts` only. It never queries the base issuer fact tables or opens a database connection. The caller supplies a read-only connection.

The adapter maps exact metric codes to the financial calculation engine's canonical fact keys, checks reporting metadata consistency, enforces expected units, rejects duplicate mapped facts and mixed monetary currencies, and returns dataset IDs for lineage. Unknown metric codes are listed but not interpreted. It does not convert currencies, infer missing facts, or retrieve price/dividend data.

The tests use a fake DB-API connection and verify query scope and fail-closed validation. They do not constitute a live PostgreSQL integration test. A provisioned database, applied migrations, restricted database role, and approved real or synthetic dataset are still required before this adapter can be used against a live service.


## Approved issuer analysis service

`mse_analytics.issuer_service.analyze_published_issuer` composes the approved-view repository with the comparable-period calculation adapter. It loads the requested current period and, only when explicitly requested, a prior period; it then validates issuer, currency, reporting basis and chronology before calculating growth. Without a prior period, growth remains unavailable and is explained in the result.

Market price and annual dividend per share are explicit caller-supplied inputs. This service does not silently retrieve or assume them, because their source, permission and date alignment must be verified independently. It requires published monetary facts to establish reporting currency. Tests use a fake read connection; a live PostgreSQL integration test remains outstanding.
