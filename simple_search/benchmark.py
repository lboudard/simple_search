# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from random import randint
from random_words import RandomWords
from multiprocessing import Pool
from search import whoosh_search, elasticsearch_search
from time import time
import cProfile
import pstats
import StringIO


class QueryGenerator(object):
    '''
    Query rnadom generator to generate tuples (user_id, query_terms)
    '''
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


def bench_queries(search_method, queries, limit=100, profile=False):
    '''
    process queries sequentially into search engine and collect runtime statistics
    '''
    ret = {}
    runtimes = []
    if profile:
        # TODO profile in context manager instead
        pr = cProfile.Profile()
        pr.enable()
    start = time()
    for q in queries:
        res = search_method(*q)
        if 'runtime' in res:
            runtimes.append(float(res.get('runtime')))
        elif 'took' in res:
            runtimes.append(float(res.get('took')))
    end = time()
    if profile:
        pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
    ret['process_time'] = float(end - start)
    ret['limit'] = limit
    ret['avg_time'] = sum(runtimes) / float(len(runtimes))
    ret['max_query_time'] = max(runtimes)
    return ret


result_list = []


def log_result(result):
    result_list.append(result)

def main():
    '''
    benchmark query engine on random generated queries
    with multithreaded batches
    '''
    # FIXME should rather use apache bench
    # http://techieroop.com/test-elasticsearch-query-performance/#.VlspjN8veYU
    thread_limit = 1000
    queries_per_thread = 50
    qg = QueryGenerator()
    queries = [next(qg) for _ in range(thread_limit * queries_per_thread)]
    start = time()
    pool = Pool()
    for i in range(thread_limit):
        pool.apply_async(
            bench_queries,
            args=(elasticsearch_search, queries[
                i * queries_per_thread: (i + 1) * queries_per_thread]),
            kwds={'limit': queries_per_thread},
            callback=log_result)
    pool.close()
    pool.join()
    end = time()
    print('nb threads: ' + str(thread_limit))
    print('nb queries_per_thread: ' + str(queries_per_thread))
    print('max single thread time (s):' + str(max(
        result_list, key=lambda x: x['process_time'])['process_time']))
    print('max single query time (ms): ' + str(max(
        result_list, key=lambda x: x['max_query_time'])['max_query_time']))
    avg_query_times = map(lambda x: x['avg_time'], result_list)
    print('avg query time (ms): ' + str(
        sum(avg_query_times) / float(len(avg_query_times))))
    print('total process time (s): ' + str(end - start))


if __name__ == '__main__':
    main()
