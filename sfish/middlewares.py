# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from scrapy.http import HtmlResponse

from utils.crawl_xici_ip import GetIp
import random


class LittlefishSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentMiddleware(object):
    def __init__(self, crawler):
        super(UserAgentMiddleware, self).__init__()
        self.settings = crawler.settings
        self.ua_list = self.settings['USER_AGENT']
        # self.ua = UserAgent()
        # self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    def process_request(self, request, spider):
        def get_ua():
            ua = random.choice(self.ua_list)
            return ua

        ua = get_ua()
        request.headers.setdefault("User-Agent", ua)
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


class ProxyIpMiddleware(object):
    def process_request(self, request, spider):
        # request.meta["proxy"] = GetIp().get_ip()
        pass


class FdsMiddleware(object):

    def process_request(self, request, spider):
        try:
            spider.browser.get(request.url)
        except Exception as e:
            # print(e.__cause__)
            pass
        # import time
        # time.sleep(10)
        print(spider.browser.page_source)
        print("url --> {0}".format(request.url))
        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8')


class BiliMovieMiddleware(object):

    def process_request(self, request, spider):
        try:
            url = request.url.replace('_escaped_fragment_=page%3D', '#!page=')
            spider.browser.get(url)
            # source = spider.browser.page_source
        except Exception as e:
            print(e.__cause__)
            pass
        print("url --> {0}".format(url))
        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8')
