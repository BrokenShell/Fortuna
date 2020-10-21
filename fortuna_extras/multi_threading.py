""" Random Number Tests with Multithreading.
The builtin Python Random library is not thread compatible and incorrectly
produces the same `random` number for all threads. Conversely, Fortuna is thread
compatible and will correctly produce random results for all threads. """
from Fortuna import random_range
from random import randrange
import concurrent.futures
import time


if __name__ == '__main__':
    rand_limit = 100  # Distribution range 0-99
    n_jobs = 8  # Total number of threads

    print("\nRandom.randrange:")
    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(randrange, [rand_limit] * n_jobs)
    print(list(results))
    finish = time.perf_counter()
    print(f'Time: {round(finish-start, 2)} second(s)')

    print("\nFortuna.random_range:")
    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(random_range, [rand_limit] * n_jobs)
    print(list(results))
    finish = time.perf_counter()
    print(f'Time: {round(finish-start, 2)} second(s)')
