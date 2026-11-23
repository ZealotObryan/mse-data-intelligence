"use client";

import { useMemo, useState } from "react";
import styles from "./SyntheticCompanyComparison.module.css";

type Security = { symbol: string; name: string; sector: string; price: number; change: number; vol: string; cap: string };
const fmt = (value: number) => new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(value);
const volumeValue = (value: string) => { const n = Number.parseFloat(value); return value.toUpperCase().includes("M") ? n * 1_000_000 : value.toUpperCase().includes("K") ? n * 1_000 : n; };
const capValue = (value: string) => { const n = Number.parseFloat(value.replace(/[^0-9.]/g, "")); return value.toUpperCase().includes("B") ? n * 1_000_000_000 : value.toUpperCase().includes("M") ? n * 1_000_000 : n; };

export default function SyntheticCompanyComparison({ securities }: { securities: Security[] }) {
  const [selected, setSelected] = useState<string[]>([]);
  const compared = useMemo(() => selected.map((symbol) => securities.find((security) => security.symbol === symbol)).filter((security): security is Security => Boolean(security)), [selected, securities]);
  const ranked = useMemo(() => [...compared].sort((a, b) => b.change - a.change), [compared]);
  function toggle(symbol: string) {
    setSelected((current) => current.includes(symbol) ? current.filter((item) => item !== symbol) : current.length < 3 ? [...current, symbol] : current);
  }
  return (
    <section className={styles.panel} aria-labelledby="comparison-title">
      <div className={styles.header}><div><span className={styles.eyebrow}>SIDE-BY-SIDE RESEARCH</span><h2 id="comparison-title">Compare sample companies</h2><p>Select two or three securities to compare the available demo fields.</p></div><span className={styles.counter}>{selected.length} / 3 selected</span></div>
      <div className={styles.choices} role="group" aria-label="Choose securities to compare">
        {securities.map((security) => <label key={security.symbol} className={selected.includes(security.symbol) ? styles.choiceSelected : styles.choice}>
          <input type="checkbox" checked={selected.includes(security.symbol)} disabled={!selected.includes(security.symbol) && selected.length >= 3} onChange={() => toggle(security.symbol)} />
          <span><b>{security.symbol}</b><small>{security.name}</small></span>
        </label>)}
      </div>
      {compared.length < 2 ? <div className={styles.empty}>Choose at least two companies to see a side-by-side comparison.</div> : <>
        <div className={styles.tableWrap} role="region" aria-label="Company comparison table" tabIndex={0}>
          <table className={styles.table}><thead><tr><th scope="col">Metric</th>{compared.map((security) => <th scope="col" key={security.symbol}><b>{security.symbol}</b><small>{security.name}</small></th>)}</tr></thead>
            <tbody>
              <tr><th scope="row">Sector</th>{compared.map((s) => <td key={s.symbol}>{s.sector}</td>)}</tr>
              <tr><th scope="row">Sample price</th>{compared.map((s) => <td key={s.symbol}>MWK {fmt(s.price)}</td>)}</tr>
              <tr><th scope="row">Illustrative change</th>{compared.map((s) => <td key={s.symbol} className={s.change >= 0 ? styles.up : styles.down}>{s.change >= 0 ? "+" : ""}{s.change.toFixed(2)}%</td>)}</tr>
              <tr><th scope="row">Sample volume</th>{compared.map((s) => <td key={s.symbol}>{s.vol}</td>)}</tr>
              <tr><th scope="row">Sample market cap</th>{compared.map((s) => <td key={s.symbol}>{s.cap}</td>)}</tr>
            </tbody>
          </table>
        </div>
        <p className={styles.insight}>Among the selected examples, <b>{ranked[0].name}</b> has the highest illustrative percentage movement ({ranked[0].change >= 0 ? "+" : ""}{ranked[0].change.toFixed(2)}%). This is a comparison of synthetic fixtures only, not an investment signal.</p>
        <button type="button" className={styles.clear} onClick={() => setSelected([])}>Clear comparison</button>
      </>}
      <p className={styles.note}>All figures are synthetic demo values. No verified issuer financial statements, valuation multiples, dividend history or real MSE market data are connected. Volume and market capitalisation are shown as supplied fixtures; no inferred fundamentals are presented.</p>
    </section>
  );
}
