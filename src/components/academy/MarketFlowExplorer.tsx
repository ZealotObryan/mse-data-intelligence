"use client";

import { useState } from "react";
import styles from "./MarketMechanics.module.css";

export default function MarketFlowExplorer() {
  const [market, setMarket] = useState<"primary" | "secondary">("primary");
  const primary = market === "primary";
  return (
    <section className={styles.card} aria-labelledby="market-flow-title">
      <div className={styles.heading}><div><span className={styles.kicker}>MARKET STRUCTURE · EXPLAINER 04</span><h2 id="market-flow-title">Where does the money go?</h2><p>Compare a new share issue with a later trade between investors.</p></div><span className={styles.tag}>INTERACTIVE</span></div>
      <div className={styles.toggle} role="group" aria-label="Choose market type">
        <button type="button" aria-pressed={primary} className={primary?styles.selected:""} onClick={()=>setMarket("primary")}>Primary market</button>
        <button type="button" aria-pressed={!primary} className={!primary?styles.selected:""} onClick={()=>setMarket("secondary")}>Secondary market</button>
      </div>
      <div className={styles.flow} aria-live="polite">
        <div className={styles.party}><span>{primary?"ISSUER":"SELLING INVESTOR"}</span><b>{primary?"Company":"Investor A"}</b><small>{primary?"Creates and offers new shares":"Already owns the shares"}</small></div>
        <div className={styles.arrow}><b>{primary?"New shares":"Existing shares"}</b><span>→</span></div>
        <div className={styles.party}><span>BUYER</span><b>{primary?"Investor":"Investor B"}</b><small>{primary?"Subscribes to the issue":"Purchases from another investor"}</small></div>
      </div>
      <div className={styles.cashFlow}>
        <div className={styles.cashIcon}>MWK</div>
        <div><b>{primary?"Cash flows to the issuing company":"Cash flows to the selling investor"}</b><p>{primary?"The company receives the proceeds from the new issue, subject to issue costs and terms.":"The seller receives the sale proceeds. The company does not receive money from this ordinary secondary-market trade."}</p></div>
      </div>
      <div className={styles.takeaway}><b>Key distinction</b><span>{primary?"Primary market = new securities are issued; capital is raised by the issuer.":"Secondary market = existing securities change hands; investors trade with one another."}</span></div>
      <p className={styles.note}>Simplified educational illustration. Real issuance structures, intermediaries, settlement and fees can vary. This is not a live transaction or a description of a specific MSE offer.</p>
    </section>
  );
}
