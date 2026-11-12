-- MSE Data Intelligence: enforce source approval at publication time.
-- Apply after 001_initial_data_foundation.sql.
BEGIN;

CREATE OR REPLACE FUNCTION enforce_dataset_publication_gate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    source_permission TEXT;
    source_redistribution BOOLEAN;
    source_uses TEXT[];
BEGIN
    IF NEW.publication_status <> 'approved_public' THEN
        RETURN NEW;
    END IF;

    IF NEW.validation_status <> 'passed' THEN
        RAISE EXCEPTION 'dataset % cannot be published: validation is not passed', NEW.dataset_id;
    END IF;

    SELECT permission_status, redistribution_allowed, permitted_uses
      INTO source_permission, source_redistribution, source_uses
      FROM data_sources
     WHERE source_id = NEW.source_id;

    IF NOT FOUND OR source_permission <> 'approved' THEN
        RAISE EXCEPTION 'dataset % cannot be published: source permission is not approved', NEW.dataset_id;
    END IF;

    IF NEW.data_class <> 'synthetic_demo' AND (
        NEW.redistribution_allowed IS DISTINCT FROM TRUE
        OR source_redistribution IS DISTINCT FROM TRUE
        OR NOT ('public_display' = ANY(NEW.permitted_uses))
        OR NOT ('public_display' = ANY(source_uses))
    ) THEN
        RAISE EXCEPTION 'dataset % cannot be published: explicit public redistribution permission is missing', NEW.dataset_id;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS datasets_publication_gate ON datasets;
CREATE TRIGGER datasets_publication_gate
BEFORE INSERT OR UPDATE OF publication_status, validation_status, source_id,
    data_class, redistribution_allowed, permitted_uses
ON datasets
FOR EACH ROW
EXECUTE FUNCTION enforce_dataset_publication_gate();

-- Public consumers receive only observations belonging to approved datasets.
-- Raw tables remain private; apply database role grants and RLS separately.
CREATE OR REPLACE VIEW public_market_observations AS
SELECT
    o.observation_id,
    o.instrument_id,
    i.issuer_name,
    i.instrument_name,
    i.exchange_symbol,
    i.sector,
    o.observation_date,
    o.metric_key,
    o.numeric_value,
    o.currency,
    o.unit,
    d.dataset_id,
    d.attribution_text
FROM market_observations AS o
JOIN datasets AS d ON d.dataset_id = o.dataset_id
JOIN data_sources AS s ON s.source_id = d.source_id
JOIN instruments AS i ON i.instrument_id = o.instrument_id
WHERE d.publication_status = 'approved_public'
  AND d.validation_status = 'passed'
  AND s.permission_status = 'approved'
  AND o.validation_status = 'passed';

COMMIT;

-- Before granting SELECT on public_market_observations, verify the view owner,
-- underlying table privileges, PostgreSQL security-invoker behavior, and the
-- deployment's RLS/role model. Never grant public access to raw tables.
