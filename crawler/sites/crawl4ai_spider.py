"""Crawl4AI 爬虫适配器 —— 通用 AI 友好型爬取

Crawl4AI 特点：
  - 内置 Playwright 渲染 JS 页面
  - 输出 Markdown / cleaned_html / structured data
  - 支持 CSS / XPath / LLM 等多种提取策略
  - 自动反检测、UA 轮换、代理支持

适用场景：
  - 任何需要 JS 渲染的目标站（阳光高考、教育考试院等）
  - 需要结构化数据提取（表格、列表）
  - 需要 Markdown 输出的页面（可喂给 LLM）
"""

import asyncio
import logging
from typing import Any

from ..base import SpiderBase, retry_on_failure
from ..config import config
from ..models import University, ScoreLine

logger = logging.getLogger(__name__)


class Crawl4AISpider(SpiderBase):
    """Crawl4AI 通用爬虫 —— 适合 JS 渲染 + 结构化提取"""

    name = "crawl4ai"
    source = "crawl4ai"
    data_types = ["院校", "分数线", "招生计划", "通用"]

    def __init__(self):
        super().__init__()
        self._crawler = None

    def _ensure_crawler(self):
        """懒加载 AsyncWebCrawler 实例"""
        if self._crawler is None:
            try:
                from crawl4ai import AsyncWebCrawler
                self._crawler = AsyncWebCrawler(
                    headless=config.headless,
                    verbose=False,
                    # 反检测
                    user_agent_mode="random",
                    # 代理（如有）
                    proxy=config.proxy or None,
                )
                self.logger.info("Crawl4AI 已就绪 (headless=%s)", config.headless)
            except ImportError:
                raise RuntimeError(
                    "Crawl4AI 未安装，请先运行: pip install crawl4ai"
                )
        return self._crawler

    # ── 公共接口 ───────────────────────────────────────────

    def crawl(self, params: dict[str, Any]) -> list[dict]:
        """同步入口（封装异步调用）"""
        return asyncio.run(self._async_crawl(params))

    @retry_on_failure(max_retries=3, base_delay=2)
    async def _async_crawl(self, params: dict[str, Any]) -> list[dict]:
        url = params.get("url", "")
        if not url:
            raise ValueError("缺少 url 参数")

        extraction = self._build_extraction(params)
        crawler = self._ensure_crawler()

        # 启动（首次会初始化浏览器）
        await crawler.start()

        try:
            result = await crawler.arun(
                url=url,
                # 等待 JS 渲染完成
                wait_for=params.get("wait_for", None),
                js_code=params.get("js_code", None),
                # 页面加载超时
                page_timeout=(params.get("timeout", config.timeout) * 1000),
                # CSS 选择器限定范围
                css_selector=params.get("css_selector", None),
                # 去除导航/页脚/广告等噪音
                remove_overlay_elements=True,
                excluded_tags=params.get("excluded_tags",
                                          ["nav", "footer", "script", "style"]),
                # 提取策略
                extraction_strategy=extraction,
                # 缓存
                bypass_cache=False,
            )

            return [{
                "url": url,
                "markdown": result.markdown or "",
                "cleaned_html": result.cleaned_html or "",
                "html": result.html or "",
                "extracted": result.extracted_content or "",
                "links": result.links or [],
                "media": result.media or {},
                "success": result.success,
                "error": result.error_message or "",
                "data_type": params.get("data_type", "通用"),
                "metadata": result.metadata or {},
            }]
        finally:
            await crawler.close()

    # ── parse ──────────────────────────────────────────────

    def parse(self, raw_data: Any) -> list[Any]:
        """根据 data_type 分发解析"""
        if not raw_data:
            return []

        if isinstance(raw_data, list):
            item = raw_data[0] if raw_data else {}
        elif isinstance(raw_data, dict):
            item = raw_data
        else:
            return []

        if not item.get("success"):
            self.logger.warning("爬取失败: %s", item.get("error"))
            return []

        data_type = item.get("data_type", "通用")

        # 优先使用 LLM 提取的结果
        if item.get("extracted"):
            return self._parse_extracted(item["extracted"], data_type)

        # 其次用 Markdown 结构化解析
        markdown = item.get("markdown", "")
        html = item.get("cleaned_html", "") or item.get("html", "")

        if data_type == "院校":
            return self._parse_universities_from_md(markdown, html)
        elif data_type == "分数线":
            return self._parse_scorelines_from_md(markdown, html)
        else:
            # 通用：返回 markdown 包装
            return [{"data_type": data_type, "markdown": markdown,
                     "html": html, "url": item.get("url")}]

    def parse_markdown(self, raw_data: Any) -> str:
        """提取 Markdown 文本（供 LLM 消费）"""
        if not raw_data:
            return ""
        if isinstance(raw_data, list):
            item = raw_data[0] if raw_data else {}
        else:
            item = raw_data
        return item.get("markdown", "")

    def parse_links(self, raw_data: Any) -> list[dict]:
        """提取页面链接"""
        if not raw_data:
            return []
        if isinstance(raw_data, list):
            item = raw_data[0] if raw_data else {}
        else:
            item = raw_data
        return item.get("links", [])

    # ── 提取策略 ───────────────────────────────────────────

    def _build_extraction(self, params: dict):
        """根据参数构建提取策略"""
        extract_type = params.get("extract_type", "none")

        if extract_type == "llm":
            from crawl4ai.extraction_strategy import LLMExtractionStrategy
            return LLMExtractionStrategy(
                provider=params.get("llm_provider", "openai/gpt-4o-mini"),
                api_token=params.get("llm_api_token", None),
                instruction=params.get("extract_instruction",
                                        "提取页面中所有大学名称、所在地、类型、层次信息"),
                schema=params.get("extract_schema", None),
                chunk_token_threshold=params.get("chunk_token_threshold", 4000),
            )

        elif extract_type == "json":
            from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
            schema = params.get("extract_schema")

            if not schema:
                # 通用 schema：提取所有表格行
                schema = {
                    "name": "Table",
                    "baseSelector": "table tr",
                    "fields": [
                        {"name": "cols", "selector": "td",
                         "type": "list", "fields": [
                             {"name": "text", "type": "text"}
                         ]}
                    ]
                }
            return JsonCssExtractionStrategy(schema, verbose=False)

        elif extract_type == "css":
            from crawl4ai.extraction_strategy import CosineStrategy
            return CosineStrategy(
                semantic_filter=params.get("semantic_filter", ""),
                word_count_threshold=params.get("word_count_threshold", 10),
            )

        return None  # 不提取，返回完整内容

    # ── 内部分析器 ─────────────────────────────────────────

    def _parse_extracted(self, extracted: Any, data_type: str) -> list:
        """解析 LLM / JSON 提取的结果"""
        if isinstance(extracted, list):
            return extracted  # LLM 提取的已经是结构化数据
        if isinstance(extracted, str):
            try:
                import json
                return json.loads(extracted)
            except json.JSONDecodeError:
                return [{"raw": extracted}]
        return [extracted]

    def _parse_universities_from_md(self, markdown: str, html: str) -> list[University]:
        """从 Markdown 表格解析大学信息"""
        results = []
        # 尝试解析 Markdown 表格
        for table_block in markdown.split("\n\n"):
            if "|" not in table_block:
                continue
            lines = table_block.strip().split("\n")
            if len(lines) < 3:
                continue
            for line in lines[2:]:  # 跳表头 + 分隔行
                cols = [c.strip() for c in line.split("|") if c.strip()]
                if len(cols) >= 2:
                    results.append(University(
                        name=cols[0] if len(cols) > 0 else "",
                        province=cols[1] if len(cols) > 1 else "",
                        source=self.name,
                    ))
        return results

    def _parse_scorelines_from_md(self, markdown: str, html: str) -> list[ScoreLine]:
        """从 Markdown 表格解析分数线"""
        results = []
        for table_block in markdown.split("\n\n"):
            if "|" not in table_block:
                continue
            lines = table_block.strip().split("\n")
            if len(lines) < 3:
                continue
            for line in lines[2:]:
                cols = [c.strip() for c in line.split("|") if c.strip()]
                if len(cols) >= 4:
                    try:
                        score = int(cols[3].replace("分", ""))
                    except (ValueError, IndexError):
                        score = None
                    results.append(ScoreLine(
                        university_name=cols[0] if len(cols) > 0 else "",
                        province=cols[1] if len(cols) > 1 else "",
                        year=2024,
                        batch=cols[2] if len(cols) > 2 else "",
                        min_score=score,
                        source=self.name,
                    ))
        return results

    def close(self):
        """清理（异步清理需要在事件循环中完成）"""
        pass  # crawler 在每次 crawl 后自动关闭
