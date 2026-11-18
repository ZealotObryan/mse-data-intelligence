"use client";

import { useMemo, useState } from "react";
import styles from "./RiskReturnExplorer.module.css";

const money = (value: number) => new Intl.NumberFormat("en-MW", { style: "currency", currency: "MWK", maximumFractionDigits: 0 }).format(value);

export default function RiskReturnExplorer() {
  const [capital, setCapital] = useState("1000000");
  const [annualReturn, setAnnualReturn] = useState("8");
  const [annualVolatility, setAnnualVolatility] = useState("15");
  const [years, setYears] = useState("3");
  const values = [capital, annualReturn, annualVolatility, years].map(Number);
  const valid = values.every(Number.isFinite) && Number(capital) > 0 && Number(annualReturn) > -100 && Number(annualVolatility) >= 0 && Number(annualVolatility) <= 100 && Number(annualReturn) <= 100 && Number(years) > 0 && Number(years) <= 30;
  const result = useMemo(() => {
    if (!valid) return null;
    const principal = Number(capital);
    const r = Number(annualReturn) / 100;
    const v = Number(annualVolatility) / 100;
    const period = Number(years);
    const central = principal * Math.pow(1 + r, period);
    const rangeMultiplier = Math.exp(v * Math.sqrt(period));
    return {
      central,
      lower: central / rangeMultiplier,
      upper: central * rangeMultiplier,
      gain: central - principal
    };
  }, [capital, annualReturn, annualVolatility, years, valid]);

  return (
    <section className={styles.card} aria-labelledby="risk-return-title">
      <div className={styles.heading}>
        <div><span className={styles.kicker}>RISK & RETURN · EXPLORER 06</span><h2 id="risk-return-title">Explore risk and potential outcomes</h2><p>Change the assumptions to see how different return and volatility inputs affect an illustrative investment scenario.</p></div>
        <span className={styles.tag}>SCENARIO ONLY</span>
      </div>
      <div className={styles.layout}>
        <div className={styles.controls}>
          <label>Starting amount (MWK)<input type="number" min="1" value={capital} onChange={e => setCapital(e.target.value)} /></label>
          <label>Assumed annual return (%)<input type="number" min="-99" max="100" step="0.5" value={annualReturn} onChange={e => setAnnualReturn(e.target.value)} /></label>
          <label>Assumed annual volatility (%)<input type="number" min="0" max="100" step="0.5" value={annualVolatility} onChange={e => setAnnualVolatility(e.target.value)} /></label>
          <label>Time horizon (years)<input type="number" min="0.1" max="30" step="0.5" value={years} onChange={e => setYears(e.target.value)} /></label>
        </div>
        <div className={styles.results} aria-live="polite">
          {result ? <>
            <span className={styles.label}>Illustrative central outcome</span><strong className={styles.big}>{money(result.central)}</strong>
            <div className={styles.metrics}><div><small>Illustrative gain / loss</small><b>{money(result.gain)}</b></div><div><small>Starting capital</small><b>{money(Number(capital))}</b></div></div>
            <div className={styles.range}><div><span>Lower scenario</span><b>{money(result.lower)}</b></div><div className={styles.rangeTrack}><i style={{left:"0%",width:"100%"}} /></div><div><span>Upper scenario</span><b>{money(result.upper)}</b></div></div>
            <p className={styles.explain}>The scenario range uses a simplified volatility adjustment that grows with the square root of time. It is not a confidence interval, forecast, probability estimate or maximum-loss calculation.</p>
          </> : <p className={styles.warning}>Enter a positive starting amount, a return from -99% to 100%, volatility from 0–100%, and a horizon up to 30 years.</p>}
        </div>
      </div>
      <p className={styles.disclosure}>Educational illustration only. Returns are assumed to compound annually; volatility is a user-entered assumption, not measured MSE volatility. Actual returns can be negative, irregular and materially different. Fees, taxes, inflation and liquidity are excluded.</p>
    </section>
  );
}
