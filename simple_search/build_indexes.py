# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from generate_fixtures import songs_file
from os.path import abspath, dirname, join
from schema import SongIndexSchema
from whoosh.filedb.filestore import FileStorage


base_dir = dirname(dirname(abspath(__file__)))
index_dir = join(base_dir, "index_dir")

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


def create_indexes():
    storage = FileStorage(index_dir)
    storage.create_index(SongIndexSchema, indexname="songs")


def get_index(idx_name):
    storage = FileStorage(index_dir)
    return storage.open_index(indexname=idx_name)


def add_documents(documents):
    ix = get_index("songs")
    writer = ix.writer()
    for document in documents:
        writer.add_document(**document)
    writer.commit()


def parse_raw_song(line):
    values = line.split("|")
    song = {k: parser(values[i]) for i, (k, parser) in enumerate(songs_fields)}
    song['concat_title_artist'] = str(song['artist_id']) + song['title']
    return song


def import_indexes_from_fixtures():
    create_indexes()
    documents = []
    with open(songs_file) as f:
        for line in f:
            documents.append(parse_raw_song(line))
    add_documents(documents)


if __name__ == '__main__':
    import_indexes_from_fixtures()
