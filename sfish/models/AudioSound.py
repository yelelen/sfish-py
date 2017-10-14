from elasticsearch_dsl import Keyword, DocType, Integer, Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word")

connections.create_connection(hosts=["localhost"])


class AudioSound(DocType):
    as_order = Integer()
    as_album_id = Integer()
    as_album_title = Keyword()
    as_title = Keyword()
    as_duration = Integer()
    as_favorites_count = Integer()
    as_formatted_created_at = Keyword()
    as_play_paths = Keyword()
    as_zhubo_id = Integer()
    as_intro = Keyword()
    as_play_count = Integer()

    class Meta:
        index = "audio"
        doc_type = "sounds"

if __name__ == "__main__":
    AudioSound().init()

