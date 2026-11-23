export type FreshnessStatus = "current" | "delayed" | "stale" | "unavailable" | "unknown" | "demo";
export type FreshnessMetadata = { mode?: "demo" | "source"; availability?: "available" | "unavailable"; observedAt?: string | null; ingestedAt?: string | null; maxAgeMs?: number; delayedAfterMs?: number };
export type FreshnessAssessment = { status: FreshnessStatus; observedAt: string | null; ingestedAt: string | null; ageMs: number | null; reason: string };
export function assessDataFreshness(metadata: FreshnessMetadata | null | undefined, now?: number): FreshnessAssessment;
