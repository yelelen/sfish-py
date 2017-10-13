import requests
from scrapy import Selector
import pymongo
from items import BookAuthorItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "book",  # 库名
    'MONGO_COLL': "book_author",
    'MONGO_COLL_AUTHOR_NUM': "book_author_num",
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
coll_num = db[settings["MONGO_COLL_AUTHOR_NUM"]]

base_url = r'https://my.qidian.com/author/'


def get_author():
    print('-----------------get_author--------------------')
    author_ids = list(coll_num.find())

    for author_id in author_ids:
        url = base_url + str(author_id["_id"])
        print('get author url ---> ' + url)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sel = Selector(r)
            item = BookAuthorItem()
            item["_id"] = author_id["_id"]
            item["name"] = sel.css('.header-msg h3::text').extract()[0]
            item["cover"] = 'http:' + sel.css('.header-avatar-img::attr(src)').extract()[0]

            brief = sel.css('.header-msg-desc::text').extract()
            if brief:
                item["brief"] = brief[0]
            else:
                item["brief"] = ''

            nums = sel.css('.header-msg-strong::text').extract()
            item["book_count"] = int(nums[0])
            item["text_count"] = nums[1] + '万'
            item["write_days"] = int(nums[2])

            item["books"] = sel.css('.author-work .author-item .author-item-title a::attr(data-bid)').extract()

            try:
                if not coll.find_one({"_id": item["_id"]}):
                    coll.insert_one(item)
                    print('insert author ----> ' + item["name"])
                else:
                    coll.update_one({"_id": item["_id"]}, {"$set": {"book_count": item["book_count"],
                                                                    "text_count": item["text_count"],
                                                                    "write_days": item["write_days"],
                                                                    "books": item["books"]}})
                    print('update author ---> ' + item["name"])
            except Exception as e:
                print(e.__cause__)
                pass
        else:
            continue
    client.close()

if __name__ == '__main__':
    get_author()