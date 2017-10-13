import requests
from scrapy import Selector
import pymongo
import json
from items import AudioZhuboItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "audio",  # 库名
    'MONGO_COLL': "zhubos",
    'MONGO_COLL_ZHUBO_NUM': "zhubo_num",
    # MONGO_USER = "zhangsan"
    # MONGO_PSW = "123456"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

client = pymongo.MongoClient(host=settings["MONGO_HOST"], port=settings["MONGO_PORT"])
# 数据库登录需要帐号密码的话
# self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
db = client[settings["MONGO_DB"]]
coll = db[settings["MONGO_COLL"]]
coll_zhubo_num = db[settings["MONGO_COLL_ZHUBO_NUM"]]

# _id = scrapy.Field()
# portrait = scrapy.Field()
# nackname = scrapy.Field()
# brief = scrapy.Field()
# fans_count = scrapy.Field()
# follow_count = scrapy.Field()
# sounds_count = scrapy.Field()


def get_zhubos():
    zhubos = list(coll_zhubo_num.find())
    for item in zhubos:
        # http: // www.ximalaya.com / zhubo / 1266964 /
        url = r'http://www.ximalaya.com/zhubo/{0}/'.format(item['_id'])
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            z = AudioZhuboItem()
            sel = Selector(r)
            z['_id'] = item['_id']
            z['portrait'] = sel.css('.pic.mgtb-20 img::attr(src)').extract()[0]
            z['nackname'] = sel.css('.txt-lg5 span::text').extract()[0]
            z['brief'] = sel.css('.elli.mgtb-10 span::attr(title)').extract()[0]
            ls = sel.css('.btn2.mgr-20 span::text').extract()
            z['fans_count'] = int(ls[0])
            z['follow_count'] = int(ls[1])
            z['love_count'] = int(ls[2])
            z['sounds_count'] = int(sel.css('.mgtb-20 .btn2 span::text').extract()[3])

            try:
                if not coll.find_one({"_id": z['_id']}):
                    coll.insert_one(z)
                else:
                    coll.update_one({"_id": z['_id']}, {"$set": {"fans_count": z["fans_count"],
                                                                   "follow_count": z["follow_count"],
                                                                 "sounds_count": z["sounds_count"],
                                                                 "love_count": z["love_count"]}})
                print('get zhubo -----------> ' + z['nackname'])
            except Exception as e:
                print(e.__cause__)
                pass
    client.close()

if __name__ == '__main__':
    get_zhubos()

