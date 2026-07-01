"""阳光高考网爬虫 —— gaokao.chsi.com.cn（Scrapling DynamicFetcher）"""
import json
import random
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from ..base import SpiderBase, retry_on_failure
from ..config import config
from ..models import University, ScoreLine


class YangGuangSpider(SpiderBase):
    name = "yangguang"
    source = "gaokao.chsi.com.cn"
    data_types = ["院校库", "分数线", "招生计划"]

    BASE_URL = "https://gaokao.chsi.com.cn"

    def __init__(self):
        super().__init__()
        self._fetcher = None

    def _ensure_fetcher(self):
        """懒加载 Scrapling DynamicFetcher（Playwright 内核）"""
        if self._fetcher is None:
            from scrapling import DynamicFetcher
            self._fetcher = DynamicFetcher()
            self.logger.info("Scrapling DynamicFetcher 已就绪 (Playwright + Stealth)")
        return self._fetcher

    # ── crawl ──────────────────────────────────────────────

    def crawl(self, params: dict[str, Any]) -> list[dict]:
        data_type = params.get("data_type", "院校库")
        if data_type == "院校库":
            return self._crawl_universities(params)
        elif data_type == "分数线":
            return self._crawl_scorelines(params)
        else:
            self.logger.warning("不支持的数据类型: %s", data_type)
            return []

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_universities(self, params: dict) -> list[dict]:
        page = params.get("page", 1)
        start = 20 * (page - 1)
        url = f"{self.BASE_URL}/sch/search.do?start={start}" if start else \
              f"{self.BASE_URL}/sch/search.do"
        fetcher = self._ensure_fetcher()
        results = []

        resp = fetcher.fetch(url, headless=config.headless,
                             network_idle=True, wait=3,
                             timeout=60000)  # ms
        html = resp.html_content  # Scrapling Response 属性
        results.append({
            "html": html, "page": page,
            "data_type": "院校库",
        })

        # 分页逻辑（根据实际情况调整）
        soup = BeautifulSoup(html, "lxml")
        pagination = soup.select(".ch-page a")
        max_page = 1
        for link in pagination:
            try:
                n = int(link.get_text(strip=True))
                max_page = max(max_page, n)
            except ValueError:
                continue

        # 爬取后续页面
        for pg in range(page + 1, min(max_page + 1, page + 5)):
            self.rate_limit()
            try:
                resp = fetcher.fetch(
                    f"{self.BASE_URL}/sch/search.do?start={20 * (pg - 1)}",
                    headless=config.headless, network_idle=True, wait=3,
                    timeout=60000,
                )
                results.append({
                    "html": resp.html_content, "page": pg,
                    "data_type": "院校库",
                })
            except Exception as e:
                self.logger.error("第 %d 页爬取失败: %s", pg, e)

        return results

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_scorelines(self, params: dict) -> list[dict]:
        school_id = params.get("school_id", "")
        province_id = params.get("province_id", "")
        year = params.get("year", 2024)

        if not school_id:
            return []

        url = f"{self.BASE_URL}/sch/school/infoScore.do?schId={school_id}&provinceId={province_id}&year={year}"
        fetcher = self._ensure_fetcher()
        resp = fetcher.fetch(url, headless=config.headless,
                             network_idle=True, wait=3,
                             timeout=60000)
        return [{
            "html": resp.html_content, "school_id": school_id,
            "province_id": province_id, "year": year,
            "data_type": "分数线",
        }]

    # ── parse ──────────────────────────────────────────────

    def parse(self, raw_data: Any) -> list[Any]:
        if not raw_data:
            return []

        if isinstance(raw_data, list):
            items = raw_data
        elif isinstance(raw_data, dict):
            items = [raw_data]
        else:
            return []

        all_results = []
        for item in items:
            html = item.get("html", "")
            data_type = item.get("data_type", "")
            if not html:
                continue

            if data_type == "院校库":
                all_results.extend(self.parse_universities(html))
            elif data_type == "分数线":
                all_results.extend(self.parse_scorelines(html, item))
        return all_results

    # ── 大学解析 ───────────────────────────────────────────

    def parse_universities(self, html: str) -> list[University]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        for item in soup.select(".sch-item"):
            # 校名
            name_tag = item.select_one(".sch-title .name, .sch-name, .school-name")
            if not name_tag:
                name_tag = item.select_one("a")
            if not name_tag:
                continue
            name = name_tag.get_text(strip=True)
            if not name:
                continue

            # schId
            href = ""
            for a in item.select("a[href]"):
                if "schId" in a.get("href", ""):
                    href = a["href"]
                    break
            code = ""
            if href:
                import re
                m = re.search(r'schId[=_](\d+)', href)
                if m:
                    code = m.group(1)

            # 省份 + 主管部门
            province = ""
            belong = ""
            dept_tag = item.select_one(".sch-department")
            if dept_tag:
                dept_text = dept_tag.get_text(strip=True)
                parts = dept_text.split("|")
                if parts:
                    province = parts[0].strip()
                for part in parts:
                    if "主管部门" in part:
                        belong = part.replace("主管部门：", "").replace("主管部门:", "").strip()

            # 层次标签（本科/双一流/985/211）
            features = []
            level = ""
            for tag in item.select(".sch-level-tag"):
                text = tag.get_text(strip=True)
                if "本科" in text:
                    level = "本科"
                elif "专科" in text:
                    level = "专科"
                if "双一流" in text:
                    features.append("双一流")
                if "985" in text:
                    features.append("985")
                if "211" in text:
                    features.append("211")

            # 满意度评分
            satisfaction = None
            score_tag = item.select_one(".manyidu-star-box .num, .ivu-rate input[type=hidden]")
            if score_tag:
                val = score_tag.get("value") or score_tag.get_text(strip=True)
                try:
                    satisfaction = float(val)
                except (ValueError, TypeError):
                    pass

            results.append(University(
                name=name, code=code, province=province,
                type="", level=level, features=features,
                source=self.name, belong=belong,
                satisfaction_score=satisfaction,
            ))
        return results

    # ── 分数线解析 ─────────────────────────────────────────

    def parse_scorelines(self, html: str, meta: dict) -> list[ScoreLine]:
        soup = BeautifulSoup(html, "lxml")
        school_name = self._extract_school_name(soup)
        province = meta.get("province", "")
        year = meta.get("year", 0)

        results = []
        for table in soup.select("table"):
            rows = table.select("tr")[1:]  # 跳表头
            for row in rows:
                cols = row.select("td, th")
                if len(cols) < 4:
                    continue
                try:
                    score = int(cols[3].get_text(strip=True).replace("分", ""))
                except (ValueError, IndexError):
                    score = None
                results.append(ScoreLine(
                    university_name=school_name,
                    province=province,
                    year=year,
                    batch=cols[1].get_text(strip=True) if len(cols) > 1 else "",
                    min_score=score,
                    source=self.name,
                ))
        return results

    # ── 工具方法 ───────────────────────────────────────────

    @staticmethod
    def _extract_school_name(soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1, .school-name, .title, .sch-title")
        return tag.get_text(strip=True) if tag else ""

    def close(self):
        """释放 fetcher 资源"""
        self._fetcher = None
