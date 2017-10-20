import json

import requests

from models.AudioSound import AudioSound

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
}

AudioSound.init()


def get_sounds(sound_nums):
    search = AudioSound.search()
    for num in sound_nums:
        print('get sound track ---> ' + str(num))

        r = requests.get(r"http://www.ximalaya.com/tracks/{0}.json".format(num), headers=headers)
        if r.status_code == 200:
            item = AudioSound()
            src = json.loads(r.text, encoding='utf-8')
            item['as_order'] = num
            item.meta.id = item['as_order']
            item['as_album_id'] = src['album_id']
            item['as_album_title'] = src['album_title']
            item['as_title'] = src['title']
            item['as_duration'] = src['duration']
            item['as_favorites_count'] = src['favorites_count']
            item['as_formatted_created_at'] = src['formatted_created_at']
            paths = src['play_path'] + ',' + src['play_path_32'] + ',' + src['play_path_64']
            item['as_play_paths'] = paths
            item['as_zhubo_id'] = src['uid']
            item['as_intro'] = src['intro']
            item['as_play_count'] = src['play_count']

        try:
            rs = search.query('term', as_order=num).execute()
            if len(rs) <= 0:
                item.save()
            else:
                item.update(as_favorites_count=item['as_favorites_count'], as_play_count=item['as_play_count'])
        except Exception as e:
            print(e.__cause__)


if __name__ == '__main__':
    get_sounds([46319254, 46319743, 46526731, 46527217, 46527620, 46527998, 46529013])
