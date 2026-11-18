"use client";

import { useMemo, useState } from "react";
import styles from "./PortfolioBuilder.module.css";

const initial = [
  { name: "Illustrative holding A", value: "40", description: "Hypothetical listed equity" },
  { name: "Illustrative holding B", value: "30", description: "Hypothetical listed equity" },
  { name: "Illustrative holding C", value: "20", description: "Hypothetical listed equity" },
  { name: "Cash allocation", value: "10", description: "Uninvested portfolio balance" }
];

export default function PortfolioBuilder() {
  const [allocations, setAllocations] = useState(initial);
  const total = useMemo(() => allocations.reduce((sum, item) => sum + (Number(item.value) || 0), 0), [allocations]);
  const largest = useMemo(() => allocations.reduce((best, item) => Number(item.value) > Number(best.value) ? item : best, allocations[0]), [allocations]);
  const valid = allocations.every(item => item.value.trim() !== "" && Number.isFinite(Number(item.value)) && Number(item.value) >= 0 && Number(item.value) <= 100);
  const balanced = valid && Math.abs(total - 100) < 0.001;

  function update(index: number, value: string) {
    setAllocations(current => current.map((item, i) => i === index ? { ...item, value } : item));
  }

  function reset() {
    setAllocations(initial);
  }

  return (
    <section className={styles.card} aria-labelledby="portfolio-builder-title">
      <div className={styles.header}>
        <div>
          <span className={styles.kicker}>PORTFOLIO BASICS · EXPLORER 05</span>
          <h2 id="portfolio-builder-title">Build a hypothetical portfolio</h2>
          <p>Adjust the allocation to see how much of a portfolio sits in each illustrative holding.</p>
        </div>
        <span className={styles.tag}>ILLUSTRATIVE</span>
      </div>

      <div className={styles.content}>
        <div className={styles.inputs}>
          {allocations.map((item, index) => (
            <label className={styles.field} key={item.name}>
              <span><b>{item.name}</b><small>{item.description}</small></span>
              <div className={styles.inputWrap}>
                <input type="number" min="0" max="100" step="1" inputMode="decimal" value={item.value} onChange={event => update(index, event.target.value)} aria-label={item.name + " allocation percentage"} />
                <span>%</span>
              </div>
            </label>
          ))}
          <button type="button" className={styles.reset} onClick={reset}>Reset example</button>
        </div>

        <div className={styles.summary} aria-live="polite">
          <div className={styles.total}>
            <span>Total allocation</span>
            <strong>{valid ? total.toFixed(1) : "—"}%</strong>
            <small>{balanced ? "Allocations add up to 100%" : "A complete portfolio allocation should total 100%"}</small>
          </div>
          <div className={styles.barList}>
            {allocations.map(item => {
              const value = Number(item.value);
              const share = valid && total > 0 ? Math.max(0, Math.min(100, value / total * 100)) : 0;
              return (
                <div className={styles.barRow} key={item.name}>
                  <div><span>{item.name}</span><b>{Number.isFinite(value) ? value.toFixed(1) : "—"}%</b></div>
                  <div className={styles.track}><span style={{ width: share + "%" }} /></div>
                </div>
              );
            })}
          </div>
          {valid && total > 0 && <div className={styles.observation}><b>What stands out?</b><p>{largest.name} is the largest allocation at {Number(largest.value).toFixed(1)}% of the planned portfolio. A larger single holding can make overall results more dependent on that holding.</p></div>}
          {!valid && <p className={styles.warning} role="alert">Use values from 0% to 100% for each allocation.</p>}
          {valid && !balanced && <p className={styles.warning} role="status">Your allocations currently total {total.toFixed(1)}%. Adjust them to reach 100%.</p>}
        </div>
      </div>
      <p className={styles.note}>This is a learning exercise, not a recommended portfolio. The example uses fictional holdings, assumes no price movements and does not calculate risk, expected return, fees or tax. Diversification does not eliminate investment risk.</p>
    </section>
  );
}
