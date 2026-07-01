"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8005/api";

interface TestMeta {
  name: string;
  icon: string;
  count: number;
  desc: string;
}

interface Question {
  id: string;
  test: string;
  dim: string | number;
  text: string;
}

interface Result {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
  suggestions?: string[];
}

const SCORE_LABELS = ["", "完全不符合", "比较不符合", "不确定", "比较符合", "完全符合"];

export default function PersonalityPage() {
  const [tests, setTests] = useState<Record<string, TestMeta>>({});
  const [step, setStep] = useState<"select" | "test" | "result">("select");
  const [activeTest, setActiveTest] = useState<string>("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/personality/config`).then(r => r.json()).then(data => setTests(data.tests || {}));
  }, []);

  const startTest = async (testKey: string) => {
    setActiveTest(testKey);
    try {
      const res = await fetch(`${API_BASE}/personality/questions/${testKey}`);
      const data = await res.json();
      setQuestions(data.questions || []);
    } catch {
      setQuestions([]);
    }
    setAnswers({});
    setCurrentQ(0);
    setStep("test");
  };

  const handleAnswer = (qid: string, score: number) => {
    setAnswers(prev => ({ ...prev, [qid]: score }));
    if (currentQ < questions.length - 1) {
      setCurrentQ(prev => prev + 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/personality/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          test_type: activeTest,
          answers: Object.entries(answers).map(([question_id, score]) => ({ question_id, score })),
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
      setStep("result");
    } catch (e: any) {
      setResult({ error: e.message } as any);
      setStep("result");
    } finally {
      setLoading(false);
    }
  };

  const progress = questions.length > 0 ? ((currentQ + 1) / questions.length) * 100 : 0;
  const answered = Object.keys(answers).length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🧭 性格与职业测评</h1>
        <p className="text-sm text-slate-500 mt-1">多维度了解自己，为志愿填报提供科学参考</p>
      </div>

      {/* ═══ 选择测试 ═══ */}
      {step === "select" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(tests).map(([key, t]) => (
            <button
              key={key}
              onClick={() => startTest(key)}
              className="card text-left hover:shadow-md hover:border-blue-200 transition-all group"
            >
              <div className="flex items-start gap-3">
                <span className="text-3xl">{t.icon}</span>
                <div className="flex-1">
                  <h3 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">{t.name}</h3>
                  <p className="text-xs text-slate-400 mt-1">{t.desc}</p>
                  <p className="text-xs text-blue-500 mt-2 font-medium">{t.count} 道题 · 约 {Math.ceil(t.count * 8 / 60)} 分钟</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* ═══ 答题 ═══ */}
      {step === "test" && questions.length > 0 && questions[currentQ] && (
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="card">
            <div className="flex items-center justify-between text-sm text-slate-500 mb-2">
              <span>{tests[activeTest]?.name || activeTest}</span>
              <span>{currentQ + 1} / {questions.length}　已答 {answered}</span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="card">
            <p className="text-lg font-medium text-slate-800 mb-6 leading-relaxed">{questions[currentQ].text}</p>
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map(s => (
                <button
                  key={s}
                  onClick={() => handleAnswer(questions[currentQ].id, s)}
                  className={`w-full p-3 rounded-lg border text-left transition-all ${
                    answers[questions[currentQ].id] === s
                      ? "border-blue-500 bg-blue-50 text-blue-700 font-semibold"
                      : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  {s}. {SCORE_LABELS[s]}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-between">
            <button onClick={() => setCurrentQ(p => Math.max(0, p - 1))} disabled={currentQ === 0}
              className="px-4 py-2 text-sm text-slate-500 hover:text-slate-700 disabled:opacity-30">← 上一题</button>
            {currentQ === questions.length - 1 ? (
              <button onClick={handleSubmit} disabled={loading || answered < questions.length} className="btn-primary">
                {loading ? "分析中..." : "查看结果"}
              </button>
            ) : <span />}
          </div>
        </div>
      )}

      {/* ═══ 结果 ═══ */}
      {step === "result" && result && (
        <div className="space-y-6">
          {result.error && (
            <div className="card border-red-200 bg-red-50">
              <p className="text-red-600 text-sm">分析失败：{result.error}</p>
            </div>
          )}
          {/* 九型人格 */}
          {result.enneagram && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🔮 九型人格分析</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl">
                  <p className="text-xs text-slate-400 mb-1">主要类型</p>
                  <p className="text-xl font-bold text-blue-700">{result.enneagram.primary.name}</p>
                  <p className="text-sm text-slate-600 mt-2">{result.enneagram.primary.desc}</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
                  <p className="text-xs text-slate-400 mb-1">次要类型</p>
                  <p className="text-xl font-bold text-purple-700">{result.enneagram.secondary.name}</p>
                  <p className="text-sm text-slate-600 mt-2">{result.enneagram.secondary.desc}</p>
                </div>
              </div>
              <div className="space-y-1.5">
                {Object.entries(result.enneagram.scores).map(([t, score]) => {
                  const names = ["", "完美主义", "助人", "成就", "个人主义", "观察", "忠诚", "享乐", "挑战", "和平"];
                  return (
                    <div key={t} className="flex items-center gap-2">
                      <span className="w-12 text-xs text-slate-500 text-right">{names[Number(t)]}</span>
                      <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full transition-all ${Number(t) === result.enneagram.primary.type ? "bg-blue-500" : "bg-slate-300"}`}
                          style={{ width: `${(Number(score) / 5) * 100}%` }} />
                      </div>
                      <span className="w-8 text-xs text-slate-400 text-right">{String(score)}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* MBTI */}
          {result.mbti && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🧬 MBTI 人格类型</h2>
              <div className="flex items-center gap-4 mb-4">
                <span className="text-5xl font-black text-blue-600">{result.mbti.type}</span>
                <div>
                  <p className="text-lg font-bold text-slate-700">{result.mbti.name}</p>
                  <p className="text-sm text-slate-500">{result.mbti.desc}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(result.mbti.dimensions).map(([dim, val]) => {
                  const numVal = Number(val);
                  const [a, b] = dim.split("/");
                  const pct = (numVal / 5) * 100;
                  return (
                    <div key={dim} className="p-3 bg-slate-50 rounded-lg">
                      <div className="flex justify-between text-xs text-slate-500 mb-1">
                        <span className={numVal >= 3 ? "font-bold text-blue-600" : ""}>{a}</span>
                        <span className={numVal < 3 ? "font-bold text-blue-600" : ""}>{b}</span>
                      </div>
                      <div className="h-2 bg-slate-200 rounded-full relative">
                        <div className="absolute top-0 h-full bg-blue-400 rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                      <p className="text-center text-xs text-slate-400 mt-1">{numVal.toFixed(1)}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 霍兰德 */}
          {result.holland && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🔧 霍兰德职业兴趣</h2>
              <div className="flex flex-wrap gap-2 mb-4">
                {result.holland.top3.map((t: { code: string; name: string }) => (
                  <span key={t.code} className="px-4 py-2 rounded-xl bg-blue-100 text-blue-700 font-bold text-lg">
                    {t.code}型 · {t.name}
                  </span>
                ))}
              </div>
              {result.holland.top3.map((t: { code: string; name: string; desc: string }) => (
                <p key={t.code} className="text-sm text-slate-600 mb-2"><b>{t.name}</b>：{t.desc}</p>
              ))}
              <div className="mt-3 space-y-1.5">
                {Object.entries(result.holland.scores).map(([code, score]) => (
                  <div key={code} className="flex items-center gap-2">
                    <span className="w-8 text-xs text-slate-500 text-right font-medium">{code}</span>
                    <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${(Number(score) / 5) * 100}%` }} />
                    </div>
                    <span className="w-8 text-xs text-slate-400 text-right">{String(score)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {result.holland.careers.map((c: string) => (
                  <span key={c} className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">{c}</span>
                ))}
              </div>
            </div>
          )}

          {/* DISC */}
          {result.disc && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🎯 DISC 性格画像</h2>
              <div className="flex items-center gap-4 mb-4">
                <span className="text-4xl font-black text-amber-500">{result.disc.profile}</span>
                <div>
                  <p className="text-lg font-bold text-slate-700">{result.disc.primary.name}</p>
                  <p className="text-sm text-slate-500">{result.disc.primary.desc}</p>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-3">
                {Object.entries(result.disc.scores).map(([code, score]) => (
                  <div key={code} className="text-center p-3 bg-slate-50 rounded-lg">
                    <p className="text-2xl font-bold text-amber-600">{String(score)}</p>
                    <p className="text-xs text-slate-400 mt-1">{code}型</p>
                    <p className="text-[10px] text-slate-400">{DISC_LABELS[code]}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 大五人格 */}
          {result.bigfive && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">📊 大五人格 (OCEAN)</h2>
              <div className="space-y-3">
                {Object.entries(result.bigfive.scores).map(([dim, score]) => (
                  <div key={dim} className="flex items-center gap-3">
                    <span className="w-20 text-sm font-medium text-slate-600">{result.bigfive.labels[dim]}</span>
                    <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${dim === "N" ? "bg-rose-400" : "bg-violet-400"}`}
                        style={{ width: `${(Number(score) / 5) * 100}%` }} />
                    </div>
                    <span className="w-10 text-sm text-slate-500 text-right font-mono">{String(score)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-5 gap-2">
                {Object.entries(result.bigfive.scores).map(([dim, score]) => (
                  <div key={dim} className="text-center p-2 bg-slate-50 rounded-lg">
                    <p className="text-xs font-medium text-slate-500">{result.bigfive.labels[dim]}</p>
                    <p className={`text-lg font-bold ${Number(score) >= 3.5 ? "text-emerald-600" : Number(score) <= 2.5 ? "text-rose-500" : "text-slate-600"}`}>
                      {Number(score) >= 3.5 ? "高" : Number(score) <= 2.5 ? "低" : "中"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 职业适应性 */}
          {result.career && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🧭 职业适应性</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                {Object.entries(result.career.scores).map(([dim, score]) => (
                  <div key={dim} className="text-center p-3 bg-slate-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">{String(score)}</p>
                    <p className="text-xs text-slate-400 mt-1">{result.career.labels[dim]}</p>
                  </div>
                ))}
              </div>
              <div className="p-3 bg-amber-50 rounded-lg text-center">
                <span className="text-sm text-slate-600">综合适应性：</span>
                <span className="text-xl font-bold text-amber-600 ml-2">{result.career.overall}</span>
                <span className="text-sm text-slate-400"> / 5.0</span>
              </div>
            </div>
          )}

          {/* 专业推荐 */}
          {result.suggestions && result.suggestions.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-bold text-slate-800 mb-4">🎓 综合推荐专业</h2>
              <div className="flex flex-wrap gap-2">
                {result.suggestions.map((m: string, i: number) => (
                  <span key={i} className={`px-4 py-2 rounded-full text-sm font-medium ${i < 3 ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-600"}`}>{m}</span>
                ))}
              </div>
              <p className="text-xs text-slate-400 mt-3">* 基于全部测评维度综合分析</p>
            </div>
          )}

          <div className="text-center">
            <button onClick={() => { setStep("select"); setResult(null); setQuestions([]); }}
              className="px-6 py-2 text-sm text-slate-500 hover:text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50">
              返回选择其他测试
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const DISC_LABELS: Record<string, string> = { D: "支配", I: "影响", S: "稳健", C: "谨慎" };
