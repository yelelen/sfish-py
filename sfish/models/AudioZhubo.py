from elasticsearch_dsl import Keyword, DocType, Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class AudioZhubo(DocType):
    az_order = Integer()
    az_portrait = Keyword()
    az_nickname = Keyword()
    az_brief = Keyword()
    az_fans_count = Integer()
    az_follow_count = Integer()
    az_sounds_count = Keyword()
    az_love_count = Keyword()

    class Meta:
        index = "audio"
        doc_type = "zhubos"

if __name__ == "__main__":
    AudioZhubo().init()

