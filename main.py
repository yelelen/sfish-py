import sys
import os
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", "mmjpg"])
# execute(["scrapy", "crawl", "fds"])
# execute(["scrapy", "crawl", "bili_anime_detail"])
# execute(["scrapy", "crawl", "bili_movie_west"])
# execute(["scrapy", "crawl", "audio_album"])

