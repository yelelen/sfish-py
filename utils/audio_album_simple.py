import requests
from elasticsearch_dsl.connections import connections
from scrapy import Selector
from models.AudioAlbumSimple import AudioAlbumSimple

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

es = connections.create_connection(AudioAlbumSimple._doc_type.using)
AudioAlbumSimple.init()

def gen_suggest(index, text, weight, analyzer):
    used_words = set()
    suggests = []

    if text:
        words = es.indices.analyze(index=index, analyzer=analyzer,
                                        body={"text": text})
        analyzed_words = set([x["token"] for x in words["tokens"] if len(x["token"]) > 1])
        new_words = analyzed_words - used_words
        for item in new_words:
            used_words.add(item)
    else:
        new_words = set()
    if new_words:
        suggests.append({"input": list(new_words), "weight": weight})

    return suggests


def get_album_simple(page_url):
    search = AudioAlbumSimple.search()
    r = requests.get(page_url, headers=headers)
    s = Selector(r)

    items = []
    dicts = s.css('.discoverAlbum_item').extract()
    try:
        for x in dicts:
            item = AudioAlbumSimple()
            sel = Selector(text=x)
            item["aas_order"] = int(sel.css('.discoverAlbum_item::attr(album_id)').extract()[0])
            item["aas_cover"] = sel.css('.albumfaceOutter a span img::attr(src)').extract()[0]
            item["aas_title"] = sel.css('.albumfaceOutter a span img::attr(alt)').extract()[0]
            item["aas_play_count"] = int(sel.css('.sound_playcount::text').extract()[0])
            item["aas_suggest"] = gen_suggest(AudioAlbumSimple._doc_type.index, item["aas_title"], 10, analyzer="ik_max_word")
            items.append(item)

        for z in items:

                rs = search.query("term", aas_order=z["aas_order"]).execute()
                if len(rs) <= 0:
                    z.save()
                else:
                    z.update(aas_play_count=z["aas_play_count"])
    except Exception as e:
        print(e.__cause__)
    return items

if __name__ == '__main__':
    get_album_simple(page_url="http://www.ximalaya.com/dq/music-%E9%9F%B3%E4%B9%90%E5%B0%8F%E8%AE%B2%E5%A0%82/15")
