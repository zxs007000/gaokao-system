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
