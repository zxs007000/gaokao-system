"""爬虫管理 API —— 启动爬虫、查看状态、导入数据"""
import asyncio
import logging
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form

router = APIRouter()

logger = logging.getLogger("crawler_admin")

# ── 后台任务状态 ──────────────────────────────────────────
_crawl_status: dict = {"running": False, "spider": "", "log": [], "error": ""}


def _run_crawl(spider_name: str):
    """在后台线程中运行爬虫"""
    global _crawl_status
    _crawl_status = {"running": True, "spider": spider_name, "log": [], "error": ""}

    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        python_exe = sys.executable

        process = subprocess.Popen(
            [python_exe, "-m", "crawler.run", spider_name],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        for line in process.stdout:
            line = line.strip()
            if line:
                _crawl_status["log"].append(line)
                if len(_crawl_status["log"]) > 200:
                    _crawl_status["log"] = _crawl_status["log"][-200:]

        process.wait()

        for line in process.stderr:
            line = line.strip()
            if line:
                _crawl_status["log"].append(f"[ERR] {line}")

        if process.returncode != 0:
            _crawl_status["error"] = f"爬虫退出码: {process.returncode}"

    except Exception as e:
        _crawl_status["error"] = str(e)
    finally:
        _crawl_status["running"] = False


@router.get("/crawler/spiders")
def list_spiders():
    """列出所有可用爬虫"""
    try:
        from crawler.registry import spider_registry
        spiders = spider_registry.list()
        return {"spiders": spiders, "total": len(spiders)}
    except Exception as e:
        return {"spiders": [], "total": 0, "error": str(e)}


@router.post("/crawler/run")
def start_crawl(spider: str = Form(...)):
    """启动指定爬虫（后台运行）"""
    global _crawl_status

    if _crawl_status["running"]:
        return {
            "ok": False,
            "message": f"已有爬虫在运行: {_crawl_status['spider']}",
        }

    try:
        from crawler.registry import spider_registry
        if spider not in spider_registry.list():
            return {"ok": False, "message": f"未知爬虫: {spider}"}
    except Exception:
        pass  # 即使无法验证也尝试运行

    thread = threading.Thread(target=_run_crawl, args=(spider,), daemon=True)
    thread.start()

    return {"ok": True, "message": f"爬虫 {spider} 已启动", "spider": spider}


@router.get("/crawler/status")
def crawl_status():
    """获取爬虫运行状态和日志"""
    return _crawl_status


@router.post("/crawler/import/excel")
def import_excel_data(file_path: str = ""):
    """导入 Excel 招生计划数据"""
    if not file_path:
        return {"ok": False, "message": "请提供 Excel 文件路径"}

    path = Path(file_path)
    if not path.exists():
        return {"ok": False, "message": f"文件不存在: {file_path}"}

    project_root = Path(__file__).resolve().parent.parent.parent
    python_exe = sys.executable

    try:
        # 在子进程中执行导入
        code = f"""
import sys; sys.path.insert(0, '{project_root}')
from import_excel import import_excel
import_excel('{file_path}')
"""
        result = subprocess.run(
            [python_exe, "-c", code],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        return {
            "ok": result.returncode == 0,
            "message": "导入完成" if result.returncode == 0 else f"导入失败，退出码: {result.returncode}",
            "output": (result.stdout + result.stderr)[:5000],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "导入超时（超过 5 分钟）"}
    except Exception as e:
        return {"ok": False, "message": str(e)}


@router.get("/crawler/db-stats")
def db_stats():
    """数据库统计信息"""
    import sqlite3
    db_path = Path(__file__).resolve().parent.parent.parent / "data" / "db" / "gaokao.db"

    if not db_path.exists():
        return {
            "ok": False,
            "message": f"数据库不存在: {db_path}",
            "db_path": str(db_path),
        }

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        tables = {}
        for table in ["universities", "scorelines", "score_distribution", "enrollment_plans"]:
            try:
                count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except Exception:
                count = 0
            tables[table] = count

        # 最新数据年份
        try:
            latest = cur.execute("SELECT MAX(year) FROM scorelines").fetchone()[0] or 0
        except Exception:
            latest = 0

        # 数据库文件大小
        size_mb = round(db_path.stat().st_size / (1024 * 1024), 1)

        conn.close()
        return {
            "ok": True,
            "tables": tables,
            "latest_year": latest,
            "size_mb": size_mb,
            "db_path": str(db_path),
        }
    except Exception as e:
        return {"ok": False, "message": str(e)}
