-- MSE Data Intelligence: permission-aware relational data foundation
-- PostgreSQL 15+. This migration creates structure only; it imports no market data.
BEGIN;

CREATE TABLE IF NOT EXISTS data_sources (
    source_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    source_url TEXT,
    source_class TEXT NOT NULL CHECK (source_class IN (
        'official_public','licensed_market','issuer_disclosure','synthetic_demo','internal'
    )),
    licence_name TEXT,
    licence_reference TEXT,
    permission_status TEXT NOT NULL DEFAULT 'unknown' CHECK (permission_status IN (
        'unknown','pending_review','approved','restricted','revoked'
    )),
    permitted_uses TEXT[] NOT NULL DEFAULT '{}',
    redistribution_allowed BOOLEAN,
    attribution_text TEXT,
    terms_reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (source_url IS NULL OR source_url ~ '^https?://'),
    CHECK (source_class NOT IN ('official_public','licensed_market','issuer_disclosure')
           OR (source_url IS NOT NULL AND licence_name IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id TEXT PRIMARY KEY,
    source_id BIGINT NOT NULL REFERENCES data_sources(source_id),
    dataset_name TEXT NOT NULL,
    data_class TEXT NOT NULL CHECK (data_class IN (
        'synthetic_demo','official_public','licensed_market','issuer_disclosure','derived'
    )),
    source_document_id TEXT,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL,
    coverage_start DATE,
    coverage_end DATE,
    validation_status TEXT NOT NULL DEFAULT 'pending' CHECK (validation_status IN (
        'pending','passed','warning','rejected'
    )),
    publication_status TEXT NOT NULL DEFAULT 'blocked' CHECK (publication_status IN (
        'blocked','internal_only','approved_public','withdrawn'
    )),
    permitted_uses TEXT[] NOT NULL DEFAULT '{}',
    redistribution_allowed BOOLEAN,
    attribution_text TEXT,
    collector_version TEXT,
    checksum_sha256 CHAR(64),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (coverage_start IS NULL OR coverage_end IS NULL OR coverage_start <= coverage_end),
    CHECK (checksum_sha256 IS NULL OR checksum_sha256 ~ '^[a-fA-F0-9]{64}$'),
    CHECK (publication_status <> 'approved_public' OR validation_status = 'passed'),
    CHECK (publication_status <> 'approved_public' OR data_class = 'synthetic_demo'
           OR (redistribution_allowed IS TRUE AND 'public_display' = ANY(permitted_uses)))
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    ingestion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    source_name TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    run_status TEXT NOT NULL DEFAULT 'received' CHECK (run_status IN (
        'received','processing','succeeded','warning','failed','rejected'
    )),
    parser_version TEXT NOT NULL,
    checksum_sha256 CHAR(64) NOT NULL CHECK (checksum_sha256 ~ '^[a-fA-F0-9]{64}$'),
    artifact_uri TEXT NOT NULL,
    original_filename TEXT,
    bytes_received BIGINT NOT NULL DEFAULT 0 CHECK (bytes_received >= 0),
    rows_received BIGINT CHECK (rows_received IS NULL OR rows_received >= 0),
    rows_accepted BIGINT CHECK (rows_accepted IS NULL OR rows_accepted >= 0),
    rows_rejected BIGINT CHECK (rows_rejected IS NULL OR rows_rejected >= 0),
    error_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (dataset_id, checksum_sha256),
    CHECK (completed_at IS NULL OR completed_at >= started_at)
);

CREATE TABLE IF NOT EXISTS instruments (
    instrument_id TEXT PRIMARY KEY,
    issuer_name TEXT NOT NULL,
    instrument_name TEXT NOT NULL,
    exchange_symbol TEXT,
    instrument_type TEXT NOT NULL DEFAULT 'equity',
    sector TEXT,
    currency CHAR(3) NOT NULL,
    listing_date DATE,
    delisting_date DATE,
    source_id BIGINT REFERENCES data_sources(source_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (currency ~ '^[A-Z]{3}$'),
    CHECK (delisting_date IS NULL OR listing_date IS NULL OR delisting_date >= listing_date)
);
CREATE UNIQUE INDEX IF NOT EXISTS instruments_symbol_active_uq
    ON instruments(exchange_symbol) WHERE exchange_symbol IS NOT NULL AND delisting_date IS NULL;

CREATE TABLE IF NOT EXISTS market_observations (
    observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES datasets(dataset_id),
    ingestion_id BIGINT REFERENCES ingestion_runs(ingestion_id),
    instrument_id TEXT NOT NULL REFERENCES instruments(instrument_id),
    observation_date DATE NOT NULL,
    metric_key TEXT NOT NULL,
    numeric_value NUMERIC(24,8) NOT NULL,
    currency CHAR(3),
    unit TEXT,
    source_locator TEXT,
    validation_status TEXT NOT NULL DEFAULT 'pending' CHECK (validation_status IN (
        'pending','passed','warning','rejected'
    )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (dataset_id, instrument_id, observation_date, metric_key),
    CHECK (currency IS NULL OR currency ~ '^[A-Z]{3}$')
);
CREATE INDEX IF NOT EXISTS market_observations_instrument_date_idx
    ON market_observations(instrument_id, observation_date DESC);
CREATE INDEX IF NOT EXISTS market_observations_dataset_date_idx
    ON market_observations(dataset_id, observation_date DESC);
CREATE INDEX IF NOT EXISTS market_observations_metric_date_idx
    ON market_observations(metric_key, observation_date DESC);

CREATE TABLE IF NOT EXISTS validation_issues (
    issue_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_id BIGINT NOT NULL REFERENCES ingestion_runs(ingestion_id) ON DELETE CASCADE,
    severity TEXT NOT NULL CHECK (severity IN ('info','warning','error')),
    issue_code TEXT NOT NULL,
    message TEXT NOT NULL,
    row_locator TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS validation_issues_run_severity_idx
    ON validation_issues(ingestion_id, severity);

COMMIT;

-- Security deployment note:
-- Keep raw source artifacts and ingestion metadata private by default.
-- Configure least-privilege database roles and row-level security before
-- exposing any tables through an application API. Do not grant public reads
-- to datasets or observations until the dataset publication gate approves them.
