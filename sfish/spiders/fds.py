# -*- coding: utf-8 -*-
from scrapy import Request, signals
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pymongo
from items import FdsItemLoader, FdsItem


#from selenium import webdriver
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class FdsSpider(CrawlSpider):
    name = 'fds'
    allowed_domains = ['www.feidieshuo.com']
    start_urls = ['http://www.feidieshuo.com']
    _follow_links = True
    crawler = None
    rules = (
        Rule(LinkExtractor(allow=(r'/media/play/\d{4}',), tags=('a', 'area'), attrs='href', unique=True, process_value='process_link'), follow=True, callback='parse_fds'),
    )

    custom_settings = {
        'ITEM_PIPELINES': {'sfish.pipelines.FdsPipeline': 101},
        # 'DOWNLOADER_MIDDLEWARES': {'sfish.middlewares.FdsMiddleware': 100}
        'MONGO_HOST': "127.0.0.1",  # 主机IP
        'MONGO_PORT': 27017,  # 端口号
        'MONGO_DB': "fds",  # 库名
        'MONGO_COLL': "fds"  # collection名
        # MONGO_USER = "zhangsan"
        # MONGO_PSW = "123456"

    }

    #def __init__(self, **kwargs):
        # self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        # self.dcap["phantomjs.page.settings.userAgent"] = (
        #     "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")  # 设置user-agent请求头
        # self.dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
        # self.browser = webdriver.PhantomJS(
        #     executable_path='/home/yelelen/Software/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
        #     desired_capabilities=self.dcap)
        # self.browser.set_page_load_timeout(20)  # 设置页面最长加载时间为40s
        #super(FdsSpider, self).__init__()
        #pass

    def __init__(self, crawler):
        self.crawler = crawler
        settings = crawler.settings
        self.client = pymongo.MongoClient(host=settings["MONGO_HOST"], port=settings["MONGO_PORT"])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[settings["MONGO_DB"]]
        self.coll = self.db[settings["MONGO_COLL"]]

        super(FdsSpider, self).__init__()


    def process_link(self, value):
        yield Request(url=self.start_urls + value, callback=self.parse_fds)

    def parse_start_url(self, response):
        from utils.book import book_main
        book_main()
        from utils.audio_label import get_label
        get_label()

    def parse_fds(self, response):
        loader = FdsItemLoader(item=FdsItem(), response=response)
        loader.add_css("_id", "#videoid::attr(value)")
        loader.add_css("channelid", "#channelid::attr(value)")
        loader.add_css("title", ".t-word-text h3::text")
        loader.add_css("desc", ".word-content p::text")
        loader.add_css("like", ".t-word-text-right a span::text")
        loader.add_css("url", ".player-video-left script::text")
        loader.add_css("seen", ".mr-1-5::text")
        item = loader.load_item()

        return item


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)
