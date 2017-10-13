from elasticsearch_dsl import Keyword, DocType, Integer, Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word")

connections.create_connection(hosts=["localhost"])


class AudioAlbum(DocType):
    order = Integer()
    zhubo_id = Integer()
    cover = Keyword()
    title = Text(analyzer="ik_max_word")
    tag = Text(analyzer="simple")
    last_update = Keyword()
    play_count = Keyword()
    desc = Keyword()
    sounds = Keyword()
    suggest = Completion(analyzer=ik_analyzer)


    class Meta:
        index = "audio"
        doc_type = "album"

if __name__ == "__main__":
    AudioAlbum().init()

