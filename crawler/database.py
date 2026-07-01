"""数据库操作层 —— 去重、批量插入、session 复用"""
import logging
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import config
from .models import ScoreLine, University

logger = logging.getLogger(__name__)

# ── SQLAlchemy 模型定义（建表用） ──────────────────────────────────
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# 注意：这些 Column 定义仅用于 create_all，不用于查询（查询走 raw SQL）
def _build_orm_classes():
    from sqlalchemy import Column, Integer, String, Float, Text

    class _University(Base):
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
        city = Column(String)
        school_nature = Column(String)
        belong = Column(String)
        is_985 = Column(Integer)
        is_211 = Column(Integer)
        is_dual_class = Column(Integer)
        create_year = Column(Integer)
        area = Column(Integer)
        ruanke_rank = Column(Integer)
        qs_rank = Column(Integer)
        xyh_rank = Column(Integer)
        num_master = Column(Integer)
        num_doctor = Column(Integer)
        num_academician = Column(Integer)
        recommend_master_rate = Column(String)
        gaokao_cn_id = Column(String)

    class _ScoreLine(Base):
        __tablename__ = "scorelines"
        id = Column(Integer, primary_key=True)
        university_name = Column(String)
        province = Column(String)
        year = Column(Integer)
        batch = Column(String)
        min_score = Column(Integer)
        avg_score = Column(Integer)
        max_score = Column(Integer)
        min_rank = Column(Integer)
        major_name = Column(String)
        source = Column(String)
        subject = Column(String)
        enrollment_type = Column(String)

    class _ScoreDistribution(Base):
        __tablename__ = "score_distribution"
        id = Column(Integer, primary_key=True)
        province = Column(String)
        year = Column(Integer)
        subject = Column(String)
        level = Column(String)
        score = Column(Integer)
        cumulative_rank = Column(Integer)
        count = Column(Integer)
        source = Column(String)

    return _University, _ScoreLine, _ScoreDistribution


UniversityTable, ScoreLineTable, ScoreDistTable = _build_orm_classes()


def migrate_schema(engine):
    """给已有表添加新列（如果不存在）"""
    with engine.connect() as conn:
        # universities 表新列
        univ_cols = [
            ("city", "TEXT"), ("school_nature", "TEXT"), ("belong", "TEXT"),
            ("is_985", "INTEGER"), ("is_211", "INTEGER"), ("is_dual_class", "INTEGER"),
            ("create_year", "INTEGER"), ("area", "INTEGER"),
            ("ruanke_rank", "INTEGER"), ("qs_rank", "INTEGER"), ("xyh_rank", "INTEGER"),
            ("num_master", "INTEGER"), ("num_doctor", "INTEGER"), ("num_academician", "INTEGER"),
            ("recommend_master_rate", "TEXT"), ("gaokao_cn_id", "TEXT"),
        ]
        for col, typ in univ_cols:
            try:
                conn.execute(text(f"ALTER TABLE universities ADD COLUMN {col} {typ}"))
            except Exception:
                pass  # 列已存在

        # scorelines 表新列
        score_cols = [("subject", "TEXT"), ("enrollment_type", "TEXT")]
        for col, typ in score_cols:
            try:
                conn.execute(text(f"ALTER TABLE scorelines ADD COLUMN {col} {typ}"))
            except Exception:
                pass
        conn.commit()


class Database:
    """数据库操作封装：去重、批量写入、连接复用"""

    def __init__(self, db_path: str = "data/db/gaokao.db"):
        if db_path == ":memory:":
            url = "sqlite://"
        else:
            url = f"sqlite:///{db_path}"
        self.engine = create_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
            pool_size=1,            # SQLite 单连接即可
        )
        Base.metadata.create_all(self.engine)
        migrate_schema(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self):
        """上下文管理器，自动 commit / rollback / close"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── 大学 ──────────────────────────────────────────────

    def upsert_universities(self, universities: list[University]) -> int:
        """批量 upsert 大学（按 name 去重，新值覆盖旧值）"""
        if not universities:
            return 0
        with self.session_scope() as sess:
            count = 0
            for u in universities:
                existing = sess.query(UniversityTable).filter_by(name=u.name).first()
                if existing:
                    existing.code = u.code or existing.code
                    existing.province = u.province or existing.province
                    existing.type = u.type or existing.type
                    existing.level = u.level or existing.level
                    existing.features = ",".join(u.features) if u.features else existing.features
                    existing.website = u.website or existing.website
                    existing.satisfaction_score = u.satisfaction_score or existing.satisfaction_score
                    existing.source = u.source or existing.source
                    if u.city: existing.city = u.city
                    if u.school_nature: existing.school_nature = u.school_nature
                    if u.belong: existing.belong = u.belong
                    if u.is_985 is not None: existing.is_985 = u.is_985
                    if u.is_211 is not None: existing.is_211 = u.is_211
                    if u.is_dual_class is not None: existing.is_dual_class = u.is_dual_class
                    if u.create_year: existing.create_year = u.create_year
                    if u.area: existing.area = u.area
                    if u.ruanke_rank: existing.ruanke_rank = u.ruanke_rank
                    if u.qs_rank: existing.qs_rank = u.qs_rank
                    if u.xyh_rank: existing.xyh_rank = u.xyh_rank
                    if u.num_master: existing.num_master = u.num_master
                    if u.num_doctor: existing.num_doctor = u.num_doctor
                    if u.num_academician: existing.num_academician = u.num_academician
                    if u.recommend_master_rate: existing.recommend_master_rate = u.recommend_master_rate
                    if u.gaokao_cn_id: existing.gaokao_cn_id = u.gaokao_cn_id
                else:
                    sess.add(UniversityTable(
                        name=u.name, code=u.code, province=u.province,
                        type=u.type, level=u.level,
                        features=",".join(u.features) if u.features else "",
                        website=u.website, satisfaction_score=u.satisfaction_score,
                        source=u.source, city=u.city, school_nature=u.school_nature,
                        belong=u.belong, is_985=u.is_985, is_211=u.is_211,
                        is_dual_class=u.is_dual_class, create_year=u.create_year,
                        area=u.area, ruanke_rank=u.ruanke_rank, qs_rank=u.qs_rank,
                        xyh_rank=u.xyh_rank, num_master=u.num_master,
                        num_doctor=u.num_doctor, num_academician=u.num_academician,
                        recommend_master_rate=u.recommend_master_rate,
                        gaokao_cn_id=u.gaokao_cn_id,
                    ))
                count += 1
            return count

    def get_university(self, name: str) -> Optional[University]:
        with self.session_scope() as sess:
            row = sess.query(UniversityTable).filter_by(name=name).first()
            if not row:
                return None
            return University(
                name=row.name, code=row.code or "", province=row.province or "",
                type=row.type or "", level=row.level or "",
                features=row.features.split(",") if row.features else [],
                website=row.website, satisfaction_score=row.satisfaction_score,
                source=row.source or "", city=row.city or "",
                school_nature=row.school_nature or "", belong=row.belong or "",
                is_985=row.is_985, is_211=row.is_211, is_dual_class=row.is_dual_class,
                create_year=row.create_year, area=row.area,
                ruanke_rank=row.ruanke_rank, qs_rank=row.qs_rank, xyh_rank=row.xyh_rank,
                num_master=row.num_master, num_doctor=row.num_doctor,
                num_academician=row.num_academician,
                recommend_master_rate=row.recommend_master_rate or "",
                gaokao_cn_id=row.gaokao_cn_id or "",
            )

    # ── 分数线 ────────────────────────────────────────────

    # 去重键：(university_name, province, year, batch, major_name, source)
    _SCORELINE_INSERT_SQL = text("""
        INSERT OR IGNORE INTO scorelines
            (university_name, province, year, batch, min_score, avg_score,
             max_score, min_rank, major_name, source, subject, enrollment_type)
        VALUES
            (:university_name, :province, :year, :batch, :min_score, :avg_score,
             :max_score, :min_rank, :major_name, :source, :subject, :enrollment_type)
    """)

    def insert_scorelines_batch(self, lines: list[ScoreLine]) -> int:
        """批量插入分数线，按 (校名+省+年+批次+专业+来源) 去重"""
        if not lines:
            return 0
        with self.session_scope() as sess:
            rows = [
                {
                    "university_name": sl.university_name,
                    "province": sl.province,
                    "year": sl.year,
                    "batch": sl.batch or "",
                    "min_score": sl.min_score,
                    "avg_score": sl.avg_score,
                    "max_score": sl.max_score,
                    "min_rank": sl.min_rank,
                    "major_name": sl.major_name or "",
                    "source": sl.source or "",
                    "subject": sl.subject or "",
                    "enrollment_type": sl.enrollment_type or "",
                }
                for sl in lines
            ]
            result = sess.execute(self._SCORELINE_INSERT_SQL, rows)
            return result.rowcount

    def insert_scoreline(self, line: ScoreLine) -> int:
        """插入单条分数线（去重）"""
        return self.insert_scorelines_batch([line])

    def get_scorelines(self, university_name: str, province: str = "",
                       year: int = None) -> list[ScoreLine]:
        with self.session_scope() as sess:
            q = sess.query(ScoreLineTable).filter_by(university_name=university_name)
            if province:
                q = q.filter_by(province=province)
            if year:
                q = q.filter_by(year=year)
            return [
                ScoreLine(
                    university_name=r.university_name, province=r.province,
                    year=r.year, batch=r.batch or "",
                    min_score=r.min_score, avg_score=r.avg_score,
                    max_score=r.max_score, min_rank=r.min_rank,
                    major_name=r.major_name, source=r.source or "",
                )
                for r in q.all()
            ]

    # ── 通用查询 ──────────────────────────────────────────

    def count(self, table: str) -> int:
        with self.session_scope() as sess:
            return sess.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()


# ── 兼容旧接口 ──────────────────────────────────────────────
# 保留 insert_university / insert_scoreline 的单条方法，内部调用批量版

Database.insert_university = lambda self, u: Database.upsert_universities(self, [u])
