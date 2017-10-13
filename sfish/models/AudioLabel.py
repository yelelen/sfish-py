from elasticsearch_dsl import Keyword, DocType, Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class AudioLabel(DocType):
    order = Integer()
    cid = Integer()
    url = Keyword()
    name = Keyword()

    class Meta:
        index = "audio"
        doc_type = "label"

if __name__ == "__main__":
    AudioLabel().init()

