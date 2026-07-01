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
