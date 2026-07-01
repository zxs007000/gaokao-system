from crawler.run import CrawlerRunner

def test_runner_init():
    runner = CrawlerRunner()
    assert runner.registry is not None

def test_runner_list():
    runner = CrawlerRunner()
    spiders = runner.list_spiders()
    assert "yangguang" in spiders
    assert "gaokao_com" in spiders
