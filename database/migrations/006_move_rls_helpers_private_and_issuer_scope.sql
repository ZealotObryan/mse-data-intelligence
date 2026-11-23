-- Move RLS helper functions out of the exposed API schema.
-- SECURITY DEFINER is required to read protected role/scope mappings without
-- recursive RLS; the functions return booleans only and use a pinned search_path.
BEGIN;
CREATE SCHEMA IF NOT EXISTS private;
REVOKE ALL ON SCHEMA private FROM PUBLIC, anon;
GRANT USAGE ON SCHEMA private TO authenticated;
ALTER FUNCTION public.has_app_role(TEXT) SET SCHEMA private;
ALTER FUNCTION public.has_dataset_access(TEXT,TEXT[]) SET SCHEMA private;
REVOKE ALL ON FUNCTION private.has_app_role(TEXT) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION private.has_dataset_access(TEXT,TEXT[]) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION private.has_app_role(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION private.has_dataset_access(TEXT,TEXT[]) TO authenticated;

CREATE POLICY issuers_read_assigned ON public.issuers
FOR SELECT TO authenticated USING (
  private.has_app_role('platform_admin')
  OR EXISTS (SELECT 1 FROM public.issuer_profile_versions p
    WHERE p.issuer_id=issuers.issuer_id
      AND private.has_dataset_access(p.dataset_id,ARRAY['read','steward','publish']))
  OR EXISTS (SELECT 1 FROM public.issuer_financial_periods p
    WHERE p.issuer_id=issuers.issuer_id
      AND private.has_dataset_access(p.dataset_id,ARRAY['read','steward','publish']))
);

-- Recreate the policies with the private-schema helpers. The exact role and
-- dataset predicates remain unchanged from migration 005.
DROP POLICY datasets_read_assigned ON public.datasets;
CREATE POLICY datasets_read_assigned ON public.datasets FOR SELECT TO authenticated USING (
 private.has_app_role('platform_admin')
 OR (private.has_app_role('analyst') AND private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']))
 OR (private.has_app_role('data_steward') AND private.has_dataset_access(dataset_id,ARRAY['steward','publish']))
 OR (private.has_app_role('publisher') AND private.has_dataset_access(dataset_id,ARRAY['publish']))
);
DROP POLICY data_sources_read_assigned ON public.data_sources;
CREATE POLICY data_sources_read_assigned ON public.data_sources FOR SELECT TO authenticated USING (
 private.has_app_role('platform_admin') OR EXISTS (SELECT 1 FROM public.datasets d WHERE d.source_id=data_sources.source_id AND
 ((private.has_app_role('analyst') AND private.has_dataset_access(d.dataset_id,ARRAY['read','steward','publish']))
 OR (private.has_app_role('data_steward') AND private.has_dataset_access(d.dataset_id,ARRAY['steward','publish']))
 OR (private.has_app_role('publisher') AND private.has_dataset_access(d.dataset_id,ARRAY['publish']))))
);
DROP POLICY ingestion_runs_read_assigned ON public.ingestion_runs;
CREATE POLICY ingestion_runs_read_assigned ON public.ingestion_runs FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY instruments_read_assigned ON public.instruments;
CREATE POLICY instruments_read_assigned ON public.instruments FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR EXISTS (SELECT 1 FROM public.market_observations o WHERE o.instrument_id=instruments.instrument_id AND private.has_dataset_access(o.dataset_id,ARRAY['read','steward','publish'])));
DROP POLICY market_observations_read_assigned ON public.market_observations;
CREATE POLICY market_observations_read_assigned ON public.market_observations FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY validation_issues_read_assigned ON public.validation_issues;
CREATE POLICY validation_issues_read_assigned ON public.validation_issues FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR EXISTS (SELECT 1 FROM public.ingestion_runs r WHERE r.ingestion_id=validation_issues.ingestion_id AND private.has_dataset_access(r.dataset_id,ARRAY['steward','publish'])));
DROP POLICY issuer_profiles_read_assigned ON public.issuer_profile_versions;
CREATE POLICY issuer_profiles_read_assigned ON public.issuer_profile_versions FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY issuer_periods_read_assigned ON public.issuer_financial_periods;
CREATE POLICY issuer_periods_read_assigned ON public.issuer_financial_periods FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY issuer_facts_read_assigned ON public.issuer_financial_facts;
CREATE POLICY issuer_facts_read_assigned ON public.issuer_financial_facts FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR EXISTS (SELECT 1 FROM public.issuer_financial_periods p WHERE p.financial_period_id=issuer_financial_facts.financial_period_id AND private.has_dataset_access(p.dataset_id,ARRAY['read','steward','publish'])));
DROP POLICY dividends_read_assigned ON public.dividends;
CREATE POLICY dividends_read_assigned ON public.dividends FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY actions_read_assigned ON public.corporate_actions;
CREATE POLICY actions_read_assigned ON public.corporate_actions FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
DROP POLICY announcements_read_assigned ON public.issuer_announcements;
CREATE POLICY announcements_read_assigned ON public.issuer_announcements FOR SELECT TO authenticated USING (private.has_app_role('platform_admin') OR private.has_dataset_access(dataset_id,ARRAY['read','steward','publish']));
COMMIT;
