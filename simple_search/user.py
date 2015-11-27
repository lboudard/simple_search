# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from redis import StrictRedis

r = StrictRedis(host='localhost', port=6379)


def get_user_key(user_id):
    return "user_artists_profile:" + str(user_id)


def get_user_artists_profile(user_id):
    return r.zrange(
        get_user_key(user_id), 0, -1, withscores=True)


def add_user_artists(user_id, artists_scores):
    return r.zadd(
        get_user_key(user_id), **artists_scores)


if __name__ == '__main__':
    # add_user_artists(1, {"25": 0.8, "365": 0.4, "1": 0.9})
    print get_user_artists_profile(1)
