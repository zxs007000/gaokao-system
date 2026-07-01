"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import SettingsModal from "./SettingsModal";

const navItems = [
  { href: "/", label: "首页", icon: "🏠" },
  { href: "/recommend", label: "志愿推荐", icon: "🎯" },
  { href: "/analysis", label: "院校分析", icon: "📊" },
  { href: "/personality", label: "性格测试", icon: "🧭" },
  { href: "/trends", label: "趋势分析", icon: "📈" },
  { href: "/compare", label: "院校对比", icon: "⚖️" },
];

export default function Navbar() {
  const pathname = usePathname();
  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));
  const [showAIConfig, setShowAIConfig] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 sm:px-6 h-14">
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <span className="text-2xl">🎓</span>
            <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              高考志愿分析
            </span>
          </Link>

          <nav className="flex items-center gap-1">
            {navItems.map(item => (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive(item.href)
                    ? "bg-blue-50 text-blue-600"
                    : "text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                }`}
              >
                <span>{item.icon}</span>
                {item.label}
              </Link>
            ))}
            <button
              onClick={() => setShowAIConfig(true)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-all ml-1"
              title="AI 配置"
            >
              ⚙️
            </button>
          </nav>
        </div>
      </header>
      <SettingsModal open={showAIConfig} onClose={() => setShowAIConfig(false)} />
    </>
  );
}
