"use client";

import ReactECharts from "echarts-for-react";
import { CompareData } from "@/lib/api";

export default function RadarCompare({ data }: { data: Record<string, CompareData> }) {
  const names = Object.keys(data);
  if (names.length < 2) return <p className="text-slate-400 py-8 text-center">请选择至少 2 所大学进行对比</p>;

  const series = names.map(name => {
    const d = data[name];
    const latest = d.scores.length > 0 ? d.scores[d.scores.length - 1] : null;
    return {
      value: [
        latest?.min_score || 0,
        latest?.min_rank ? 100000 - latest.min_rank : 0,
        d.plans.total_quota || 0,
        d.plans.major_count || 0,
      ],
      name,
    };
  });

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      backgroundColor: "#fff",
      borderColor: "#e2e8f0",
      textStyle: { color: "#1e293b" },
    },
    legend: {
      data: names,
      selected: names.reduce((acc, n) => { acc[n] = true; return acc; }, {} as Record<string, boolean>),
      textStyle: { color: "#64748b" },
      bottom: 0,
    },
    radar: {
      indicator: [
        { name: "最新分数", max: 750 },
        { name: "录取位次(反)", max: 200000 },
        { name: "招生计划", max: 5000 },
        { name: "专业数量", max: 200 },
      ],
      axisName: { color: "#64748b" },
      splitArea: { areaStyle: { color: ["transparent"] } },
      splitLine: { lineStyle: { color: "#e2e8f0" } },
      axisLine: { lineStyle: { color: "#e2e8f0" } },
    },
    series: [{ type: "radar", data: series }],
    color: ["#3b82f6", "#ef4444", "#f59e0b", "#10b981"],
  };

  return <ReactECharts option={option} style={{ height: 400 }} />;
}
