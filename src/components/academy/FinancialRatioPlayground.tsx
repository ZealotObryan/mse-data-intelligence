"use client";

import { useMemo, useState } from "react";
import styles from "./FinancialRatioPlayground.module.css";

const defaults = { revenue: "1200000", netIncome: "120000", currentAssets: "500000", currentLiabilities: "250000", debt: "300000", equity: "600000", shares: "60000", price: "30" };
const fields = [
  ["revenue","Revenue (MWK)"],["netIncome","Net income (MWK)"],["currentAssets","Current assets (MWK)"],["currentLiabilities","Current liabilities (MWK)"],["debt","Total debt (MWK)"],["equity","Total equity (MWK)"],["shares","Weighted-average shares"],["price","Reference price per share (MWK)"]
] as const;
export default function FinancialRatioPlayground() {
  const [facts,setFacts] = useState(defaults);
  const metrics = useMemo(() => {
    const n = Object.fromEntries(Object.entries(facts).map(([k,v])=>[k,Number(v)])) as Record<string,number>;
    const finite = Object.values(n).every(Number.isFinite) && Object.values(facts).every(value => value.trim() !== "");
    return {
      finite,
      netMargin: finite && n.revenue !== 0 ? n.netIncome/n.revenue : null,
      currentRatio: finite && n.currentLiabilities > 0 ? n.currentAssets/n.currentLiabilities : null,
      debtEquity: finite && n.equity > 0 ? n.debt/n.equity : null,
      eps: finite && n.shares > 0 ? n.netIncome/n.shares : null,
      pe: finite && n.price > 0 && n.shares > 0 && n.netIncome > 0 ? n.price/(n.netIncome/n.shares) : null
    };
  },[facts]);
  const fmt = (v:number|null,suffix="") => v===null || !Number.isFinite(v) ? "Unavailable" : v.toFixed(2)+suffix;
  const items = [
    {name:"Net profit margin",value:fmt(metrics.netMargin===null?null:metrics.netMargin*100,"%"),formula:"Net income ÷ revenue",meaning:"The share of revenue remaining as net profit. A negative result indicates a loss."},
    {name:"Current ratio",value:fmt(metrics.currentRatio,"×"),formula:"Current assets ÷ current liabilities",meaning:"A short-term liquidity measure. Context matters; a higher figure is not automatically better."},
    {name:"Debt-to-equity",value:fmt(metrics.debtEquity,"×"),formula:"Total debt ÷ total equity",meaning:"Compares debt financing with shareholders’ equity. Definitions and sector context matter."},
    {name:"Earnings per share",value:fmt(metrics.eps),formula:"Net income ÷ weighted-average shares",meaning:"A simplified EPS calculation. Prefer the issuer’s reported EPS when available."},
    {name:"Price-to-earnings",value:fmt(metrics.pe,"×"),formula:"Reference share price ÷ positive EPS",meaning:"Relates price to earnings. It is unavailable when earnings or the reference price are not positive."}
  ];
  return <section className={styles.card} aria-labelledby="ratio-playground-title">
    <div className={styles.heading}><div><span className={styles.kicker}>FINANCIAL STATEMENTS · EXPLORER 07</span><h2 id="ratio-playground-title">Financial Ratio Playground</h2><p>Change fictional financial statement inputs and see how common ratios are calculated.</p></div><span className={styles.tag}>FICTIONAL DATA</span></div>
    <div className={styles.layout}>
      <div className={styles.inputs}>{fields.map(([key,label])=><label key={key}>{label}<input type="number" value={facts[key]} onChange={e=>setFacts(current=>({...current,[key]:e.target.value}))}/></label>)}<button type="button" onClick={()=>setFacts(defaults)}>Reset example</button></div>
      <div className={styles.metrics}>{items.map(item=><article key={item.name}><div className={styles.metricTop}><h3>{item.name}</h3><strong>{metrics.finite?item.value:"Check inputs"}</strong></div><small>{item.formula}</small><p>{item.meaning}</p></article>)}</div>
    </div>
    <p className={styles.disclosure}>All starting values are fictional and are not attributable to any MSE-listed company. The calculations do not verify accounting definitions, reporting periods, currencies, audit status or market-price dates. Ratios are descriptive, not investment recommendations.</p>
  </section>;
}
