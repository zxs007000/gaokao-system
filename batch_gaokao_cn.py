"""Batch fetch all school details and score lines from gaokao.cn"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import sqlite3
import time
import logging
from crawler.database import Database
from crawler.sites.gaokao_cn import GaoKaoCnSpider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("batch")

db = Database()
spider = GaoKaoCnSpider()

conn = sqlite3.connect('data/db/gaokao.db')
c = conn.cursor()

# Get all schools with gaokao_cn_id
c.execute("SELECT gaokao_cn_id, name FROM universities WHERE gaokao_cn_id IS NOT NULL AND gaokao_cn_id != ''")
all_schools = c.fetchall()
conn.close()

print(f"共 {len(all_schools)} 所大学需要处理")

# ── Phase 1: School details (all schools) ──
print("\n=== Phase 1: 获取所有大学详细信息 ===")
c2 = sqlite3.connect('data/db/gaokao.db').cursor()
c2.execute("SELECT gaokao_cn_id FROM universities WHERE ruanke_rank IS NOT NULL")
already_detailed = {r[0] for r in c2.fetchall()}
c2.connection.close()

detail_count = 0
detail_errors = 0
for i, (school_id, name) in enumerate(all_schools):
    if school_id in already_detailed:
        continue
    try:
        raw = spider.crawl({"data_type": "院校详情", "school_id": school_id})
        parsed = spider.parse(raw)
        if parsed:
            db.upsert_universities(parsed)
            detail_count += 1
    except Exception as e:
        detail_errors += 1
        if detail_errors <= 5:
            logger.warning("详情失败 %s: %s", name, e)

    if (i + 1) % 100 == 0:
        logger.info("  进度: %d/%d (新增%d, 错误%d)", i + 1, len(all_schools), detail_count, detail_errors)
    time.sleep(0.1)

logger.info("Phase 1 完成: 新增%d所详情, 错误%d", detail_count, detail_errors)

# ── Phase 2: Score lines (all schools) ──
print("\n=== Phase 2: 获取所有大学分数线 ===")
c3 = sqlite3.connect('data/db/gaokao.db').cursor()
c3.execute("SELECT gaokao_cn_id, name FROM universities WHERE gaokao_cn_id IS NOT NULL AND gaokao_cn_id != ''")
all_schools_for_scores = c3.fetchall()
c3.connection.close()

score_count = 0
score_errors = 0
for i, (school_id, name) in enumerate(all_schools_for_scores):
    try:
        raw = spider.crawl({"data_type": "分数线", "school_id": school_id, "school_name": name})
        parsed = spider.parse(raw)
        if parsed:
            db.insert_scorelines_batch(parsed)
            score_count += len(parsed)
    except Exception as e:
        score_errors += 1
        if score_errors <= 5:
            logger.warning("分数线失败 %s: %s", name, e)

    if (i + 1) % 100 == 0:
        logger.info("  进度: %d/%d (新增%d条, 错误%d)", i + 1, len(all_schools_for_scores), score_count, score_errors)
    time.sleep(0.1)

logger.info("Phase 2 完成: 新增%d条分数线, 错误%d", score_count, score_errors)

# ── Final summary ──
print(f"\n=== 最终统计 ===")
print(f"universities: {db.count('universities')}")
print(f"scorelines: {db.count('scorelines')}")
print(f"Phase 1 详情: 新增{detail_count}所, 错误{detail_errors}")
print(f"Phase 2 分数线: 新增{score_count}条, 错误{score_errors}")
