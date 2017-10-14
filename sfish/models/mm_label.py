from elasticsearch_dsl import Keyword, DocType, Integer
from elasticsearch_dsl.connections import connections


connections.create_connection(hosts=["localhost"])


class MMLabel(DocType):
    mml_cover = Keyword()
    mml_label = Keyword()
    mml_order = Integer()

    class Meta:
        index = 'mm'
        doc_type = 'mmlabel'


if __name__ == "__main__":
    MMLabel.init()
