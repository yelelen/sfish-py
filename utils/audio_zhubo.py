import requests
from scrapy import Selector

from models.AudioZhubo import AudioZhubo

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}


AudioZhubo.init()


def get_zhubos(zhubo_id):
    search = AudioZhubo.search()
    try:
        # http: // www.ximalaya.com / zhubo / 1266964 /
        url = r'http://www.ximalaya.com/zhubo/{0}/'.format(zhubo_id)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            z = AudioZhubo()
            sel = Selector(r)
            z['az_order'] = zhubo_id
            z.meta.id = z['az_order']
            z['az_portrait'] = sel.css('.pic.mgtb-20 img::attr(src)').extract()[0]
            z['az_nickname'] = sel.css('.txt-lg5 span::text').extract()[0]
            z['az_brief'] = sel.css('.elli.mgtb-10 span::attr(title)').extract()[0]
            ls = sel.css('.btn2.mgr-20 span::text').extract()
            z['az_fans_count'] = int(ls[0])
            z['az_follow_count'] = int(ls[1])
            z['az_love_count'] = int(ls[2])
            z['az_sounds_count'] = int(sel.css('.mgtb-20 .btn2 span::text').extract()[3])

            rs = search.query('term', az_order=zhubo_id).execute()
            if len(rs) <= 0:
                z.save()
            else:
                z.update(az_follow_count=z['az_follow_count'],
                         az_fans_count=z['az_fans_count'],
                         az_love_count=z['az_love_count'],
                         az_sounds_count=z['az_sounds_count'])
    except Exception as e:
        print(e.__cause__)


if __name__ == '__main__':
    get_zhubos(1266964)

