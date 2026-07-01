"""首页统计数据 API"""
from fastapi import APIRouter, Depends
import sqlite3
from ..database import get_db

router = APIRouter()


@router.get("/stats")
def get_stats(db: sqlite3.Connection = Depends(get_db)):
    universities = db.execute("SELECT COUNT(*) FROM universities").fetchone()[0]

    scorelines = db.execute("SELECT COUNT(*) FROM scorelines WHERE min_score IS NOT NULL").fetchone()[0]

    years = db.execute("SELECT COUNT(DISTINCT year) FROM scorelines WHERE year >= 2020").fetchone()[0]

    # 最近更新的省份数
    provinces = db.execute("SELECT COUNT(DISTINCT province) FROM scorelines").fetchone()[0]

    # 985/211/双一流 数量
    top = db.execute("""
        SELECT
            COUNT(CASE WHEN is_985 = 1 THEN 1 END) as n985,
            COUNT(CASE WHEN is_211 = 1 THEN 1 END) as n211,
            COUNT(CASE WHEN is_dual_class = 1 THEN 1 END) as ndc
        FROM universities
    """).fetchone()

    # 最近更新的数据年份
    latest_year = db.execute("SELECT MAX(year) FROM scorelines").fetchone()[0]

    return {
        "universities": universities,
        "scorelines": scorelines,
        "provinces": provinces,
        "years": years,
        "latest_year": latest_year,
        "top": {"n985": top["n985"], "n211": top["n211"], "n_dc": top["ndc"]},
    }
