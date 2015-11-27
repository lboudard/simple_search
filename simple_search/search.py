# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from build_indexes import get_index
from flask import Flask, jsonify, request
from user import get_user_artists_profile
from whoosh.qparser import QueryParser
import logging
import sys

app = Flask(__name__)
app.logger.setLevel(logging.INFO)  # use the native logger of flask
app.logger.disabled = False
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

ix = get_index("songs")
qp = QueryParser("title", ix.schema)


@app.route('/user/<user_id>/search')
def search(user_id):
    query = request.args.get('q')
    user_artists_profile = get_user_artists_profile(user_id)
    user_artists_profile.append(("*", 0.001))
    q = qp.parse(
        "(" + ") OR (".join([
            (query +
             " artist_id:" + str(artist_id) + "^" + str(artist_score)) for (
                artist_id, artist_score) in user_artists_profile]) + ")")
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=10)
        return jsonify({
            'items': [hit.fields() for hit in results]})


if __name__ == '__main__':
    app.run()
