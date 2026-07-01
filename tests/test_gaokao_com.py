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
