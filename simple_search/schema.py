# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED, NUMERIC


class SongIndexSchema(SchemaClass):
    song_id = ID(stored=True, unique=True)
    artist_id = ID(stored=True, sortable=True)
    title = TEXT(stored=True)
    artist = TEXT(stored=True)
    popularity = NUMERIC(stored=True, field_boost=1.0)
    concat_title_artist = TEXT(stored=True)
