# -*- coding: utf-8 -*-
from scrapy import signals
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import pymongo
from items import MmItemLoader, MmItem


class MmjpgSpider(CrawlSpider):
    name = 'mmjpg'
    allowed_domains = ['www.mmjpg.com']
    start_urls = ['http://www.mmjpg.com/']
    _follow_links = True
    crawler = None

    custom_settings = {
        'ITEM_PIPELINES': {'sfish.pipelines.MmPipeline': 300},
        # 'MONGO_HOST': "127.0.0.1",  # 主机IP
        # 'MONGO_PORT': 27017,  # 端口号
        # 'MONGO_DB': "mm",  # 库名
        # 'MONGO_COLL': "mmjpg"# collection名
        # MONGO_USER = "zhangsan"
        # MONGO_PSW = "123456"
    }

    rules = (
        Rule(LinkExtractor(allow=r'mm/\d{1,4}$'), callback='parse_mm', follow=True),
    )

    def __init__(self, crawler):
        self.crawler = crawler
        # settings = crawler.settings
        # self.client = pymongo.MongoClient(host=settings["MONGO_HOST"], port=settings["MONGO_PORT"])
        # # 数据库登录需要帐号密码的话
        # # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        # self.db = self.client[settings["MONGO_DB"]]
        # self.coll = self.db[settings["MONGO_COLL"]]

        super(MmjpgSpider, self).__init__()

    def parse_start_url(self, response):
        from utils.mm_label import get_mm_label
        get_mm_label()

    def parse_mm(self, response):
        loader = MmItemLoader(item=MmItem(), response=response)
        loader.add_css("title", ".article h2::text")
        loader.add_css("seen_num", ".info i::text")
        loader.add_css("fav_num", "#like::text")
        loader.add_css("first_image_url", ".content a img::attr(src)")
        loader.add_css("_id", ".content a img::attr(src)")
        loader.add_css("order", ".content a img::attr(src)")
        loader.add_css("total_num", ".page a::text")
        loader.add_css("tags", ".tags a::text")

        mm_item = loader.load_item()
        yield mm_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)

