-- MSE Data Intelligence: trusted application roles and dataset-scoped RLS.
BEGIN;

CREATE TABLE public.app_user_roles (
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('learner','analyst','data_steward','publisher','platform_admin')),
  assigned_by UUID REFERENCES auth.users(id),
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, role)
);
CREATE TABLE public.dataset_access (
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  dataset_id TEXT NOT NULL REFERENCES public.datasets(dataset_id) ON DELETE CASCADE,
  access_level TEXT NOT NULL CHECK (access_level IN ('read','steward','publish')),
  granted_by UUID REFERENCES auth.users(id),
  granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id,dataset_id,access_level)
);
CREATE TABLE public.audit_events (
  audit_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  actor_user_id UUID REFERENCES auth.users(id),
  actor_type TEXT NOT NULL CHECK (actor_type IN ('user','system')),
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  reason TEXT,
  details JSONB NOT NULL DEFAULT '{}'::jsonb,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX dataset_access_user_dataset_idx ON public.dataset_access(user_id,dataset_id);
CREATE INDEX dataset_access_dataset_level_idx ON public.dataset_access(dataset_id,access_level);

ALTER TABLE public.app_user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dataset_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_events ENABLE ROW LEVEL SECURITY;

-- SECURITY DEFINER helpers are narrowly scoped, pinned to a safe search_path,
-- fully qualified, and executable only by authenticated users. They expose
-- booleans, never the underlying role/assignment rows.
CREATE OR REPLACE FUNCTION public.has_app_role(p_role TEXT)
RETURNS BOOLEAN
LANGUAGE SQL STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, auth
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.app_user_roles r
    WHERE r.user_id = (SELECT auth.uid()) AND r.role = p_role
  );
$$;
CREATE OR REPLACE FUNCTION public.has_dataset_access(p_dataset_id TEXT, p_levels TEXT[])
RETURNS BOOLEAN
LANGUAGE SQL STABLE SECURITY DEFINER
SET search_path = pg_catalog, public, auth
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.dataset_access a
    WHERE a.user_id = (SELECT auth.uid())
      AND a.dataset_id = p_dataset_id
      AND a.access_level = ANY(p_levels)
  );
$$;

REVOKE ALL ON FUNCTION public.has_app_role(TEXT) FROM PUBLIC, anon;
REVOKE ALL ON FUNCTION public.has_dataset_access(TEXT,TEXT[]) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.has_app_role(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_dataset_access(TEXT,TEXT[]) TO authenticated;

-- Default-deny identity and scope administration. Users can only read their
-- own role and assignment rows. All role/scope writes are service-side only.
CREATE POLICY app_roles_read_own ON public.app_user_roles
  FOR SELECT TO authenticated USING (user_id = (SELECT auth.uid()));
CREATE POLICY dataset_access_read_own ON public.dataset_access
  FOR SELECT TO authenticated USING (user_id = (SELECT auth.uid()));
CREATE POLICY audit_events_read_own ON public.audit_events
  FOR SELECT TO authenticated USING (actor_user_id = (SELECT auth.uid()));

-- Raw data access is only for explicitly assigned datasets and roles.
CREATE POLICY datasets_read_assigned ON public.datasets
  FOR SELECT TO authenticated
  USING (
    public.has_app_role('platform_admin')
    OR (public.has_app_role('analyst') AND public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']))
    OR (public.has_app_role('data_steward') AND public.has_dataset_access(dataset_id, ARRAY['steward','publish']))
    OR (public.has_app_role('publisher') AND public.has_dataset_access(dataset_id, ARRAY['publish']))
  );

CREATE POLICY data_sources_read_assigned ON public.data_sources
  FOR SELECT TO authenticated
  USING (
    public.has_app_role('platform_admin')
    OR EXISTS (
      SELECT 1 FROM public.datasets d
      WHERE d.source_id = data_sources.source_id
        AND (
          (public.has_app_role('analyst') AND public.has_dataset_access(d.dataset_id, ARRAY['read','steward','publish']))
          OR (public.has_app_role('data_steward') AND public.has_dataset_access(d.dataset_id, ARRAY['steward','publish']))
          OR (public.has_app_role('publisher') AND public.has_dataset_access(d.dataset_id, ARRAY['publish']))
        )
    )
  );

CREATE POLICY ingestion_runs_read_assigned ON public.ingestion_runs
  FOR SELECT TO authenticated USING (
    public.has_app_role('platform_admin')
    OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish'])
  );
CREATE POLICY instruments_read_assigned ON public.instruments
  FOR SELECT TO authenticated USING (
    public.has_app_role('platform_admin')
    OR EXISTS (
      SELECT 1 FROM public.market_observations o
      WHERE o.instrument_id = instruments.instrument_id
        AND public.has_dataset_access(o.dataset_id, ARRAY['read','steward','publish'])
    )
  );
CREATE POLICY market_observations_read_assigned ON public.market_observations
  FOR SELECT TO authenticated USING (
    public.has_app_role('platform_admin')
    OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish'])
  );
CREATE POLICY validation_issues_read_assigned ON public.validation_issues
  FOR SELECT TO authenticated USING (
    public.has_app_role('platform_admin')
    OR EXISTS (
      SELECT 1 FROM public.ingestion_runs r
      WHERE r.ingestion_id = validation_issues.ingestion_id
        AND public.has_dataset_access(r.dataset_id, ARRAY['steward','publish'])
    )
  );

-- Issuer records inherit scope through their dataset. No unrestricted issuer
-- directory or financial data is exposed to a generic authenticated user.
CREATE POLICY issuer_profiles_read_assigned ON public.issuer_profile_versions
  FOR SELECT TO authenticated USING (public.has_app_role('platform_admin') OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']));
CREATE POLICY issuer_periods_read_assigned ON public.issuer_financial_periods
  FOR SELECT TO authenticated USING (public.has_app_role('platform_admin') OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']));
CREATE POLICY issuer_facts_read_assigned ON public.issuer_financial_facts
  FOR SELECT TO authenticated USING (
    public.has_app_role('platform_admin') OR EXISTS (
      SELECT 1 FROM public.issuer_financial_periods p
      WHERE p.financial_period_id=issuer_financial_facts.financial_period_id
        AND public.has_dataset_access(p.dataset_id, ARRAY['read','steward','publish'])
    )
  );
CREATE POLICY dividends_read_assigned ON public.dividends
  FOR SELECT TO authenticated USING (public.has_app_role('platform_admin') OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']));
CREATE POLICY actions_read_assigned ON public.corporate_actions
  FOR SELECT TO authenticated USING (public.has_app_role('platform_admin') OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']));
CREATE POLICY announcements_read_assigned ON public.issuer_announcements
  FOR SELECT TO authenticated USING (public.has_app_role('platform_admin') OR public.has_dataset_access(dataset_id, ARRAY['read','steward','publish']));

-- Authenticated clients receive read-only SQL privileges on scoped raw data.
-- All writes and publication approvals remain on trusted server workflows.
GRANT SELECT ON public.app_user_roles, public.dataset_access,
  public.datasets, public.data_sources, public.ingestion_runs, public.instruments,
  public.market_observations, public.validation_issues, public.issuers,
  public.issuer_profile_versions, public.issuer_financial_periods,
  public.issuer_financial_facts, public.dividends, public.corporate_actions,
  public.issuer_announcements
TO authenticated;
GRANT SELECT ON public.audit_events TO authenticated;

-- No public visitor access is granted by this migration. The four views remain
-- ungranted until the app's public-data publication contract is verified.
COMMIT;
