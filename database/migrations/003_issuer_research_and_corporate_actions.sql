-- MSE Data Intelligence: issuer research and corporate actions foundation.
-- Apply after 001_initial_data_foundation.sql and 002_publication_gate.sql.
-- All records retain dataset/source lineage. No real issuer data is seeded here.
BEGIN;

CREATE TABLE IF NOT EXISTS issuers (
    issuer_id TEXT PRIMARY KEY,
    legal_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    registration_number TEXT,
    industry TEXT,
    website_url TEXT,
    country_code CHAR(2) NOT NULL DEFAULT 'MW',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (website_url IS NULL OR website_url ~ '^https?://'),
    CHECK (country_code ~ '^[A-Z]{2}$')
);

-- Effective-dated issuer facts support name/sector/website changes without
-- rewriting what was known at an earlier point in time.
ALTER TABLE instruments
    ADD COLUMN IF NOT EXISTS issuer_id TEXT REFERENCES issuers(issuer_id);
CREATE INDEX IF NOT EXISTS instruments_issuer_idx ON instruments(issuer_id);

CREATE TABLE IF NOT EXISTS issuer_profile_versions (
    profile_version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuers(issuer_id),
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    effective_from DATE NOT NULL,
    effective_to DATE,
    profile JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (effective_to IS NULL OR effective_to >= effective_from),
    CHECK (jsonb_typeof(profile) = 'object'),
    UNIQUE (issuer_id, dataset_id, effective_from)
);
CREATE INDEX IF NOT EXISTS issuer_profile_effective_idx
    ON issuer_profile_versions(issuer_id, effective_from DESC);

-- Financial statements are stored at statement-period grain; individual
-- facts are separate rows so reported units, currency and comparative periods
-- remain explicit and auditable.
CREATE TABLE IF NOT EXISTS issuer_financial_periods (
    financial_period_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuers(issuer_id),
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    statement_type TEXT NOT NULL CHECK (statement_type IN (
        'income_statement','balance_sheet','cash_flow','other'
    )),
    period_start DATE,
    period_end DATE NOT NULL,
    fiscal_year INTEGER,
    fiscal_period TEXT,
    reporting_basis TEXT,
    audited BOOLEAN,
    published_at TIMESTAMPTZ,
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (period_start IS NULL OR period_start <= period_end),
    CHECK (fiscal_year IS NULL OR fiscal_year BETWEEN 1900 AND 2200),
    UNIQUE (issuer_id, dataset_id, statement_type, period_end, fiscal_period)
);
CREATE INDEX IF NOT EXISTS issuer_financial_periods_lookup_idx
    ON issuer_financial_periods(issuer_id, period_end DESC);

CREATE TABLE IF NOT EXISTS issuer_financial_facts (
    financial_fact_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    financial_period_id BIGINT NOT NULL REFERENCES issuer_financial_periods(financial_period_id) ON DELETE CASCADE,
    metric_code TEXT NOT NULL,
    metric_label TEXT NOT NULL,
    numeric_value NUMERIC(28,8) NOT NULL,
    currency CHAR(3),
    unit TEXT NOT NULL DEFAULT 'currency',
    comparative_period_end DATE,
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (currency IS NULL OR currency ~ '^[A-Z]{3}$'),
    CHECK (unit IN ('currency','shares','per_share','percentage','ratio','days','count','other')),
    UNIQUE (financial_period_id, metric_code, comparative_period_end)
);
CREATE INDEX IF NOT EXISTS issuer_financial_facts_metric_idx
    ON issuer_financial_facts(metric_code, financial_period_id);

CREATE TABLE IF NOT EXISTS dividends (
    dividend_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuers(issuer_id),
    instrument_id TEXT REFERENCES instruments(instrument_id),
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    dividend_type TEXT NOT NULL DEFAULT 'cash' CHECK (dividend_type IN ('cash','stock','special','other')),
    amount_per_share NUMERIC(24,8),
    currency CHAR(3),
    declaration_date DATE,
    ex_dividend_date DATE,
    record_date DATE,
    payment_date DATE,
    fiscal_period TEXT,
    status TEXT NOT NULL DEFAULT 'announced' CHECK (status IN (
        'proposed','announced','approved','paid','cancelled','unknown'
    )),
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (amount_per_share IS NULL OR amount_per_share >= 0),
    CHECK (currency IS NULL OR currency ~ '^[A-Z]{3}$'),
    CHECK (ex_dividend_date IS NULL OR record_date IS NULL OR ex_dividend_date <= record_date),
    CHECK (record_date IS NULL OR payment_date IS NULL OR record_date <= payment_date),
    UNIQUE (issuer_id, dataset_id, dividend_type, declaration_date, ex_dividend_date, payment_date)
);
CREATE INDEX IF NOT EXISTS dividends_issuer_dates_idx
    ON dividends(issuer_id, ex_dividend_date DESC);

CREATE TABLE IF NOT EXISTS corporate_actions (
    corporate_action_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuers(issuer_id),
    instrument_id TEXT REFERENCES instruments(instrument_id),
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    action_type TEXT NOT NULL CHECK (action_type IN (
        'split','consolidation','rights_issue','bonus_issue','merger',
        'acquisition','name_change','delisting','suspension','resumption','other'
    )),
    announcement_date DATE,
    effective_date DATE,
    ratio_numerator NUMERIC(24,8),
    ratio_denominator NUMERIC(24,8),
    description TEXT,
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (ratio_numerator IS NULL OR ratio_numerator > 0),
    CHECK (ratio_denominator IS NULL OR ratio_denominator > 0),
    UNIQUE (issuer_id, dataset_id, action_type, announcement_date, effective_date)
);
CREATE INDEX IF NOT EXISTS corporate_actions_issuer_dates_idx
    ON corporate_actions(issuer_id, effective_date DESC);

CREATE TABLE IF NOT EXISTS issuer_announcements (
    announcement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    issuer_id TEXT NOT NULL REFERENCES issuers(issuer_id),
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    announcement_type TEXT NOT NULL DEFAULT 'other',
    headline TEXT NOT NULL,
    summary TEXT,
    announced_at TIMESTAMPTZ,
    document_url TEXT,
    source_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (document_url IS NULL OR document_url ~ '^https?://'),
    UNIQUE (issuer_id, dataset_id, headline, announced_at)
);
CREATE INDEX IF NOT EXISTS issuer_announcements_issuer_date_idx
    ON issuer_announcements(issuer_id, announced_at DESC);

-- Public-facing read views inherit publication approval from the linked dataset
-- and source. Raw tables remain private; grants/RLS are a separate deployment step.
CREATE OR REPLACE VIEW public_issuer_financial_facts WITH (security_invoker = true) AS
SELECT i.issuer_id, i.display_name, p.statement_type, p.period_start,
       p.period_end, p.fiscal_year, p.fiscal_period, p.reporting_basis,
       p.audited, f.metric_code, f.metric_label, f.numeric_value,
       f.currency, f.unit, f.comparative_period_end, p.dataset_id
FROM issuer_financial_facts f
JOIN issuer_financial_periods p ON p.financial_period_id = f.financial_period_id
JOIN issuers i ON i.issuer_id = p.issuer_id
JOIN datasets d ON d.dataset_id = p.dataset_id
JOIN data_sources s ON s.source_id = d.source_id
WHERE d.publication_status = 'approved_public'
  AND d.validation_status = 'passed'
  AND s.permission_status = 'approved';

CREATE OR REPLACE VIEW public_issuer_dividends WITH (security_invoker = true) AS
SELECT v.dividend_id, v.issuer_id, v.instrument_id, v.dividend_type,
       v.amount_per_share, v.currency, v.declaration_date, v.ex_dividend_date,
       v.record_date, v.payment_date, v.fiscal_period, v.status, v.dataset_id
FROM dividends v
JOIN datasets d ON d.dataset_id = v.dataset_id
JOIN data_sources s ON s.source_id = d.source_id
WHERE d.publication_status = 'approved_public'
  AND d.validation_status = 'passed'
  AND s.permission_status = 'approved';

CREATE OR REPLACE VIEW public_issuer_announcements WITH (security_invoker = true) AS
SELECT a.announcement_id, a.issuer_id, a.announcement_type, a.headline,
       a.summary, a.announced_at, a.document_url, a.dataset_id
FROM issuer_announcements a
JOIN datasets d ON d.dataset_id = a.dataset_id
JOIN data_sources s ON s.source_id = d.source_id
WHERE d.publication_status = 'approved_public'
  AND d.validation_status = 'passed'
  AND s.permission_status = 'approved';

COMMIT;

-- Before granting SELECT on public views, harden view ownership and RLS.
-- On PostgreSQL 15+, consider WITH (security_invoker = true); otherwise keep
-- views in a private schema or revoke anon/authenticated access.
