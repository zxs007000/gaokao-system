"""高考网爬虫 —— college.gaokao.com"""
from typing import Any

from bs4 import BeautifulSoup

from ..base import SpiderBase, retry_on_failure
from ..config import config
from ..models import University, ScoreLine


class GaokaoComSpider(SpiderBase):
    name = "gaokao_com"
    source = "college.gaokao.com"
    data_types = ["院校信息", "录取分数", "专业信息"]

    BASE_URL = "https://college.gaokao.com"

    def __init__(self):
        super().__init__()
        self._fetcher = None

    def _ensure_fetcher(self):
        if self._fetcher is None:
            from scrapling import StealthyFetcher
            self._fetcher = StealthyFetcher()
        return self._fetcher

    # ── crawl ──────────────────────────────────────────────

    def crawl(self, params: dict[str, Any]) -> list[dict]:
        data_type = params.get("data_type", "院校信息")
        school_id = params.get("school_id")
        province_id = params.get("province_id")

        if not school_id:
            return []

        if data_type == "院校信息":
            return self._crawl_school(school_id)
        elif data_type == "录取分数":
            return self._crawl_scores(school_id, province_id)
        else:
            self.logger.warning("不支持的数据类型: %s", data_type)
            return []

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_school(self, school_id: int) -> list[dict]:
        url = f"{self.BASE_URL}/school/{school_id}/"
        self.logger.info("爬取院校信息 school_id=%d", school_id)
        fetcher = self._ensure_fetcher()
        resp = fetcher.fetch(url, headless=config.headless)
        return [{"html": resp.text, "school_id": school_id, "data_type": "院校信息"}]

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_scores(self, school_id: int, province_id: int | None) -> list[dict]:
        url = f"{self.BASE_URL}/school/tinfo/{school_id}/result/"
        if province_id:
            url += f"{province_id}/"
        url += "1/"
        self.logger.info("爬取录取分数 school_id=%d province=%s", school_id, province_id)
        fetcher = self._ensure_fetcher()
        resp = fetcher.fetch(url, headless=config.headless)
        return [{"html": resp.text, "school_id": school_id,
                 "province_id": province_id, "data_type": "录取分数"}]

    # ── parse ──────────────────────────────────────────────

    def parse(self, raw_data: Any) -> list[Any]:
        if not raw_data:
            return []

        if isinstance(raw_data, list):
            item = raw_data[0] if raw_data else {}
        elif isinstance(raw_data, dict):
            item = raw_data
        else:
            return []

        html = item.get("html", "")
        data_type = item.get("data_type", "")
        if not html:
            return []

        if data_type == "录取分数":
            school_name = self._extract_school_name(html)
            province = ""  # TODO: 从 params 透传或从页面提取
            return self.parse_scores(html, school_name, province)
        else:
            return self._parse_school_info(html)

    def _parse_school_info(self, html: str) -> list:
        soup = BeautifulSoup(html, "lxml")
        name_tag = soup.select_one("h1, .school-name, .title")
        if not name_tag:
            return []
        name = name_tag.get_text(strip=True)

        # 尝试提取更多信息
        province = ""
        uni_type = ""
        info_items = soup.select(".info-item, .basic-info li, .school-info span")
        for item in info_items:
            text = item.get_text(strip=True)
            if "所在地" in text:
                province = text.replace("所在地：", "").replace("所在地", "").strip()
            elif "类型" in text or "层次" in text:
                uni_type = text.replace("类型：", "").replace("层次：", "").strip()

        return [University(
            name=name, code="", province=province,
            type=uni_type, level="", source=self.name,
        )]

    def parse_scores(self, html: str, school_name: str = "",
                     province: str = "") -> list[ScoreLine]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        for table in soup.select("table"):
            rows = table.select("tr")[1:]  # 跳表头
            for row in rows:
                cols = row.select("td")
                if len(cols) < 4:
                    continue
                year_text = cols[0].get_text(strip=True)
                try:
                    year = int(year_text)
                except ValueError:
                    continue
                results.append(ScoreLine(
                    university_name=school_name,
                    province=province,
                    year=year,
                    batch=cols[1].get_text(strip=True) if len(cols) > 1 else "",
                    min_score=self._parse_int(cols[2].get_text(strip=True)) if len(cols) > 2 else None,
                    avg_score=self._parse_int(cols[3].get_text(strip=True)) if len(cols) > 3 else None,
                    source=self.name,
                ))
        return results

    @staticmethod
    def _extract_school_name(html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        tag = soup.select_one("h1, .school-name, .title")
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _parse_int(text: str) -> int | None:
        try:
            return int(text.strip().replace("分", ""))
        except (ValueError, TypeError):
            return None
