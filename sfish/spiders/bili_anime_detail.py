import json
import os
import time

import pymongo
from scrapy import Spider, Request, signals

from items import AnimeDetailItem, AnimeEpisodeItem


class BiliAnimeDetailSpider(Spider):
    name = 'bili_anime_detail'
    _follow_links = True
    crawler = None
    start_urls = [
        r'http://bangumi.bilibili.com/web_api/season/index_global?page=1&page_size=20&version=0&is_finish=0&start_year=0&tag_id=&index_type=1&index_sort=0&quarter=0']

    custom_settings = {
        'ITEM_PIPELINES': {'sfish.pipelines.BiliAnimeDetailPipeline': 101},
        'MONGO_HOST': "127.0.0.1",  # 主机IP
        'MONGO_PORT': 27017,  # 端口号
        'MONGO_DB': "bili",  # 库名
        'MONGO_COLL': "anime",
        'MONGO_COLL_DETAIL': "anime_detail",
        'MONGO_COLL_EPI': "anime_epi",  # collection名
        'JOB_DIR': '/home/yelelen/bili_anime_detail.job'
        # MONGO_USER = "zhangsan"
        # MONGO_PSW = "123456"
        # 'MAX_PROC': 8,
        # 'MAX_PER_PROC': 2,
        # 'DOWNLOAD_DELAY': 5
    }

    def get_now_micro(self):
        return round(time.time() * 1000)

    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.client = pymongo.MongoClient(host=self.settings["MONGO_HOST"], port=self.settings["MONGO_PORT"])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[self.settings["MONGO_DB"]]
        self.coll = self.db[self.settings["MONGO_COLL"]]
        self.coll_detail = self.db[self.settings["MONGO_COLL_DETAIL"]]
        self.coll_epi = self.db[self.settings["MONGO_COLL_EPI"]]

        self.id_index = 1
        self.anime_id_list = [x.get("_id") for x in self.coll.find()]
        self.anime_id_list_len = len(self.anime_id_list)
        self.start_urls = [
            r'http://bangumi.bilibili.com/jsonp/seasoninfo/{0}.ver?callback=seasonListCallback&jsonp=jsonp&_={1}'.format(
                self.anime_id_list[self.id_index], self.get_now_micro())]
        super(BiliAnimeDetailSpider, self).__init__()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self, spider, reason):
        self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)

    def get_actor(self, value):
        s = ""
        for x in value:
            s += x["actor"] + " "
        return s

    def parse(self, response):
        anime_detail = AnimeDetailItem()
        anime_epi = AnimeEpisodeItem()
        text = response.text.replace('"code":0', '"code":"0"')
        text = text.replace("seasonListCallback(", "")
        text = text.replace(");", "")
        src = json.loads(text)
        result = src['result']

        anime_detail["_id"] = self.anime_id_list[self.id_index]
        anime_detail["actor"] = self.get_actor(result["actor"])
        anime_detail["alias"] = result["alias"]
        anime_detail["area"] = result["area"]
        anime_detail["bangumi_title"] = result["bangumi_title"]
        anime_detail["mid"] = int(result["episodes"][0]["mid"])
        anime_detail["evaluate"] = result["evaluate"]
        anime_detail["favorites"] = int(result["favorites"])
        anime_detail["is_finish"] = result['media']['publish']['is_finish']
        anime_detail["is_started"] = result['media']['publish']['is_started']
        anime_detail["newest_ep_id"] = int(result["newest_ep_id"])
        anime_detail["newest_ep_index"] = int(result["newest_ep_index"])
        anime_detail["pub_time"] = result["pub_time"]
        anime_detail["season_status"] = result["season_status"]
        anime_detail["play_count"] = int(result["play_count"])
        anime_detail["url"] = result["share_url"]
        anime_detail["total_count"] = int(result["total_count"])
        anime_detail["brief"] = result["brief"]
        anime_detail["cover"] = result["cover"]
        yield anime_detail

        epis = result["episodes"]
        for x in epis:
            anime_epi["_id"] = int(x["episode_id"])
            anime_epi["av_id"] = int(x["av_id"])
            anime_epi["cover"] = x["cover"]
            anime_epi["episode_status"] = x["episode_status"]
            anime_epi["index"] = int(x["index"])
            anime_epi["index_title"] = x["index_title"]
            if "is_new" in x:
                anime_epi["is_new"] = int(x["is_new"])
            else:
                anime_epi["is_new"] = 0
            anime_epi["mid"] = x["mid"]
            anime_epi["update_time"] = x["update_time"]
            play_url = x["webplay_url"]
            anime_epi["url"], anime_epi["size"] = self.get_epi_url(play_url)
            yield anime_epi

        self.id_index += 1
        if self.id_index < self.anime_id_list_len:
            self.next_url = r'http://bangumi.bilibili.com/jsonp/seasoninfo/{0}.ver?callback=seasonListCallback&jsonp=jsonp&_={1}'.format(
                self.anime_id_list[self.id_index], self.get_now_micro())
            yield Request(self.next_url)

    def get_epi_url(self, url):
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
            return urls, size
        except:
            self.movie_size = 0
