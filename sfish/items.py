# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst


class MmItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def get_fav_num(value):
    match = re.match(r".*?(\d+).*", value)
    return int(match.group(1))


def get_seen_num(value):
    seen_text = value[3]
    match = re.match(r".*?(\d+).*", seen_text)
    return int(match.group(1))


def get_order(value):
    match = re.match(r".*/\d{4}/(\d+)/.*", value)
    print(match.group(1))
    return int(match.group(1))


class MmItem(scrapy.Item):
    title = scrapy.Field()
    seen_num = scrapy.Field(
        input_processor=get_seen_num,
    )
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_fav_num),
    )
    first_image_url = scrapy.Field()
    _id = scrapy.Field(
        input_processor=MapCompose(get_order)
    )
    order = scrapy.Field(
        input_processor=MapCompose(get_order)
    )
    total_num = scrapy.Field(
        input_processor=(lambda x: int(x[-2])),
    )
    tags = scrapy.Field(
        output_processor=(lambda x: " ".join(x))
    )

    '''--------------------------------------------'''


def get_url(value):
    value = value.replace("'", "")
    value = value.replace("\n", "")
    value = value.replace("\r", "")
    value = value.replace('"+"', "")
    match = re.match(r'.*videourl:"(http.+\.mp4)"?.*', value)
    if match:
        r = match.group(1)
        return r


class FdsItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class FdsItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    seen = scrapy.Field()
    url = scrapy.Field(
        input_processor=MapCompose(get_url),
    )
    desc = scrapy.Field()
    channelid = scrapy.Field()
    like = scrapy.Field()

    '''------------------------------------------------------------'''


class BiliMovieItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def get_movie_id(value):
    if 'av' not in value and 'AV' not in value:
        return value
    match = re.match(r'.*[av|AV](\d{5,9}).*', value)
    r = match.group(1)
    return r


def get_img_url(value):
    r = value.replace("//", "")
    return r


def get_movie_tag(value):
    r = ""
    for s in value:
        r = r + " " + s
    return r


class MovieItem(scrapy.Item):
    _id = scrapy.Field(
        input_processor=MapCompose(get_movie_id)
    )
    title = scrapy.Field()
    seen = scrapy.Field()
    like = scrapy.Field()
    size = scrapy.Field()
    tag = scrapy.Field(
        output_processor=get_movie_tag
    )
    desc = scrapy.Field()
    url = scrapy.Field(
        output_processor=(lambda x: x)
    )
    time = scrapy.Field()
    img = scrapy.Field(
        input_processor=MapCompose(get_img_url)
    )


'''----------------------------------------------'''
class AnimeItem(scrapy.Item):
    _id = scrapy.Field()
    cover = scrapy.Field()
    favorites = scrapy.Field()
    is_finish = scrapy.Field()
    newest_ep_index = scrapy.Field()
    pub_time = scrapy.Field()
    season_status = scrapy.Field()
    title = scrapy.Field()
    total_count = scrapy.Field()
    update_time = scrapy.Field()
    url = scrapy.Field()
    week = scrapy.Field()
'''-----------------------------------------------------'''

class AnimeDetailItem(scrapy.Item):
    _id = scrapy.Field()
    actor = scrapy.Field()
    alias = scrapy.Field()
    area = scrapy.Field()
    bangumi_title = scrapy.Field()
    brief = scrapy.Field()
    cover = scrapy.Field()
    mid = scrapy.Field()
    evaluate = scrapy.Field()
    favorites = scrapy.Field()
    is_finish = scrapy.Field()
    is_started = scrapy.Field()
    newest_ep_id = scrapy.Field()
    newest_ep_index = scrapy.Field()
    pub_time = scrapy.Field()
    season_status = scrapy.Field()
    play_count = scrapy.Field()
    url = scrapy.Field()
    total_count = scrapy.Field()


class AnimeEpisodeItem(scrapy.Item):
    _id = scrapy.Field()  # episode_id
    av_id = scrapy.Field()
    cover = scrapy.Field()
    episode_status = scrapy.Field()
    index = scrapy.Field()
    index_title = scrapy.Field()
    is_new = scrapy.Field()
    mid = scrapy.Field()
    update_time = scrapy.Field()
    url = scrapy.Field()
    size = scrapy.Field()

'''---------------------------------------------------------------'''


class AudioLabelItem(scrapy.Item):
    order = scrapy.Field()
    cid = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

'''----------------------------------------------------------------------'''

class AudioAlbumLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AudioAlbumItem(scrapy.Item):
    order = scrapy.Field()
    zhubo_id = scrapy.Field()
    cover = scrapy.Field()
    title = scrapy.Field()
    tag = scrapy.Field()
    last_update = scrapy.Field()
    play_count = scrapy.Field()
    desc = scrapy.Field()
    sounds = scrapy.Field()
    play_num = scrapy.Field()


class AudioZhuboNumItem(scrapy.Item):
    order = scrapy.Field()


class AudioSoundNumItem(scrapy.Item):
    order = scrapy.Field()


class AudioSoundItem(scrapy.Item):
    _id = scrapy.Field()
    album_id = scrapy.Field()
    album_title = scrapy.Field()
    title = scrapy.Field()
    duration = scrapy.Field()
    favorites_count = scrapy.Field()
    formatted_created_at = scrapy.Field()
    is_favorited = scrapy.Field()
    play_paths = scrapy.Field()
    played_secs = scrapy.Field()
    zhubo_id = scrapy.Field()
    intro = scrapy.Field()
    play_count = scrapy.Field()


class AudioZhuboItem(scrapy.Item):
    _id = scrapy.Field()
    portrait = scrapy.Field()
    nackname = scrapy.Field()
    brief = scrapy.Field()
    fans_count = scrapy.Field()
    follow_count = scrapy.Field()
    sounds_count = scrapy.Field()
    love_count = scrapy.Field()



'''-------------------------------------------------'''


class BookNumItem(scrapy.Item):
    _id = scrapy.Field()


class BookChapterNumItem(scrapy.Item):
    _id = scrapy.Field()


class BookAuthorNumItem(scrapy.Item):
    _id = scrapy.Field()


class BookDetailItem(scrapy.Item):
    _id = scrapy.Field()
    cover = scrapy.Field()
    title = scrapy.Field()
    author_id = scrapy.Field()
    ahthor_name = scrapy.Field()
    book_status = scrapy.Field()
    type = scrapy.Field()
    subtype = scrapy.Field()
    text_count = scrapy.Field()
    breif = scrapy.Field()
    volumes = scrapy.Field()


class BookChapterIndexItem(scrapy.Item):
    _id = scrapy.Field()
    order_id = scrapy.Field()


class BookVolumeItem(scrapy.Item):
    _id = scrapy.Field()
    book_id = scrapy.Field()
    chapters = scrapy.Field()
    titles = scrapy.Field()


class BookAuthorItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    cover = scrapy.Field()
    brief = scrapy.Field()
    book_count = scrapy.Field()
    text_count = scrapy.Field()
    write_days = scrapy.Field()
    books = scrapy.Field()


class BookChapterItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    book_id = scrapy.Field()
    author_id = scrapy.Field()
    book_name = scrapy.Field()
    author_name = scrapy.Field()
    text_count = scrapy.Field()
    update_time = scrapy.Field()
    texts = scrapy.Field()

