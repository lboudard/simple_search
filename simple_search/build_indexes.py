# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from generate_fixtures import songs_file
from os.path import abspath, dirname, join
from schema import SongIndexSchema
from whoosh.filedb.filestore import FileStorage


base_dir = dirname(dirname(abspath(__file__)))
index_dir = join(base_dir, "index_dir")


class IndexBuilder(object):
    songs_fields = [("song_id", lambda x: x),
                    ("title", lambda x: x.strip()),
                    ("popularity", lambda x: int(x)),
                    ("artist", lambda x: x),
                    ("artist_id", lambda x: x.strip())]

    # raw_docs = [
    #     "1|Help|154681|The Beatles|25",
    #     "2|Requiem|45002|Mozart|365",
    #     "3|Get Lucky|714522|Daft Punk, Parrell Williams|78404",
    #     "4|Lucky Strike|125|Maroon 5|1"]

    @classmethod
    def create_indexes(cls):
        storage = FileStorage(index_dir)
        storage.create_index(SongIndexSchema, indexname="songs")

    @classmethod
    def get_index(cls, idx_name):
        storage = FileStorage(index_dir)
        return storage.open_index(indexname=idx_name)

    @classmethod
    def add_documents(cls, documents):
        ix = cls.get_index("songs")
        writer = ix.writer()
        for document in documents:
            writer.add_document(**document)
        writer.commit()

    @classmethod
    def parse_raw_song(cls, line):
        values = line.split("|")
        song = {k: parser(values[i]) for i, (k, parser) in enumerate(cls.songs_fields)}
        song['concat_title_artist'] = str(song['artist_id']) + ' ' + song['title']
        return song

    @classmethod
    def import_indexes_from_fixtures(cls):
        cls.create_indexes()
        documents = []
        with open(songs_file) as f:
            for line in f:
                documents.append(cls.parse_raw_song(line))
        cls.add_documents(documents)


if __name__ == '__main__':
    IndexBuilder.import_indexes_from_fixtures()
