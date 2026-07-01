"""分数线趋势 API"""
from fastapi import APIRouter, Depends, Query
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/trends/multi")
def get_multi_trends(
    universities: str = Query(..., min_length=1),
    province: str = Query(..., min_length=1),
    db: sqlite3.Connection = Depends(get_db),
):
    names = [n.strip() for n in universities.split(",") if n.strip()]
    if not names:
        return {"data": {}}

    prov_pattern = f"%{province}%"
    data: dict = {}

    for name in names:
        rows = db.execute(
            """SELECT year, min_score, min_rank
               FROM scorelines
               WHERE university_name = ? AND province LIKE ?
               ORDER BY year""",
            [name, prov_pattern],
        ).fetchall()

        data[name] = [
            {"year": r[0], "min_score": r[1], "min_rank": r[2]}
            for r in rows
        ]

    return {"data": data}
