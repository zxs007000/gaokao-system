"use client";

import { useState } from "react";
import { searchUniversities, UniversityResult, fetchScoreTrend, fetchEnrollmentPlans, fetchMajorRanking, fetchUniversityQuality, ScoreTrendData, EnrollmentPlanData, MajorRankData, UniversityQualityData } from "@/lib/api";

const provinces = ["北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海","宁夏","新疆","内蒙古","西藏"];

export default function AnalysisPage() {
  const [query, setQuery] = useState("");
  const [province, setProvince] = useState("河北");
  const [results, setResults] = useState<UniversityResult[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [trend, setTrend] = useState<{ trend: ScoreTrendData[]; volatility: number | null; trend_direction: string } | null>(null);
  const [plans, setPlans] = useState<{ total_plan_2025: number; major_count: number; plans: EnrollmentPlanData[] } | null>(null);
  const [majors, setMajors] = useState<{ majors: MajorRankData[] } | null>(null);
  const [quality, setQuality] = useState<UniversityQualityData | null>(null);
  const [tab, setTab] = useState<"overview" | "trend" | "plans" | "majors">("overview");

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await searchUniversities(query);
      setResults(res);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (name: string) => {
    setSelected(name);
    setTab("overview");
    setTrend(null);
    setPlans(null);
    setMajors(null);
    setQuality(null);
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        fetchScoreTrend(name, province),
        fetchEnrollmentPlans(name, province),
        fetchMajorRanking(name, province),
        fetchUniversityQuality(name),
      ]);
      if (results[0].status === "fulfilled") setTrend(results[0].value);
      if (results[1].status === "fulfilled") setPlans(results[1].value);
      if (results[2].status === "fulfilled") setMajors(results[2].value);
      if (results[3].status === "fulfilled") setQuality(results[3].value);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">📊 院校深度分析</h1>
        <p className="text-sm text-slate-500 mt-1">多维度剖析院校实力，数据驱动决策</p>
      </div>

      {/* Search */}
      <div className="card">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">搜索大学</label>
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSearch()}
              placeholder="输入大学名称..."
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">省份</label>
            <select value={province} onChange={e => setProvince(e.target.value)} className="w-28">
              {provinces.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            {loading ? "搜索中..." : "搜索"}
          </button>
        </div>

        {/* Search Results */}
        {results.length > 0 && (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            {results.map(r => (
              <button
                key={r.name}
                onClick={() => handleSelect(r.name)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  selected === r.name
                    ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                }`}
              >
                <p className="font-semibold text-sm text-slate-800 truncate">{r.name}</p>
                <div className="flex gap-1 mt-1 flex-wrap">
                  {r.tags.map(t => (
                    <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 font-medium">{t}</span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Content */}
      {selected && (
        <div className="space-y-6 animate-fadeIn">
          {/* Tabs */}
          <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
            {([
              ["overview", "院校概览"],
              ["trend", "分数趋势"],
              ["plans", "招生计划"],
              ["majors", "专业热度"],
            ] as const).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  tab === key ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-700"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Overview Tab */}
          {tab === "overview" && quality && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Basic Info */}
              <div className="card">
                <h3 className="font-bold text-slate-800 mb-3">基本信息</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-slate-400">校名</span><span className="font-medium">{quality.name}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">省份</span><span>{quality.province}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">类型</span><span>{quality.type}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">层次</span><span>{quality.level}</span></div>
                  <div className="flex gap-1.5 mt-2">
                    {quality.is_985 && <span className="tag bg-amber-100 text-amber-700">985</span>}
                    {quality.is_211 && <span className="tag bg-blue-100 text-blue-700">211</span>}
                    {quality.is_dual_class && <span className="tag bg-purple-100 text-purple-700">双一流</span>}
                  </div>
                </div>
              </div>

              {/* Rankings */}
              <div className="card">
                <h3 className="font-bold text-slate-800 mb-3">排名</h3>
                <div className="grid grid-cols-3 gap-3">
                  {quality.rankings.ruanke && (
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-blue-600">#{quality.rankings.ruanke}</p>
                      <p className="text-xs text-slate-400 mt-1">软科</p>
                    </div>
                  )}
                  {quality.rankings.qs && (
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-emerald-600">#{quality.rankings.qs}</p>
                      <p className="text-xs text-slate-400 mt-1">QS</p>
                    </div>
                  )}
                  {quality.rankings.xyh && (
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                      <p className="text-2xl font-bold text-violet-600">#{quality.rankings.xyh}</p>
                      <p className="text-xs text-slate-400 mt-1">校友会</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Academic */}
              <div className="card">
                <h3 className="font-bold text-slate-800 mb-3">学术实力</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xl font-bold text-amber-600">{quality.academic.postgrad_rate || "—"}</p>
                    <p className="text-xs text-slate-400 mt-1">保研率</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xl font-bold text-blue-600">{quality.academic.master_programs || "—"}</p>
                    <p className="text-xs text-slate-400 mt-1">硕士点</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xl font-bold text-emerald-600">{quality.academic.doctor_programs || "—"}</p>
                    <p className="text-xs text-slate-400 mt-1">博士点</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg">
                    <p className="text-xl font-bold text-violet-600">{quality.academic.academicians || "—"}</p>
                    <p className="text-xs text-slate-400 mt-1">院士</p>
                  </div>
                </div>
              </div>

              {/* Campus */}
              <div className="card">
                <h3 className="font-bold text-slate-800 mb-3">校园</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">创建年份</span>
                    <span>{quality.campus.founded || "—"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">校园面积</span>
                    <span>{quality.campus.area_mu ? `${quality.campus.area_mu}亩` : "—"}</span>
                  </div>
                  {trend && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-slate-400">分数趋势</span>
                        <span className={`font-medium ${trend.trend_direction === "上升" ? "text-red-500" : trend.trend_direction === "下降" ? "text-emerald-500" : "text-slate-600"}`}>
                          {trend.trend_direction === "上升" ? "↑" : trend.trend_direction === "下降" ? "↓" : "→"} {trend.trend_direction}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">波动性</span>
                        <span>{trend.volatility ? `${trend.volatility}分` : "—"}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Trend Tab */}
          {tab === "trend" && trend && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-800">历年分数线趋势</h3>
                <div className="flex gap-2 text-xs">
                  <span className="text-slate-400">趋势: <span className={`font-medium ${trend.trend_direction === "上升" ? "text-red-500" : trend.trend_direction === "下降" ? "text-emerald-500" : "text-slate-600"}`}>{trend.trend_direction}</span></span>
                  <span className="text-slate-400">波动: <span className="font-medium text-slate-600">{trend.volatility}分</span></span>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-slate-100">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-slate-400">年份</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">最低分</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">平均分</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">最高分</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">平均位次</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">专业数</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {trend.trend.map((t, i) => (
                      <tr key={t.year} className="hover:bg-slate-50">
                        <td className="py-2 px-3 font-medium">{t.year}</td>
                        <td className="py-2 px-3 text-right font-mono text-blue-600">{t.min_score ?? "—"}</td>
                        <td className="py-2 px-3 text-right font-mono">{t.avg_score ?? "—"}</td>
                        <td className="py-2 px-3 text-right font-mono">{t.max_score ?? "—"}</td>
                        <td className="py-2 px-3 text-right text-slate-400">{t.avg_rank?.toLocaleString() ?? "—"}</td>
                        <td className="py-2 px-3 text-right">{t.major_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Plans Tab */}
          {tab === "plans" && plans && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-800">2025年招生计划</h3>
                <div className="text-xs text-slate-400">
                  共 <span className="font-medium text-slate-600">{plans.major_count}</span> 个专业，
                  计划招生 <span className="font-medium text-blue-600">{plans.total_plan_2025}</span> 人
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-slate-100">
                      <th className="text-left py-2 px-3 text-xs font-semibold text-slate-400">专业</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">2025计划</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">2024分数</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">2023分数</th>
                      <th className="text-right py-2 px-3 text-xs font-semibold text-slate-400">涨跌</th>
                      <th className="text-left py-2 px-3 text-xs font-semibold text-slate-400">保研率</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {plans.plans.map((p, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-2 px-3 font-medium">{p.major}</td>
                        <td className="py-2 px-3 text-right font-mono text-blue-600">{p.plan_2025}</td>
                        <td className="py-2 px-3 text-right font-mono">{p.score_2024 ?? "—"}</td>
                        <td className="py-2 px-3 text-right font-mono">{p.score_2023 ?? "—"}</td>
                        <td className="py-2 px-3 text-right">
                          {p.score_change !== null ? (
                            <span className={`font-medium ${p.score_change > 0 ? "text-red-500" : p.score_change < 0 ? "text-emerald-500" : "text-slate-400"}`}>
                              {p.score_change > 0 ? "+" : ""}{p.score_change}
                            </span>
                          ) : "—"}
                        </td>
                        <td className="py-2 px-3 text-xs text-slate-500">{p.postgrad_rate || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Majors Tab */}
          {tab === "majors" && majors && (
            <div className="card">
              <h3 className="font-bold text-slate-800 mb-4">专业热度排名（按录取分）</h3>
              <div className="space-y-2">
                {majors.majors.slice(0, 20).map((m, i) => {
                  const maxScore = majors.majors[0]?.lowest_score || 700;
                  const pct = m.lowest_score ? (m.lowest_score / maxScore) * 100 : 0;
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className={`w-6 text-center text-xs font-bold ${i < 3 ? "text-amber-500" : "text-slate-400"}`}>
                        {i + 1}
                      </span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-slate-700">{m.major}</span>
                          <span className="text-xs text-slate-400">{m.lowest_score ?? "—"}分 / 位次{m.best_rank?.toLocaleString() ?? "—"}</span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${i < 3 ? "bg-gradient-to-r from-amber-400 to-amber-500" : "bg-gradient-to-r from-blue-400 to-blue-500"}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
