"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "首页", icon: "🏠" },
  { href: "/recommend", label: "志愿推荐", icon: "🎯" },
  { href: "/trends", label: "趋势分析", icon: "📈" },
  { href: "/compare", label: "院校对比", icon: "⚖️" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <aside className="fixed left-0 top-0 w-64 h-full bg-dark-800 border-r border-white/5 flex flex-col z-40">
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <Link href="/" className="flex items-center gap-3">
          <span className="text-2xl">🎓</span>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-neon-green to-neon-blue bg-clip-text text-transparent">
              高考志愿分析
            </h1>
            <p className="text-xs text-gray-500">数据驱动 · 智能推荐</p>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(item => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${
              isActive(item.href)
                ? "bg-neon-green/10 text-neon-green font-medium"
                : "text-gray-400 hover:bg-white/5 hover:text-white"
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/5">
        <div className="text-xs text-gray-500 space-y-1">
          <p>数据来源：阳光高考 · 各省考试院</p>
          <p>覆盖 2020–2025 年投档数据</p>
        </div>
      </div>
    </aside>
  );
}
