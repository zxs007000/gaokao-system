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
    city: str = ""
    school_nature: str = ""
    belong: str = ""
    is_985: Optional[int] = None
    is_211: Optional[int] = None
    is_dual_class: Optional[int] = None
    create_year: Optional[int] = None
    area: Optional[int] = None
    ruanke_rank: Optional[int] = None
    qs_rank: Optional[int] = None
    xyh_rank: Optional[int] = None
    num_master: Optional[int] = None
    num_doctor: Optional[int] = None
    num_academician: Optional[int] = None
    recommend_master_rate: str = ""
    gaokao_cn_id: str = ""

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
    subject: str = ""
    enrollment_type: str = ""

@dataclass
class EnrollmentPlan:
    university_name: str
    province: str
    year: int
    major_name: str
    quota: int
    source: str = ""

@dataclass
class EnrollmentPlanDetail:
    """详细招生计划 - 从Excel导入"""
    batch: str = ""
    enrollment_type: str = ""
    university_name: str = ""
    major_group_code: str = ""
    major_group_name: str = ""
    major_code: str = ""
    major_name: str = ""
    subject_requirement: str = ""
    notes: str = ""
    duration: str = ""
    tuition: str = ""
    school_nature: str = ""
    university_level: str = ""
    first_class_type: str = ""
    direct_department: str = ""
    province: str = ""
    city: str = ""
    city_nature: str = ""
    plan_2025: Optional[int] = None
    score_2024: Optional[int] = None
    rank_2024: Optional[int] = None
    score_2023: Optional[int] = None
    rank_2023: Optional[int] = None
    score_2022: Optional[int] = None
    rank_2022: Optional[int] = None
    discipline_evaluation: str = ""
    postgrad_recommend_rate: str = ""
    first_level_discipline: str = ""
    second_level_category: str = ""
    ranking_shanghai: str = ""
    ranking_summary: str = ""
    doctoral_programs: str = ""
    master_programs: str = ""
    school_type: str = ""
    source: str = "excel"
