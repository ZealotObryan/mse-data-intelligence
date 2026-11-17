"use client";

import { useMemo, useState } from "react";
import styles from "./DividendCalculator.module.css";

const money = new Intl.NumberFormat("en-MW", { maximumFractionDigits: 2 });
export default function DividendCalculator() {
  const [shares, setShares] = useState("250");
  const [dividend, setDividend] = useState("8.5");
  const [currency, setCurrency] = useState<"MWK" | "USD">("MWK");
  const result = useMemo(() => {
    const count = Number(shares);
    const perShare = Number(dividend);
    if (!Number.isFinite(count) || !Number.isFinite(perShare) || count < 0 || perShare < 0) return null;
    return count * perShare;
  }, [shares, dividend]);
  return (
    <section className={styles.card} aria-labelledby="dividend-title">
      <div className={styles.header}>
        <div><span className={styles.kicker}>LEARN BY DOING · CALCULATOR</span><h3 id="dividend-title">Dividend income calculator</h3><p>Estimate the gross dividend amount from a hypothetical shareholding.</p></div>
        <span className={styles.tag}>Illustrative</span>
      </div>
      <div className={styles.fields}>
        <label>Number of shares<input type="number" min="0" step="1" inputMode="numeric" value={shares} onChange={e=>setShares(e.target.value)}/></label>
        <label>Dividend per share<input type="number" min="0" step="0.01" inputMode="decimal" value={dividend} onChange={e=>setDividend(e.target.value)}/></label>
        <label>Currency<select value={currency} onChange={e=>setCurrency(e.target.value as "MWK"|"USD")}><option value="MWK">MWK</option><option value="USD">USD</option></select></label>
      </div>
      {result===null ? <p className={styles.error} role="alert">Enter valid non-negative numbers for shares and dividend per share.</p> : <div className={styles.result} aria-live="polite"><span>Estimated gross dividend</span><strong>{currency} {money.format(result)}</strong><small>{money.format(Number(shares))} shares × {currency} {money.format(Number(dividend))} per share</small></div>}
      <p className={styles.note}>This estimate is before any applicable withholding tax or other deductions. It assumes the declared dividend is paid in full and you hold the shares on the relevant entitlement date. It is not a forecast or investment recommendation.</p>
    </section>
  );
}
