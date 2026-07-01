"""爬虫注册表 —— 自动发现 + 手动注册"""
import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Optional

from .base import SpiderBase

logger = logging.getLogger(__name__)


class SpiderRegistry:
    _spiders: dict[str, type[SpiderBase]] = {}

    def __init__(self):
        self._discover()

    def _discover(self):
        """自动发现 sites/ 目录下的爬虫模块"""
        sites_path = Path(__file__).parent / "sites"
        for _, module_name, _ in pkgutil.iter_modules([str(sites_path)]):
            if module_name.startswith("_"):
                continue
            try:
                module = importlib.import_module(f"crawler.sites.{module_name}")
            except ImportError as e:
                # 依赖缺失（如 crawl4ai 未安装）→ 跳过但不报错
                logger.debug("跳过模块 %s: %s", module_name, e)
                continue

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, SpiderBase)
                    and attr is not SpiderBase
                    and attr.name
                ):
                    self._spiders[attr.name] = attr
                    logger.debug("发现爬虫: %s", attr.name)

    def list(self) -> list[str]:
        return list(self._spiders.keys())

    list_spiders = list  # 兼容旧接口

    def get(self, name: str) -> Optional[type[SpiderBase]]:
        return self._spiders.get(name)

    def register(self, spider_class: type[SpiderBase]):
        """手动注册爬虫"""
        if spider_class.name:
            self._spiders[spider_class.name] = spider_class


# 模块级单例
spider_registry = SpiderRegistry()
