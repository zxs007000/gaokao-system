# 高考数据分析 Dashboard 设计文档

## [S1] Problem

现有高考数据库包含 113 万+条分数线、2000 所大学、1.3 万条招生计划详情、3.1 万条一分一段数据，但缺乏可视化分析工具。需要构建一个综合 Dashboard，帮助考生/家长进行志愿填报决策。

## [S2] Solution Overview

构建 React + Next.js 前端 + FastAPI 后端的高考数据分析系统，包含三个核心功能模块：志愿推荐、分数线趋势分析、院校对比。

**技术栈：**
- 前端：React + Next.js + Tailwind CSS + ECharts
- 后端：FastAPI + SQLite（复用现有 gaokao.db）
- 数据库：SQLite（已有数据，无需迁移）

## [S3] Architecture

```
┌─────────────────────────────────────────────┐
│           Frontend (React + Next.js)         │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ 志愿推荐  │ │ 分数线趋势│ │ 院校对比  │ │
│  └───────────┘ └───────────┘ └───────────┘ │
│              ECharts 可视化                  │
└────────────────────┬────────────────────────┘
                     │ REST API
┌────────────────────┴────────────────────────┐
│           Backend (FastAPI)                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ 推荐引擎  │ │ 趋势查询  │ │ 对比查询  │ │
│  └───────────┘ └───────────┘ └───────────┘ │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────┴────────────────────────┐
│           Data Layer (SQLite)                │
│  gaokao.db (113万+ 分数线, 2000大学)        │
└─────────────────────────────────────────────┘
```

## [S4] Feature: 志愿推荐引擎

**输入：** 分数 + 省份 + 科类（文/理/历史/物理）

**处理流程：**
1. 查询 score_distribution 表，根据分数确定位次（cumulative_rank）
2. 查询 scorelines 表，筛选目标省份 + 目标科类的历年录取数据
3. 按位次匹配：位次接近的大学为"稳"，位次略高的为"冲"，位次略低的为"保"
4. 结合多年数据计算录取概率（基于位次波动范围）

**输出：** 推荐列表
- 大学名称、省份、类型、层次
- 历年录取分数（2022-2025）
- 推荐分层：冲 / 稳 / 保
- 录取概率（%）

**API 接口：** `GET /api/recommend?score=600&province=河北&subject=物理`

**关键 SQL 逻辑：**
- 一分一段位次查询：`SELECT cumulative_rank FROM score_distribution WHERE province=? AND year=? AND subject=? AND score<=? ORDER BY score DESC LIMIT 1`
- 匹配大学：`SELECT * FROM scorelines WHERE province=? AND year IN (2022,2023,2024,2025) AND min_score BETWEEN ? AND ?`

## [S5] Feature: 分数线趋势分析

**功能：** 选择大学 + 省份 → 展示 2019-2025 年分数线变化

**可视化：**
- 折线图：X 轴为年份，Y 轴为分数
- 支持多校叠加对比（最多 5 所）
- K 线图模式：展示最低/平均/最高分

**API 接口：** `GET /api/trends?university=清华大学&province=河北&years=2019-2025`

**关键 SQL：**
```sql
SELECT year, MIN(min_score) as min_score, AVG(avg_score) as avg_score, MAX(max_score) as max_score
FROM scorelines
WHERE university_name=? AND province=?
GROUP BY year ORDER BY year
```

## [S6] Feature: 院校对比工具

**功能：** 选择 2-4 所大学 → 多维度对比

**对比维度：**
- 分数线对比（历年最低分）
- 录取位次对比
- 招生计划对比（2025年计划数）
- 学科评估对比（如有数据）

**可视化：**
- 雷达图：各维度归一化后对比
- 表格：详细数据对比

**API 接口：** `GET /api/compare?universities=清华大学,北京大学&province=河北`

## [S7] UI Design

**风格：** 深色主题 + 霓虹色点缀（金融感）

**页面结构：**
- 左侧导航栏：首页 / 志愿推荐 / 分数线趋势 / 院校对比
- 首页 Dashboard：数据概览卡片（大学数量、分数线数量、覆盖省份等）
- 各功能页：顶部参数配置区 + 中央图表区

**颜色方案：**
- 背景：#0a0a0a / #1a1a2e
- 卡片：#16213e
- 主色：#00d4aa（霓虹绿）
- 辅色：#ff6b6b（冲）、#ffd93d（稳）、#6bcb77（保）

## [S8] Project Structure

```
D:\gaokao-system\
├── api/                        # FastAPI 后端
│   ├── main.py                 # FastAPI 入口
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── recommend.py        # 志愿推荐 API
│   │   ├── trends.py           # 趋势查询 API
│   │   └── compare.py          # 对比查询 API
│   └── database.py             # 数据库连接（复用现有）
├── frontend/                   # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # 全局布局
│   │   │   ├── page.tsx        # 首页 Dashboard
│   │   │   ├── recommend/
│   │   │   │   └── page.tsx    # 志愿推荐页
│   │   │   ├── trends/
│   │   │   │   └── page.tsx    # 分数线趋势页
│   │   │   └── compare/
│   │   │       └── page.tsx    # 院校对比页
│   │   ├── components/
│   │   │   ├── Sidebar.tsx     # 左侧导航
│   │   │   ├── ScoreTrendChart.tsx  # 趋势折线图
│   │   │   ├── RadarCompare.tsx     # 雷达对比图
│   │   │   ├── RecommendTable.tsx   # 推荐结果表
│   │   │   └── StatCard.tsx         # 数据概览卡片
│   │   └── lib/
│   │       └── api.ts          # API 调用封装
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── crawler/                    # 已有爬虫系统（不动）
├── data/db/gaokao.db           # 已有数据库（不动）
└── docs/
```

## [S9] Development Order

1. **FastAPI 后端** — 3 个 API 接口 + 数据库连接
2. **Next.js 项目初始化** — 布局 + 导航 + 全局样式
3. **志愿推荐页** — 核心功能，输入表单 + 推荐结果表
4. **分数线趋势页** — ECharts 折线图 + 多校叠加
5. **院校对比页** — 雷达图 + 数据表格
6. **首页 Dashboard** — 数据概览卡片

## [S10] Data Access Pattern

所有数据查询复用现有 `crawler/database.py` 中的 `Database` 类，不新建数据库连接。

**查询模式：**
- 志愿推荐：直接用 SQLite raw SQL（性能优先）
- 趋势分析：复用 `Database.get_scorelines()` 方法
- 院校对比：自定义查询聚合多年数据

## [S11] Constraints

- 不修改现有爬虫代码和数据库结构
- 前端独立运行（Next.js dev server），后端独立运行（FastAPI uvicorn）
- 第一版不考虑用户认证/登录
- 第一版不考虑数据实时更新（静态数据即可）
