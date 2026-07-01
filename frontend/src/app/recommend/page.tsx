"use client";

import { useState } from "react";
import { fetchRecommend, RecommendResult } from "@/lib/api";
import RecommendTable from "@/components/RecommendTable";
import AIChatPanel from "@/components/AIChatPanel";

const provinces = ["北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海","宁夏","新疆","内蒙古","西藏"];
const subjects = ["物理", "历史"];

export default function RecommendPage() {
  const [score, setScore] = useState(600);
  const [province, setProvince] = useState("河北");
  const [subject, setSubject] = useState("物理");
  const [results, setResults] = useState<RecommendResult[]>([]);
  const [rank, setRank] = useState<number | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    setLoading(true); setErrors([]); setSearched(false);
    try {
      const data = await fetchRecommend(score, province, subject);
      setResults(data.results || []);
      setRank(data.rank);
      setErrors(data.errors || []);
      setSearched(true);
    } catch (e: any) {
      setErrors([`请求失败：${e.message}。请确认后端 API 已启动。`]);
    } finally { setLoading(false); }
  };

  const chong = results.filter(r => r.tier === "冲").length;
  const wen  = results.filter(r => r.tier === "稳").length;
  const bao  = results.filter(r => r.tier === "保").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🎯 志愿推荐</h1>
        <p className="text-sm text-slate-500 mt-1">输入你的分数，获取冲/稳/保三档推荐</p>
      </div>

      {/* Form Card */}
      <div className="card">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">分数</label>
            <input type="number" value={score} onChange={e => setScore(Number(e.target.value))} className="w-24 text-center font-bold text-lg" min={0} max={750} />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">省份</label>
            <select value={province} onChange={e => setProvince(e.target.value)} className="w-28">
              {provinces.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">科类</label>
            <select value={subject} onChange={e => setSubject(e.target.value)} className="w-28">
              {subjects.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            {loading ? "分析中..." : "智能推荐"}
          </button>
        </div>
        {rank && (
          <p className="mt-4 text-sm text-slate-500">
            你当前位次：<span className="text-blue-600 font-bold text-lg">{rank.toLocaleString()}</span> 名
          </p>
        )}
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="card border-red-200 bg-red-50">
          {errors.map((e, i) => <p key={i} className="text-red-600 text-sm">{e}</p>)}
          {!rank && <p className="text-xs text-red-400 mt-1">提示：部分省份使用"物理类"/"历史类"或"理科"/"文科"，系统已自动匹配。</p>}
        </div>
      )}

      {/* Main Content: Results + AI Chat */}
      <div className="flex gap-6 flex-col lg:flex-row">
        {/* Results */}
        <div className={`flex-1 ${searched ? "" : "w-full"}`}>
          {searched && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-800">
                  推荐结果（共 {results.length} 所）
                </h2>
                {results.length > 0 && (
                  <div className="flex gap-2 text-xs font-semibold">
                    <span className="tag tag-chong">冲 {chong}</span>
                    <span className="tag tag-wen">稳 {wen}</span>
                    <span className="tag tag-bao">保 {bao}</span>
                  </div>
                )}
              </div>
              <RecommendTable results={results} />
            </div>
          )}

          {!searched && (
            <div className="card text-center py-12">
              <p className="text-4xl mb-3">🎯</p>
              <p className="text-slate-400">输入分数后点击「智能推荐」，右侧 AI 顾问会帮你分析</p>
            </div>
          )}
        </div>

        {/* AI Chat Panel */}
        <div className="w-full lg:w-[380px] shrink-0">
          <div className="lg:sticky lg:top-20" style={{ height: "calc(100vh - 120px)" }}>
            <AIChatPanel context={{
              score,
              province,
              subject,
              rank: rank || undefined,
              recommendations: results.length > 0 ? results : undefined,
            }} />
          </div>
        </div>
      </div>
    </div>
  );
}
