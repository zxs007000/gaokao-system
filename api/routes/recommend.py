"""志愿推荐 API — v3"""
from fastapi import APIRouter, Depends, HTTPException, Query
import sqlite3
import math
from ..database import get_db

router = APIRouter()

SUBJECT_ALIASES = {
    "物理": ["物理", "物理类", "理科", "综合"],
    "历史": ["历史", "历史类", "文科", "综合"],
    "综合": ["综合"],
}

RANK_RANGE_RATIO = 0.50

YEAR_WEIGHTS = {2025: 1.0, 2024: 0.7, 2023: 0.4, 2022: 0.2, 2021: 0.1}

# 专科/职业院校关键词，用于过滤（类型+层次+校名）
VOCATIONAL_KEYWORDS = ["专科", "职业", "高等专科学校", "职业技术", "高等职业技术", "高等专科"]


def resolve_subject(db: sqlite3.Connection, province: str, subject: str) -> str:
    candidates = SUBJECT_ALIASES.get(subject, [subject])
    placeholders = ",".join("?" for _ in candidates)
    existing = db.execute(
        f"SELECT DISTINCT subject FROM score_distribution WHERE province=? AND subject IN ({placeholders})",
        [province] + candidates,
    ).fetchall()
    if existing:
        return existing[0][0]
    for c in candidates:
        cnt = db.execute(
            "SELECT COUNT(*) FROM score_distribution WHERE province=? AND subject=?",
            [province, c],
        ).fetchone()[0]
        if cnt > 0:
            return c
    raise HTTPException(400, f"省份 {province} 无科目 {subject} 的排名数据")


def _is_vocational(name: str, uni_type: str, uni_level: str) -> bool:
    """判断是否为专科/职业院校（检查类型+层次+校名）"""
    text = f"{uni_type or ''} {uni_level or ''} {name or ''}"
    return any(kw in text for kw in VOCATIONAL_KEYWORDS)


def compute_weighted_rank(db: sqlite3.Connection, university_name: str, province: str) -> dict:
    """计算多年加权位次：每年只取中位数，避免同年多专业干扰"""
    rows = db.execute("""
        SELECT year, min_rank
        FROM scorelines
        WHERE university_name = ?
          AND province LIKE ?
          AND min_rank IS NOT NULL AND min_rank > 0
          AND year IN (2025, 2024, 2023, 2022, 2021)
        ORDER BY year DESC, min_rank ASC
    """, [university_name, f"%{province}%"]).fetchall()

    if not rows:
        return {"weighted_rank": None, "rank_years": 0, "rank_std": 0}

    # 按年份分组，每年取中位数
    year_ranks: dict[int, list[int]] = {}
    for year, rank in rows:
        year_ranks.setdefault(year, []).append(rank)

    yearly_medians = []
    for year in sorted(year_ranks.keys(), reverse=True):
        ranks = sorted(year_ranks[year])
        mid = len(ranks) // 2
        median = ranks[mid]
        yearly_medians.append((year, median))

    if not yearly_medians:
        return {"weighted_rank": None, "rank_years": 0, "rank_std": 0}

    # 加权平均
    total_weight = sum(YEAR_WEIGHTS.get(y, 0) for y, _ in yearly_medians)
    if total_weight <= 0:
        return {"weighted_rank": None, "rank_years": 0, "rank_std": 0}

    weighted_rank = sum(r * YEAR_WEIGHTS.get(y, 0) for y, r in yearly_medians) / total_weight

    # 变异系数
    medians = [r for _, r in yearly_medians]
    if len(medians) > 1:
        mean_r = sum(medians) / len(medians)
        variance = sum((r - mean_r) ** 2 for r in medians) / len(medians)
        cv = math.sqrt(variance) / mean_r if mean_r > 0 else 0
    else:
        cv = 0

    return {
        "weighted_rank": weighted_rank,
        "rank_years": len(yearly_medians),
        "rank_std": cv,
    }


@router.get("/recommend")
def recommend(
    score: int = Query(..., ge=0, le=750),
    province: str = Query(..., min_length=1),
    subject: str = Query("物理", min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    actual_subject = resolve_subject(db, province, subject)

    # 查位次
    rank_row = db.execute(
        "SELECT cumulative_rank FROM score_distribution WHERE province=? AND score=? AND subject=?",
        [province, score, actual_subject],
    ).fetchone()
    if not rank_row:
        rank_row = db.execute(
            "SELECT cumulative_rank FROM score_distribution WHERE province=? AND subject=? ORDER BY ABS(score-?) LIMIT 1",
            [province, actual_subject, score],
        ).fetchone()
    if not rank_row:
        raise HTTPException(404, f"未找到 {province} {subject} {score}分 的排名数据")

    user_rank = rank_row[0]
    rank_low = int(user_rank * (1 - RANK_RANGE_RATIO))
    rank_high = int(user_rank * (1 + RANK_RANGE_RATIO))

    prov_pattern = f"%{province}%"

    # 只统计落在用户位次范围内的记录，避免极端值污染AVG
    rows = db.execute("""
        SELECT s.university_name, s.province, u.type, u.level,
               u.is_985, u.is_211, u.is_dual_class,
               AVG(s.min_rank) as avg_rank,
               COUNT(*) as rank_count
        FROM scorelines s
        LEFT JOIN universities u ON s.university_name = u.name
        WHERE s.min_rank IS NOT NULL AND s.min_rank > 0
          AND s.min_rank BETWEEN ? AND ?
          AND s.province LIKE ?
        GROUP BY s.university_name
    """, [rank_low, rank_high, prov_pattern]).fetchall()

    # 查每所学校的总记录数（含无位次的），用于判断数据完整度
    uni_names_all = [r[0] for r in rows]
    total_counts = {}
    if uni_names_all:
        placeholders = ",".join("?" for _ in uni_names_all)
        tc_rows = db.execute(f"""
            SELECT university_name, COUNT(*) as total
            FROM scorelines
            WHERE university_name IN ({placeholders}) AND province LIKE ?
            GROUP BY university_name
        """, uni_names_all + [prov_pattern]).fetchall()
        for name, total in tc_rows:
            total_counts[name] = total

    if not rows:
        return {
            "score": score, "subject": subject, "actual_subject": actual_subject,
            "province": province, "rank": user_rank,
            "rank_range": [rank_low, rank_high], "total_count": 0, "results": [],
        }

    # 批量获取最新分数
    uni_names = [r[0] for r in rows]
    latest_scores = {}
    if uni_names:
        placeholders = ",".join("?" for _ in uni_names)
        score_rows = db.execute(f"""
            SELECT university_name, min_score
            FROM scorelines
            WHERE university_name IN ({placeholders})
              AND province LIKE ?
              AND min_score IS NOT NULL
            ORDER BY year DESC
        """, uni_names + [prov_pattern]).fetchall()
        for name, ms in score_rows:
            if name not in latest_scores:
                latest_scores[name] = ms

    # 为每所院校计算加权位次并过滤
    results = []
    for name, uni_prov, uni_type, uni_level, is985, is211, is_dual, sql_avg_rank, rank_count in rows:
        # 过滤专科（同时检查校名，因为很多学校不在universities表里）
        if _is_vocational(name, uni_type, uni_level):
            continue

        wr = compute_weighted_rank(db, name, province)

        # 用加权位次，无数据时回退到 SQL AVG
        effective_rank = wr["weighted_rank"] if wr["weighted_rank"] else sql_avg_rank

        # 数据完整度惩罚：有位次的记录占比太低，说明数据不可靠，位次往差了调
        total = total_counts.get(name, rank_count)
        if total > 0:
            completeness = rank_count / total
            if completeness < 0.3:
                # 数据太稀疏，惩罚系数 1.3~2.0
                penalty = 1.3 + (0.3 - completeness) * 2.3
                effective_rank = effective_rank * penalty

        # 二次过滤：加权位次必须在合理范围内
        if effective_rank < rank_low * 0.3 or effective_rank > rank_high * 2.0:
            continue

        ratio = effective_rank / user_rank if user_rank > 0 else 1

        # 分档
        if ratio < 0.85:
            tier = "冲"
        elif ratio <= 1.15:
            tier = "稳"
        else:
            tier = "保"

        # 概率
        prob = _calc_probability(ratio)
        if wr["rank_std"] > 0.1:
            uncertainty = min(0.2, (wr["rank_std"] - 0.1) * 2)
            prob = int(prob * (1 - uncertainty) + 50 * uncertainty)
        prob = max(5, min(98, prob))

        # 标签
        tags = []
        if is985: tags.append("985")
        if is211: tags.append("211")
        if is_dual: tags.append("双一流")

        results.append({
            "name": name,
            "province": uni_prov or "",
            "type": uni_type or "",
            "level": uni_level or "",
            "latest_score": latest_scores.get(name),
            "avg_rank": round(effective_rank),
            "probability": prob,
            "tier": tier,
            "majors": rank_count,
            "rank_years": wr["rank_years"],
            "rank_stability": "稳定" if wr["rank_std"] < 0.05 else ("波动" if wr["rank_std"] < 0.15 else "大波动"),
            "tags": tags,
        })

    # 分档排序
    chong = sorted([r for r in results if r["tier"] == "冲"], key=lambda x: x["avg_rank"])[:8]
    wen = sorted([r for r in results if r["tier"] == "稳"], key=lambda x: x["avg_rank"])[:8]
    bao = sorted([r for r in results if r["tier"] == "保"], key=lambda x: -x["avg_rank"])[:6]

    return {
        "score": score, "subject": subject, "actual_subject": actual_subject,
        "province": province, "rank": user_rank,
        "rank_range": [rank_low, rank_high],
        "total_count": len(results),
        "results": chong + wen + bao,
    }


def _calc_probability(ratio: float) -> int:
    if ratio < 0.7:
        return max(5, int(30 - (0.7 - ratio) * 100))
    elif ratio < 0.85:
        return int(30 + (ratio - 0.7) * 133)
    elif ratio < 1.0:
        return int(50 + (ratio - 0.85) * 200)
    elif ratio < 1.15:
        return int(80 + (1.15 - ratio) * 100)
    elif ratio < 1.5:
        return int(95 - (ratio - 1.15) * 20)
    else:
        return min(98, int(88 - (ratio - 1.5) * 10))
