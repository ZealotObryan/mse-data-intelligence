import styles from "./MarketDataFreshness.module.css";
type Props = { status?: "current" | "delayed" | "stale" | "unavailable" | "unknown" | "demo"; observedAt?: string | null; sourceName?: string | null; note?: string };
const labels = { current: "Current", delayed: "Delayed", stale: "Stale", unavailable: "Unavailable", unknown: "Unknown", demo: "Demo data" };
export default function MarketDataFreshness({ status = "demo", observedAt = null, sourceName = null, note }: Props) {
  const timestamp = observedAt && Number.isFinite(Date.parse(observedAt)) ? new Intl.DateTimeFormat("en-MW", { dateStyle: "medium", timeStyle: "short", timeZone: "Africa/Blantyre" }).format(new Date(observedAt)) : null;
  const explanation = note ?? (status === "demo" ? "Synthetic fixtures only. No exchange observation timestamp or live-feed freshness is available." : status === "unknown" ? "Freshness cannot be verified because source timing or policy metadata is missing." : status === "unavailable" ? "The source has reported that market observations are unavailable." : "Freshness is determined from the source observation timestamp and the configured policy.");
  return <section className={styles.panel} aria-label="Market data quality and freshness">
    <div className={styles.heading}><div><span className={styles.eyebrow}>DATA QUALITY</span><h3>Market data status</h3></div><span className={styles.badge + " " + styles[status]}><i aria-hidden="true" />{labels[status]}</span></div>
    <p>{explanation}</p><div className={styles.meta}><span>Source: <b>{sourceName || (status === "demo" ? "Synthetic demonstration fixtures" : "Not identified")}</b></span><span>Observed: <b>{timestamp || "Not supplied"}</b></span></div>
    {status === "demo" && <small className={styles.disclaimer}>Do not interpret this status as current, delayed or stale MSE market information.</small>}
  </section>;
}
