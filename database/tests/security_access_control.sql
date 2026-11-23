-- Run as a database owner in a disposable Supabase project after migrations 001-004.
-- The transaction is rolled back; only synthetic fixtures are used.
BEGIN;

DO $$
DECLARE
  v_source_id BIGINT;
  v_dataset_id TEXT;
  v_table_count INTEGER;
  v_rls_count INTEGER;
BEGIN
  SELECT count(*), count(*) FILTER (WHERE c.relrowsecurity)
    INTO v_table_count, v_rls_count
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE n.nspname = 'public' AND c.relkind = 'r';

  IF v_table_count <> 13 OR v_rls_count <> 13 THEN
    RAISE EXCEPTION 'Expected RLS on all 13 public application tables; found % of %', v_rls_count, v_table_count;
  END IF;

  IF has_table_privilege('anon', 'public.data_sources', 'SELECT')
     OR has_table_privilege('authenticated', 'public.data_sources', 'SELECT')
     OR has_table_privilege('anon', 'public.public_market_observations', 'SELECT')
     OR has_table_privilege('authenticated', 'public.public_issuer_dividends', 'SELECT') THEN
    RAISE EXCEPTION 'Unexpected browser-role access to private tables or views';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname='public' AND c.relname='public_market_observations'
      AND c.relkind='v' AND 'security_invoker=true' = ANY(c.reloptions)
  ) THEN
    RAISE EXCEPTION 'Market publication view is not security_invoker';
  END IF;

  -- Negative publication test: an unapproved source cannot be published.
  INSERT INTO public.data_sources(source_key, source_name, source_class, permission_status)
  VALUES ('__security_test_denied__', 'Security test denied', 'synthetic_demo', 'unknown')
  RETURNING source_id INTO v_source_id;
  v_dataset_id := '__security_test_denied_dataset__';
  INSERT INTO public.datasets(dataset_id, source_id, dataset_name, data_class, collected_at, validation_status, publication_status)
  VALUES (v_dataset_id, v_source_id, 'Security test denied dataset', 'synthetic_demo', now(), 'passed', 'blocked');

  BEGIN
    UPDATE public.datasets SET publication_status='approved_public' WHERE dataset_id=v_dataset_id;
    RAISE EXCEPTION 'Unapproved source was incorrectly published';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM = 'Unapproved source was incorrectly published' THEN RAISE; END IF;
  END;

  DELETE FROM public.datasets WHERE dataset_id=v_dataset_id;
  DELETE FROM public.data_sources WHERE source_id=v_source_id;

  -- Positive publication test: an eligible synthetic dataset passes the gate.
  INSERT INTO public.data_sources(source_key, source_name, source_class, permission_status)
  VALUES ('__security_test_allowed__', 'Security test allowed', 'synthetic_demo', 'approved')
  RETURNING source_id INTO v_source_id;
  v_dataset_id := '__security_test_allowed_dataset__';
  INSERT INTO public.datasets(dataset_id, source_id, dataset_name, data_class, collected_at, validation_status, publication_status)
  VALUES (v_dataset_id, v_source_id, 'Security test allowed dataset', 'synthetic_demo', now(), 'passed', 'blocked');
  UPDATE public.datasets SET publication_status='approved_public' WHERE dataset_id=v_dataset_id;

  IF NOT EXISTS (SELECT 1 FROM public.datasets WHERE dataset_id=v_dataset_id AND publication_status='approved_public') THEN
    RAISE EXCEPTION 'Eligible synthetic dataset did not pass publication gate';
  END IF;

  DELETE FROM public.datasets WHERE dataset_id=v_dataset_id;
  DELETE FROM public.data_sources WHERE source_id=v_source_id;
END $$;

ROLLBACK;
