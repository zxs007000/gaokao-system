"use client";

import { useState } from "react";
import { fetchCompare, CompareData } from "@/lib/api";
import RadarCompare from "@/components/RadarCompare";
import UniversityInput from "@/components/UniversityInput";

const provinces = ["北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海","宁夏","新疆","内蒙古","西藏"];

export default function ComparePage() {
  const [input, setInput] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [province, setProvince] = useState("河北");
  const [data, setData] = useState<Record<string, CompareData>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const add = (name?: string) => {
    const n = name || input;
    if (n && !selected.includes(n) && selected.length < 4) {
      setSelected([...selected, n]);
      setInput("");
    }
  };
  const remove = (name: string) => setSelected(selected.filter(u => u !== name));

  const handleCompare = async () => {
    if (selected.length < 2) return;
    setLoading(true); setError("");
    try {
      const r = await fetchCompare(selected, province);
      setData(r.data || {});
      if (Object.keys(r.data || {}).length < 2) setError("部分大学未找到数据");
    } catch (e: any) {
      setError(`请求失败：${e.message}`);
    } finally { setLoading(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">⚖️ 院校对比</h1>
        <p className="text-sm text-slate-500 mt-1">从分数、位次、招生人数等多个维度对比几所大学</p>
      </div>

      <div className="card">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[220px]">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">大学名称</label>
            <UniversityInput
              value={input}
              onChange={setInput}
              onSelect={add}
              placeholder="搜索大学，回车或点击添加（最多4所）"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">省份</label>
            <select value={province} onChange={e => setProvince(e.target.value)} className="w-28">
              {provinces.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <button onClick={handleCompare} disabled={loading || selected.length < 2} className="btn-primary">
            {loading ? "对比中..." : "开始对比"}
          </button>
        </div>
        {selected.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {selected.map(name => (
              <span key={name} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-violet-50 text-violet-700 rounded-full text-sm font-medium animate-fadeIn">
                {name}
                <button onClick={() => remove(name)} className="text-violet-400 hover:text-red-500 transition-colors leading-none">×</button>
              </span>
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="card border-red-200 bg-red-50">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {Object.keys(data).length >= 2 && (
        <>
          <div className="card">
            <h2 className="text-lg font-bold text-slate-800 mb-4">雷达图对比</h2>
            <RadarCompare data={data} />
          </div>

          <div className="card">
            <h2 className="text-lg font-bold text-slate-800 mb-4">详细数据</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">大学</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">最新分数</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">最低位次</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">招生计划</th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">专业数量</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {Object.entries(data).map(([name, d]) => {
                    const latest = d.scores.length > 0 ? d.scores[d.scores.length - 1] : null;
                    return (
                      <tr key={name} className="hover:bg-slate-50">
                        <td className="py-3 px-4 font-semibold text-slate-800">{name}</td>
                        <td className="py-3 px-4 text-right font-mono text-blue-600 font-semibold">{latest?.min_score ?? "—"}</td>
                        <td className="py-3 px-4 text-right text-slate-500">{latest?.min_rank?.toLocaleString() ?? "—"}</td>
                        <td className="py-3 px-4 text-right text-slate-500">{d.plans.total_quota || "—"}</td>
                        <td className="py-3 px-4 text-right text-slate-500">{d.plans.major_count || "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
