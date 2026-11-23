-- MSE Data Intelligence: default-deny access baseline for Supabase.
-- Apply after migrations 001-003. No browser-facing role is granted access yet.
BEGIN;

-- Migration 002's market view must use invoker privileges, like the issuer views.
ALTER VIEW public.public_market_observations SET (security_invoker = true);

-- Enable RLS on every application table in the exposed public schema.
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ingestion_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.validation_issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuer_profile_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuer_financial_periods ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuer_financial_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dividends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.corporate_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuer_announcements ENABLE ROW LEVEL SECURITY;

-- Default deny for anonymous and ordinary authenticated clients. Raw tables and
-- views remain inaccessible until the verified identity/role model is deployed.
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL PRIVILEGES ON public.public_market_observations,
  public.public_issuer_financial_facts,
  public.public_issuer_dividends,
  public.public_issuer_announcements
FROM anon, authenticated;

-- Trigger functions are not callable as RPC endpoints.
REVOKE EXECUTE ON FUNCTION public.enforce_dataset_publication_gate()
  FROM PUBLIC, anon, authenticated;

-- Keep future objects private when created by the migration owner.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated;

COMMIT;
