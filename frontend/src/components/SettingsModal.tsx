"use client";

import { useState, useEffect, useCallback } from "react";

// ═══════════════════════════════════════════════════════════════
// AI 配置部分（从原 AIConfigModal 迁移）
// ═══════════════════════════════════════════════════════════════

interface AIConfig {
  apiKey: string;
  model: string;
  baseUrl: string;
}

const MODEL_PRESETS: Record<string, { label: string; baseUrl: string; models: string[] }> = {
  deepseek: { label: "DeepSeek", baseUrl: "https://api.deepseek.com", models: ["deepseek-chat", "deepseek-reasoner"] },
  qwen: { label: "通义千问", baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1", models: ["qwen-plus", "qwen-max", "qwen-turbo"] },
  glm: { label: "智谱GLM", baseUrl: "https://open.bigmodel.cn/api/paas/v4", models: ["glm-4", "glm-4-flash"] },
  moonshot: { label: "Moonshot", baseUrl: "https://api.moonshot.cn/v1", models: ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"] },
  openai: { label: "OpenAI", baseUrl: "https://api.openai.com/v1", models: ["gpt-4o", "gpt-4o-mini"] },
};

const STORAGE_KEY = "gaokao_ai_config";

function loadConfig(): AIConfig {
  if (typeof window === "undefined") return { apiKey: "", model: "deepseek-chat", baseUrl: "https://api.deepseek.com" };
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return { apiKey: "", model: "deepseek-chat", baseUrl: "https://api.deepseek.com" };
}

function saveConfig(config: AIConfig) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export function getAIConfig(): AIConfig {
  return loadConfig();
}

// ═══════════════════════════════════════════════════════════════
// 表格行
// �══════════════════════════════════════════════════════════════

interface DBStats {
  ok: boolean;
  message?: string;
  tables?: Record<string, number>;
  latest_year?: number;
  size_mb?: number;
  db_path?: string;
}

interface SpiderInfo {
  spiders: string[];
  total: number;
  error?: string;
}

interface CrawlStatus {
  running: boolean;
  spider: string;
  log: string[];
  error: string;
}

// ═══════════════════════════════════════════════════════════════
// 主组件
// ═══════════════════════════════════════════════════════════════

const API = "http://localhost:8005/api";

export default function SettingsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [tab, setTab] = useState<"ai" | "data">("ai");

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fadeIn" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden max-h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-indigo-50 shrink-0">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-800">系统设置</h2>
            <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/80 text-slate-400 hover:text-slate-600 transition-colors">
              ✕
            </button>
          </div>
          {/* Tabs */}
          <div className="flex gap-1 mt-3 bg-slate-100 rounded-lg p-0.5">
            <button
              onClick={() => setTab("ai")}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                tab === "ai" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              🤖 AI 配置
            </button>
            <button
              onClick={() => setTab("data")}
              className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-all ${
                tab === "data" ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"
              }`}
            >
              📊 数据管理
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1">
          {tab === "ai" ? <AIPanel /> : <DataPanel />}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// AI 配置面板
// ═══════════════════════════════════════════════════════════════

function AIPanel() {
  const [config, setConfig] = useState<AIConfig>({ apiKey: "", model: "deepseek-chat", baseUrl: "https://api.deepseek.com" });
  const [provider, setProvider] = useState("deepseek");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const c = loadConfig();
    setConfig(c);
    const matched = Object.entries(MODEL_PRESETS).find(([, v]) => {
      try { return c.baseUrl.includes(new URL(v.baseUrl).hostname); } catch { return false; }
    });
    if (matched) setProvider(matched[0]);
  }, []);

  const handleProviderChange = (p: string) => {
    setProvider(p);
    const preset = MODEL_PRESETS[p];
    if (preset) setConfig(c => ({ ...c, baseUrl: preset.baseUrl, model: preset.models[0] }));
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch(`${API}/ai/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      setTestResult({ ok: data.ok, msg: data.message });
    } catch (e: any) {
      setTestResult({ ok: false, msg: `连接失败：${e.message}` });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    saveConfig(config);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY);
    setConfig({ apiKey: "", model: "deepseek-chat", baseUrl: "https://api.deepseek.com" });
    setProvider("deepseek");
    setTestResult(null);
  };

  const preset = MODEL_PRESETS[provider];

  return (
    <div className="px-6 py-5 space-y-4">
      {/* Provider */}
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">模型服务商</label>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(MODEL_PRESETS).map(([key, p]) => (
            <button
              key={key}
              onClick={() => handleProviderChange(key)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                provider === key
                  ? "bg-blue-500 text-white shadow-md"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* API Key */}
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">API Key</label>
        <input
          type="password"
          value={config.apiKey}
          onChange={e => setConfig(c => ({ ...c, apiKey: e.target.value }))}
          placeholder="sk-..."
          className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
        />
      </div>

      {/* Model */}
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">模型</label>
        <select
          value={config.model}
          onChange={e => setConfig(c => ({ ...c, model: e.target.value }))}
          className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent bg-white"
        >
          {preset?.models.map(m => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
      </div>

      {/* Base URL */}
      <div>
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
          API 地址 <span className="text-slate-400 normal-case">(一般不用改)</span>
        </label>
        <input
          type="text"
          value={config.baseUrl}
          onChange={e => setConfig(c => ({ ...c, baseUrl: e.target.value }))}
          className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
        />
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={`px-3 py-2 rounded-lg text-sm ${testResult.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
          {testResult.ok ? "✓ " : "✗ "}{testResult.msg}
        </div>
      )}

      {/* Saved */}
      {saved && (
        <div className="px-3 py-2 rounded-lg text-sm bg-blue-50 text-blue-700">✓ 配置已保存</div>
      )}

      {/* Buttons */}
      <div className="flex items-center justify-between pt-2">
        <div className="flex gap-2">
          <button
            onClick={handleTest}
            disabled={!config.apiKey || testing}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-40"
          >
            {testing ? "测试中..." : "测试连接"}
          </button>
          <button
            onClick={handleClear}
            disabled={!config.apiKey}
            className="px-4 py-2 text-sm font-medium text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-40"
          >
            清除 Key
          </button>
        </div>
        <button
          onClick={handleSave}
          disabled={!config.apiKey}
          className="px-5 py-2 text-sm font-medium bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-40"
        >
          保存配置
        </button>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// 数据管理面板
// ═══════════════════════════════════════════════════════════════

function DataPanel() {
  const [dbStats, setDbStats] = useState<DBStats | null>(null);
  const [spiders, setSpiders] = useState<SpiderInfo>({ spiders: [], total: 0 });
  const [selectedSpider, setSelectedSpider] = useState("");
  const [status, setStatus] = useState<CrawlStatus>({ running: false, spider: "", log: [], error: "" });
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  // 加载数据库统计 & 爬虫列表
  const refresh = useCallback(async () => {
    try {
      const [dbRes, spRes] = await Promise.all([
        fetch(`${API}/crawler/db-stats`),
        fetch(`${API}/crawler/spiders`),
      ]);
      setDbStats(await dbRes.json());
      setSpiders(await spRes.json());
    } catch {}
    // 刷新状态
    try {
      const stRes = await fetch(`${API}/crawler/status`);
      setStatus(await stRes.json());
    } catch {}
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // 轮询爬虫状态（如果在运行中）
  useEffect(() => {
    if (!status.running) return;
    const timer = setInterval(async () => {
      try {
        const res = await fetch(`${API}/crawler/status`);
        const s = await res.json();
        setStatus(s);
        if (!s.running) refresh(); // 完成后刷新统计
      } catch {}
    }, 2000);
    return () => clearInterval(timer);
  }, [status.running, refresh]);

  const startCrawl = async () => {
    if (!selectedSpider) return;
    setMsg(null);
    try {
      const form = new URLSearchParams();
      form.set("spider", selectedSpider);
      const res = await fetch(`${API}/crawler/run`, { method: "POST", body: form });
      const data = await res.json();
      setMsg({ ok: data.ok, text: data.message });
      refresh();
    } catch (e: any) {
      setMsg({ ok: false, text: `请求失败: ${e.message}` });
    }
  };

  return (
    <div className="px-6 py-5 space-y-5">
      {/* ── 数据库概览 ── */}
      <div>
        <h3 className="text-sm font-bold text-slate-700 mb-3">📦 数据库概览</h3>
        {dbStats ? (
          dbStats.ok ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {[
                { label: "大学", key: "universities" },
                { label: "分数线", key: "scorelines" },
                { label: "一分一段", key: "score_distribution" },
                { label: "招生计划", key: "enrollment_plans" },
              ].map(({ label, key }) => (
                <div key={key} className="bg-slate-50 rounded-lg px-3 py-2.5 text-center">
                  <div className="text-lg font-bold text-slate-800">{(dbStats.tables?.[key] ?? 0).toLocaleString()}</div>
                  <div className="text-xs text-slate-400">{label}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-red-500">{dbStats.message}</div>
          )
        ) : (
          <div className="text-sm text-slate-400">加载中...</div>
        )}
        {dbStats?.ok && (
          <div className="flex gap-4 mt-2 text-xs text-slate-400">
            <span>最新年份: {dbStats.latest_year || "—"}</span>
            <span>文件大小: {dbStats.size_mb ?? 0} MB</span>
          </div>
        )}
        <button onClick={refresh} className="mt-2 text-xs text-blue-500 hover:text-blue-600 transition-colors">
          🔄 刷新统计
        </button>
      </div>

      <hr className="border-slate-100" />

      {/* ── 启动爬虫 ── */}
      <div>
        <h3 className="text-sm font-bold text-slate-700 mb-3">🕷️ 启动爬虫</h3>

        {status.running && (
          <div className="mb-3 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-amber-700">
              <span className="animate-pulse">⏳</span>
              正在运行: <strong>{status.spider}</strong>
            </div>
            {status.log.length > 0 && (
              <div className="mt-2 max-h-32 overflow-y-auto bg-white rounded p-2 text-xs font-mono text-slate-600">
                {status.log.slice(-20).map((l, i) => (
                  <div key={i} className={l.startsWith("[ERR]") ? "text-red-500" : ""}>{l}</div>
                ))}
              </div>
            )}
            {status.error && <div className="mt-1 text-xs text-red-500">{status.error}</div>}
          </div>
        )}

        <div className="flex gap-2">
          <select
            value={selectedSpider}
            onChange={e => setSelectedSpider(e.target.value)}
            disabled={status.running}
            className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          >
            <option value="">-- 选择爬虫 --</option>
            {spiders.spiders.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <button
            onClick={startCrawl}
            disabled={!selectedSpider || status.running}
            className="px-4 py-2 text-sm font-medium bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-40 whitespace-nowrap"
          >
            ▶ 启动
          </button>
        </div>
        {spiders.error && <div className="mt-1 text-xs text-red-400">⚠ {spiders.error}</div>}
        {spiders.total === 0 && !spiders.error && (
          <div className="mt-1 text-xs text-slate-400">未发现可用爬虫</div>
        )}
      </div>

      <hr className="border-slate-100" />

      {/* ── 导入数据 ── */}
      <div>
        <h3 className="text-sm font-bold text-slate-700 mb-3">📥 导入数据</h3>
        <p className="text-xs text-slate-400 mb-2">
          导入 Excel 招生计划数据。将文件放到项目 <code className="bg-slate-100 px-1 rounded">data/</code> 目录下，输入文件名。
        </p>
        <ImportForm />
      </div>

      {/* ── 消息 ── */}
      {msg && (
        <div className={`px-3 py-2 rounded-lg text-sm ${msg.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
          {msg.ok ? "✓ " : "✗ "}{msg.text}
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// 导入表单子组件
// ═══════════════════════════════════════════════════════════════

function ImportForm() {
  const [filePath, setFilePath] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ ok: boolean; message: string; output?: string } | null>(null);

  const doImport = async () => {
    if (!filePath.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const form = new URLSearchParams();
      form.set("file_path", filePath.trim());
      const res = await fetch(`${API}/crawler/import/excel`, { method: "POST", body: form });
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setResult({ ok: false, message: `请求失败: ${e.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex gap-2">
        <input
          type="text"
          value={filePath}
          onChange={e => setFilePath(e.target.value)}
          placeholder="data/招生计划2024.xlsx"
          className="flex-1 px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={doImport}
          disabled={!filePath.trim() || loading}
          className="px-4 py-2 text-sm font-medium bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-40 whitespace-nowrap"
        >
          {loading ? "导入中..." : "导入"}
        </button>
      </div>
      {result && (
        <div className={`mt-2 px-3 py-2 rounded-lg text-xs ${result.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
          {result.message}
          {result.output && (
            <pre className="mt-1 text-xs text-slate-600 max-h-32 overflow-y-auto whitespace-pre-wrap">{result.output}</pre>
          )}
        </div>
      )}
    </div>
  );
}
