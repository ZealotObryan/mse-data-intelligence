"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./LocalWatchlist.module.css";

type Security = { symbol: string; name: string; sector: string; price: number; change: number };
const STORAGE_KEY = "mse-watchlist:v1";

export default function LocalWatchlist({ securities }: { securities: Security[] }) {
  const [symbols, setSymbols] = useState<string[]>([]);
  const [candidate, setCandidate] = useState("");
  const [ready, setReady] = useState(false);
  const [storageAvailable, setStorageAvailable] = useState(true);
  const available = useMemo(() => securities.filter((security) => !symbols.includes(security.symbol)), [securities, symbols]);
  const watched = useMemo(() => symbols.map((symbol) => securities.find((security) => security.symbol === symbol)).filter((security): security is Security => Boolean(security)), [securities, symbols]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed: unknown = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          const valid = parsed.filter((value): value is string => typeof value === "string" && securities.some((security) => security.symbol === value));
          setSymbols(Array.from(new Set(valid)));
        }
      }
    } catch {
      setStorageAvailable(false);
    } finally {
      setReady(true);
    }
  }, [securities]);

  useEffect(() => {
    if (!ready) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(symbols));
    } catch {
      setStorageAvailable(false);
    }
  }, [ready, symbols]);

  function addSecurity() {
    if (!candidate || !available.some((security) => security.symbol === candidate)) return;
    setSymbols((current) => [...current, candidate]);
    setCandidate("");
  }

  function removeSecurity(symbol: string) {
    setSymbols((current) => current.filter((item) => item !== symbol));
  }

  return (
    <section className={styles.panel} aria-labelledby="local-watchlist-title">
      <div className={styles.heading}>
        <div><span className={styles.eyebrow}>PERSONAL WORKSPACE</span><h2 id="local-watchlist-title">My watchlist</h2><p>Keep an eye on sample securities you want to research.</p></div>
        <span className={styles.count}>{watched.length} / {securities.length} saved</span>
      </div>
      <div className={styles.addRow}>
        <label className={styles.srOnly} htmlFor="watchlist-add">Add a security</label>
        <select id="watchlist-add" value={candidate} onChange={(event) => setCandidate(event.target.value)} disabled={!ready || available.length === 0}>
          <option value="">Choose a security to add</option>
          {available.map((security) => <option key={security.symbol} value={security.symbol}>{security.symbol} · {security.name}</option>)}
        </select>
        <button type="button" onClick={addSecurity} disabled={!candidate || !ready}>Add to watchlist</button>
      </div>
      {!ready ? <p className={styles.empty}>Loading your device watchlist…</p> : watched.length === 0 ? <div className={styles.empty}><b>No securities saved yet</b><span>Add a sample security above. Your list stays in this browser on this device.</span></div> : (
        <ul className={styles.list}>
          {watched.map((security) => <li key={security.symbol}>
            <div className={styles.identity}><b>{security.symbol}</b><span><strong>{security.name}</strong><small>{security.sector} · Synthetic demo security</small></span></div>
            <div className={styles.quote}><b>MWK {security.price.toLocaleString("en-US", { maximumFractionDigits: 2 })}</b><small className={security.change >= 0 ? styles.up : styles.down}>{security.change >= 0 ? "+" : ""}{security.change.toFixed(2)}%</small></div>
            <button type="button" className={styles.remove} onClick={() => removeSecurity(security.symbol)} aria-label={`Remove ${security.name} from watchlist`}>Remove</button>
          </li>)}
        </ul>
      )}
      <p className={styles.note}>{storageAvailable ? "Saved only in this browser using local device storage. It is not linked to an account and will not sync across devices." : "Browser storage is unavailable. This list may not persist after you leave or refresh this page."} All displayed prices and movements are synthetic examples, not live MSE data.</p>
    </section>
  );
}
