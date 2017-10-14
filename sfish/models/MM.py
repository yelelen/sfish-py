from elasticsearch_dsl import Text, Completion, Keyword, DocType, Integer
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word")

connections.create_connection(hosts=["localhost"])


class MM(DocType):
    mm_title = Text(analyzer="ik_max_word")
    mm_seen_num = Integer()
    mm_fav_num = Integer()
    mm_first_image_url = Keyword()
    mm_order = Integer()
    mm_total_num = Integer()
    mm_tags = Text(analyzer="simple")
    mm_suggest = Completion(analyzer=ik_analyzer)

    class Meta:
        index = 'mm'
        doc_type = 'mmjpg'

if __name__ == "__main__":
    MM().init()

