# 掌上高考爬虫 + 阳光高考网增强 设计文档

## [S1] 问题

当前爬虫系统存在两个问题：
1. **掌上高考（www.gaokao.cn）没有专用爬虫** — 设计文档列为 Tier 1 数据源，但未实现
2. **阳光高考网爬虫数据太简陋** — 只抓取 name/code/province/type/level，缺少分数线、专业、保研率等丰富数据

## [S2] 解决方案

### 任务 A：新建掌上高考爬虫（gaokao_cn.py）

掌上高考的数据直接以 JSON API 提供，无需 Playwright 渲染：

| API 端点 | 数据 | 用途 |
|----------|------|------|
| `static-data.gaokao.cn/www/2.0/school/list_v2.json` | 2991所大学基础信息 | 批量获取院校列表 |
| `static-data.gaokao.cn/www/2.0/school/{id}/info.json` | 单校详细信息（保研率/博士点/排名等） | 院校详情 |
| `static-data.gaokao.cn/www/2.0/school/{id}/dic/provincescore.json` | 该校有分数线数据的省份+年份 | 分数线索引 |
| `static-data.gaokao.cn/www/2.0/school/{id}/benchmarkScore.json` | 各省各年最低分 | 分数线批量获取 |
| `static-gkcx.gaokao.cn/www/2.0/json/rank/{school_id}/{province_id}/lists.json` | 该校某省历年录取数据 | 详细分数线 |

**实现步骤：**
1. 新建 `crawler/sites/gaokao_cn.py`，实现 JSON API 直接获取
2. 先批量获取 2991 所大学基础信息
3. 再逐校获取详细信息 + 分数线
4. 数据写入已有的 universities 和 scorelines 表

### 任务 B：增强阳光高考网爬虫

在现有 `yangguang.py` 基础上增加：
- 从列表页提取满意度评分（`.sch-score`）
- 提取更多标签信息（985/211/双一流等）
- 将提取的数据与数据库中已有数据合并

## [S3] 数据模型

### 大学表扩展字段

在现有 universities 表基础上增加（通过 ALTER TABLE）：

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| city | TEXT | 城市 | gaokao_cn |
| school_nature | TEXT | 办学性质（公办/民办） | gaokao_cn |
| belong | TEXT | 主管部门 | gaokao_cn |
| is_985 | INTEGER | 是否985 | gaokao_cn |
| is_211 | INTEGER | 是否211 | gaokao_cn |
| is_dual_class | INTEGER | 是否双一流 | gaokao_cn |
| create_year | INTEGER | 建校年份 | gaokao_cn |
| area | INTEGER | 校园面积 | gaokao_cn |
| ruanke_rank | INTEGER | 软科排名 | gaokao_cn |
| qs_rank | INTEGER | QS排名 | gaokao_cn |
| xyh_rank | INTEGER | 校友会排名 | gaokao_cn |
| num_master | INTEGER | 硕士点数 | gaokao_cn |
| num_doctor | INTEGER | 博士点数 | gaokao_cn |
| num_academician | INTEGER | 院士数 | gaokao_cn |
| recommend_master_rate | TEXT | 保研率 | gaokao_cn |
| gaokao_cn_id | TEXT | 掌上高考学校ID | gaokao_cn |

### 分数线表扩展

在现有 scorelines 表基础上增加：

| 字段 | 类型 | 说明 | 来源 |
|------|------|------|------|
| subject | TEXT | 科类/选科 | gaokao_cn |
| enrollment_type | TEXT | 招生类型（普通类/中外合作等） | gaokao_cn |

## [S4] 实现计划

### Task 1：扩展数据库 schema
- 给 universities 表添加新列（ALTER TABLE）
- 给 scorelines 表添加新列
- 更新 ORM 模型

### Task 2：掌上高考爬虫核心
- 新建 `crawler/sites/gaokao_cn.py`
- 实现 `fetch_school_list()` — 批量获取2991所大学
- 实现 `fetch_school_detail()` — 单校详细信息
- 实现 `fetch_score_lines()` — 分数线数据
- 遵循现有 SpiderBase 接口

### Task 3：掌上高考爬虫集成
- 更新 `run.py` 支持新的爬虫
- 添加批量爬取模式（先院校列表 → 逐校详情+分数线）

### Task 4：增强阳光高考网爬虫
- 在 `yangguang.py` 的 `parse_universities()` 中增加更多字段提取
- 满意度评分、标签等

### Task 5：数据导入与验证
- 运行掌上高考爬虫获取全部院校数据
- 运行分数线爬取
- 验证数据完整性

## [S5] 验证标准

1. universities 表新增字段有数据（gaokao_cn 来源）
2. scorelines 表新增 gaokao_cn 来源的分数线
3. 2991所大学全部入库
4. 至少 Top 100 大学有详细信息（保研率、排名等）
