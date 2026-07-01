# 🎯 高考志愿分析平台

> 基于真实录取数据的 AI 高考志愿填报辅助系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

---

## 📖 简介

一个**开源的高考志愿填报辅助平台**，集数据采集、智能分析、可视化展示于一体。系统基于全国各省官方录取数据，结合 AI 对话能力，为考生提供个性化的志愿填报建议。

### 核心功能

| 功能 | 说明 |
|------|------|
| 📊 **数据爬虫** | 自动采集全国各省教育考试院、高校官网的录取数据 |
| 🤖 **AI 志愿顾问** | 基于大模型的智能对话，提供个性化选校建议 |
| 📈 **录取趋势分析** | 历年分数线、位次变化趋势可视化 |
| 🎯 **冲稳保推荐** | 根据分数/位次，智能推荐冲、稳、保院校 |
| 🧠 **性格测评** | 结合专业倾向测评，推荐适合的专业方向 |
| 🔍 **院校对比** | 多维度对比不同院校的录取数据 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────┐
│          Frontend (Next.js)          │
│   React + TypeScript + Tailwind     │
└──────────────┬──────────────────────┘
               │ HTTP API
┌──────────────▼──────────────────────┐
│       Backend (FastAPI / Python)     │
│    AI 对话 · 数据查询 · 智能推荐     │
└──────────────┬──────────────────────┘
       ┌───────┴───────┐
       ▼               ▼
┌────────────┐  ┌──────────────┐
│  爬虫引擎   │  │  SQLite 数据库 │
│ Crawler    │  │  112万+ 条数据 │
└────────────┘  └──────────────┘
```

### 技术栈

- **后端**：Python 3.11+, FastAPI, OpenAI SDK
- **前端**：Next.js, React, TypeScript, Tailwind CSS
- **数据**：SQLite（约 112MB，含 29 省录取数据）
- **爬虫**：aiohttp, BeautifulSoup, Crawl4AI

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+

### 1. 克隆仓库

```bash
git clone https://github.com/zxs007000/gaokao-system.git
cd gaokao-system
```

### 2. 下载数据库（二选一）

**方式 A — Git LFS（推荐）：**
```bash
git lfs pull
```

**方式 B — Release 直链下载（无需 Git LFS）：**
```bash
# 下载到 data/db/ 目录
curl -L -o data/db/gaokao.db https://github.com/zxs007000/gaokao-system/releases/download/v1.0.0/gaokao.db
# Windows PowerShell:
# Invoke-WebRequest -Uri https://github.com/zxs007000/gaokao-system/releases/download/v1.0.0/gaokao.db -OutFile data/db/gaokao.db
```

### 3. 启动后端

```bash
pip install -r requirements.txt
python start.py
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问

浏览器打开 `http://localhost:3000`

---

## 📂 项目结构

```
├── api/                    # 后端 API
│   ├── main.py            # FastAPI 入口
│   ├── database.py        # 数据库连接
│   └── routes/            # API 路由
│       ├── ai.py          # AI 配置测试
│       ├── ai_chat.py     # AI 志愿顾问对话
│       ├── recommend.py   # 院校推荐
│       ├── universities.py # 院校数据查询
│       ├── analysis.py    # 数据分析
│       ├── trends.py      # 趋势分析
│       ├── compare.py     # 院校对比
│       ├── stats.py       # 统计信息
│       └── personality.py # 性格测评
├── crawler/                # 数据爬虫引擎
│   ├── base.py            # 爬虫基类
│   ├── config.py          # 爬虫配置
│   ├── database.py        # 数据存储
│   ├── models.py          # 数据模型
│   ├── registry.py        # 爬虫注册
│   ├── run.py             # 爬虫运行入口
│   └── sites/             # 各数据源爬虫
├── data/                   # 数据文件
│   ├── db/                # SQLite 数据库（LFS）
│   ├── raw/               # 原始抓取数据
│   └── cleaned/           # 清洗后数据
├── frontend/               # Next.js 前端
├── docs/                   # 设计文档
├── tests/                  # 单元测试
├── requirements.txt        # Python 依赖
├── start.py                # 后端启动脚本
└── start-all.bat           # Windows 一键启动
```

---

## ⚙️ 配置

在 API 调用时，前端界面中可配置：

- **API Key**：你的 LLM API Key（支持 DeepSeek / OpenAI 兼容接口）
- **模型**：选择使用的模型（deepseek-chat / gpt-4o 等）
- **接口地址**：自定义 API Base URL

---

## 📊 数据来源

系统数据来源于公开渠道：

- 各省教育考试院官方投档线公告
- 高校官网招生信息
- 阳光高考平台

> ⚠️ 数据仅供学习参考，正式填报请以各省教育考试院官方数据为准。

---

## 📜 开源协议

本项目基于 **MIT License** 开源 — 欢迎自由使用、修改、分发。

---

## 🤝 贡献

欢迎 Issue 和 PR！

- [ ] 更多省份录取数据接入
- [ ] WebSocket 实时对话
- [ ] 小程序 / Telegram Bot
- [ ] Docker 一键部署
