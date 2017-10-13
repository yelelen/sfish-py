import requests
from scrapy import Selector
import pymongo
from items import BookChapterItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "book",  # 库名
    'MONGO_COLL': "book_chapter",
    'MONGO_COLL_TEXT_NUM': "book_text_num",
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
coll_num = db[settings["MONGO_COLL_TEXT_NUM"]]

base_url = 'https://read.qidian.com/chapter/'


def get_chapter():
    print('-----------------get_chapter--------------------')

    chapter_ids = list(coll_num.find())
    for chapter_id in chapter_ids:
        url = base_url + chapter_id["_id"]
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sel = Selector(r)
            item = BookChapterItem()
            item["_id"] = chapter_id["_id"]
            item["title"] = sel.css('.j_chapterName::text').extract()[0]
            item["book_id"] = int(sel.css('.info.fl a::attr(data-bid)').extract()[0])
            item["author_id"] = int(sel.css('.info.fl a::attr(data-auid)').extract()[0])
            item["book_name"] = sel.css('.info.fl a::text').extract()[0]
            item["author_name"] = sel.css('.info.fl a::text').extract()[1]
            item["text_count"] = str(sel.css('.j_chapterWordCut::text').extract()[0]) + sel.css('.info.fl i::text').extract()[0]
            item["update_time"] = sel.css('.j_updateTime::text').extract()[0]
            item["texts"] = sel.css('.read-content.j_readContent p::text').extract()

            try:
                if not coll.find_one({"_id": item["_id"]}):
                    coll.insert_one(item)
                    print('insert chapter ----> ' + item["title"])
            except Exception as e:
                print(e.__cause__)
                pass

        else:
            continue
    client.close()


if __name__ == "__main__":
    get_chapter()