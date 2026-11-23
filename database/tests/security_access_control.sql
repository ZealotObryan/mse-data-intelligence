-- Run as a database owner in a disposable Supabase project after migrations 001-006.
-- Transaction is rolled back; use synthetic fixtures only.
BEGIN;
DO $$
DECLARE
  v_table_count INTEGER;
  v_rls_count INTEGER;
  v_policy_count INTEGER;
BEGIN
  SELECT count(*),count(*) FILTER (WHERE c.relrowsecurity)
    INTO v_table_count,v_rls_count
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='public' AND c.relkind='r';
  IF v_table_count<>16 OR v_rls_count<>16 THEN
    RAISE EXCEPTION 'Expected RLS on 16/16 application tables; found %/%',v_rls_count,v_table_count;
  END IF;
  SELECT count(*) INTO v_policy_count FROM pg_policies WHERE schemaname='public';
  IF v_policy_count<16 THEN RAISE EXCEPTION 'Expected table policies; found %',v_policy_count; END IF;
  IF has_table_privilege('anon','public.datasets','SELECT')
     OR has_table_privilege('anon','public.public_market_observations','SELECT') THEN
    RAISE EXCEPTION 'Anonymous role unexpectedly has data access';
  END IF;
  IF NOT has_table_privilege('authenticated','public.datasets','SELECT')
     OR has_table_privilege('authenticated','public.app_user_roles','INSERT')
     OR has_table_privilege('authenticated','public.dataset_access','INSERT')
     OR has_table_privilege('authenticated','public.audit_events','INSERT') THEN
    RAISE EXCEPTION 'Authenticated grants do not match read-only baseline';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='public' AND p.proname IN ('has_app_role','has_dataset_access')) THEN
    RAISE EXCEPTION 'RLS helper RPCs must not remain in exposed public schema';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='private' AND p.proname='has_app_role' AND p.prosecdef
      AND 'search_path=pg_catalog, public, auth'=ANY(p.proconfig)) THEN
    RAISE EXCEPTION 'Pinned private role helper is missing';
  END IF;
END $$;

-- Negative publication test.
DO $$
DECLARE v_source_id BIGINT; v_dataset_id TEXT := '__security_test_denied_dataset__';
BEGIN
 INSERT INTO public.data_sources(source_key,source_name,source_class,permission_status)
 VALUES ('__security_test_denied__','Security test denied','synthetic_demo','unknown')
 RETURNING source_id INTO v_source_id;
 INSERT INTO public.datasets(dataset_id,source_id,dataset_name,data_class,collected_at,validation_status,publication_status)
 VALUES (v_dataset_id,v_source_id,'Security test denied dataset','synthetic_demo',now(),'passed','blocked');
 BEGIN
  UPDATE public.datasets SET publication_status='approved_public' WHERE dataset_id=v_dataset_id;
  RAISE EXCEPTION 'Unapproved source was incorrectly published';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='Unapproved source was incorrectly published' THEN RAISE; END IF;
 END;
END $$;
ROLLBACK;

-- Authenticated-role smoke test: with no JWT subject or role mapping, no rows
-- are visible. Run separately from the owner transaction.
SET ROLE authenticated;
SELECT count(*) AS visible_datasets_without_identity FROM public.datasets;
RESET ROLE;
