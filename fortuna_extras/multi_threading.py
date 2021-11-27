""" Random Number Tests with Multithreading.
The builtin Python Random library is not thread compatible and incorrectly
produces the same `random` number for all threads. Conversely, Fortuna is thread
compatible and will correctly produce random results for all threads. """
import time

from Fortuna import random_range
from random import randrange
from concurrent.futures import ProcessPoolExecutor


def proc_pool(func):
    jobs = 16
    limit = 100
    with ProcessPoolExecutor() as exe:
        result = exe.map(func, [limit] * jobs)
    return tuple(result)


if __name__ == '__main__':
    print("Baseline:")
    start = time.perf_counter()
    print(f"{tuple(random_range(100) for _ in range(820000))}")
    stop = time.perf_counter()
    print(f"Wall Time: {stop - start:.3f}s\n")

    start = time.perf_counter()
    print(f"{proc_pool(randrange) = }")
    stop = time.perf_counter()
    print(f"Wall Time: {stop - start:.3f}s\n")

    start = time.perf_counter()
    print(f"{proc_pool(random_range) = }")
    stop = time.perf_counter()
    print(f"Wall Time: {stop - start:.3f}s\n")
