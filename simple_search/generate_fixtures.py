# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random_words import RandomWords, RandomNicknames
from random import randint, random, betavariate
from os.path import abspath, dirname, join

base_dir = dirname(dirname(abspath(__file__)))
user_file = join(base_dir, 'data/user_artists.txt')
songs_file = join(base_dir, 'data/songs.txt')


def generate_user_file(
        limit, artists_per_user_limit=100, artist_id_limit=1000000):
    """
    generates files like
    4587|547:1|6984:0.98|147856:0.05
    uid|artist_id:score|artist_id:score
    """
    with open(user_file, 'w+') as f:
        for i in range(limit):
            line = [str(i)]
            nb_artists = int(betavariate(2, 2) * artists_per_user_limit)
            for _ in range(nb_artists):
                line.append(str(int(
                    betavariate(2, 5) * artist_id_limit)) + ':' + str(random()))
            f.write('|'.join(line) + '\n')


def generate_songs_file(
        limit, artist_id_limit=1000000, popularity_limit=1000000):
    """
    generates files like
    1|Help|154681|The Beatles|25
    """
    rw = RandomWords()
    rn = RandomNicknames()
    with open(songs_file, 'w+') as f:
        for i in range(limit):
            line = [str(i)]
            # title
            line.append(' '.join(rw.random_words(count=randint(1, 5))))
            line.append(str(int(popularity_limit * betavariate(2, 5))))
            # artist
            line.append(' '.join(rn.random_nicks(count=randint(1, 3))))
            line.append(str(randint(0, artist_id_limit)))
            f.write('|'.join(line) + '\n')


def main():
    generate_user_file(1000000)
    generate_songs_file(20000000)


if __name__ == '__main__':
    main()
