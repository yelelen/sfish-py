from elasticsearch_dsl import DocType, Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class AudioSoundNum(DocType):
    order = Integer()

    class Meta:
        index = "audio"
        doc_type = "SoundNum"

if __name__ == "__main__":
    AudioSoundNum().init()

