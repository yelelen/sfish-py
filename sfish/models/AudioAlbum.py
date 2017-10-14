from elasticsearch_dsl import Keyword, DocType, Integer, Text, Completion, Long
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word")

connections.create_connection(hosts=["localhost"])


class AudioAlbum(DocType):
    aa_order = Integer()
    aa_zhubo_id = Integer()
    aa_cover = Keyword()
    aa_title = Text(analyzer="ik_max_word")
    aa_tag = Text(analyzer="simple")
    aa_last_update = Keyword()
    aa_play_count = Keyword()
    aa_desc = Keyword()
    aa_sounds = Keyword()
    aa_play_num = Long()
    aa_suggest = Completion(analyzer=ik_analyzer)


    class Meta:
        index = "audio"
        doc_type = "album"

if __name__ == "__main__":
    AudioAlbum().init()

