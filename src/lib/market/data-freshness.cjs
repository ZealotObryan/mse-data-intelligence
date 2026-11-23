function assessDataFreshness(metadata, now = Date.now()) {
  if (!metadata || metadata.mode === "demo") return { status: "demo", observedAt: null, ingestedAt: metadata?.ingestedAt ?? null, ageMs: null, reason: "Synthetic demonstration data has no exchange freshness." };
  if (metadata.availability === "unavailable") return { status: "unavailable", observedAt: metadata.observedAt ?? null, ingestedAt: metadata.ingestedAt ?? null, ageMs: null, reason: "The source reports that observations are unavailable." };
  const observed = Date.parse(metadata.observedAt ?? "");
  const maxAgeMs = metadata.maxAgeMs;
  const delayedAfterMs = metadata.delayedAfterMs ?? maxAgeMs;
  if (!Number.isFinite(observed) || !Number.isFinite(now) || !Number.isFinite(maxAgeMs) || maxAgeMs < 0 || !Number.isFinite(delayedAfterMs) || delayedAfterMs < 0 || delayedAfterMs > maxAgeMs) return { status: "unknown", observedAt: metadata.observedAt ?? null, ingestedAt: metadata.ingestedAt ?? null, ageMs: null, reason: "A valid source observation time and freshness policy are required." };
  const ageMs = now - observed;
  if (ageMs < 0) return { status: "unknown", observedAt: metadata.observedAt, ingestedAt: metadata.ingestedAt ?? null, ageMs, reason: "The source observation time is in the future." };
  const status = ageMs > maxAgeMs ? "stale" : ageMs > delayedAfterMs ? "delayed" : "current";
  return { status, observedAt: metadata.observedAt, ingestedAt: metadata.ingestedAt ?? null, ageMs, reason: status === "current" ? "Within the configured freshness window." : status === "delayed" ? "Outside the preferred update window." : "Outside the maximum permitted freshness window." };
}
module.exports = { assessDataFreshness };
