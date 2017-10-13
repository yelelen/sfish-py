import json
import os

import pymongo
from scrapy import Selector, signals, Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from items import BiliMovieItemLoader, MovieItem


class BiliMovieSpider(CrawlSpider):
    name = 'bili_movie_west'
    allowed_domains = ['www.bilibili.com']
    _follow_links = True
    crawler = None
    start_urls = ['http://www.bilibili.com/video/movie_west_1.html#!page=2']
    rules = (
        Rule(LinkExtractor(allow=r'/video/av\d{4,10}', tags='a', attrs='href', unique=True), follow=False,
             callback='parse_movie'),
    )

    custom_settings = {
        'ITEM_PIPELINES': {'sfish.pipelines.BiliMoviePipeline': 101},
        'DOWNLOADER_MIDDLEWARES': {'sfish.middlewares.BiliMovieMiddleware': 100},
        'MONGO_HOST': "127.0.0.1",  # 主机IP
        'MONGO_PORT': 27017,  # 端口号
        'MONGO_DB': "bili",  # 库名
        'MONGO_COLL': "movie_west",  # collection名
        'RETRY_ENABLED': False,
        'REDIRECT_ENABLED': False,
    }

    def __init__(self, crawler):
        self.crawler = crawler
        self.url = ""
        self.next_page = 1
        self.pages = 0
        self.count = 0
        self.is_first_page = True
        self.movie_size = 0

        self.settings = crawler.settings
        self.client = pymongo.MongoClient(host=self.settings["MONGO_HOST"], port=self.settings["MONGO_PORT"])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[self.settings["MONGO_DB"]]
        self.coll = self.db[self.settings["MONGO_COLL"]]

        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        headers = {
            'Referer': 'http://www.bilibili.com/'
        }
        for key, value in headers.items():
            self.dcap['phantomjs.page.customHeaders.{}'.format(key)] = value

        self.dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")  # 设置user-agent请求头
        self.dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片
        self.browser = webdriver.PhantomJS(
            executable_path='/home/yelelen/Software/phantomjs-2.1.1-linux-x86_64/bin/phantomjs',
            desired_capabilities=self.dcap)
        # self.browser.set_page_load_timeout(20)  # 设置页面最长加载时间为40s

        # display = Display(visible=False, size=(800, 600))
        # display.start()
        #
        # #设置chrome不加载图片
        # chrome_opt = webdriver.ChromeOptions()
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_opt.add_experimental_option('prefs', prefs)
        # self.browser = webdriver.Chrome(executable_path='/home/yelelen/Software/chromedriver', chrome_options=chrome_opt)

        super(BiliMovieSpider, self).__init__()
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # spider = super(BiliMovieSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def parse_movie(self, response):
        print(response.url)
        loader = BiliMovieItemLoader(item=MovieItem(), response=response)
        if 'movie' in response.url:
            loader.add_css("img", "body img::attr(src)")
            loader.add_css("_id", "body::attr(aid)")
            loader.add_css("like", "#order_count::text")
            loader.add_value("tag", self.get_movie_tag(response))
            loader.add_css("desc", ".info_msg::text")
            loader.add_value("time", self.get_movie_time(response))
            loader.add_css("title", ".info_head::text")
        else:
            loader.add_css("_id", ".appeal-gray::text")
            loader.add_css("like", "#stow_count::text")
            loader.add_css("img", ".cover_image::attr(src)")
            loader.add_css("tag", ".tag-area.clearfix .tag a::text")
            loader.add_css("desc", "#v_desc::text")
            loader.add_css("time", ".tminfo time i::text")
            loader.add_css("title", ".v-title h1::text")

        loader.add_value("url", self.get_url(response.url))
        loader.add_value("size", self.movie_size)
        loader.add_css("seen", "#dianji::text")
        item = loader.load_item()

        self.count += 1
        if self.count >= 20:
            self.count = 0
            if self.next_page <= self.pages:
                print("go to page %d" % self.next_page)
                yield Request('http://www.bilibili.com/video/movie_west_1.html#!page={0}'.format(self.next_page),
                              dont_filter=True)
        yield item

    def parse_start_url(self, response):
        s = Selector(response=response)
        self.next_page = s.css(".p.nextPage::attr(page)").extract()[0]
        print('self.next_page = ' + str(self.next_page))
        self.next_page = int(self.next_page)
        if self.is_first_page:
            self.pages = int(s.css(".p.endPage::text").extract()[0])
            self.is_first_page = False

    def spider_closed(self, spider, reason):
        self.browser.quit()
        self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)


    def get_url(self, url):
        urls = []
        size = 0
        try:
            res = os.popen("you-get --json " + url).read()
            stream = json.loads(res)['streams']
            if 'flv' in stream.keys():
                urls = json.loads(res)['streams']['flv']['src']
                size = json.loads(res)['streams']['flv']['size']
            elif 'mp4' in stream.keys():
                urls = json.loads(res)['streams']['mp4']['src']
                size = json.loads(res)['streams']['mp4']['size']
            self.movie_size = size
            return urls
        except:
            self.movie_size = 0

    def get_movie_tag(self, response):
        s = Selector(response=response)
        tag = s.css('.info_base span::text').extract()[0]
        return tag

    def get_movie_time(self, response):
        s = Selector(response=response)
        time = s.css('.info_base span::text').extract()[1]
        return time
