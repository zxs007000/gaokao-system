"use client";

import { useState, useRef, useEffect } from "react";
import { getAIConfig } from "./SettingsModal";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatContext {
  score?: number;
  province?: string;
  subject?: string;
  rank?: number;
  recommendations?: any[];
}

export default function AIChatPanel({ context }: { context?: ChatContext }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "你好！我是高考志愿顾问 AI 🎓\n\n可以帮你分析志愿方案、解读录取数据、提供填报建议。有什么想问的？" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const config = getAIConfig();
    if (!config.apiKey) {
      setError("请先在右上角 ⚙️ 配置 AI API Key");
      return;
    }

    const userMsg = input.trim();
    setInput("");
    setError("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const allMessages = [...messages, { role: "user" as const, content: userMsg }]
        .filter(m => !m.content.startsWith("你好！我是高考志愿顾问"));

      const res = await fetch("http://localhost:8005/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: allMessages,
          apiKey: config.apiKey,
          model: config.model,
          baseUrl: config.baseUrl,
          context: context || {},
        }),
      });

      const data = await res.json();
      if (data.ok) {
        setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
      } else {
        setError(data.error || "请求失败");
      }
    } catch (e: any) {
      setError(`连接失败：${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center gap-2">
          <span className="text-lg">🤖</span>
          <div>
            <h3 className="text-sm font-bold text-slate-800">AI 顾问</h3>
            <p className="text-[10px] text-slate-400">基于大模型的志愿咨询</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] px-3 py-2.5 rounded-2xl text-sm leading-relaxed ${
              msg.role === "user"
                ? "bg-blue-500 text-white rounded-br-md"
                : "bg-slate-100 text-slate-700 rounded-bl-md"
            }`}>
              <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 px-4 py-3 rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-100 text-xs text-red-600">
          {error}
        </div>
      )}

      {/* Input */}
      <div className="p-3 border-t border-slate-100">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="输入你的问题..."
            className="flex-1 text-sm"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="btn-primary px-4 text-sm"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
