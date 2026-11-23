"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { ColorType, LineSeries, createChart } from "lightweight-charts";
import { normalizeDailyBars } from "@/lib/market/normalize-bars.cjs";
import styles from "./SyntheticInstrumentDetail.module.css";
type Instrument={symbol:string;name:string;sector:string;price:number;change:number;vol:string;cap:string;spark:number[]};
const DATES=["2026-01-05","2026-01-06","2026-01-07","2026-01-08","2026-01-09","2026-01-12","2026-01-13","2026-01-14","2026-01-15"];
export default function SyntheticInstrumentDetail({instrument,onClose}:{instrument:Instrument;onClose:()=>void}){
 const [range,setRange]=useState<"5"|"all">("all"),chartRef=useRef<HTMLDivElement>(null);
 const bars=useMemo(()=>normalizeDailyBars(instrument.spark.map((close,index)=>({date:DATES[index],open:String(close),high:String(close),low:String(close),close:String(close),volume:null}))).bars,[instrument.spark]);
 const visible=range==="5"?bars.slice(-5):bars,latest=visible.at(-1);
 useEffect(()=>{const el=chartRef.current;if(!el||!visible.length)return;
 const chart=createChart(el,{autoSize:true,layout:{background:{type:ColorType.Solid,color:"transparent"},textColor:"#8793a7",fontFamily:"Arial, sans-serif",fontSize:11},grid:{vertLines:{color:"rgba(135,147,167,.07)"},horzLines:{color:"rgba(135,147,167,.14)"}},rightPriceScale:{borderColor:"rgba(135,147,167,.2)"},timeScale:{borderColor:"rgba(135,147,167,.2)",timeVisible:false},handleScroll:false,handleScale:false});
 const series=chart.addSeries(LineSeries,{color:"#347653",lineWidth:2,priceLineVisible:false,lastValueVisible:true,crosshairMarkerRadius:4});
 series.setData(visible.map(bar=>({time:bar.date,value:Number(bar.close)})));chart.timeScale().fitContent();return()=>chart.remove();
 },[visible]);
 return <section className={styles.detail} aria-label={instrument.name+" illustrative instrument detail"}>
 <div className={styles.header}><div><span className={styles.eyebrow}>SYNTHETIC DEMO SECURITY · {instrument.symbol}</span><h2>{instrument.name}</h2><p>{instrument.sector} · Illustrative observations only</p></div><button type="button" className={styles.close} onClick={onClose}>Close detail ×</button></div>
 <div className={styles.summary}><div><small>REFERENCE PRICE</small><b>MWK {instrument.price.toLocaleString("en-US",{maximumFractionDigits:2})}</b></div><div><small>FIXTURE CHANGE</small><b className={instrument.change>=0?styles.up:styles.down}>{instrument.change>=0?"+":""}{instrument.change.toFixed(2)}%</b></div><div><small>FIXTURE MARKET CAP</small><b>{instrument.cap}</b></div><div><small>FIXTURE VOLUME</small><b>{instrument.vol}</b></div></div>
 <div className={styles.chartPanel}><div className={styles.chartHeading}><div><b>Illustrative close-price history</b><small>Close-only sample · not exchange OHLCV data</small></div><div className={styles.ranges} aria-label="Chart observation range"><button type="button" aria-pressed={range==="5"} onClick={()=>setRange("5")}>5 observations</button><button type="button" aria-pressed={range==="all"} onClick={()=>setRange("all")}>All 9</button></div></div>
 <div ref={chartRef} className={styles.chart} role="img" aria-label={"Illustrative closing-price line chart for "+instrument.name}/><div className={styles.chartFoot}><span>{visible.length} sample observations</span><span>Dates and values are synthetic</span></div></div>
 <div className={styles.ohlc}><div><small>LAST SAMPLE DATE</small><b>{latest?.date??"Unavailable"}</b></div><div><small>OPEN / HIGH / LOW / CLOSE</small><b>{latest?[latest.open,latest.high,latest.low,latest.close].map(v=>Number(v).toFixed(2)).join(" / "):"Unavailable"}</b></div><div><small>VOLUME</small><b>Not supplied</b></div></div>
 <p className={styles.disclaimer}>This instrument profile is a UI demonstration. The plotted observations are synthetic, use flat OHLC values to exercise the normalization contract, and must not be interpreted as real MSE prices, trading history or investment information.</p></section>;
}