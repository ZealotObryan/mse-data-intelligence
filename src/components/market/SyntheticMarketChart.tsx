"use client";

import { useEffect, useRef } from "react";
import { AreaSeries, ColorType, createChart } from "lightweight-charts";
import styles from "./SyntheticMarketChart.module.css";

export type IndexedPoint = { date: string; value: number };

export function normalizeIndexedPoints(data: IndexedPoint[]) {
  return [...data]
    .filter((point) => {
      if (!Number.isFinite(point.value) || !/^\d{4}-\d{2}-\d{2}$/.test(point.date)) return false;
      const parsed = new Date(`${point.date}T00:00:00Z`);
      return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === point.date;
    })
    .sort((a, b) => a.date.localeCompare(b.date))
    .filter((point, index, points) => index === 0 || point.date !== points[index - 1].date);
}

type Props = { data: IndexedPoint[] };

export default function SyntheticMarketChart({ data }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const normalized = normalizeIndexedPoints(data);
    if (normalized.length === 0) return;

    const chart = createChart(container, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#8793a7",
        attributionLogo: true,
        fontFamily: "Arial, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "rgba(135, 147, 167, 0.08)" },
        horzLines: { color: "rgba(135, 147, 167, 0.16)" },
      },
      rightPriceScale: { borderColor: "rgba(135, 147, 167, 0.2)" },
      timeScale: { borderColor: "rgba(135, 147, 167, 0.2)", timeVisible: false },
      handleScroll: false,
      handleScale: false,
      crosshair: { vertLine: { labelBackgroundColor: "#347653" }, horzLine: { labelBackgroundColor: "#347653" } },
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: "#347653",
      topColor: "rgba(52, 118, 83, 0.24)",
      bottomColor: "rgba(52, 118, 83, 0.015)",
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
    });

    series.setData(normalized.map((point) => ({ time: point.date, value: point.value })));
    chart.timeScale().fitContent();

    return () => chart.remove();
  }, [data]);

  if (normalizeIndexedPoints(data).length === 0) {
    return <div className={styles.empty} role="status">No valid illustrative observations are available for this chart.</div>;
  }

  return (
    <div className={styles.frame}>
      <div ref={containerRef} className={styles.chart} role="img" aria-label="Synthetic indexed market performance chart. Illustrative values only, not actual Malawi Stock Exchange data." />
      <div className={styles.attribution}>
        <span>Synthetic indexed series · not an MSE index</span>
        <a href="https://www.tradingview.com/" target="_blank" rel="noreferrer">TradingView Lightweight Charts™ · Copyright © 2025 TradingView, Inc.</a>
      </div>
    </div>
  );
}
