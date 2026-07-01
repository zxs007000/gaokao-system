"""院校对比 API"""
from fastapi import APIRouter, Depends, Query
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/compare")
def compare_universities(
    universities: str = Query(..., min_length=1),
    province: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    names = [n.strip() for n in universities.split(",") if n.strip()]
    if len(names) < 2:
        return {"data": {}, "error": "至少需要2所大学进行对比"}

    prov_pattern = f"%{province}%"
    data: dict = {}

    for name in names:
        # University info
        info = db.execute(
            "SELECT type, level, ruanke_rank, recommend_master_rate FROM universities WHERE name = ?",
            [name],
        ).fetchone()

        # Score trends
        scores = db.execute(
            "SELECT year, min_score, min_rank FROM scorelines WHERE university_name = ? AND province LIKE ? ORDER BY year",
            [name, prov_pattern],
        ).fetchall()

        # Enrollment plans
        plan = db.execute(
            "SELECT COUNT(*) as major_count, SUM(CAST(plan_2025 AS INTEGER)) as total_quota FROM enrollment_plans_detail WHERE university_name = ? AND province = ?",
            [name, prov_pattern.strip("%")],
        ).fetchone()

        data[name] = {
            "info": {
                "name": name,
                "province": province,
                "type": info[0] if info else "",
                "level": info[1] if info else "",
                "ruanke_rank": str(info[2]) if info and info[2] else None,
                "recommend_master_rate": str(info[3]) if info and info[3] else "0",
            },
            "scores": [{"year": r[0], "min_score": r[1], "min_rank": r[2]} for r in scores],
            "plans": {"major_count": plan[0] if plan and plan[0] else 0, "total_quota": plan[1] if plan and plan[1] else 0},
        }

    return {"data": data}
