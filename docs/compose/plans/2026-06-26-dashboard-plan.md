# 高考数据分析 Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建高考数据分析 Dashboard，包含志愿推荐、分数线趋势分析、院校对比三个核心功能

**Architecture:** FastAPI 后端提供 3 个 REST API 接口，复用现有 SQLite 数据库。Next.js 前端使用 ECharts 实现可视化，深色主题金融风格。

**Tech Stack:** Python 3.11, FastAPI, SQLite, React, Next.js, Tailwind CSS, ECharts

---

## File Structure

```
D:\gaokao-system\
├── api/
│   ├── main.py                     # FastAPI 入口 + CORS
│   ├── database.py                 # 数据库连接（复用 crawler/database.py）
│   └── routes/
│       ├── __init__.py
│       ├── recommend.py            # 志愿推荐 API
│       ├── trends.py               # 趋势查询 API
│       └── compare.py              # 对比查询 API
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # 全局布局 + 侧边栏
│   │   │   ├── page.tsx            # 首页 Dashboard
│   │   │   ├── globals.css         # 全局样式（深色主题）
│   │   │   ├── recommend/
│   │   │   │   └── page.tsx        # 志愿推荐页
│   │   │   ├── trends/
│   │   │   │   └── page.tsx        # 分数线趋势页
│   │   │   └── compare/
│   │   │       └── page.tsx        # 院校对比页
│   │   ├── components/
│   │   │   ├── Sidebar.tsx         # 左侧导航
│   │   │   ├── ScoreTrendChart.tsx # ECharts 趋势折线图
│   │   │   ├── RadarCompare.tsx    # ECharts 雷达对比图
│   │   │   ├── RecommendTable.tsx  # 推荐结果表格
│   │   │   └── StatCard.tsx        # 数据概览卡片
│   │   └── lib/
│   │       └── api.ts              # API 调用封装
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.js
```

---

### Task 1: FastAPI 后端初始化

**Covers:** [S3, S10]

**Files:**
- Create: `D:\gaokao-system\api\__init__.py`
- Create: `D:\gaokao-system\api\main.py`
- Create: `D:\gaokao-system\api\database.py`
- Create: `D:\gaokao-system\api\routes\__init__.py`
- Create: `D:\gaokao-system\requirements-api.txt`

- [ ] **Step 1: Create requirements-api.txt**

```
fastapi>=0.104.0
uvicorn>=0.24.0
```

- [ ] **Step 2: Create api/database.py**

```python
"""数据库连接 —— 复用现有 gaokao.db"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "db" / "gaokao.db"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

- [ ] **Step 3: Create api/main.py**

```python
"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import recommend, trends, compare

app = FastAPI(title="高考数据分析 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(compare.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Create api/routes/__init__.py (empty)**

- [ ] **Step 5: Create placeholder route files**

```python
# api/routes/recommend.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/recommend")
def recommend(score: int, province: str, subject: str, db: sqlite3.Connection = Depends(get_db)):
    """志愿推荐接口"""
    # TODO: Task 2 实现
    return {"score": score, "province": province, "subject": subject, "results": []}
```

```python
# api/routes/trends.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/trends")
def trends(university: str, province: str, db: sqlite3.Connection = Depends(get_db)):
    """分数线趋势接口"""
    # TODO: Task 3 实现
    return {"university": university, "province": province, "data": []}
```

```python
# api/routes/compare.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/compare")
def compare(universities: str, province: str, db: sqlite3.Connection = Depends(get_db)):
    """院校对比接口"""
    # TODO: Task 4 实现
    return {"universities": universities.split(","), "province": province, "data": {}}
```

- [ ] **Step 6: Install dependencies and test**

```bash
cd D:\gaokao-system
pip install -r requirements-api.txt
python -m uvicorn api.main:app --reload --port 8000
```

Visit `http://localhost:8000/api/health` — should return `{"status": "ok"}`

- [ ] **Step 7: Commit**

```bash
git add api/ requirements-api.txt
git commit -m "feat: add FastAPI backend skeleton with health endpoint"
```

---

### Task 2: 志愿推荐 API

**Covers:** [S4]

**Files:**
- Modify: `D:\gaokao-system\api\routes\recommend.py`

- [ ] **Step 1: Implement recommend endpoint**

```python
# api/routes/recommend.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/recommend")
def recommend(
    score: int,
    province: str,
    subject: str = "物理",
    db: sqlite3.Connection = Depends(get_db),
):
    """志愿推荐：输入分数+省份+科类，返回冲/稳/保推荐"""

    # 1. 查询位次
    rank_row = db.execute(
        """
        SELECT cumulative_rank FROM score_distribution
        WHERE province = ? AND subject = ? AND score <= ?
        ORDER BY score DESC LIMIT 1
        """,
        (province, subject, score),
    ).fetchone()

    if not rank_row:
        return {"score": score, "province": province, "rank": None, "results": []}

    rank = rank_row["cumulative_rank"]

    # 2. 查询匹配的大学（历年录取位次接近的）
    # 使用最近一年的数据为主
    rows = db.execute(
        """
        SELECT
            s.university_name,
            u.province as uni_province,
            u.type as uni_type,
            u.level as uni_level,
            s.year,
            s.min_score,
            s.min_rank,
            s.batch
        FROM scorelines s
        LEFT JOIN universities u ON s.university_name = u.name
        WHERE s.province = ?
          AND s.year >= 2022
          AND s.min_score IS NOT NULL
          AND s.min_rank IS NOT NULL
          AND s.min_rank BETWEEN ? AND ?
        ORDER BY s.year DESC, s.min_rank ASC
        """,
        (province, int(rank * 0.7), int(rank * 1.3)),
    ).fetchall()

    # 3. 按大学聚合，计算推荐分层
    uni_data = {}
    for row in rows:
        name = row["university_name"]
        if name not in uni_data:
            uni_data[name] = {
                "name": name,
                "province": row["uni_province"] or "",
                "type": row["uni_type"] or "",
                "level": row["uni_level"] or "",
                "scores": [],
                "ranks": [],
            }
        uni_data[name]["scores"].append(row["min_score"])
        uni_data[name]["ranks"].append(row["min_rank"])

    # 4. 分层：冲/稳/保
    results = []
    for name, data in uni_data.items():
        avg_rank = sum(data["ranks"]) / len(data["ranks"]) if data["ranks"] else 0
        latest_score = data["scores"][0] if data["scores"] else 0

        if avg_rank < rank * 0.9:
            tier = "冲"
            probability = max(10, min(40, int((rank / avg_rank) * 30)))
        elif avg_rank <= rank * 1.1:
            tier = "稳"
            probability = max(40, min(80, int((rank / avg_rank) * 60)))
        else:
            tier = "保"
            probability = max(70, min(95, int((rank / avg_rank) * 80)))

        results.append({
            "name": name,
            "province": data["province"],
            "type": data["type"],
            "level": data["level"],
            "latest_score": latest_score,
            "avg_rank": int(avg_rank),
            "tier": tier,
            "probability": probability,
            "score_trend": data["scores"][:4],
        })

    # 按 tier 排序：保 → 稳 → 冲
    tier_order = {"保": 0, "稳": 1, "冲": 2}
    results.sort(key=lambda x: (tier_order.get(x["tier"], 3), -x["probability"]))

    return {
        "score": score,
        "province": province,
        "subject": subject,
        "rank": rank,
        "results": results,
    }
```

- [ ] **Step 2: Test the API**

```bash
curl "http://localhost:8000/api/recommend?score=600&province=河北&subject=物理"
```

- [ ] **Step 3: Commit**

```bash
git add api/routes/recommend.py
git commit -m "feat: add recommend API with tier classification"
```

---

### Task 3: 分数线趋势 API

**Covers:** [S5]

**Files:**
- Modify: `D:\gaokao-system\api\routes\trends.py`

- [ ] **Step 1: Implement trends endpoint**

```python
# api/routes/trends.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/trends")
def get_trends(
    university: str,
    province: str,
    db: sqlite3.Connection = Depends(get_db),
):
    """分数线趋势：返回某校某省历年分数线"""
    rows = db.execute(
        """
        SELECT
            year,
            MIN(min_score) as min_score,
            AVG(CASE WHEN avg_score IS NOT NULL THEN avg_score END) as avg_score,
            MAX(max_score) as max_score,
            MIN(min_rank) as min_rank,
            COUNT(*) as record_count
        FROM scorelines
        WHERE university_name = ? AND province = ?
          AND min_score IS NOT NULL
        GROUP BY year
        ORDER BY year
        """,
        (university, province),
    ).fetchall()

    data = []
    for row in rows:
        data.append({
            "year": row["year"],
            "min_score": row["min_score"],
            "avg_score": round(row["avg_score"]) if row["avg_score"] else None,
            "max_score": row["max_score"],
            "min_rank": row["min_rank"],
        })

    return {
        "university": university,
        "province": province,
        "data": data,
    }


@router.get("/trends/multi")
def get_multi_trends(
    universities: str,
    province: str,
    db: sqlite3.Connection = Depends(get_db),
):
    """多校趋势对比"""
    names = [n.strip() for n in universities.split(",") if n.strip()]
    result = {}
    for name in names[:5]:
        rows = db.execute(
            """
            SELECT year, MIN(min_score) as min_score
            FROM scorelines
            WHERE university_name = ? AND province = ? AND min_score IS NOT NULL
            GROUP BY year ORDER BY year
            """,
            (name, province),
        ).fetchall()
        result[name] = [{"year": r["year"], "min_score": r["min_score"]} for r in rows]

    return {"province": province, "data": result}
```

- [ ] **Step 2: Test**

```bash
curl "http://localhost:8000/api/trends?university=清华大学&province=河北"
curl "http://localhost:8000/api/trends/multi?universities=清华大学,北京大学&province=河北"
```

- [ ] **Step 3: Commit**

```bash
git add api/routes/trends.py
git commit -m "feat: add trends API with single and multi-university support"
```

---

### Task 4: 院校对比 API

**Covers:** [S6]

**Files:**
- Modify: `D:\gaokao-system\api\routes\compare.py`

- [ ] **Step 1: Implement compare endpoint**

```python
# api/routes/compare.py
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/compare")
def compare_universities(
    universities: str,
    province: str,
    db: sqlite3.Connection = Depends(get_db),
):
    """院校对比：多维度对比 2-4 所大学"""
    names = [n.strip() for n in universities.split(",") if n.strip()][:4]

    result = {}
    for name in names:
        # 大学基本信息
        uni = db.execute(
            "SELECT * FROM universities WHERE name = ?", (name,)
        ).fetchone()

        # 历年分数线
        scores = db.execute(
            """
            SELECT year, MIN(min_score) as min_score,
                   AVG(CASE WHEN avg_score IS NOT NULL THEN avg_score END) as avg_score,
                   MIN(min_rank) as min_rank
            FROM scorelines
            WHERE university_name = ? AND province = ? AND min_score IS NOT NULL
            GROUP BY year ORDER BY year
            """,
            (name, province),
        ).fetchall()

        # 2025 招生计划
        plans = db.execute(
            """
            SELECT COUNT(*) as major_count, SUM(plan_2025) as total_quota
            FROM enrollment_plans_detail
            WHERE university_name = ? AND province = ?
            """,
            (name, province),
        ).fetchone()

        result[name] = {
            "info": {
                "name": uni["name"] if uni else name,
                "province": uni["province"] if uni else "",
                "type": uni["type"] if uni else "",
                "level": uni["level"] if uni else "",
            } if uni else {"name": name},
            "scores": [
                {
                    "year": r["year"],
                    "min_score": r["min_score"],
                    "avg_score": round(r["avg_score"]) if r["avg_score"] else None,
                    "min_rank": r["min_rank"],
                }
                for r in scores
            ],
            "plans": {
                "major_count": plans["major_count"] if plans else 0,
                "total_quota": plans["total_quota"] if plans else 0,
            },
        }

    return {"province": province, "data": result}
```

- [ ] **Step 2: Test**

```bash
curl "http://localhost:8000/api/compare?universities=清华大学,北京大学&province=河北"
```

- [ ] **Step 3: Commit**

```bash
git add api/routes/compare.py
git commit -m "feat: add compare API with multi-dimensional university comparison"
```

---

### Task 5: Next.js 项目初始化

**Covers:** [S7, S8]

**Files:**
- Create: `D:\gaokao-system\frontend\` (Next.js project)

- [ ] **Step 1: Create Next.js project**

```bash
cd D:\gaokao-system
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
```

- [ ] **Step 2: Install ECharts**

```bash
cd D:\gaokao-system\frontend
npm install echarts echarts-for-react
```

- [ ] **Step 3: Configure dark theme in tailwind.config.ts**

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          green: "#00d4aa",
          red: "#ff6b6b",
          yellow: "#ffd93d",
          blue: "#4ecdc4",
        },
        dark: {
          900: "#0a0a0a",
          800: "#1a1a2e",
          700: "#16213e",
          600: "#1f2b47",
        },
      },
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 4: Create globals.css with dark theme**

```css
/* src/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a2e;
  --bg-card: #16213e;
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0a0;
  --neon-green: #00d4aa;
  --neon-red: #ff6b6b;
  --neon-yellow: #ffd93d;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* 卡片样式 */
.card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

/* 霓虹发光效果 */
.neon-glow {
  box-shadow: 0 0 10px rgba(0, 212, 170, 0.3);
}

/* 输入框样式 */
input, select {
  background: var(--bg-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  outline: none;
}

input:focus, select:focus {
  border-color: var(--neon-green);
  box-shadow: 0 0 5px rgba(0, 212, 170, 0.3);
}

/* 按钮样式 */
.btn-primary {
  background: var(--neon-green);
  color: #0a0a0a;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  box-shadow: 0 0 15px rgba(0, 212, 170, 0.5);
}
```

- [ ] **Step 5: Create API utility**

```typescript
// src/lib/api.ts
const API_BASE = "http://localhost:8000/api";

export interface RecommendResult {
  name: string;
  province: string;
  type: string;
  level: string;
  latest_score: number;
  avg_rank: number;
  tier: "冲" | "稳" | "保";
  probability: number;
  score_trend: number[];
}

export interface TrendData {
  year: number;
  min_score: number | null;
  avg_score: number | null;
  max_score: number | null;
  min_rank: number | null;
}

export interface CompareData {
  info: { name: string; province: string; type: string; level: string };
  scores: TrendData[];
  plans: { major_count: number; total_quota: number };
}

export async function fetchRecommend(
  score: number,
  province: string,
  subject: string
): Promise<{ rank: number; results: RecommendResult[] }> {
  const res = await fetch(
    `${API_BASE}/recommend?score=${score}&province=${encodeURIComponent(province)}&subject=${encodeURIComponent(subject)}`
  );
  return res.json();
}

export async function fetchTrends(
  university: string,
  province: string
): Promise<{ data: TrendData[] }> {
  const res = await fetch(
    `${API_BASE}/trends?university=${encodeURIComponent(university)}&province=${encodeURIComponent(province)}`
  );
  return res.json();
}

export async function fetchMultiTrends(
  universities: string[],
  province: string
): Promise<{ data: Record<string, TrendData[]> }> {
  const res = await fetch(
    `${API_BASE}/trends/multi?universities=${encodeURIComponent(universities.join(","))}&province=${encodeURIComponent(province)}`
  );
  return res.json();
}

export async function fetchCompare(
  universities: string[],
  province: string
): Promise<{ data: Record<string, CompareData> }> {
  const res = await fetch(
    `${API_BASE}/compare?universities=${encodeURIComponent(universities.join(","))}&province=${encodeURIComponent(province)}`
  );
  return res.json();
}
```

- [ ] **Step 6: Create Sidebar component**

```tsx
// src/components/Sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "首页", icon: "📊" },
  { href: "/recommend", label: "志愿推荐", icon: "🎯" },
  { href: "/trends", label: "分数线趋势", icon: "📈" },
  { href: "/compare", label: "院校对比", icon: "⚖️" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen bg-dark-800 border-r border-white/5 p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-neon-green">高考数据分析</h1>
        <p className="text-sm text-gray-500 mt-1">Gaokao Analytics</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              pathname === item.href
                ? "bg-dark-600 text-neon-green neon-glow"
                : "text-gray-400 hover:bg-dark-700 hover:text-white"
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 7: Update layout.tsx**

```tsx
// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "高考数据分析 Dashboard",
  description: "高考志愿填报数据分析工具",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
```

- [ ] **Step 8: Test frontend runs**

```bash
cd D:\gaokao-system\frontend
npm run dev
```

Visit `http://localhost:3000` — should show dark theme with sidebar

- [ ] **Step 9: Commit**

```bash
cd D:\gaokao-system
git add frontend/
git commit -m "feat: initialize Next.js frontend with dark theme and sidebar"
```

---

### Task 6: 首页 Dashboard

**Covers:** [S7]

**Files:**
- Create: `D:\gaokao-system\frontend\src\components\StatCard.tsx`
- Modify: `D:\gaokao-system\frontend\src\app\page.tsx`

- [ ] **Step 1: Create StatCard component**

```tsx
// src/components/StatCard.tsx
interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color?: string;
}

export default function StatCard({ title, value, icon, color = "text-neon-green" }: StatCardProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Implement Dashboard page**

```tsx
// src/app/page.tsx
"use client";

import StatCard from "@/components/StatCard";

export default function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">数据概览</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="大学数量" value="2,000" icon="🏫" />
        <StatCard title="分数线记录" value="1,139,271" icon="📊" color="text-neon-blue" />
        <StatCard title="招生计划" value="13,314" icon="📋" color="text-neon-yellow" />
        <StatCard title="一分一段" value="31,775" icon="📈" color="text-neon-red" />
      </div>

      <div className="mt-8 card">
        <h2 className="text-lg font-semibold mb-4">快速开始</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a href="/recommend" className="p-4 rounded-lg bg-dark-700 hover:bg-dark-600 transition-all">
            <span className="text-2xl">🎯</span>
            <h3 className="font-medium mt-2">志愿推荐</h3>
            <p className="text-sm text-gray-400 mt-1">输入分数，智能推荐院校</p>
          </a>
          <a href="/trends" className="p-4 rounded-lg bg-dark-700 hover:bg-dark-600 transition-all">
            <span className="text-2xl">📈</span>
            <h3 className="font-medium mt-2">分数线趋势</h3>
            <p className="text-sm text-gray-400 mt-1">查看历年分数线变化</p>
          </a>
          <a href="/compare" className="p-4 rounded-lg bg-dark-700 hover:bg-dark-600 transition-all">
            <span className="text-2xl">⚖️</span>
            <h3 className="font-medium mt-2">院校对比</h3>
            <p className="text-sm text-gray-400 mt-1">多维度对比大学</p>
          </a>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Test**

```bash
cd D:\gaokao-system\frontend
npm run dev
```

Visit `http://localhost:3000` — should show dashboard with stat cards

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add dashboard page with stat cards"
```

---

### Task 7: 志愿推荐页

**Covers:** [S4, S7]

**Files:**
- Create: `D:\gaokao-system\frontend\src\components\RecommendTable.tsx`
- Create: `D:\gaokao-system\frontend\src\app\recommend\page.tsx`

- [ ] **Step 1: Create RecommendTable component**

```tsx
// src/components/RecommendTable.tsx
"use client";

import { RecommendResult } from "@/lib/api";

interface Props {
  results: RecommendResult[];
}

const tierColors: Record<string, string> = {
  "冲": "bg-neon-red/20 text-neon-red",
  "稳": "bg-neon-yellow/20 text-neon-yellow",
  "保": "bg-neon-green/20 text-neon-green",
};

export default function RecommendTable({ results }: Props) {
  if (!results.length) return <p className="text-gray-400">暂无推荐结果</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left py-3 px-4">推荐</th>
            <th className="text-left py-3 px-4">大学</th>
            <th className="text-left py-3 px-4">省份</th>
            <th className="text-left py-3 px-4">类型</th>
            <th className="text-left py-3 px-4">层次</th>
            <th className="text-right py-3 px-4">最新分数</th>
            <th className="text-right py-3 px-4">平均位次</th>
            <th className="text-right py-3 px-4">概率</th>
            <th className="text-left py-3 px-4">分数趋势</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, i) => (
            <tr key={i} className="border-b border-white/5 hover:bg-dark-700">
              <td className="py-3 px-4">
                <span className={`px-2 py-1 rounded text-xs font-medium ${tierColors[r.tier] || ""}`}>
                  {r.tier}
                </span>
              </td>
              <td className="py-3 px-4 font-medium">{r.name}</td>
              <td className="py-3 px-4 text-gray-400">{r.province}</td>
              <td className="py-3 px-4 text-gray-400">{r.type}</td>
              <td className="py-3 px-4 text-gray-400">{r.level}</td>
              <td className="py-3 px-4 text-right text-neon-green">{r.latest_score}</td>
              <td className="py-3 px-4 text-right text-gray-400">{r.avg_rank.toLocaleString()}</td>
              <td className="py-3 px-4 text-right">
                <span className={`font-medium ${r.probability >= 70 ? "text-neon-green" : r.probability >= 40 ? "text-neon-yellow" : "text-neon-red"}`}>
                  {r.probability}%
                </span>
              </td>
              <td className="py-3 px-4 text-gray-400 text-xs">
                {r.score_trend.join(" → ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 2: Create recommend page**

```tsx
// src/app/recommend/page.tsx
"use client";

import { useState } from "react";
import { fetchRecommend, RecommendResult } from "@/lib/api";
import RecommendTable from "@/components/RecommendTable";

const provinces = [
  "北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江",
  "江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南",
  "广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海",
  "宁夏","新疆","内蒙古","西藏",
];

const subjects = ["物理", "历史", "理科", "文科"];

export default function RecommendPage() {
  const [score, setScore] = useState(600);
  const [province, setProvince] = useState("河北");
  const [subject, setSubject] = useState("物理");
  const [results, setResults] = useState<RecommendResult[]>([]);
  const [rank, setRank] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await fetchRecommend(score, province, subject);
      setResults(data.results || []);
      setRank(data.rank);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">志愿推荐</h1>

      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm text-gray-400 mb-1">分数</label>
            <input
              type="number"
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
              className="w-32"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">省份</label>
            <select value={province} onChange={(e) => setProvince(e.target.value)}>
              {provinces.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">科类</label>
            <select value={subject} onChange={(e) => setSubject(e.target.value)}>
              {subjects.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            {loading ? "查询中..." : "智能推荐"}
          </button>
        </div>
        {rank && (
          <p className="mt-4 text-sm text-gray-400">
            你的位次约 <span className="text-neon-green font-medium">{rank.toLocaleString()}</span> 名
          </p>
        )}
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">推荐结果（共 {results.length} 所）</h2>
        <RecommendTable results={results} />
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Test**

```bash
cd D:\gaokao-system\frontend
npm run dev
```

Visit `http://localhost:3000/recommend` — input score and search

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add recommend page with search form and result table"
```

---

### Task 8: 分数线趋势页

**Covers:** [S5, S7]

**Files:**
- Create: `D:\gaokao-system\frontend\src\components\ScoreTrendChart.tsx`
- Create: `D:\gaokao-system\frontend\src\app\trends\page.tsx`

- [ ] **Step 1: Create ScoreTrendChart component**

```tsx
// src/components/ScoreTrendChart.tsx
"use client";

import ReactECharts from "echarts-for-react";
import { TrendData } from "@/lib/api";

interface Props {
  data: Record<string, TrendData[]>;
}

export default function ScoreTrendChart({ data }: Props) {
  const years = [...new Set(Object.values(data).flat().map((d) => d.year))].sort();

  const series = Object.entries(data).map(([name, points]) => ({
    name,
    type: "line" as const,
    data: years.map((y) => {
      const p = points.find((d) => d.year === y);
      return p?.min_score ?? null;
    }),
    smooth: true,
    symbol: "circle",
    symbolSize: 6,
  }));

  const option = {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis" as const },
    legend: {
      data: Object.keys(data),
      textStyle: { color: "#a0a0a0" },
    },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: {
      type: "category" as const,
      data: years.map(String),
      axisLabel: { color: "#a0a0a0" },
      axisLine: { lineStyle: { color: "#333" } },
    },
    yAxis: {
      type: "value" as const,
      axisLabel: { color: "#a0a0a0" },
      splitLine: { lineStyle: { color: "#222" } },
    },
    series,
    color: ["#00d4aa", "#ff6b6b", "#ffd93d", "#4ecdc4", "#9b59b6"],
  };

  return <ReactECharts option={option} style={{ height: 400 }} />;
}
```

- [ ] **Step 2: Create trends page**

```tsx
// src/app/trends/page.tsx
"use client";

import { useState } from "react";
import { fetchMultiTrends, TrendData } from "@/lib/api";
import ScoreTrendChart from "@/components/ScoreTrendChart";

const provinces = [
  "北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江",
  "江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南",
  "广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海",
  "宁夏","新疆","内蒙古","西藏",
];

export default function TrendsPage() {
  const [universityInput, setUniversityInput] = useState("清华大学");
  const [universities, setUniversities] = useState<string[]>([]);
  const [province, setProvince] = useState("河北");
  const [data, setData] = useState<Record<string, TrendData[]>>({});
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    const names = universities.length > 0 ? universities : [universityInput];
    if (!names[0]) return;

    setLoading(true);
    try {
      const result = await fetchMultiTrends(names, province);
      setData(result.data || {});
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addUniversity = () => {
    if (universityInput && !universities.includes(universityInput) && universities.length < 5) {
      setUniversities([...universities, universityInput]);
      setUniversityInput("");
    }
  };

  const removeUniversity = (name: string) => {
    setUniversities(universities.filter((u) => u !== name));
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">分数线趋势</h1>

      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm text-gray-400 mb-1">大学名称</label>
            <input
              value={universityInput}
              onChange={(e) => setUniversityInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addUniversity()}
              placeholder="输入大学名称回车添加"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">省份</label>
            <select value={province} onChange={(e) => setProvince(e.target.value)}>
              {provinces.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <button onClick={handleSearch} disabled={loading} className="btn-primary">
            {loading ? "查询中..." : "查询趋势"}
          </button>
        </div>
        {universities.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {universities.map((name) => (
              <span key={name} className="px-3 py-1 bg-dark-600 rounded-full text-sm flex items-center gap-2">
                {name}
                <button onClick={() => removeUniversity(name)} className="text-gray-400 hover:text-white">×</button>
              </span>
            ))}
          </div>
        )}
      </div>

      {Object.keys(data).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">分数线变化趋势</h2>
          <ScoreTrendChart data={data} />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Test**

Visit `http://localhost:3000/trends` — search for university trends

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add trends page with ECharts line chart"
```

---

### Task 9: 院校对比页

**Covers:** [S6, S7]

**Files:**
- Create: `D:\gaokao-system\frontend\src\components\RadarCompare.tsx`
- Create: `D:\gaokao-system\frontend\src\app\compare\page.tsx`

- [ ] **Step 1: Create RadarCompare component**

```tsx
// src/components/RadarCompare.tsx
"use client";

import ReactECharts from "echarts-for-react";
import { CompareData } from "@/lib/api";

interface Props {
  data: Record<string, CompareData>;
}

export default function RadarCompare({ data }: Props) {
  const names = Object.keys(data);
  if (names.length < 2) return <p className="text-gray-400">请选择至少 2 所大学进行对比</p>;

  // 计算雷达图指标
  const indicators = [
    { name: "最新分数", max: 750 },
    { name: "录取位次", max: 100000 },
    { name: "招生计划数", max: 1000 },
    { name: "专业数量", max: 100 },
  ];

  const series = names.map((name) => {
    const d = data[name];
    const latestScore = d.scores.length > 0 ? d.scores[d.scores.length - 1].min_score || 0 : 0;
    const latestRank = d.scores.length > 0 ? d.scores[d.scores.length - 1].min_rank || 0 : 0;

    return {
      value: [
        latestScore,
        100000 - latestRank, // 位次越小越好，反转
        d.plans.total_quota || 0,
        d.plans.major_count || 0,
      ],
      name,
    };
  });

  const option = {
    backgroundColor: "transparent",
    tooltip: {},
    legend: {
      data: names,
      textStyle: { color: "#a0a0a0" },
    },
    radar: {
      indicator: indicators,
      axisName: { color: "#a0a0a0" },
      splitArea: { areaStyle: { color: ["transparent"] } },
      splitLine: { lineStyle: { color: "#333" } },
      axisLine: { lineStyle: { color: "#333" } },
    },
    series: [
      {
        type: "radar",
        data: series,
      },
    ],
    color: ["#00d4aa", "#ff6b6b", "#ffd93d", "#4ecdc4"],
  };

  return <ReactECharts option={option} style={{ height: 400 }} />;
}
```

- [ ] **Step 2: Create compare page**

```tsx
// src/app/compare/page.tsx
"use client";

import { useState } from "react";
import { fetchCompare, CompareData } from "@/lib/api";
import RadarCompare from "@/components/RadarCompare";

const provinces = [
  "北京","天津","上海","重庆","河北","山西","辽宁","吉林","黑龙江",
  "江苏","浙江","安徽","福建","江西","山东","河南","湖北","湖南",
  "广东","广西","海南","四川","贵州","云南","陕西","甘肃","青海",
  "宁夏","新疆","内蒙古","西藏",
];

export default function ComparePage() {
  const [input, setInput] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [province, setProvince] = useState("河北");
  const [data, setData] = useState<Record<string, CompareData>>({});
  const [loading, setLoading] = useState(false);

  const addUniversity = () => {
    if (input && !selected.includes(input) && selected.length < 4) {
      setSelected([...selected, input]);
      setInput("");
    }
  };

  const removeUniversity = (name: string) => {
    setSelected(selected.filter((u) => u !== name));
  };

  const handleCompare = async () => {
    if (selected.length < 2) return;
    setLoading(true);
    try {
      const result = await fetchCompare(selected, province);
      setData(result.data || {});
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">院校对比</h1>

      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm text-gray-400 mb-1">大学名称</label>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addUniversity()}
              placeholder="回车添加（最多4所）"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">省份</label>
            <select value={province} onChange={(e) => setProvince(e.target.value)}>
              {provinces.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <button onClick={handleCompare} disabled={loading || selected.length < 2} className="btn-primary">
            {loading ? "对比中..." : "开始对比"}
          </button>
        </div>
        {selected.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {selected.map((name) => (
              <span key={name} className="px-3 py-1 bg-dark-600 rounded-full text-sm flex items-center gap-2">
                {name}
                <button onClick={() => removeUniversity(name)} className="text-gray-400 hover:text-white">×</button>
              </span>
            ))}
          </div>
        )}
      </div>

      {Object.keys(data).length >= 2 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">多维度对比</h2>
          <RadarCompare data={data} />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Test**

Visit `http://localhost:3000/compare` — add 2+ universities and compare

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add compare page with radar chart visualization"
```

---

### Task 10: 集成测试和最终验证

**Covers:** [S3, S4, S5, S6, S7]

**Files:**
- None (testing only)

- [ ] **Step 1: Start backend**

```bash
cd D:\gaokao-system
python -m uvicorn api.main:app --reload --port 8000
```

- [ ] **Step 2: Start frontend**

```bash
cd D:\gaokao-system\frontend
npm run dev
```

- [ ] **Step 3: Test all pages**

1. Visit `http://localhost:3000` — Dashboard 显示统计卡片
2. Visit `http://localhost:3000/recommend` — 输入分数 600，省份 河北，科类 物理，点击推荐
3. Visit `http://localhost:3000/trends` — 输入清华大学，省份 河北，查询趋势
4. Visit `http://localhost:3000/compare` — 输入清华大学、北京大学，省份 河北，开始对比

- [ ] **Step 4: Final commit**

```bash
cd D:\gaokao-system
git add .
git commit -m "chore: complete dashboard integration"
```

---

## Self-Review

1. **Spec coverage:** ✅ S3 (architecture) → Task 1,5; S4 (recommend) → Task 2,7; S5 (trends) → Task 3,8; S6 (compare) → Task 4,9; S7 (UI) → Task 5,6,7,8,9; S8 (structure) → Task 5; S10 (data access) → Task 1
2. **Placeholder scan:** ✅ No TBD/TODO placeholders
3. **Type consistency:** ✅ API interfaces (RecommendResult, TrendData, CompareData) used consistently across backend and frontend
