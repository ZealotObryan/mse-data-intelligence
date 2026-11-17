"use client";

import { useMemo, useState } from "react";
import styles from "./MarketMechanics.module.css";

type Side = "buy" | "sell";
type Order = { id: number; side: Side; price: number; quantity: number };

const initialOrders: Order[] = [
  { id: 1, side: "buy", price: 985, quantity: 120 },
  { id: 2, side: "buy", price: 980, quantity: 200 },
  { id: 3, side: "buy", price: 975, quantity: 150 },
  { id: 4, side: "sell", price: 995, quantity: 100 },
  { id: 5, side: "sell", price: 1000, quantity: 180 },
  { id: 6, side: "sell", price: 1010, quantity: 140 }
];

export default function OrderBookSimulator() {
  const [orders, setOrders] = useState<Order[]>(initialOrders);
  const [side, setSide] = useState<Side>("buy");
  const [price, setPrice] = useState("990");
  const [quantity, setQuantity] = useState("50");
  const [message, setMessage] = useState("Add a hypothetical order, then test whether the best bid and ask can cross.");
  const [lastTrade, setLastTrade] = useState<{ price: number; quantity: number } | null>(null);

  const bids = useMemo(() => orders.filter(o => o.side === "buy").sort((a,b) => b.price-a.price), [orders]);
  const asks = useMemo(() => orders.filter(o => o.side === "sell").sort((a,b) => a.price-b.price), [orders]);
  const bestBid = bids[0]?.price ?? null;
  const bestAsk = asks[0]?.price ?? null;
  const spread = bestBid !== null && bestAsk !== null ? bestAsk-bestBid : null;

  function addOrder() {
    const p = Number(price), q = Number(quantity);
    if (!Number.isFinite(p) || !Number.isFinite(q) || p <= 0 || q <= 0 || !Number.isInteger(q)) {
      setMessage("Enter a positive price and a whole-number quantity.");
      return;
    }
    setOrders(current => [...current, { id: Math.max(0, ...current.map(o=>o.id))+1, side, price:p, quantity:q }]);
    setMessage(`Hypothetical ${side} order added: ${q} shares at MWK ${p.toFixed(2)}.`);
    setLastTrade(null);
  }

  function matchOrders() {
    if (!bids.length || !asks.length || bestBid! < bestAsk!) {
      setMessage("No match: the highest bid is below the lowest ask. A trade is not formed in this simplified model.");
      setLastTrade(null);
      return;
    }
    const bid = bids[0], ask = asks[0], traded = Math.min(bid.quantity, ask.quantity);
    const tradePrice = ask.price;
    setOrders(current => current.flatMap(o => {
      if (o.id === bid.id || o.id === ask.id) {
        const remaining = o.quantity-traded;
        return remaining > 0 ? [{...o, quantity:remaining}] : [];
      }
      return [o];
    }));
    setLastTrade({ price: tradePrice, quantity: traded });
    setMessage(`Illustrative match: ${traded} shares at MWK ${tradePrice.toFixed(2)}. Remaining quantities stay in the book.`);
  }

  function reset() {
    setOrders(initialOrders);
    setLastTrade(null);
    setMessage("Order book reset to its original hypothetical orders.");
  }

  return (
    <section className={styles.card} aria-labelledby="order-book-title">
      <div className={styles.heading}><div><span className={styles.kicker}>MARKET MECHANICS · SIMULATOR 03</span><h2 id="order-book-title">Explore an order book</h2><p>See how buyers’ bids and sellers’ asks interact. All orders below are fictional.</p></div><span className={styles.tag}>SIMULATED</span></div>
      <div className={styles.metrics}>
        <div><small>BEST BID</small><b>{bestBid===null?"—":`MWK ${bestBid.toFixed(2)}`}</b><span>Highest buyer price</span></div>
        <div><small>BEST ASK</small><b>{bestAsk===null?"—":`MWK ${bestAsk.toFixed(2)}`}</b><span>Lowest seller price</span></div>
        <div><small>BID–ASK SPREAD</small><b>{spread===null?"—":`MWK ${spread.toFixed(2)}`}</b><span>Ask minus bid</span></div>
      </div>
      <div className={styles.book}>
        <div><h3>Buy orders <span>Bid</span></h3>{bids.length ? bids.slice(0,5).map(o=><div className={styles.order} key={o.id}><b>{o.price.toFixed(2)}</b><span>{o.quantity.toLocaleString()}</span></div>):<p className={styles.empty}>No buy orders</p>}</div>
        <div><h3>Sell orders <span>Ask</span></h3>{asks.length ? asks.slice(0,5).map(o=><div className={styles.order} key={o.id}><b>{o.price.toFixed(2)}</b><span>{o.quantity.toLocaleString()}</span></div>):<p className={styles.empty}>No sell orders</p>}</div>
      </div>
      <div className={styles.orderForm}>
        <label>Order side<select value={side} onChange={e=>setSide(e.target.value as Side)}><option value="buy">Buy (bid)</option><option value="sell">Sell (ask)</option></select></label>
        <label>Price (MWK)<input inputMode="decimal" value={price} onChange={e=>setPrice(e.target.value)} /></label>
        <label>Quantity (shares)<input inputMode="numeric" value={quantity} onChange={e=>setQuantity(e.target.value)} /></label>
        <button type="button" onClick={addOrder}>Add order</button>
      </div>
      <div className={styles.actions}><button type="button" onClick={matchOrders}>Try matching orders</button><button type="button" className={styles.secondary} onClick={reset}>Reset book</button></div>
      <p className={styles.feedback} role="status">{message}</p>
      {lastTrade&&<div className={styles.trade}><b>Last simulated trade</b><span>{lastTrade.quantity.toLocaleString()} shares × MWK {lastTrade.price.toFixed(2)}</span></div>}
      <p className={styles.note}>Learning model only: this demonstrates price crossing and a simplified resting-ask execution. It is not the Malawi Stock Exchange matching engine, trading rules, queue priority or an executable quote.</p>
    </section>
  );
}
