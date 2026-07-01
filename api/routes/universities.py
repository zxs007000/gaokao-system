"""大学搜索 API"""
from fastapi import APIRouter, Depends, Query
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/universities/search")
def search_universities(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: sqlite3.Connection = Depends(get_db),
):
    rows = db.execute(
        """
        SELECT name, province, type, level, ruanke_rank,
               is_985, is_211, is_dual_class
        FROM universities
        WHERE name LIKE ?
        ORDER BY
            CASE WHEN is_985 = 1 THEN 0 ELSE 1 END,
            CASE WHEN is_211 = 1 THEN 0 ELSE 1 END,
            CASE WHEN is_dual_class = 1 THEN 0 ELSE 1 END,
            ruanke_rank ASC
        LIMIT ?
        """,
        (f"%{q}%", limit),
    ).fetchall()

    results = []
    for r in rows:
        tags = []
        if r["is_985"]: tags.append("985")
        if r["is_211"]: tags.append("211")
        if r["is_dual_class"]: tags.append("双一流")
        results.append({
            "name": r["name"],
            "province": r["province"],
            "type": r["type"],
            "level": r["level"],
            "ruanke_rank": r["ruanke_rank"],
            "tags": tags,
        })

    return {"results": results, "count": len(results)}
