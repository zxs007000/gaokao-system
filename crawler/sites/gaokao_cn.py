"""掌上高考爬虫 —— www.gaokao.cn（JSON API 直接获取）"""
import json
import logging
import time
from typing import Any
from urllib.request import urlopen, Request

from ..base import SpiderBase, retry_on_failure
from ..config import config
from ..models import University, ScoreLine

logger = logging.getLogger(__name__)

PROVINCE_MAP = {
    "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
    "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏",
    "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东",
    "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西",
    "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南",
    "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏",
    "65": "新疆",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def _fetch_json(url: str) -> dict:
    """直接 HTTP GET 获取 JSON"""
    req = Request(url, headers=HEADERS)
    resp = urlopen(req, timeout=30)
    return json.loads(resp.read())


class GaoKaoCnSpider(SpiderBase):
    name = "gaokao_cn"
    source = "www.gaokao.cn"
    data_types = ["院校列表", "院校详情", "分数线"]

    BASE_URL = "https://static-data.gaokao.cn/www/2.0"

    def crawl(self, params: dict[str, Any]) -> list[dict]:
        data_type = params.get("data_type", "院校列表")
        if data_type == "院校列表":
            return self._crawl_school_list()
        elif data_type == "院校详情":
            return self._crawl_school_detail(params)
        elif data_type == "分数线":
            return self._crawl_score_lines(params)
        else:
            self.logger.warning("不支持的数据类型: %s", data_type)
            return []

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_school_list(self) -> list[dict]:
        """批量获取2991所大学基础信息"""
        url = f"{self.BASE_URL}/school/list_v2.json?a=www.gaokao.cn"
        self.logger.info("获取掌上高考院校列表...")
        data = _fetch_json(url)
        schools = data.get("data", {})
        self.logger.info("获取到 %d 所大学", len(schools))
        return [{"school_list": schools, "data_type": "院校列表"}]

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_school_detail(self, params: dict) -> list[dict]:
        """获取单校详细信息"""
        school_id = params.get("school_id", "")
        if not school_id:
            return []
        url = f"{self.BASE_URL}/school/{school_id}/info.json?a=www.gaokao.cn"
        self.logger.info("获取院校详情 school_id=%s", school_id)
        data = _fetch_json(url)
        return [{"school_detail": data.get("data", {}), "school_id": school_id,
                 "data_type": "院校详情"}]

    @retry_on_failure(max_retries=3, base_delay=2)
    def _crawl_score_lines(self, params: dict) -> list[dict]:
        """获取某校各省份各年份最低分（使用 benchmarkScore API）"""
        school_id = params.get("school_id", "")
        school_name = params.get("school_name", "")
        if not school_id:
            return []
        url = f"{self.BASE_URL}/school/{school_id}/benchmarkScore.json?a=www.gaokao.cn"
        self.logger.info("获取分数线 school_id=%s", school_id)
        data = _fetch_json(url)
        return [{"benchmark_data": data.get("data", {}), "school_id": school_id,
                 "school_name": school_name, "data_type": "分数线"}]

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
            data_type = item.get("data_type", "")
            if data_type == "院校列表":
                all_results.extend(self._parse_school_list(item))
            elif data_type == "院校详情":
                all_results.extend(self._parse_school_detail(item))
            elif data_type == "分数线":
                all_results.extend(self._parse_score_lines(item))
        return all_results

    def _parse_school_list(self, item: dict) -> list[University]:
        """解析院校列表 → University 列表"""
        schools = item.get("school_list", {})
        results = []
        for school_id, info in schools.items():
            name = info.get("name", "")
            if not name:
                continue
            features = []
            if info.get("f985") == "1":
                features.append("985")
            if info.get("f211") == "1":
                features.append("211")
            if info.get("dual_class") == "1":
                features.append("双一流")

            results.append(University(
                name=name,
                code=school_id,
                province=info.get("p", ""),
                type=info.get("level", ""),
                level="本科" if info.get("level") == "普通本科" else info.get("level", ""),
                features=features,
                source=self.name,
                city=info.get("c", ""),
                school_nature=info.get("nature", ""),
                is_985=1 if info.get("f985") == "1" else 0,
                is_211=1 if info.get("f211") == "1" else 0,
                is_dual_class=1 if info.get("dual_class") == "1" else 0,
                gaokao_cn_id=school_id,
            ))
        return results

    def _parse_school_detail(self, item: dict) -> list[University]:
        """解析院校详情 → University（补充详细字段）"""
        detail = item.get("school_detail", {})
        if not detail:
            return []

        name = detail.get("name", "")
        if not name:
            return []

        features = []
        if detail.get("f985") == "1":
            features.append("985")
        if detail.get("f211") == "1":
            features.append("211")
        dual_name = detail.get("dual_class_name", "")
        if dual_name:
            features.append(dual_name)

        def safe_int(val):
            try:
                return int(val) if val and str(val) != "0" else None
            except (ValueError, TypeError):
                return None

        return [University(
            name=name,
            code=detail.get("data_code", ""),
            province=PROVINCE_MAP.get(detail.get("province_id", ""), ""),
            type=detail.get("type_name", ""),
            level=detail.get("level_name", ""),
            features=features,
            source=self.name,
            city="",
            school_nature=detail.get("school_nature_name", ""),
            belong=detail.get("belong", ""),
            is_985=1 if detail.get("f985") == "1" else 0,
            is_211=1 if detail.get("f211") == "1" else 0,
            is_dual_class=1 if detail.get("dual_class_name") else 0,
            create_year=safe_int(detail.get("create_date")),
            area=safe_int(detail.get("area")),
            ruanke_rank=safe_int(detail.get("ruanke_rank")),
            qs_rank=safe_int(detail.get("qs_rank")),
            xyh_rank=safe_int(detail.get("xyh_rank")),
            num_master=safe_int(detail.get("num_master")),
            num_doctor=safe_int(detail.get("num_doctor")),
            num_academician=safe_int(detail.get("num_academician")),
            recommend_master_rate=detail.get("recommend_master_rate", ""),
            gaokao_cn_id=item.get("school_id", ""),
        )]

    def _parse_score_lines(self, item: dict) -> list[ScoreLine]:
        """解析 benchmarkScore 数据 → ScoreLine 列表

        benchmark_data 格式: {"2025_11_3": 685, "2024_33_3": 700, ...}
        key = {year}_{province_id}_{type_id}
        type_id: 3=普通类本科批, 2073=普通类(新高考), 2074=物理类, 等
        """
        benchmark_data = item.get("benchmark_data", {})
        school_name = item.get("school_name", "")

        TYPE_MAP = {
            "3": "本科批", "2073": "本科批", "2074": "本科批",
            "6": "提前批", "7": "一批", "8": "二批",
            "14": "提前批", "36": "一批", "46": "一批",
            "51": "一批", "86": "一批",
        }

        results = []
        for key, score in benchmark_data.items():
            parts = key.split("_")
            if len(parts) < 3 or not score:
                continue
            year_str, prov_id, type_id = parts[0], parts[1], "_".join(parts[2:])
            try:
                year = int(year_str)
            except ValueError:
                continue
            province_name = PROVINCE_MAP.get(prov_id, "")
            batch = TYPE_MAP.get(type_id, f"类型{type_id}")

            results.append(ScoreLine(
                university_name=school_name,
                province=province_name,
                year=year,
                batch=batch,
                min_score=int(score) if score else None,
                source=self.name,
                subject="综合",
            ))
        return results

    @staticmethod
    def _safe_int(val) -> int | None:
        try:
            return int(val) if val else None
        except (ValueError, TypeError):
            return None
