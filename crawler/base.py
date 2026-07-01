"""爬虫基类 —— retry、logging、速率控制"""
import functools
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Callable

from .config import config

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = None,
    base_delay: float = 1.0,
    backoff: float = 2.0,
):
    """装饰器：请求失败自动重试，指数退避"""
    max_retries = max_retries if max_retries is not None else config.max_retries

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt == max_retries:
                        logger.error(
                            "%s 失败 %d 次: %s", func.__name__, max_retries + 1, e
                        )
                        raise
                    delay = base_delay * (backoff ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        "%s 第 %d 次重试（%.1fs 后）: %s",
                        func.__name__, attempt + 1, delay, e,
                    )
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


class SpiderBase(ABC):
    """所有爬虫的抽象基类"""

    name: str = ""         # 爬虫标识
    source: str = ""       # 数据来源
    data_types: list[str] = []  # 支持的数据类型

    def __init__(self):
        self.logger = logging.getLogger(f"spider.{self.name}")

    @abstractmethod
    def crawl(self, params: dict[str, Any]) -> Any:
        """爬取原始数据"""
        ...

    @abstractmethod
    def parse(self, raw_data: Any) -> list[Any]:
        """解析为 model 对象列表"""
        ...

    def rate_limit(self):
        """请求间随机延时"""
        delay = random.uniform(config.delay_min, config.delay_max)
        self.logger.debug("延时 %.1fs", delay)
        time.sleep(delay)

    def save_raw(self, data: Any, filename: str):
        """保存原始数据到磁盘"""
        import json
        from pathlib import Path
        path = Path(config.data_dir) / "raw" / f"{self.name}_{filename}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        # 不保存 HTML 字符串（体积太大），只保存结构化数据
        clean = []
        for item in (data if isinstance(data, list) else [data]):
            if isinstance(item, dict) and "html" in item:
                # 保留元信息，去 HTML
                clean.append({k: v for k, v in item.items() if k != "html"})
            else:
                clean.append(item)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean, f, ensure_ascii=False, indent=2)
        self.logger.info("原始数据已保存: %s", path)
