from scrapy import Selector
import requests
from models.mm_label import MMLabel

url = "http://www.mmjpg.com/more/"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

MMLabel.init()
search = MMLabel.search()


def get_mm_label():
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'  # 解决乱码问题
    index = 500
    if r.status_code == 200:
        sel = Selector(r)
        label_lists = sel.css('.tag ul li a').extract()
        for x in label_lists:
            s = Selector(text=x)
            item = MMLabel()
            item["mml_cover"] = s.css('a img::attr(src)').extract()[0]
            item["mml_label"] = s.css('a::text').extract()[0]
            item["mml_order"] = index
            item.meta.id = item['mml_order']
            print('get label ---> ' + item['mml_label'])

            try:
                rs = search.query("term", mml_order=item["mml_order"]).execute()
                if len(rs) <= 0:
                    item.save()
            except Exception as e:
                print(e.__cause__)
            index -= 1

if __name__ == "__main__":
    get_mm_label()

