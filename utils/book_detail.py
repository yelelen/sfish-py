import requests
from scrapy import Selector
import pymongo
from items import BookDetailItem, BookChapterIndexItem, BookVolumeItem, BookChapterNumItem, BookAuthorNumItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "book",  # 库名
    'MONGO_COLL_DETAIL_MAN': "book_detail_man",
    'MONGO_COLL_DETAIL_MM': "book_detail_mm",
    'MONGO_COLL_AUTHOR_NUM': "book_author_num",
    'MONGO_COLL_TEXt_NUM': "book_text_num",
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
coll_detail_man = db[settings["MONGO_COLL_DETAIL_MAN"]]
coll_detail_mm = db[settings["MONGO_COLL_DETAIL_MM"]]
coll_author_num = db[settings["MONGO_COLL_AUTHOR_NUM"]]
coll_text_num = db[settings["MONGO_COLL_TEXt_NUM"]]
coll_book_man_num = db[settings["MONGO_COLL_MAN"]]
coll_book_mm_num = db[settings["MONGO_COLL_MM"]]

base_url = 'https://book.qidian.com/info/'


def get_book_detail(is_man=True):
    print('-----------------get_book_num_detail--------------------')

    if not is_man:
        book_ids = list(coll_book_mm_num.find())
        coll_detail = coll_detail_mm
    else:
        book_ids = list(coll_book_man_num.find())
        coll_detail = coll_detail_man

    # book_man_ids = list(coll_book_man_num.find())
    # book_man_ids = [{"_id": 1005053013}]
    # book_mm_ids = list(coll_book_mm_num.find())
    book_chapters = []

    for man_id in book_ids:
        info_url = base_url + str(man_id["_id"])
        print('book info url ---> ' + info_url)
        r_info = requests.get(info_url, headers=headers)
        if r_info.status_code == 200:

            item = BookDetailItem()
            sel = Selector(r_info)
            item["_id"] = man_id
            item["cover"] = 'https:' + sel.css('#bookImg img::attr(src)').extract()[0]
            item["author_id"] = int(sel.css('.author-photo::attr(data-authorid)').extract()[0])
            item["ahthor_name"] = sel.css('.writer::text').extract()[0]
            item["book_status"] = sel.css('.tag span::text').extract()[0]
            item["type"] = sel.css('.tag a::text').extract()[0]
            item["subtype"] = sel.css('.tag a::text').extract()[1]
            num = sel.css('.book-info em::text').extract()[1]
            unit = sel.css('.book-info cite::text').extract()[0]
            item["text_count"] = str(num) + unit
            item["breif"] = sel.css('.book-intro p::text').extract()[0].replace('<br>', ',').strip()

            ch_url = info_url + "#Catalog"
            r_ch = requests.get(ch_url, headers=headers)
            s = Selector(r_ch)
            volumes = s.css('.volume').extract()
            vols = []
            for v in volumes:
                sv = Selector(text=v)
                v_item = BookVolumeItem()
                v_item["_id"] = int(sv.css('.subscri::attr(href)').extract()[0].split('/')[-1])
                v_item["book_id"] = man_id

                t = []
                t.append(sv.css('h3::text').extract()[-2].strip())
                t.append(sv.css('h3::text').extract()[-1])
                t.append(sv.css('h3 em::text').extract()[1])
                t.append(sv.css('h3 em cite::text').extract()[0])
                t.append(sv.css('h3 em::text').extract()[-1])
                v_item["titles"] = t

                chapter_indexs = []
                for c in sv.css('ul li').extract():
                    sl = Selector(text=c)
                    ch_item = BookChapterIndexItem()
                    ch_item["order_id"] = int(sl.css('li::attr(data-rid)').extract()[0])
                    ls = sl.css('li a::attr(data-cid)').extract()[0].split("/")
                    ch_item["_id"] = ls[-2] + '/' + ls[-1]
                    chapter_item = BookChapterNumItem()
                    chapter_item["_id"] = ch_item["_id"]

                    chapter_indexs.append(ch_item)
                    book_chapters.append(chapter_item)

                v_item["chapters"] = chapter_indexs
                vols.append(v_item)
            item["volumes"] = vols

            # print(book_chapters)

            try:
                if not coll_detail.find_one({"_id": item["_id"]}):
                    coll_detail.insert_one(item)
                    if not coll_author_num.find_one({"_id": item["author_id"]}):
                        author_item = BookAuthorNumItem()
                        author_item["_id"] = item["author_id"]
                        coll_author_num.insert_one(author_item)
                        print('insert author -----> ' + str(item["author_id"]))

                    coll_text_num.insert(book_chapters)
                    book_chapters = []

                else:
                    coll_detail.update_one({"_id": item["_id"]}, {"$set": {"book_status": item["book_status"],
                                                                           "text_count": item["text_count"],
                                                                           "volumes": item["volumes"]}})
                    for chap in book_chapters:
                        if not coll_text_num.find_one({"_id": chap["_id"]}):
                            coll_text_num.insert_one(chap)

                    book_chapters = []
            except Exception as e:
                print(e.__cause__)
                pass
        else:
            continue
    client.close()

if __name__ == '__main__':
    get_book_detail(False)
