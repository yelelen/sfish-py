from elasticsearch_dsl import Keyword, DocType, Integer, Text, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word")

connections.create_connection(hosts=["localhost"])


class AudioAlbumSimple(DocType):
    aas_order = Integer()
    aas_cover = Keyword()
    aas_title = Text(analyzer="ik_max_word")
    aas_play_count = Integer()
    aas_suggest = Completion(analyzer=ik_analyzer)

    class Meta:
        index = "audio"
        doc_type = "album_simple"

if __name__ == "__main__":
    AudioAlbumSimple().init()

