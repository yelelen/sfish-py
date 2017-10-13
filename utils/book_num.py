import requests
from scrapy import Selector
import pymongo
from items import BookNumItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "book",  # 库名
    'MONGO_COLL_MAN': "book_num_man",
    'MONGO_COLL_MM': "book_num_mm",
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
coll_man = db[settings["MONGO_COLL_MAN"]]
coll_mm = db[settings["MONGO_COLL_MM"]]

man_url = 'https://www.qidian.com/free/all?orderId=&vip=hidden&style=1&pageSize=20&siteid=1&hiddenField=1&page='
mm_url = 'https://www.qidian.com/mm/free/all?orderId=&vip=hidden&style=1&pageSize=20&siteid=0&hiddenField=1&page='


def get_book_nums(url, coll):
    print('-----------------get_book_nums--------------------')

    page_index = 1
    has_next_page = True
    while has_next_page:
        print('go to page --> ' + str(page_index))
        next_url = url + str(page_index)
        print(next_url)
        r = requests.get(next_url, headers=headers)
        if r.status_code == 200:
            sel = Selector(r)
            book_nums = sel.css('.book-mid-info h4 a::attr(data-bid)').extract()
            for num in book_nums:
                item = BookNumItem()
                if not coll.find_one({"_id": int(num)}):
                    item['_id'] = int(num)
                    coll.insert_one(item)
                    print('insert book num ---> ' + num)
                else:
                    print('has book num ----> ' + num)
            next = sel.css('lbf-pagination-next.lbf-pagination-disabled').extract()
            if next:
                has_next_page = False
            else:
                page_index += 1
        else:
            page_index += 1
    client.close()


def get_book_nums_main():
    get_book_nums(man_url, coll_man)
    get_book_nums(mm_url, coll_mm)

if __name__ == '__main__':
    get_book_nums_main()
