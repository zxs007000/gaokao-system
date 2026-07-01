"use client";

import { useState } from "react";
import { fetchMultiTrends, TrendData } from "@/lib/api";
import ScoreTrendChart from "@/components/ScoreTrendChart";
import UniversityInput from "@/components/UniversityInput";

const provinces = ["北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江","江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南","广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海","宁夏","新疆","内蒙古","西藏"];

export default function TrendsPage() {
  const [input, setInput] = useState("");
  const [universities, setUniversities] = useState<string[]>([]);
  const [province, setProvince] = useState("河北");
  const [data, setData] = useState<Record<string, TrendData[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const add = (name?: string) => {
    const n = name || input;
    if (n && !universities.includes(n) && universities.length < 5) {
      setUniversities([...universities, n]);
      setInput("");
    }
  };
  const remove = (name: string) => setUniversities(universities.filter(u => u !== name));

  const handleSearch = async () => {
    const names = universities.length > 0 ? universities : (input ? [input] : []);
    if (!names[0]) return;
    setLoading(true); setError("");
    try {
      const r = await fetchMultiTrends(names, province);
      setData(r.data || {});
      if (Object.keys(r.data || {}).length === 0) setError("未找到数据，请确认大学名称和省份正确");
    } catch (e: any) {
      setError(`请求失败：${e.message}`);
    } finally { setLoading(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">📈 分数线趋势</h1>
        <p className="text-sm text-slate-500 mt-1">查看多所大学历年录取分数线的变化规律</p>
      </div>

      <div className="card">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[220px]">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">大学名称</label>
            <UniversityInput
              value={input}
              onChange={setInput}
              onSelect={add}
              placeholder="搜索大学，回车或点击添加（最多5所）"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">省份</label>
            <select value={province} onChange={e => setProvince(e.target.value)} className="w-28">
              {provinces.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <button onClick={handleSearch} disabled={loading || (universities.length === 0 && !input.trim())} className="btn-primary">
            {loading ? "查询中..." : "查询趋势"}
          </button>
        </div>
        {universities.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {universities.map(name => (
              <span key={name} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium animate-fadeIn">
                {name}
                <button onClick={() => remove(name)} className="text-blue-400 hover:text-red-500 transition-colors leading-none">×</button>
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

      {Object.keys(data).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-slate-800 mb-4">分数线变化趋势</h2>
          <ScoreTrendChart data={data} />
        </div>
      )}
    </div>
  );
}
