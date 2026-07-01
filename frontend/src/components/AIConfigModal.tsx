"use client";

import { useState, useEffect } from "react";

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

export default function AIConfigModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [config, setConfig] = useState<AIConfig>({ apiKey: "", model: "deepseek-chat", baseUrl: "https://api.deepseek.com" });
  const [provider, setProvider] = useState("deepseek");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; msg: string } | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (open) {
      const c = loadConfig();
      setConfig(c);
      // detect provider from baseUrl
      const matched = Object.entries(MODEL_PRESETS).find(([, v]) => c.baseUrl.includes(new URL(v.baseUrl).hostname));
      if (matched) setProvider(matched[0]);
      setTestResult(null);
      setSaved(false);
    }
  }, [open]);

  const handleProviderChange = (p: string) => {
    setProvider(p);
    const preset = MODEL_PRESETS[p];
    if (preset) {
      setConfig(c => ({ ...c, baseUrl: preset.baseUrl, model: preset.models[0] }));
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch("http://localhost:8005/api/ai/test", {
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
    setTimeout(() => { setSaved(false); onClose(); }, 800);
  };

  if (!open) return null;

  const preset = MODEL_PRESETS[provider];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-fadeIn" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-800">AI 配置</h2>
              <p className="text-xs text-slate-400 mt-0.5">配置 AI 顾问的 API 接入</p>
            </div>
            <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/80 text-slate-400 hover:text-slate-600 transition-colors">
              ✕
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4">
          {/* Provider */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">模型服务商</label>
            <div className="grid grid-cols-5 gap-1.5">
              {Object.entries(MODEL_PRESETS).map(([key, p]) => (
                <button
                  key={key}
                  onClick={() => handleProviderChange(key)}
                  className={`px-2 py-2 rounded-lg text-xs font-medium transition-all ${
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
              className="w-full"
            />
          </div>

          {/* Model */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">模型</label>
            <select
              value={config.model}
              onChange={e => setConfig(c => ({ ...c, model: e.target.value }))}
              className="w-full"
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
              className="w-full"
            />
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`px-3 py-2 rounded-lg text-sm ${testResult.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}>
              {testResult.ok ? "✓ " : "✗ "}{testResult.msg}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <button
            onClick={handleTest}
            disabled={!config.apiKey || testing}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-40"
          >
            {testing ? "测试中..." : "测试连接"}
          </button>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 rounded-lg transition-colors">
              取消
            </button>
            <button
              onClick={handleSave}
              disabled={!config.apiKey}
              className="btn-primary text-sm px-5"
            >
              {saved ? "✓ 已保存" : "保存"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
