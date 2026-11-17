"use client";

import { useMemo, useState } from "react";
import styles from "./InvestmentReturnSimulator.module.css";

const currency = new Intl.NumberFormat("en-MW", { style: "currency", currency: "MWK", maximumFractionDigits: 0 });
function formatMWK(value: number) { return currency.format(value).replace("MWK", "MWK"); }

export default function InvestmentReturnSimulator() {
  const [investment, setInvestment] = useState("100000");
  const [movement, setMovement] = useState("12");
  const result = useMemo(() => {
    const principal = Number(investment);
    const change = Number(movement);
    if (!Number.isFinite(principal) || !Number.isFinite(change) || principal < 0) return null;
    const gain = principal * (change / 100);
    return { principal, change, gain, endingValue: principal + gain };
  }, [investment, movement]);
  const isLoss = (result?.gain ?? 0) < 0;

  return (
    <section className={styles.simulator} aria-labelledby="investment-return-title">
      <div className={styles.header}>
        <div>
          <span className={styles.eyebrow}>LEARN BY DOING · SIMULATION</span>
          <h3 id="investment-return-title">Investment return simulator</h3>
          <p>Explore how a hypothetical share-price movement changes an investment’s value.</p>
        </div>
        <span className={styles.demoTag}>Illustrative example</span>
      </div>
      <div className={styles.controls}>
        <label className={styles.field}>
          <span>Starting investment</span>
          <div className={styles.inputWrap}><span>MWK</span><input inputMode="decimal" type="number" min="0" step="1000" value={investment} onChange={(event) => setInvestment(event.target.value)} aria-label="Starting investment in Malawi kwacha" /></div>
        </label>
        <label className={styles.field}>
          <span>Share-price movement</span>
          <div className={styles.inputWrap}><input inputMode="decimal" type="number" step="0.5" value={movement} onChange={(event) => setMovement(event.target.value)} aria-label="Share-price movement percentage" /><span>%</span></div>
          <input className={styles.slider} type="range" min="-50" max="50" step="0.5" value={Number.isFinite(Number(movement)) ? Math.min(50, Math.max(-50, Number(movement))) : 0} onChange={(event) => setMovement(event.target.value)} aria-label="Adjust share-price movement from minus 50 to plus 50 percent" />
          <div className={styles.rangeLabels}><span>−50%</span><span>0%</span><span>+50%</span></div>
        </label>
      </div>
      {result ? (
        <div className={styles.results} aria-live="polite">
          <div className={styles.resultCard}><span>Starting value</span><strong>{formatMWK(result.principal)}</strong></div>
          <div className={styles.resultCard}><span>Gain / loss</span><strong className={isLoss ? styles.loss : styles.gain}>{result.gain > 0 ? "+" : ""}{formatMWK(result.gain)}</strong></div>
          <div className={`${styles.resultCard} ${styles.totalCard}`}><span>Illustrative ending value</span><strong>{formatMWK(result.endingValue)}</strong></div>
        </div>
      ) : <p className={styles.validation} role="alert">Enter a valid investment amount of zero or more and a valid percentage movement.</p>}
      <div className={styles.formula}><b>How it is calculated</b><span>Gain or loss = starting investment × (price movement ÷ 100)</span><span>Ending value = starting investment + gain or loss</span></div>
      <p className={styles.disclaimer}>This is a simplified educational simulation. It excludes brokerage fees, taxes, dividends, liquidity effects and other costs. It uses no live MSE prices and is not investment advice.</p>
    </section>
  );
}
