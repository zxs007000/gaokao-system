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
