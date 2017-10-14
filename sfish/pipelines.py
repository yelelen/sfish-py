# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from elasticsearch_dsl.connections import connections

from items import AnimeDetailItem, AnimeEpisodeItem
from models.AudioAlbum import AudioAlbum
from models.MM import MM


class MmPipeline(object):
    def __init__(self):
        self.es = connections.create_connection(MM._doc_type.using)
        MM.init()
        self.search = MM.search()

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
            mm = MM()
            mm["mm_title"] = item["title"]
            mm["mm_seen_num"] = item["seen_num"]
            mm["mm_fav_num"] = item["fav_num"]
            mm["mm_first_image_url"] = item["first_image_url"]
            mm["mm_order"] = item["order"]
            mm["mm_total_num"] = item["total_num"]
            mm["mm_tags"] = item["tags"]
            mm["mm_suggest"] = self.gen_suggest(MM._doc_type.index, item["title"], 10,
                                                "ik_max_word") + self.gen_suggest(
                MM._doc_type.index, item["tags"], 7, "simple")

            rs = self.search.query("term", mm_order=mm["mm_order"]).execute()
            if len(rs) > 0:
                mm.update(mm_seen_num=mm["mm_seen_num"], mm_fav_num=mm["mm_fav_num"])
            else:
                mm.save()
        except Exception as e:
            print(e.__cause__)
        return item

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
        AudioAlbum.init()
        self.search_album = AudioAlbum.search()

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

        try:
            es_item = AudioAlbum()
            es_item["aa_order"] = item["order"]
            es_item["aa_zhubo_id"] = item["zhubo_id"]
            es_item["aa_cover"] = item["cover"]
            es_item["aa_title"] = item["title"]
            es_item["aa_tag"] = item["tag"]
            es_item["aa_last_update"] = item["last_update"]
            es_item["aa_play_count"] = item.get("play_count", "0")
            es_item["aa_desc"] = item.get("desc", '主播比较懒，还没有该专辑的相关描述哦')
            es_item["aa_sounds"] = item["sounds"]
            es_item["aa_suggest"] = self.gen_suggest(AudioAlbum._doc_type.index, item["title"], 10, analyzer="ik_max_word") \
                                 + self.gen_suggest(AudioAlbum._doc_type.index, item["tag"], 7, analyzer="simple")

            rs = self.search_album.query("term", aa_order=es_item["aa_order"]).execute()
            if len(rs) <= 0:
                es_item.save()
            else:
                es_item.update(aa_last_update=es_item["aa_last_update"], aa_play_count=es_item["aa_play_count"], aa_sounds=es_item["aa_sounds"])
        except Exception as e:
            print(e.__cause__)
        return item
