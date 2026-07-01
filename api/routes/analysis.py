"""院校深度分析 API"""
from fastapi import APIRouter, Depends, Query
import sqlite3
import math
from ..database import get_db

router = APIRouter()


@router.get("/analysis/score-trend")
def score_trend(
    university: str = Query(..., min_length=1),
    province: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    prov_pattern = f"%{province}%"
    rows = db.execute(
        """SELECT year, min_score, min_rank, major_name
           FROM scorelines
           WHERE university_name = ? AND province LIKE ? AND min_score IS NOT NULL
           ORDER BY year, major_name""",
        [university, prov_pattern],
    ).fetchall()

    by_year: dict = {}
    for r in rows:
        y = r[0]
        if y not in by_year:
            by_year[y] = {"scores": [], "ranks": []}
        by_year[y]["scores"].append(r[1])
        if r[2]:
            by_year[y]["ranks"].append(r[2])

    trend = []
    scores_list = []
    for y in sorted(by_year.keys()):
        d = by_year[y]
        avg_score = round(sum(d["scores"]) / len(d["scores"])) if d["scores"] else None
        min_score = min(d["scores"]) if d["scores"] else None
        max_score = max(d["scores"]) if d["scores"] else None
        avg_rank = round(sum(d["ranks"]) / len(d["ranks"])) if d["ranks"] else None
        trend.append({
            "year": y, "avg_score": avg_score, "min_score": min_score,
            "max_score": max_score, "avg_rank": avg_rank, "major_count": len(d["scores"]),
        })
        if avg_score:
            scores_list.append(avg_score)

    volatility = None
    trend_direction = "稳定"
    if len(scores_list) >= 2:
        mean = sum(scores_list) / len(scores_list)
        variance = sum((s - mean) ** 2 for s in scores_list) / len(scores_list)
        volatility = round(math.sqrt(variance), 1)
        if scores_list[-1] > scores_list[0] + 5:
            trend_direction = "上升"
        elif scores_list[-1] < scores_list[0] - 5:
            trend_direction = "下降"

    return {
        "university": university, "province": province,
        "trend": trend, "volatility": volatility,
        "trend_direction": trend_direction,
        "year_span": len(trend),
    }


@router.get("/analysis/enrollment-plans")
def enrollment_plans(
    university: str = Query(..., min_length=1),
    province: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        """SELECT major_name, plan_2025, score_2024, rank_2024,
                  score_2023, rank_2023, score_2022, rank_2022,
                  postgrad_recommend_rate, tuition, subject_requirement
           FROM enrollment_plans_detail
           WHERE university_name = ? AND province = ?
           ORDER BY plan_2025 DESC""",
        [university, province],
    ).fetchall()

    plans = []
    total_2025 = 0
    for r in rows:
        major, plan_25 = r[0], r[1] or 0
        s24, r24, s23, r23, s22, r22 = r[2], r[3], r[4], r[5], r[6], r[7]
        pg_rate, tuition, subj = r[8], r[9], r[10]

        change_24_25 = None
        change_23_24 = None
        if s24 and s23:
            change_23_24 = s24 - s23
        if s24:
            change_24_25 = "参考2024"

        plans.append({
            "major": major, "plan_2025": plan_25,
            "score_2024": s24, "rank_2024": r24,
            "score_2023": s23, "rank_2023": r23,
            "score_2022": s22, "rank_2022": r22,
            "score_change": change_23_24,
            "postgrad_rate": pg_rate,
            "tuition": tuition, "subject": subj,
        })
        total_2025 += plan_25

    return {
        "university": university, "province": province,
        "total_plan_2025": total_2025,
        "major_count": len(plans),
        "plans": plans,
    }


@router.get("/analysis/major-ranking")
def major_ranking(
    university: str = Query(..., min_length=1),
    province: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    prov_pattern = f"%{province}%"
    rows = db.execute(
        """SELECT major_name, MIN(min_score) as lowest_score, MIN(min_rank) as best_rank,
                  COUNT(DISTINCT year) as year_count
           FROM scorelines
           WHERE university_name = ? AND province LIKE ? AND min_score IS NOT NULL
           GROUP BY major_name
           ORDER BY lowest_score DESC""",
        [university, prov_pattern],
    ).fetchall()

    majors = []
    for i, r in enumerate(rows):
        majors.append({
            "rank": i + 1, "major": r[0],
            "lowest_score": r[1], "best_rank": r[2],
            "year_count": r[3],
        })

    return {
        "university": university, "province": province,
        "majors": majors,
    }


@router.get("/analysis/geographic")
def geographic_distribution(
    province: str = Query(None),
    db: sqlite3.Connection = Depends(get_db),
):
    if province:
        prov_pattern = f"%{province}%"
        rows = db.execute(
            """SELECT province, COUNT(*) as count,
                      AVG(CASE WHEN is_985 = 1 THEN 1.0 ELSE 0.0 END) as rate_985,
                      AVG(CASE WHEN is_211 = 1 THEN 1.0 ELSE 0.0 END) as rate_211
               FROM universities
               WHERE province LIKE ?
               GROUP BY province""",
            [prov_pattern],
        ).fetchall()
    else:
        rows = db.execute(
            """SELECT province, COUNT(*) as count,
                      AVG(CASE WHEN is_985 = 1 THEN 1.0 ELSE 0.0 END) as rate_985,
                      AVG(CASE WHEN is_211 = 1 THEN 1.0 ELSE 0.0 END) as rate_211
               FROM universities
               GROUP BY province
               ORDER BY count DESC"""
        ).fetchall()

    return {
        "distribution": [
            {"province": r[0], "count": r[1], "rate_985": round(r[2] * 100, 1), "rate_211": round(r[3] * 100, 1)}
            for r in rows
        ]
    }


@router.get("/analysis/university-quality")
def university_quality(
    university: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    info = db.execute(
        """SELECT name, province, type, level, is_985, is_211, is_dual_class,
                  ruanke_rank, qs_rank, xyh_rank,
                  num_master, num_doctor, num_academician,
                  recommend_master_rate, area, create_year
           FROM universities WHERE name = ?""",
        [university],
    ).fetchone()

    if not info:
        return {"error": "未找到该大学"}

    return {
        "name": info[0], "province": info[1], "type": info[2], "level": info[3],
        "is_985": bool(info[4]), "is_211": bool(info[5]), "is_dual_class": bool(info[6]),
        "rankings": {
            "ruanke": info[7], "qs": info[8], "xyh": info[9],
        },
        "academic": {
            "master_programs": info[10], "doctor_programs": info[11],
            "academicians": info[12], "postgrad_rate": info[13],
        },
        "campus": {"area_mu": info[14], "founded": info[15]},
    }
