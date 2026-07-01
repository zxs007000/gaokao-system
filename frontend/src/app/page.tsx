"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchStats, StatsData } from "@/lib/api";

const features = [
  {
    title: "志愿推荐",
    desc: "输入分数和省份，一键获取冲/稳/保三档志愿方案，AI顾问实时分析",
    href: "/recommend",
    icon: "🎯",
    gradient: "from-blue-500 to-blue-600",
    bg: "bg-blue-50",
  },
  {
    title: "性格测试",
    desc: "九型人格 + 职业适应性测试，了解性格特点，获取个性化专业推荐",
    href: "/personality",
    icon: "🧭",
    gradient: "from-indigo-500 to-indigo-600",
    bg: "bg-indigo-50",
  },
  {
    title: "院校分析",
    desc: "多维度深度剖析院校实力：分数趋势、招生计划、专业热度、保研率",
    href: "/analysis",
    icon: "📊",
    gradient: "from-purple-500 to-purple-600",
    bg: "bg-purple-50",
  },
  {
    title: "趋势分析",
    desc: "查看各大学历年分数线变化，把握录取走向",
    href: "/trends",
    icon: "📈",
    gradient: "from-emerald-500 to-emerald-600",
    bg: "bg-emerald-50",
  },
  {
    title: "院校对比",
    desc: "多维度对比几所大学的录取分数、排名、招生人数",
    href: "/compare",
    icon: "⚖️",
    gradient: "from-amber-500 to-amber-600",
    bg: "bg-amber-50",
  },
];

const statCards = [
  { label: "覆盖大学", key: "universities", icon: "🏫", color: "text-blue-600", bg: "bg-blue-50" },
  { label: "投档数据", key: "scorelines", icon: "📊", color: "text-emerald-600", bg: "bg-emerald-50", fmt: (v: number) => `${(v / 10000).toFixed(0)}万+` },
  { label: "覆盖省份", key: "provinces", icon: "🗺️", color: "text-violet-600", bg: "bg-violet-50" },
  { label: "数据年度", key: "latest_year", icon: "📅", color: "text-amber-600", bg: "bg-amber-50", fmt: (v: number) => `${v || "—"}` },
];

export default function HomePage() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    fetchStats()
      .then(setStats)
      .catch(e => { console.error(e); setErr(`后端连接失败：${e.message}。请先启动 API 服务。`); });
  }, []);

  return (
    <div className="space-y-10 pb-8">
      {/* Hero */}
      <div className="text-center pt-8 pb-4">
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-800 mb-3">
          高考志愿分析平台
        </h1>
        <p className="text-lg text-slate-500 max-w-xl mx-auto">
          基于历年投档数据，智能推荐志愿，洞察分数线趋势
        </p>
      </div>

      {/* Error */}
      {err && (
        <div className="card border-red-200 bg-red-50">
          <p className="text-red-600 font-medium">⚠️ {err}</p>
          <p className="text-sm text-red-400 mt-1">启动命令：<code className="bg-red-100 px-2 py-0.5 rounded text-red-600">cd api && uvicorn main:app --reload</code></p>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {statCards.map(s => {
            const raw = (stats as any)[s.key];
            const val = s.fmt ? s.fmt(raw) : (raw?.toLocaleString?.() ?? raw ?? "—");
            return (
              <div key={s.label} className="card text-center py-5">
                <span className="text-2xl mb-2 block">{s.icon}</span>
                <p className={`text-2xl font-extrabold ${s.color}`}>{val}</p>
                <p className="text-xs text-slate-400 mt-1">{s.label}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Loading */}
      {!stats && !err && (
        <div className="text-center text-slate-400 py-16">
          <div className="animate-spin inline-block w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mb-4" />
          <p>加载中...</p>
        </div>
      )}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
        {features.map(f => (
          <Link key={f.href} href={f.href} className="block">
            <div className="card card-interactive group h-full flex flex-col">
              <div className={`w-12 h-12 rounded-xl ${f.bg} flex items-center justify-center text-2xl mb-4`}>
                {f.icon}
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">{f.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed flex-1">{f.desc}</p>
              <span className={`mt-3 text-sm font-semibold bg-gradient-to-r ${f.gradient} bg-clip-text text-transparent`}>
                立即使用 →
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
