from elasticsearch_dsl import Keyword, DocType, Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class AudioLabel(DocType):
    al_order = Integer()
    al_cid = Integer()
    al_url = Keyword()
    al_name = Keyword()

    class Meta:
        index = "audio"
        doc_type = "label"

if __name__ == "__main__":
    AudioLabel().init()

