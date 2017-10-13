from elasticsearch_dsl import Keyword, DocType, Integer
from elasticsearch_dsl.connections import connections


connections.create_connection(hosts=["localhost"])


class MMLabel(DocType):
    cover = Keyword()
    label = Keyword()
    order = Integer()

    class Meta:
        index = 'mm'
        doc_type = 'mmlabel'


if __name__ == "__main__":
    MMLabel.init()
