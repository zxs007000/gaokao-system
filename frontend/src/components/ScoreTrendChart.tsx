"use client";

import ReactECharts from "echarts-for-react";
import { TrendData } from "@/lib/api";

export default function ScoreTrendChart({ data }: { data: Record<string, TrendData[]> }) {
  const years = [...new Set(Object.values(data).flat().map(d => d.year))].sort();
  const series = Object.entries(data).map(([name, points]) => ({
    name,
    type: "line" as const,
    data: years.map(y => points.find(d => d.year === y)?.min_score ?? null),
    smooth: true,
    symbol: "circle",
    symbolSize: 6,
  }));

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "#fff",
      borderColor: "#e2e8f0",
      textStyle: { color: "#1e293b" },
    },
    legend: {
      data: Object.keys(data),
      selected: Object.keys(data).reduce((acc, n) => { acc[n] = true; return acc; }, {} as Record<string, boolean>),
      textStyle: { color: "#64748b" },
      top: 0,
    },
    grid: { left: "3%", right: "4%", bottom: "3%", top: 40, containLabel: true },
    xAxis: {
      type: "category" as const,
      data: years.map(String),
      axisLabel: { color: "#94a3b8" },
      axisLine: { lineStyle: { color: "#e2e8f0" } },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "#f1f5f9" } },
    },
    series,
    color: ["#3b82f6", "#ef4444", "#f59e0b", "#10b981", "#8b5cf6"],
  };

  return <ReactECharts option={option} style={{ height: 400 }} />;
}
