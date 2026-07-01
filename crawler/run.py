"""爬虫入口 —— 调度、批量写入、进度跟踪"""
import logging
import time

from .database import Database
from .config import config
from .models import ScoreLine, University
from .registry import spider_registry


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("crawler")


class CrawlRunner:
    """调度器：发现爬虫 → 分批执行 → 批量写入"""

    def __init__(self, db: Database):
        self.db = db

    @classmethod
    def list_spiders(cls) -> list[str]:
        return sorted(spider_registry.list())

    def run(self, spider_name: str, params: dict | None = None):
        if params is None:
            params = {}

        # 延迟写入阈值：攒够 N 条或所有页爬完才写入
        BATCH_SIZE = 200

        spider_cls = spider_registry.get(spider_name)
        if not spider_cls:
            logger.error("找不到爬虫: %s", spider_name)
            return

        spider = spider_cls()
        logger.info("🚀 启动爬虫: %s", spider_name)

        try:
            universities_buf: list[University] = []
            scorelines_buf: list[ScoreLine] = []
            total_univ = 0
            total_score = 0

            # 多页爬取
            data_type = params.get("data_type", spider.data_types[0] if spider.data_types else "院校")
            page = params.get("page", 1)
            max_pages = params.get("max_pages", 1)

            while page <= max_pages:
                crawl_params = {**params, "data_type": data_type, "page": page}
                raw_data = spider.crawl(crawl_params)
                if not raw_data:
                    logger.info("第 %d 页无数据，停止分页", page)
                    break

                parsed = spider.parse(raw_data)

                for item in parsed:
                    if isinstance(item, University):
                        universities_buf.append(item)
                    elif isinstance(item, ScoreLine):
                        scorelines_buf.append(item)

                # 攒满一批就写入
                if len(universities_buf) >= BATCH_SIZE:
                    n = self.db.upsert_universities(universities_buf)
                    total_univ += n
                    logger.info("  已写入 %d 所大学 (累计 %d)", n, total_univ)
                    universities_buf.clear()

                if len(scorelines_buf) >= BATCH_SIZE:
                    n = self.db.insert_scorelines_batch(scorelines_buf)
                    total_score += n
                    logger.info("  已写入 %d 条分数线 (累计 %d)", n, total_score)
                    scorelines_buf.clear()

                page += 1
                spider.rate_limit()

            # 写入剩余数据
            if universities_buf:
                n = self.db.upsert_universities(universities_buf)
                total_univ += n
                logger.info("  已写入 %d 所大学 (累计 %d)", n, total_univ)

            if scorelines_buf:
                n = self.db.insert_scorelines_batch(scorelines_buf)
                total_score += n
                logger.info("  已写入 %d 条分数线 (累计 %d)", n, total_score)

            logger.info("✅ %s 完成: 大学 %d, 分数线 %d", spider_name, total_univ, total_score)

        finally:
            # 释放资源（如浏览器）
            if hasattr(spider, "close"):
                spider.close()


def main():
    import sys
    db = Database()
    runner = CrawlRunner(db)

    if len(sys.argv) < 2:
        print(f"用法: python -m crawler.run <spider_name> [参数...]")
        print(f"可用爬虫: {runner.list_spiders()}")
        return

    spider_name = sys.argv[1]

    # 简单参数解析: key=value 对
    params = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # 尝试转换类型
            if v.isdigit():
                v = int(v)
            params[k] = v

    runner.run(spider_name, params)


if __name__ == "__main__":
    main()
