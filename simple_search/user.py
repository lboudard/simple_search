# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from generate_fixtures import user_file
from redis import StrictRedis


r = StrictRedis(host='localhost', port=6379)


def get_user_key(user_id):
    return "user_artists_profile:" + str(user_id)


def get_user_artists_profile(user_id):
    return r.zrange(
        get_user_key(user_id), 0, -1, withscores=True)


def add_user_artists(user_id, artists_scores):
    if len(artists_scores):
        return r.zadd(
            get_user_key(user_id), **artists_scores)


def parse_raw_user(line):
    v = line.split("|")
    user_id = v[0]
    artists_scores = {}
    for as_concat in v[1:]:
        (artist, score) = as_concat.split(':')
        artists_scores[str(artist)] = float(score)
    return (user_id, artists_scores)


def import_users_from_fixtures():
    with open(user_file) as f:
        for line in f:
            (user_id, artists_scores) = parse_raw_user(
                line)
            add_user_artists(user_id, artists_scores)


if __name__ == '__main__':
    import_users_from_fixtures()
