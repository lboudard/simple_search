# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import abspath, dirname, join
import sys
base_dir = dirname(dirname(abspath(__file__)))
sys.path.append(join(base_dir, 'simple_search'))
from simple_search.build_indexes import ElasticSearchIndexBuilder
from simple_search.search import elasticsearch_search
from simple_search.user import import_users_from_fixtures
from time import sleep
import unittest


class TestUserPreferencesESQueries(unittest.TestCase):
    def setUp(self):
        ElasticSearchIndexBuilder.import_indexes_from_fixtures(
            join(base_dir, 'data/songs_test_fixtures.txt'),
            ix_name="test_songs")
        import_users_from_fixtures(
            join(base_dir, 'data/user_test_fixtures.txt'))
        # time for es to push in index
        sleep(2)

    def test_queries(self):
        songs = elasticsearch_search(
            0, 'socket', ix_name="test_songs")
        self.assertSequenceEqual(map(
            lambda song: song.get('_id'), songs.get(
                'hits').get('hits')), ["0", "2", "1"])
        songs = elasticsearch_search(
            0, 'overvoltage', ix_name="test_songs")
        self.assertSequenceEqual(map(
            lambda song: song.get('_id'), songs.get(
                'hits').get('hits')), ["5", "4", "3", "1"])
