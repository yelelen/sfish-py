import pymongo
from scrapy import signals, Selector, Request
from scrapy.spiders import CrawlSpider, Rule
from items import AudioAlbumLoader, AudioAlbumItem
from scrapy.linkextractors import LinkExtractor
import re
import requests
from models.AudioLabel import AudioLabel
from elasticsearch_dsl.connections import connections

connections.create_connection(AudioLabel._doc_type.using)


class AudioAlbumSpider(CrawlSpider):
    name = 'audio_album'
    start_urls = []
    _follow_links = True
    crawler = None
    allowed_domains = ['www.ximalaya.com']
    custom_settings = {
        # 'MONGO_HOST': "127.0.0.1",  # 主机IP
        # 'MONGO_PORT': 27017,  # 端口号
        # 'MONGO_DB': "audio",  # 库名
        # 'MONGO_COLL_ABLUM': "album",
        # 'MONGO_COLL_ZHUBO': "zhubo",
        # 'MONGO_COLL_SOUND': "sound",
        # 'MONGO_COLL_LABEL': "label",
        # 'MONGO_COLL_ZHUBO_NUM': "zhubo_num",
        # 'MONGO_COLL_SOUND_NUM': "sound_num",
        'ITEM_PIPELINES': {'sfish.pipelines.AudioAlbumPipeline': 101},
        # 'DEFAULT_REQUEST_HEADERS': {
        # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        #
        # }
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
    }

    rules = (
        Rule(LinkExtractor(allow=r'/\d+/album/\d+/', tags='a', attrs='href', unique=True), follow=False,
             callback='parse_album'),
    )

    def __init__(self, crawler):
        from utils.audio_label import get_label
        get_label()

        # self.settings = crawler.settings
        # self.client = pymongo.MongoClient(host=self.settings["MONGO_HOST"], port=self.settings["MONGO_PORT"])
        # # 数据库登录需要帐号密码的话
        # # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        # self.db = self.client[self.settings["MONGO_DB"]]
        # self.coll_label = self.db[self.settings["MONGO_COLL_LABEL"]]
        # self.coll_zhubo = self.db[self.settings["MONGO_COLL_ZHUBO"]]
        # self.coll_sound = self.db[self.settings["MONGO_COLL_SOUND"]]
        # self.coll_zhubo_num = self.db[self.settings["MONGO_COLL_ZHUBO_NUM"]]
        # self.coll_sound_num = self.db[self.settings["MONGO_COLL_SOUND_NUM"]]
        # self.label_lists = list(self.coll_label.find())
        # self.label_lists = list(self.coll_label.find({"_id": {"$gt": 466, "$lt": 469}}))
        # self.coll_album = self.db['album' + str(self.label_lists[0]['_id'])]

        self.crawler = crawler
        self.search = AudioLabel.search()
        self.label_index = 0
        self.label_lists = list(self.search.params(_source=True, size=500).execute())
        self.label_lists = [x.to_dict() for x in self.label_lists]

        self.label_count = self.label_lists.__len__()
        self.start_urls.append(self.label_lists[0]['url'])

        self.page_item_count = 0
        self.page = 1
        self.pages = 0
        self.page_album_count = 12
        self.first_page_url = ''
        self.last_page_album_count = 0

        super(AudioAlbumSpider, self).__init__()


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def parse_start_url(self, response):
        print('parse_start_url --------> ' + response.url)
        self.page = 1
        self.first_page_url = response.url

        sel = Selector(response=response)
        ls = sel.css('.pagingBar_page::text').extract()
        if '下一页' in ls:
            self.pages = int(ls[-2])
            r = requests.get(self.first_page_url + str(self.pages), headers=self.headers)
            if r.status_code == 200:
                sel = Selector(r)
                self.last_page_album_count = sel.css('.discoverAlbum_item').extract().__len__()
            self.page_album_count = 12
        else:
            self.pages = 1
            r = requests.get(self.first_page_url, headers=self.headers)
            sel = Selector(r)
            self.page_album_count = sel.css('.discoverAlbum_item').extract().__len__()

    def spider_closed(self, spider, reason):
        # self.client.close()
        print('spider closed!!!!!!!!!!!!!!' + reason)

    def parse_album(self, response):
        if re.match(r'^http://m.ximalaya.com/.*', response.url):
            return
        loader = AudioAlbumLoader(item=AudioAlbumItem(), response=response)
        loader.add_value('order', self.get_album_id(response.url))
        loader.add_value('zhubo_id', self.get_album_zhubo(response.url))
        loader.add_css('cover', '.albumface180 span img::attr(popsrc)')
        loader.add_css('title', '.detailContent_title h1::text')
        loader.add_value('tag', self.get_album_tags(response))
        loader.add_css('last_update', '.mgr-5::text')
        loader.add_css('play_count', '.detailContent_playcountDetail span::text')
        loader.add_css('desc', '.mid_intro article p::text')
        loader.add_value('sounds', self.get_sounds_id(response))

        item = loader.load_item()
        yield item

        self.page_item_count += 1
        if self.page_item_count >= self.page_album_count:
            self.page_item_count = 0
            if self.page < self.pages:
                self.page += 1
                if self.page == self.pages:
                    self.page_album_count = self.last_page_album_count
                next_url = self.first_page_url + str(self.page)
                print('next_page_url -------------------> ' + next_url)
                yield Request(next_url, callback=self.parse_page)
            else:
                self.label_index += 1
                if self.label_index < self.label_count:
                    # self.coll_album = self.db['album' + str((self.label_lists[self.label_index]['_id']))]
                    yield Request(self.label_lists[self.label_index]['url'], callback=self.parse)
                    print('go to label -------------------> ' + self.label_lists[self.label_index]['name'])
                else:
                    from utils.audio import audio_main
                    audio_main()

    def parse_page(self, response):
        return self._parse_response(response, callback=None, cb_kwargs={}, follow=True)

    def get_album_id(self, value):
        # http: // www.ximalaya.com / 56582073 / album / 6628920 /
        match = re.match(r'.*/album/(\d+)/.*', value)
        if match:
            return match.group(1)

    def get_album_zhubo(self, value):
        # http: // www.ximalaya.com / 56582073 / album / 6628920 /
        match = re.match(r'.*com/(\d+)/album/.*', value)
        if match:
            return match.group(1)

    def get_sounds_id(self, value):
        page = 1
        s = Selector(response=value)
        ids = s.css('.personal_body::attr(sound_ids)').extract()[0]
        next_pages = s.css('.pagingBar_page::text').extract()
        while '下一页' in next_pages:
            page += 1
            url = value.url.replace('?order=desc', '')
            next_url = url + '?page={}'.format(page)
            r = requests.get(next_url, headers=self.headers)
            s2 = Selector(text=r.text)
            next_pages = s2.css('.pagingBar_page::text').extract()
            ids = ids + ',' + s2.css('.personal_body::attr(sound_ids)').extract()[0]

        return ids

    def get_album_tags(self, response):
        s = Selector(response=response)
        tag = s.css('.detailContent_category a::text').extract()[0][1:-1]
        tags = s.css('.tagBtn2 span::text').extract()
        ts = ''
        if tags:
            for x in tags:
                ts += x + ' '
        return ts + tag
