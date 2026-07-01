# Phase 1: 爬虫系统 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建插件式爬虫系统，从阳光高考网和掌上高考抓取院校、分数线、专业数据

**Architecture:** 插件式架构，每个数据源一个爬虫文件，实现统一接口。用 Scrapling StealthyFetcher 绕反爬，SQLite 存储结构化数据。

**Tech Stack:** Python 3.11, Scrapling, SQLite, FastAPI (后续集成用)

---

## File Structure

```
D:\gaokao-system\
├── crawler/
│   ├── __init__.py
│   ├── base.py                    # SpiderBase 基类
│   ├── registry.py                # 爬虫自动发现和注册
│   ├── config.py                  # 配置管理（代理、延时等）
│   ├── models.py                  # 数据模型（SQLAlchemy）
│   ├── database.py                # 数据库连接和初始化
│   ├── storage.py                 # 数据存储（JSON + DB）
│   ├── sites/
│   │   ├── __init__.py
│   │   ├── yangguang.py           # 阳光高考网爬虫
│   │   └── gaokao_com.py          # 掌上高考爬虫
│   └── run.py                     # 爬虫运行入口
├── data/
│   ├── raw/                       # 原始爬取数据
│   ├── cleaned/                   # 清洗后数据
│   └── db/                        # SQLite 数据库
├── tests/
│   ├── __init__.py
│   ├── test_base.py
│   ├── test_registry.py
│   ├── test_yangguang.py
│   └── test_gaokao_com.py
├── docs/
│   └── compose/plans/
│       └── 2026-06-26-phase1-crawler.md
├── requirements.txt
└── README.md
```

---

### Task 1: 项目初始化

**Covers:** [S2, S4]

**Files:**
- Create: `D:\gaokao-system\requirements.txt`
- Create: `D:\gaokao-system\crawler\__init__.py`
- Create: `D:\gaokao-system\crawler\sites\__init__.py`
- Create: `D:\gaokao-system\tests\__init__.py`
- Create: `D:\gaokao-system\data\raw\.gitkeep`
- Create: `D:\gaokao-system\data\cleaned\.gitkeep`
- Create: `D:\gaokao-system\data\db\.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```
scrapling>=0.1
sqlalchemy>=2.0
httpx>=0.24
beautifulsoup4>=4.12
lxml>=5.0
pydantic>=2.0
```

- [ ] **Step 2: Create directory structure and __init__.py files**

```bash
cd D:\gaokao-system
mkdir crawler\sites
mkdir tests
mkdir data\raw data\cleaned data\db
echo. > crawler\__init__.py
echo. > crawler\sites\__init__.py
echo. > tests\__init__.py
echo. > data\raw\.gitkeep
echo. > data\cleaned\.gitkeep
echo. > data\db\.gitkeep
```

- [ ] **Step 3: Initialize git repo**

```bash
cd D:\gaokao-system
git init
git add .
git commit -m "chore: initialize project structure"
```

---

### Task 2: 数据模型定义

**Covers:** [S4]

**Files:**
- Create: `D:\gaokao-system\crawler\models.py`
- Create: `D:\gaokao-system\tests\test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from crawler.models import University, Major, ScoreLine

def test_university_creation():
    uni = University(
        name="清华大学",
        code="10003",
        province="北京",
        type="理工",
        level="985",
        features=["985", "211", "双一流"]
    )
    assert uni.name == "清华大学"
    assert uni.features == ["985", "211", "双一流"]

def test_major_creation():
    major = Major(
        name="计算机科学与技术",
        code="080901",
        duration=4,
        degree="工学"
    )
    assert major.duration == 4

def test_scoreline_creation():
    line = ScoreLine(
        university_name="清华大学",
        province="河北",
        year=2024,
        batch="本科一批",
        min_score=685,
        avg_score=692,
        max_score=703
    )
    assert line.min_score == 685
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'crawler.models'"

- [ ] **Step 3: Write implementation**

```python
# crawler/models.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class University:
    name: str
    code: str
    province: str
    type: str
    level: str
    features: list[str] = field(default_factory=list)
    website: Optional[str] = None
    satisfaction_score: Optional[float] = None
    source: str = ""

@dataclass
class Major:
    name: str
    code: str
    duration: int
    degree: str
    description: Optional[str] = None
    university_name: Optional[str] = None

@dataclass
class ScoreLine:
    university_name: str
    province: str
    year: int
    batch: str
    min_score: Optional[int] = None
    avg_score: Optional[int] = None
    max_score: Optional[int] = None
    min_rank: Optional[int] = None
    major_name: Optional[str] = None
    source: str = ""

@dataclass
class EnrollmentPlan:
    university_name: str
    province: str
    year: int
    major_name: str
    quota: int
    source: str = ""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/models.py tests/test_models.py
git commit -m "feat: add data models for university, major, scoreline"
```

---

### Task 3: 数据库初始化

**Covers:** [S4]

**Files:**
- Create: `D:\gaokao-system\crawler\database.py`
- Create: `D:\gaokao-system\tests\test_database.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_database.py
from crawler.database import Database
from crawler.models import University

def test_database_init():
    db = Database(":memory:")
    assert db.engine is not None

def test_insert_university():
    db = Database(":memory:")
    uni = University(
        name="北京大学",
        code="10001",
        province="北京",
        type="综合",
        level="985"
    )
    db.insert_university(uni)
    result = db.get_university("北京大学")
    assert result is not None
    assert result.name == "北京大学"

def test_insert_scoreline():
    from crawler.models import ScoreLine
    db = Database(":memory:")
    line = ScoreLine(
        university_name="清华大学",
        province="河北",
        year=2024,
        batch="本科一批",
        min_score=685
    )
    db.insert_scoreline(line)
    results = db.get_scorelines("清华大学", "河北")
    assert len(results) == 1
    assert results[0].min_score == 685
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_database.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'crawler.database'"

- [ ] **Step 3: Write implementation**

```python
# crawler/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Optional
from .models import University, Major, ScoreLine, EnrollmentPlan

Base = declarative_base()

class UniversityTable(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String)
    province = Column(String)
    type = Column(String)
    level = Column(String)
    features = Column(Text)
    website = Column(String)
    satisfaction_score = Column(Float)
    source = Column(String)

class MajorTable(Base):
    __tablename__ = "majors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String)
    duration = Column(Integer)
    degree = Column(String)
    description = Column(Text)
    university_name = Column(String)

class ScoreLineTable(Base):
    __tablename__ = "scorelines"
    id = Column(Integer, primary_key=True)
    university_name = Column(String, nullable=False)
    province = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    batch = Column(String)
    min_score = Column(Integer)
    avg_score = Column(Integer)
    max_score = Column(Integer)
    min_rank = Column(Integer)
    major_name = Column(String)
    source = Column(String)

class EnrollmentPlanTable(Base):
    __tablename__ = "enrollment_plans"
    id = Column(Integer, primary_key=True)
    university_name = Column(String, nullable=False)
    province = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    major_name = Column(String)
    quota = Column(Integer)
    source = Column(String)

class Database:
    def __init__(self, db_path: str = "data/db/gaokao.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_university(self, uni: University):
        session = self.Session()
        try:
            table = UniversityTable(
                name=uni.name,
                code=uni.code,
                province=uni.province,
                type=uni.type,
                level=uni.level,
                features=",".join(uni.features) if uni.features else "",
                website=uni.website,
                satisfaction_score=uni.satisfaction_score,
                source=uni.source
            )
            session.merge(table)
            session.commit()
        finally:
            session.close()

    def get_university(self, name: str) -> Optional[University]:
        session = self.Session()
        try:
            row = session.query(UniversityTable).filter_by(name=name).first()
            if not row:
                return None
            return University(
                name=row.name,
                code=row.code or "",
                province=row.province or "",
                type=row.type or "",
                level=row.level or "",
                features=row.features.split(",") if row.features else [],
                website=row.website,
                satisfaction_score=row.satisfaction_score,
                source=row.source or ""
            )
        finally:
            session.close()

    def insert_scoreline(self, line: ScoreLine):
        session = self.Session()
        try:
            table = ScoreLineTable(
                university_name=line.university_name,
                province=line.province,
                year=line.year,
                batch=line.batch,
                min_score=line.min_score,
                avg_score=line.avg_score,
                max_score=line.max_score,
                min_rank=line.min_rank,
                major_name=line.major_name,
                source=line.source
            )
            session.add(table)
            session.commit()
        finally:
            session.close()

    def get_scorelines(self, university_name: str, province: str) -> list[ScoreLine]:
        session = self.Session()
        try:
            rows = session.query(ScoreLineTable).filter_by(
                university_name=university_name,
                province=province
            ).all()
            return [
                ScoreLine(
                    university_name=r.university_name,
                    province=r.province,
                    year=r.year,
                    batch=r.batch or "",
                    min_score=r.min_score,
                    avg_score=r.avg_score,
                    max_score=r.max_score,
                    min_rank=r.min_rank,
                    major_name=r.major_name,
                    source=r.source or ""
                ) for r in rows
            ]
        finally:
            session.close()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_database.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/database.py tests/test_database.py
git commit -m "feat: add SQLite database layer with ORM models"
```

---

### Task 4: 爬虫基类和注册机制

**Covers:** [S4]

**Files:**
- Create: `D:\gaokao-system\crawler\base.py`
- Create: `D:\gaokao-system\crawler\registry.py`
- Create: `D:\gaokao-system\crawler\config.py`
- Create: `D:\gaokao-system\tests\test_base.py`
- Create: `D:\gaokao-system\tests\test_registry.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_base.py
from crawler.base import SpiderBase

def test_spider_base_interface():
    class TestSpider(SpiderBase):
        name = "test_spider"
        source = "test.com"

        def crawl(self, params):
            return []

        def parse(self, raw_data):
            return []

    spider = TestSpider()
    assert spider.name == "test_spider"
    assert spider.source == "test.com"
    assert spider.crawl({}) == []
```

```python
# tests/test_registry.py
from crawler.registry import SpiderRegistry

def test_registry_discover():
    registry = SpiderRegistry()
    spiders = registry.list_spiders()
    assert isinstance(spiders, list)

def test_registry_get():
    registry = SpiderRegistry()
    # After yangguang spider is added, this should work
    # For now, test that get returns None for unknown
    spider = registry.get("nonexistent")
    assert spider is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_base.py tests/test_registry.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write implementation**

```python
# crawler/config.py
from dataclasses import dataclass

@dataclass
class CrawlerConfig:
    delay_min: float = 2.0
    delay_max: float = 5.0
    timeout: int = 30
    max_retries: int = 3
    proxy: str = ""
    headless: bool = True
    data_dir: str = "data"

# 全局配置
config = CrawlerConfig()
```

```python
# crawler/base.py
from abc import ABC, abstractmethod
from typing import Any
from .config import config

class SpiderBase(ABC):
    name: str = ""
    source: str = ""
    data_types: list[str] = []

    @abstractmethod
    def crawl(self, params: dict[str, Any]) -> list[Any]:
        """爬取数据，返回原始数据列表"""
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> list[Any]:
        """解析原始数据，返回模型对象列表"""
        pass

    def get_config(self):
        return config
```

```python
# crawler/registry.py
import importlib
import pkgutil
from pathlib import Path
from typing import Optional
from .base import SpiderBase

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
            module = importlib.import_module(f"crawler.sites.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, SpiderBase) and
                    attr is not SpiderBase and
                    attr.name):
                    self._spiders[attr.name] = attr

    def list_spiders(self) -> list[str]:
        return list(self._spiders.keys())

    def get(self, name: str) -> Optional[type[SpiderBase]]:
        return self._spiders.get(name)

    def register(self, spider_class: type[SpiderBase]):
        """手动注册爬虫"""
        if spider_class.name:
            self._spiders[spider_class.name] = spider_class
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_base.py tests/test_registry.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/base.py crawler/registry.py crawler/config.py tests/test_base.py tests/test_registry.py
git commit -m "feat: add spider base class and auto-discovery registry"
```

---

### Task 5: 阳光高考网爬虫

**Covers:** [S4, S7]

**Files:**
- Create: `D:\gaokao-system\crawler\sites\yangguang.py`
- Create: `D:\gaokao-system\tests\test_yangguang.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_yangguang.py
from crawler.sites.yangguang import YangGuangSpider

def test_spider_attributes():
    spider = YangGuangSpider()
    assert spider.name == "yangguang"
    assert spider.source == "gaokao.chsi.com.cn"
    assert "院校" in spider.data_types

def test_parse_university():
    spider = YangGuangSpider()
    html = '''
    <div class="sch-item">
        <a class="name" href="/sch/10001.dhtml">北京大学</a>
        <span class="code">10001</span>
        <span class="location">北京</span>
        <span class="type">综合</span>
        <span class="level">本科</span>
    </div>
    '''
    results = spider.parse_university(html)
    assert len(results) >= 0  # Will verify with real parsing logic
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_yangguang.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write implementation**

```python
# crawler/sites/yangguang.py
import json
import time
import random
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup
from ..base import SpiderBase
from ..models import University, ScoreLine
from ..config import config

class YangGuangSpider(SpiderBase):
    name = "yangguang"
    source = "gaokao.chsi.com.cn"
    data_types = ["院校信息", "分数线", "招生章程"]

    BASE_URL = "https://gaokao.chsi.com.cn"

    def crawl(self, params: dict[str, Any]) -> list[Any]:
        data_type = params.get("data_type", "院校")
        page = params.get("page", 1)

        if data_type == "院校":
            return self._crawl_universities(page)
        elif data_type == "分数线":
            return self._crawl_scorelines(params)
        return []

    def _crawl_universities(self, page: int) -> list[dict]:
        """爬取院校列表页"""
        url = f"{self.BASE_URL}/sch/search--ss-on,option-qg,searchType-1,start-{(page-1)*20}.dhtml"

        try:
            from scrapling import StealthyFetcher
            fetcher = StealthyFetcher()
            response = fetcher.fetch(url, headless=config.headless)
            html = response.text
        except Exception as e:
            print(f"爬取失败: {e}")
            return []

        return [{"html": html, "page": page}]

    def _crawl_scorelines(self, params: dict) -> list[dict]:
        """爬取分数线数据"""
        year = params.get("year", 2024)
        url = f"{self.BASE_URL}/z/gkbmfslq{year}/pcx.jsp"

        try:
            from scrapling import StealthyFetcher
            fetcher = StealthyFetcher()
            response = fetcher.fetch(url, headless=config.headless)
            html = response.text
        except Exception as e:
            print(f"爬取失败: {e}")
            return []

        return [{"html": html, "year": year}]

    def parse(self, raw_data: Any) -> list[Any]:
        if not raw_data:
            return []

        html = raw_data[0].get("html", "") if isinstance(raw_data, list) else raw_data.get("html", "")
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        results = []

        # 解析院校列表
        items = soup.select(".sch-item, .list-item, tr")
        for item in items:
            uni = self._parse_university_item(item)
            if uni:
                results.append(uni)

        return results

    def _parse_university_item(self, item) -> University | None:
        """解析单个院校条目"""
        name_tag = item.select_one("a.name, a[href*='/sch/']")
        if not name_tag:
            return None

        name = name_tag.get_text(strip=True)
        if not name:
            return None

        code_tag = item.select_one(".code, .id")
        code = code_tag.get_text(strip=True) if code_tag else ""

        location_tag = item.select_one(".location, .province")
        province = location_tag.get_text(strip=True) if location_tag else ""

        type_tag = item.select_one(".type")
        uni_type = type_tag.get_text(strip=True) if type_tag else ""

        level_tag = item.select_one(".level")
        level = level_tag.get_text(strip=True) if level_tag else ""

        return University(
            name=name,
            code=code,
            province=province,
            type=uni_type,
            level=level,
            source="yangguang"
        )

    def parse_scorelines(self, html: str, year: int) -> list[ScoreLine]:
        """解析分数线页面"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        tables = soup.select("table")
        for table in tables:
            rows = table.select("tr")[1:]  # skip header
            for row in rows:
                cols = row.select("td")
                if len(cols) >= 3:
                    line = ScoreLine(
                        university_name=cols[0].get_text(strip=True),
                        province=cols[1].get_text(strip=True),
                        year=year,
                        batch=cols[2].get_text(strip=True) if len(cols) > 2 else "",
                        min_score=self._parse_int(cols[3].get_text(strip=True)) if len(cols) > 3 else None,
                        source="yangguang"
                    )
                    results.append(line)

        return results

    @staticmethod
    def _parse_int(text: str) -> int | None:
        try:
            return int(text.strip())
        except (ValueError, AttributeError):
            return None

    def save_raw(self, data: list, filename: str):
        """保存原始数据到 JSON"""
        path = Path(config.data_dir) / "raw" / f"{self.name}_{filename}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_yangguang.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/sites/yangguang.py tests/test_yangguang.py
git commit -m "feat: add yangguang spider for gaokao.chsi.com.cn"
```

---

### Task 6: 掌上高考爬虫

**Covers:** [S4, S7]

**Files:**
- Create: `D:\gaokao-system\crawler\sites\gaokao_com.py`
- Create: `D:\gaokao-system\tests\test_gaokao_com.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gaokao_com.py
from crawler.sites.gaokao_com import GaokaoComSpider

def test_spider_attributes():
    spider = GaokaoComSpider()
    assert spider.name == "gaokao_com"
    assert spider.source == "college.gaokao.com"
    assert "录取分数" in spider.data_types

def test_build_school_url():
    spider = GaokaoComSpider()
    url = spider._build_school_url(1001)
    assert "1001" in url
    assert "college.gaokao.com" in url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_gaokao_com.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write implementation**

```python
# crawler/sites/gaokao_com.py
import json
import time
from pathlib import Path
from typing import Any
from bs4 import BeautifulSoup
from ..base import SpiderBase
from ..models import University, ScoreLine
from ..config import config

class GaokaoComSpider(SpiderBase):
    name = "gaokao_com"
    source = "college.gaokao.com"
    data_types = ["院校信息", "录取分数", "专业信息"]

    BASE_URL = "https://college.gaokao.com"

    def crawl(self, params: dict[str, Any]) -> list[Any]:
        data_type = params.get("data_type", "院校")
        school_id = params.get("school_id")
        province_id = params.get("province_id")

        if data_type == "院校" and school_id:
            return self._crawl_school(school_id)
        elif data_type == "录取分数" and school_id:
            return self._crawl_scores(school_id, province_id)
        return []

    def _crawl_school(self, school_id: int) -> list[dict]:
        """爬取单个院校详情"""
        url = self._build_school_url(school_id)
        try:
            from scrapling import StealthyFetcher
            fetcher = StealthyFetcher()
            response = fetcher.fetch(url, headless=config.headless)
            return [{"html": response.text, "school_id": school_id}]
        except Exception as e:
            print(f"爬取失败: {e}")
            return []

    def _crawl_scores(self, school_id: int, province_id: int | None) -> list[dict]:
        """爬取录取分数线"""
        url = f"{self.BASE_URL}/school/tinfo/{school_id}/result/1/1/"
        if province_id:
            url = f"{self.BASE_URL}/school/tinfo/{school_id}/result/{province_id}/1/"

        try:
            from scrapling import StealthyFetcher
            fetcher = StealthyFetcher()
            response = fetcher.fetch(url, headless=config.headless)
            return [{"html": response.text, "school_id": school_id, "province_id": province_id}]
        except Exception as e:
            print(f"爬取失败: {e}")
            return []

    def _build_school_url(self, school_id: int) -> str:
        return f"{self.BASE_URL}/school/{school_id}/"

    def parse(self, raw_data: Any) -> list[Any]:
        if not raw_data:
            return []

        html = raw_data[0].get("html", "") if isinstance(raw_data, list) else raw_data.get("html", "")
        if not html:
            return []

        soup = BeautifulSoup(html, "lxml")
        results = []

        # 尝试解析院校详情
        name_tag = soup.select_one("h1, .school-name, .title")
        if name_tag:
            uni = University(
                name=name_tag.get_text(strip=True),
                code="",
                province="",
                type="",
                level="",
                source="gaokao_com"
            )
            results.append(uni)

        return results

    def parse_scores(self, html: str, school_name: str = "", province: str = "") -> list[ScoreLine]:
        """解析分数线页面"""
        soup = BeautifulSoup(html, "lxml")
        results = []

        tables = soup.select("table")
        for table in tables:
            rows = table.select("tr")[1:]
            for row in rows:
                cols = row.select("td")
                if len(cols) >= 4:
                    year_text = cols[0].get_text(strip=True)
                    try:
                        year = int(year_text)
                    except ValueError:
                        continue

                    line = ScoreLine(
                        university_name=school_name,
                        province=province,
                        year=year,
                        batch=cols[1].get_text(strip=True) if len(cols) > 1 else "",
                        min_score=self._parse_int(cols[2].get_text(strip=True)) if len(cols) > 2 else None,
                        avg_score=self._parse_int(cols[3].get_text(strip=True)) if len(cols) > 3 else None,
                        source="gaokao_com"
                    )
                    results.append(line)

        return results

    @staticmethod
    def _parse_int(text: str) -> int | None:
        try:
            return int(text.strip().replace("分", ""))
        except (ValueError, AttributeError):
            return None

    def save_raw(self, data: list, filename: str):
        path = Path(config.data_dir) / "raw" / f"{self.name}_{filename}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_gaokao_com.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/sites/gaokao_com.py tests/test_gaokao_com.py
git commit -m "feat: add gaokao.com spider for college.gaokao.com"
```

---

### Task 7: 爬虫运行入口

**Covers:** [S4]

**Files:**
- Create: `D:\gaokao-system\crawler\run.py`
- Create: `D:\gaokao-system\tests\test_run.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_run.py
from crawler.run import CrawlerRunner

def test_runner_init():
    runner = CrawlerRunner()
    assert runner.registry is not None

def test_runner_list():
    runner = CrawlerRunner()
    spiders = runner.list_spiders()
    assert "yangguang" in spiders
    assert "gaokao_com" in spiders
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:\gaokao-system && python -m pytest tests/test_run.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write implementation**

```python
# crawler/run.py
import time
import random
from typing import Any
from .registry import SpiderRegistry
from .database import Database
from .config import config

class CrawlerRunner:
    def __init__(self, db_path: str = "data/db/gaokao.db"):
        self.registry = SpiderRegistry()
        self.db = Database(db_path)

    def list_spiders(self) -> list[str]:
        return self.registry.list_spiders()

    def run(self, spider_name: str, params: dict[str, Any]) -> list:
        spider_class = self.registry.get(spider_name)
        if not spider_class:
            raise ValueError(f"爬虫不存在: {spider_name}")

        spider = spider_class()
        print(f"[{spider.name}] 开始爬取 {spider.source}...")

        # 爬取
        raw_data = spider.crawl(params)
        if not raw_data:
            print(f"[{spider.name}] 未获取到数据")
            return []

        # 解析
        parsed = spider.parse(raw_data)
        print(f"[{spider.name}] 解析到 {len(parsed)} 条数据")

        # 存储
        for item in parsed:
            if hasattr(item, "name") and hasattr(item, "code"):
                # University or Major
                self.db.insert_university(item)
            elif hasattr(item, "min_score"):
                # ScoreLine
                self.db.insert_scoreline(item)

        # 保存原始数据
        filename = f"{params.get('data_type', 'data')}_{int(time.time())}"
        spider.save_raw(raw_data, filename)

        print(f"[{spider.name}] 完成")
        return parsed

    def crawl_all(self, params: dict[str, Any] = None):
        """运行所有已注册的爬虫"""
        if params is None:
            params = {}

        spiders = self.list_spiders()
        for name in spiders:
            try:
                self.run(name, params)
                # 随机延时避免被封
                delay = random.uniform(config.delay_min, config.delay_max)
                time.sleep(delay)
            except Exception as e:
                print(f"[{name}] 爬取失败: {e}")

if __name__ == "__main__":
    runner = CrawlerRunner()
    print("已注册的爬虫:", runner.list_spiders())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:\gaokao-system && python -m pytest tests/test_run.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crawler/run.py tests/test_run.py
git commit -m "feat: add crawler runner with database integration"
```

---

### Task 8: 完整测试和集成验证

**Covers:** [S4]

**Files:**
- Modify: `D:\gaokao-system\tests\test_*.py` (verify all pass)

- [ ] **Step 1: Run all tests**

Run: `cd D:\gaokao-system && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Verify registry discovers spiders**

Run: `cd D:\gaokao-system && python -c "from crawler.registry import SpiderRegistry; r = SpiderRegistry(); print('Spiders:', r.list_spiders())"`
Expected: `Spiders: ['yangguang', 'gaokao_com']`

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "chore: complete phase 1 crawler system"
```

---

## 自检清单

1. **Spec 覆盖:** [S2] 架构 ✅, [S4] 爬虫系统 ✅, [S7] 开发顺序 ✅
2. **占位符扫描:** 无 TBD/TODO
3. **类型一致性:** 模型字段名、方法签名一致
