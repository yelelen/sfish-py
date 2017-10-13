import requests
from scrapy import Selector
import pymongo
import json
from items import AudioSoundItem

settings = {
    'MONGO_HOST': "127.0.0.1",  # 主机IP
    'MONGO_PORT': 27017,  # 端口号
    'MONGO_DB': "audio",  # 库名
    'MONGO_COLL': "sounds",
    'MONGO_COLL_SOUND_NUM': "sound_num",
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
coll_sound_num = db[settings["MONGO_COLL_SOUND_NUM"]]

def get_sounds():
    sound_nums = list(coll_sound_num.find())
    for num in sound_nums:
        print('get sound track ---> ' + str(num))
        r = requests.get(r"http://www.ximalaya.com/tracks/{0}.json".format(num['_id']), headers=headers)
        print(r.url)
        if r.status_code == 200:
            item = AudioSoundItem()
            src = json.loads(r.text, encoding='utf-8')
            item['_id'] = num['_id']
            item['album_id'] = src['album_id']
            item['album_title'] = src['album_title']
            item['title'] = src['title']
            item['duration'] = src['duration']
            item['favorites_count'] = src['favorites_count']
            item['formatted_created_at'] = src['formatted_created_at']
            item['is_favorited'] = src['is_favorited']
            paths = src['play_path'] + ',' + src['play_path_32'] + ',' + src['play_path_64']
            item['play_paths'] = paths.split(',')
            item['played_secs'] = src['played_secs']
            item['zhubo_id'] = src['uid']
            item['intro'] = src['intro']
            item['play_count'] = src['play_count']

            try:
                if not coll.find_one({"_id": num['_id']}):
                    coll.insert_one(item)
                else:
                    coll.update_one({"_id": num['_id']}, {"$set": {"favorites_count": item["favorites_count"],
                                                            "play_count": item["play_count"]}})

            except Exception as e:
                print(e.__cause__)
                pass
    client.close()


if __name__ == '__main__':
    get_sounds()

