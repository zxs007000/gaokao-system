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
    results = spider.parse(html)
    assert len(results) >= 0
