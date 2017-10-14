import pymongo
import requests
from items import AudioLabelItem
from scrapy import Selector
from models.AudioLabel import AudioLabel
from elasticsearch_dsl.connections import connections



# settings = {
#     'MONGO_HOST': "127.0.0.1",  # 主机IP
#     'MONGO_PORT': 27017,  # 端口号
#     'MONGO_DB': "audio",  # 库名
#     'MONGO_COLL': "label",
#     # MONGO_USER = "zhangsan"
#     # MONGO_PSW = "123456"
# }

label_url = r'http://www.ximalaya.com/dq'
base_url = r'http://www.ximalaya.com'
#
# client = pymongo.MongoClient(host=settings["MONGO_HOST"], port=settings["MONGO_PORT"])
# # 数据库登录需要帐号密码的话
# # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
# db = client[settings["MONGO_DB"]]
# coll = db[settings["MONGO_COLL"]]

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

#
# def get_label():
#     r = requests.get(label_url, headers=headers)
#     # print(r.text)
#     s = Selector(r)
#
#     items = []
#     main_labels = s.css('.sort_list li').extract()
#     second_labels = s.css('.tag_wrap div').extract()
#
#     for x in main_labels:
#         item = AudioLabelItem()
#         sel = Selector(text=x)
#         item['order'] = int(sel.css('li::attr(cid)').extract()[0])
#         item['cid'] = item['order']
#         item['name'] = sel.css('li a::text').extract()[0]
#         item['url'] = base_url + sel.css('li a::attr(href)').extract()[0]
#         items.append(item)
#
#     count = 0
#     for y in second_labels:
#         sel1 = Selector(text=y)
#         alinks = sel1.css('div a').extract()
#         for z in alinks:
#             count += 1
#             sel2 = Selector(text=z)
#             item = AudioLabelItem()
#             item['order'] = count + 300
#             item['cid'] = int(sel1.css('div::attr(data-cache)').extract()[0])
#             item['name'] = sel2.css('a::attr(tid)').extract()[0]
#             item['url'] = base_url + sel2.css('a::attr(href)').extract()[0]
#             items.append(item)
#
#     for label in items:
#         has = coll.find_one({'order': label['order']})
#         if has is None:
#             coll.insert_one(label)
#             print('get label ----> ' + label['name'])
#         else:
#             pass
#     client.close()


def get_label():
    connections.create_connection(AudioLabel._doc_type.using)
    AudioLabel.init()
    search = AudioLabel.search()
    r = requests.get(label_url, headers=headers)
    s = Selector(r)

    items = []
    main_labels = s.css('.sort_list li').extract()
    second_labels = s.css('.tag_wrap div').extract()

    for x in main_labels:
        item = AudioLabel()
        sel = Selector(text=x)
        item['al_order'] = int(sel.css('li::attr(cid)').extract()[0])
        item['al_cid'] = item['al_order']
        item['al_name'] = sel.css('li a::text').extract()[0]
        item['al_url'] = base_url + sel.css('li a::attr(href)').extract()[0]
        items.append(item)
        print(item['al_name'])

    count = 0
    for y in second_labels:
        sel1 = Selector(text=y)
        alinks = sel1.css('div a').extract()
        for z in alinks:
            count += 1
            sel2 = Selector(text=z)
            item = AudioLabel()
            item['al_order'] = count + 300
            item['al_cid'] = int(sel1.css('div::attr(data-cache)').extract()[0])
            item['al_name'] = sel2.css('a::attr(tid)').extract()[0]
            item['al_url'] = base_url + sel2.css('a::attr(href)').extract()[0]
            items.append(item)
            print(item['al_name'])

    for label in items:
        try:
            rs = search.query("term", al_order=label["al_order"]).execute()
            if len(rs) <= 0:
                label.save()
        except Exception as e:
            print(e.__cause__)
            pass


if __name__ == '__main__':
    get_label()
