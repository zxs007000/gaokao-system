from crawler.registry import SpiderRegistry


def test_registry_discover():
    registry = SpiderRegistry()
    spiders = registry.list_spiders()
    assert isinstance(spiders, list)


def test_registry_get():
    registry = SpiderRegistry()
    spider = registry.get("nonexistent")
    assert spider is None
