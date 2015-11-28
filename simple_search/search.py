# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from build_indexes import WhooshIndexBuilder, index_dir
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request
from user import get_user_artists_profile
from whoosh.qparser import QueryParser, BoostPlugin,\
    FuzzyTermPlugin, PhrasePlugin, SequencePlugin
from whoosh.query import Term, And, Or, AndMaybe
from whoosh.filedb.filestore import FileStorage, copy_to_ram
import logging
import sys

app = Flask(__name__)
app.logger.setLevel(logging.INFO)  # use the native logger of flask
app.logger.disabled = False
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

filestorage = FileStorage(index_dir)
ramstorage = copy_to_ram(filestorage)
ix = ramstorage.open_index("songs")
# ix = get_index("songs")
# qp = QueryParser("concat_title_artist", ix.schema)
qp = QueryParser("title", ix.schema)
qp.remove_plugin_class(PhrasePlugin)
qp.add_plugin(SequencePlugin())
qp.add_plugin(BoostPlugin())
qp.add_plugin(FuzzyTermPlugin())


def whoosh_search(user_id, query_terms):
    ret = {}
    user_artists_profile = get_user_artists_profile(user_id)
    # q = qp.parse("(" + "~ ".join(query.split(' ')) + "~ AND (" + " OR ".join([
    #    str(artist_id) + "^" + str(artist_score) for (
    #        artist_id, artist_score) in user_artists_profile]) + " OR *^0.0001))")
    # q = qp.parse(
    #     "(" + query + " ANDMAYBE ((" + ") OR (".join([
    #         (" artist_id:" + str(artist_id) + "^" + str(1 + artist_score)) for (
    #             artist_id, artist_score) in user_artists_profile]) + ")))")
    # see https://pythonhosted.org/Whoosh/api/query.html#whoosh.query.AndMaybe
    q = AndMaybe(
        And([Term('title', qt) for qt in query_terms.split(' ')]),
        Or([Term('artist_id', artist_id, boost=artist_score) for (
            artist_id, artist_score) in user_artists_profile]))
    # app.logger.debug(q)
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=10)
        ret = {
            'items': [hit.fields() for hit in results],
            'runtime': results.runtime}
    return ret


def elasticsearch_search(user_id, query_terms):
    ret = {}
    es = Elasticsearch()
    user_artists_profile = get_user_artists_profile(user_id)
    # query = (
    #     "(title:" + query_terms + ") AND ((" + ") OR (".join([
    #         ("artist_id:" + str(artist_id) + "^" + str(1 + artist_score)) for (
    #             artist_id, artist_score) in user_artists_profile]) + "))"
    # )
    query = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": {
                            "query": query_terms,
                            "operator": "and"
                        }
                    }
                },
                "should": [
                    {"match": {
                        "artist_id": {
                            "query": str(artist_id),
                            "boost": artist_score
                        }
                    }} for artist_id, artist_score in user_artists_profile
                ]
            }
        }
    }
    ret = es.search(index="songs", body=query)#q=query)
    return ret


@app.route('/user/<user_id>/search')
def search(user_id):
    query = request.args.get('q')
    return jsonify(elasticsearch_search(user_id, query))


if __name__ == '__main__':
    app.run()
