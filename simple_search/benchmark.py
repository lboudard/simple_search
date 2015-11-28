# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from random import randint
from random_words import RandomWords
from search import whoosh_search
from time import time
import timeit


class QueryGenerator(object):
    def __init__(self, user_limit=10000):
        self._user_limit = user_limit
        self._words_generator = RandomWords()

    def __next__(self):
        return self.next()

    def next(self):
        return (randint(0, self._user_limit), ' '.join(
            self._words_generator.random_words(count=randint(1, 5))))

    def __iter__(self):
        return self


class WhooshBench(object):

    @classmethod
    def bench_queries(cls, limit=50000):
        qg = QueryGenerator()
        queries = [next(qg) for _ in range(limit)]
        runtimes = []
        start = time()
        for q in queries:
            runtimes.append(float(whoosh_search(*q).get('runtime')))
        end = time()
        print('{limit} queries processed within {process_time} (single thread)'.format(
            limit=str(limit),
            process_time=str(end - start)))
        print('average query time: {avg_time}'.format(
            avg_time=str(sum(runtimes) / float(len(runtimes)))))
        print('max query time {max_query_time}'.format(
            max_query_time=max(runtimes)))

if __name__ == '__main__':
    WhooshBench.bench_queries()
