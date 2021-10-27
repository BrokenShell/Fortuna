""" Random Number Tests with Multithreading.
The builtin Python Random library is not thread compatible and incorrectly
produces the same `random` number for all threads. Conversely, Fortuna is thread
compatible and will correctly produce random results for all threads. """
from Fortuna import random_range
from random import randrange
from concurrent.futures import ProcessPoolExecutor


if __name__ == '__main__':

    rand_limit = 100  # Distribution range 0-99
    n_jobs = 6  # Total number of threads

    print(f"\nMulti-threaded randrange/random_range test: {n_jobs} threads")

    print("\nRandom.randrange:")
    with ProcessPoolExecutor() as executor:
        results = executor.map(randrange, [rand_limit] * n_jobs)
    print(' '.join(map(str, results)))

    print("\nFortuna.random_range:")
    with ProcessPoolExecutor() as executor:
        results = executor.map(random_range, [rand_limit] * n_jobs)
    print(' '.join(map(str, results)))
