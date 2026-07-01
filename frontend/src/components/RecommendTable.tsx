"use client";

import { RecommendResult } from "@/lib/api";

const tierConfig: Record<string, { label: string; className: string }> = {
  "冲": { label: "冲", className: "tag tag-chong" },
  "稳": { label: "稳", className: "tag tag-wen" },
  "保": { label: "保", className: "tag tag-bao" },
};

const probColor = (p: number) => {
  if (p >= 70) return "text-emerald-600";
  if (p >= 40) return "text-amber-600";
  return "text-red-500";
};

const stabilityColor = (s?: string) => {
  if (s === "稳定") return "text-emerald-500";
  if (s === "波动") return "text-amber-500";
  if (s === "大波动") return "text-red-400";
  return "text-slate-400";
};

export default function RecommendTable({ results }: { results: RecommendResult[] }) {
  if (!results.length) return <p className="text-slate-400 text-center py-8">暂无推荐结果</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b-2 border-slate-100">
            <th className="text-left py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide w-12">档次</th>
            <th className="text-left py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">大学</th>
            <th className="text-left py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide hidden sm:table-cell">省份</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide">最新分数</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide hidden md:table-cell">加权位次</th>
            <th className="text-center py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide hidden lg:table-cell">稳定性</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wide w-16">概率</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50">
          {results.map((r, i) => {
            const tier = tierConfig[r.tier] || { label: r.tier, className: "" };
            return (
              <tr key={i} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 px-3">
                  <span className={tier.className}>{tier.label}</span>
                </td>
                <td className="py-3 px-3">
                  <span className="font-semibold text-slate-800">{r.name}</span>
                  {r.tags && r.tags.length > 0 && (
                    <span className="ml-1.5">
                      {r.tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-block text-[10px] font-bold px-1 py-0.5 rounded bg-blue-50 text-blue-600 mr-1"
                        >
                          {tag}
                        </span>
                      ))}
                    </span>
                  )}
                </td>
                <td className="py-3 px-3 text-slate-400 hidden sm:table-cell">{r.province}</td>
                <td className="py-3 px-3 text-right font-mono font-semibold text-blue-600">{r.latest_score ?? "-"}</td>
                <td className="py-3 px-3 text-right text-slate-400 hidden md:table-cell">{r.avg_rank.toLocaleString()}</td>
                <td className="py-3 px-3 text-center hidden lg:table-cell">
                  <span className={`text-xs font-medium ${stabilityColor(r.rank_stability)}`}>
                    {r.rank_stability || "-"}
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <span className={`font-bold ${probColor(r.probability)}`}>
                    {r.probability}%
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
