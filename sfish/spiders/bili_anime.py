import pymongo
from scrapy import Spider, Request, signals
from items import AnimeItem
import json


class BiliAnimeSpider(Spider):
    name = 'bili_anime'
    page = 1
    pages = 0
    count = 0
    _follow_links = True
    crawler = None
    start_urls = [r'http://bangumi.bilibili.com/web_api/season/index_global?page=1&page_size=20&version=0&is_finish=0&start_year=0&tag_id=&index_type=1&index_sort=0&quarter=0']

    custom_settings = {
        'ITEM_PIPELINES': {'sfish.pipelines.BiliAnimePipeline': 101},
        'MONGO_HOST': "127.0.0.1",  # 主机IP
        'MONGO_PORT': 27017,  # 端口号
        'MONGO_DB': "bili",  # 库名
        'MONGO_COLL': "anime"  # collection名
        # MONGO_USER = "zhangsan"
        # MONGO_PSW = "123456"
        # 'MAX_PROC': 8,
        # 'MAX_PER_PROC': 2,
        # 'DOWNLOAD_DELAY': 5
    }

    def __init__(self, crawler):
        self.crawler = crawler
        settings = crawler.settings
        self.client = pymongo.MongoClient(host=settings["MONGO_HOST"], port=settings["MONGO_PORT"])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[settings["MONGO_DB"]]
        self.coll = self.db[settings["MONGO_COLL"]]

        super(BiliAnimeSpider, self).__init__()

    def parse(self, response):
        item = AnimeItem()
        text = response.text.replace('"code":0', '"code":"0"')
        src = json.loads(text)
        result = src['result']
        self.pages = int(result["pages"])
        self.count = int(result["count"])
        for x in result["list"]:
            item["_id"] = int(x["season_id"])
            item["cover"] = x["cover"]
            item["favorites"] = x["favorites"]
            item["is_finish"] = x["is_finish"]
            item["newest_ep_index"] = int(x["newest_ep_index"])
            item["pub_time"] = x["pub_time"]
            item["season_status"] = x["season_status"]
            item["title"] = x["title"]
            item["total_count"] = x["total_count"]
            item["update_time"] = x["update_time"]
            item["url"] = x["url"]
            item["week"] = x["week"]
            yield item

        self.page += 1
        if self.page <= self.pages:
            url = r'http://bangumi.bilibili.com/web_api/season/index_global?page={0}&page_size=20&version=0&is_finish=0&start_year=0&tag_id=&index_type=1&index_sort=0&quarter=0'.format(self.page)
            yield Request(url)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)


