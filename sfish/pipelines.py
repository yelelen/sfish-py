# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from elasticsearch_dsl.connections import connections
from items import AnimeDetailItem, AnimeEpisodeItem, AudioSoundNumItem, AudioZhuboNumItem
from models.MM import MM
from models.AudioAlbum import AudioAlbum
from models.AudioSoundNum import AudioSoundNum
from models.AudioZhuboNum import AudioZhuboNum


class MmPipeline(object):
    def __init__(self):
        self.es = connections.create_connection(MM._doc_type.using)
        MM.init()
        self.s = MM.search()

    def process_item(self, item, spider):
        # post_item = dict(item)
        # count = spider.coll.find({"_id": post_item["_id"]}).count()
        # if count == 0:
        #     spider.coll.insert(post_item)
        # else:
        #     spider.coll.update_one({"title": post_item["title"]},
        #                            {"$set": {"fav_num": post_item["fav_num"], "seen_num": post_item["seen_num"]}})
        # return item

        try:
            rs = self.s.query("term", order=item["order"]).execute()
            if len(rs) > 0:
                mm = rs[0]
                mm.update(seen_num=item["seen_num"], fav_num=item["fav_num"])
            else:
                self.save_mm(item)
        except:
            self.save_mm(item)
        return item

    def save_mm(self, item):
        mm = MM()
        mm["title"] = item["title"]
        mm["seen_num"] = item["seen_num"]
        mm["fav_num"] = item["fav_num"]
        mm["first_image_url"] = item["first_image_url"]
        mm["order"] = item["order"]
        mm["total_num"] = item["total_num"]
        mm["tags"] = item["tags"]
        mm["suggest"] = self.gen_suggest(MM._doc_type.index, item["title"], 10, "ik_max_word") + self.gen_suggest(
            MM._doc_type.index, item["tags"], 7, "simple")
        mm.save()

    def gen_suggest(self, index, text, weight, analyzer):
        used_words = set()
        suggests = []

        if text:
            words = self.es.indices.analyze(index=index, analyzer=analyzer,
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

# ----------------------------------------------------------------------------------------------------------------------


class FdsPipeline(object):
    def process_item(self, item, spider):
        item = dict(item)
        count = spider.coll.find({"_id": item["_id"]}).count()
        if count == 0:
            spider.coll.insert_one(item)
        else:
            spider.coll.update_one({"_id": item["_id"]}, {"$set": {"seen": item["seen"], "like": item['like']}})
        return item

# ----------------------------------------------------------------------------------------------------------------------


class BiliMoviePipeline(object):
    def process_item(self, item, spider):
        item = dict(item)
        print(item.keys())
        try:
            if "url" not in item.keys():
                return None

            x = spider.coll.find_one({"_id": item["_id"]})
            if not x:
                spider.coll.insert_one(item)
            elif "url" in x.keys():
                if x["url"] == "":
                    spider.coll.update_one({"_id": item["_id"]}, {"$set": {"url": item["url"]}})
                    spider.coll.update_one({"_id": item["_id"]},
                                           {"$set": {"seen": item["seen"], "like": item['like']}})
        except Exception as e:
            print(e.__cause__)
            pass
        return item

# ----------------------------------------------------------------------------------------------------------------------


class BiliAnimePipeline(object):
    def process_item(self, item, spider):
        item = dict(item)
        try:
            count = spider.coll.find({"_id": item["_id"]}).count()
            if count == 0:
                spider.coll.insert_one(item)
            else:
                spider.coll.update_one({"_id": item["_id"]}, {"$set": {"favorites": item["favorites"],
                                                                       "is_finish": item["is_finish"],
                                                                       "newest_ep_index": item["newest_ep_index"],
                                                                       "season_status": item["season_status"],
                                                                       "update_time": item["update_time"]}})
        except:
            pass
        return item

# ----------------------------------------------------------------------------------------------------------------------


class BiliAnimeDetailPipeline(object):
    def process_item(self, item, spider):
        # item = dict(item)
        if isinstance(item, AnimeDetailItem):
            try:
                count = spider.coll_detail.find({"_id": item["_id"]}).count()
                if count == 0:
                    spider.coll_detail.insert_one(item)
                else:
                    spider.coll.update_one({"_id": item["_id"]}, {"$set": {"favorites": item["favorites"],
                                                                           "is_finish": item["is_finish"],
                                                                           "newest_ep_index": item["newest_ep_index"],
                                                                           "season_status": item["season_status"],
                                                                           "is_started": item["is_started"],
                                                                           "total_count": item["total_count"],
                                                                           "newest_ep_id": item["newest_ep_id"],
                                                                           "play_count": item["play_count"]}})
            except Exception as e:
                print(e.__cause__)
                pass
            return item
        elif isinstance(item, AnimeEpisodeItem):
            try:
                x = spider.coll_epi.find_one({"_id": item["_id"]})
                if not x:
                    spider.coll_epi.insert_one(item)
                elif x["url"] == '':
                    spider.coll_epi.update_one({"_id": item["_id"]}, {"$set": {"url": item["url"]}})
            except Exception as e:
                print(e.__cause__)
                pass
            return item

# ----------------------------------------------------------------------------------------------------------------------


class AudioAlbumPipeline(object):
    # def process_item(self, item, spider):
    #     if item is None:
    #         return None
    #     item = dict(item)
    #     print(item.keys())
    #     try:
    #         x = spider.coll_album.find_one({"_id": item["_id"]})
    #         if not x:
    #             spider.coll_album.insert_one(item)
    #             if not spider.coll_zhubo_num.find_one("_id", item["zhubo_id"]):
    #                 z = AudioZhuboNumItem()
    #                 z["_id"] = int(item["zhubo_id"])
    #                 spider.coll_zhubo_num.insert_one(z)
    #
    #             for sound_num in item['sounds'].split(','):
    #                 if not spider.coll_sound_num.find_one("_id", sound_num):
    #                     s = AudioSoundNumItem()
    #                     s["_id"] = int(sound_num)
    #                     spider.coll_sound_num.insert_one(s)
    #         else:
    #             spider.coll_album.update_one({"_id": item["_id"]}, {"$set": {"last_update": item["last_update"],
    #                                                                          "play_count": item["play_count"],
    #                                                                          "sounds": item["sounds"]}})
    #             for sound_num in item['sounds'].split(','):
    #                 if not spider.coll_sound_num.find_one({"_id": int(sound_num)}):
    #                     s = AudioSoundNumItem()
    #                     s["_id"] = int(sound_num)
    #                     spider.coll_sound_num.insert_one(s)
    #
    #     except Exception as e:
    #         print(e.__cause__)
    #         pass
    #     return item

    def __init__(self):
        self.es_album = connections.create_connection(AudioAlbum._doc_type.using)
        self.es_zhubo_num = connections.create_connection(AudioZhuboNum._doc_type.using)
        self.es_sound_num = connections.create_connection(AudioSoundNum._doc_type.using)
        AudioAlbum.init()
        AudioZhuboNum.init()
        AudioSoundNum.init()
        self.search_album = AudioAlbum.search()
        self.search_zhubo_num = AudioZhuboNum.search()
        self.search_sound_num = AudioSoundNum.search()

    def gen_suggest(self, index, text, weight, analyzer):
        used_words = set()
        suggests = []

        if text:
            words = self.es_album.indices.analyze(index=index, analyzer=analyzer,
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

    def process_item(self, item, spider):
        if item is None:
            return None
        item = dict(item)
        # print(item.keys())

        es_item = AudioAlbum()
        es_item["order"] = item["order"]
        es_item["zhubo_id"] = item["zhubo_id"]
        es_item["cover"] = item["cover"]
        es_item["title"] = item["title"]
        es_item["tag"] = item["tag"]
        es_item["last_update"] = item["last_update"]
        es_item["play_count"] = item["play_count"]
        es_item["desc"] = item.get("desc", '主播比较懒，还没有该专辑的相关描述哦')
        es_item["sounds"] = item["sounds"]
        es_item["suggest"] = self.gen_suggest(AudioAlbum._doc_type.index, item["title"], 10, analyzer="ik_max_word")\
                             + self.gen_suggest(AudioAlbum._doc_type.index, item["tag"], 7, analyzer="simple")

        try:
            rs = self.search_album.query("term", order=es_item["order"]).execute()
            if len(rs) <= 0:
                es_item.save()
                zhubos = self.search_zhubo_num.query("term", order=es_item["zhubo_id"]).execute()
                if len(zhubos) <= 0:
                    z = AudioZhuboNum()
                    z["order"] = int(es_item["zhubo_id"])
                    z.save()

                for sound_num in es_item['sounds'].split(','):
                    sound = self.search_sound_num.query("term", order=int(sound_num)).execute()
                    if len(sound) <= 0:
                        s = AudioSoundNum()
                        s["order"] = int(sound_num)
                        s.save()
            else:
                es_item.update(last_update=es_item["last_update"], play_count=es_item["play_count"], sounds=es_item["sounds"])
                for sound_num in es_item['sounds'].split(','):
                    sound = self.search_sound_num.query("term", order=int(sound_num)).execute()
                    if len(sound) <= 0:
                        s = AudioSoundNum()
                        s["order"] = int(sound_num)
                        s.save()
        except Exception as e:
            print(e.__cause__)


            pass
        return item
