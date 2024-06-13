""" Random Number Tests with Multithreading.
The builtin Python Random library is not thread compatible and incorrectly
produces the same `random` number for all threads. Conversely, Fortuna is thread
compatible and will correctly produce random results for all threads.

*Notes:
- Fortuna can produce a half a million random numbers on a single processor
    in approximately the same time it can produce 4 random numbers on 4 cores.
    In other words, take nothing for granted - benchmark everything! """
import time
from multiprocessing import Pool, set_start_method

import Fortuna
import random


def proc_pool(func):
    jobs = 16
    limit = 100
    with Pool(processes=jobs) as pool:
        result = pool.map(func, [limit] * jobs, chunksize=1)
    return tuple(result)


if __name__ == '__main__':
    set_start_method('spawn')

    num = 384_000
    print(f"No Pool Baseline: {num} random numbers, one thread")
    print("Random")
    start = time.perf_counter()
    test2 = tuple(random.randrange(100) for _ in range(num))
    stop = time.perf_counter()
    print(f"Time: {stop - start:.3f}s\n")

    print("Fortuna")
    start = time.perf_counter()
    test1 = tuple(Fortuna.random_range(100) for _ in range(num))
    stop = time.perf_counter()
    print(f"Time: {stop - start:.3f}s\n")

    print("Multiprocessing Pool Tests")

    print("Random")
    start = time.perf_counter()
    values = proc_pool(random.randrange)
    print(f"{values} - {'PASS' if len(set(values)) >= len(values[1:-1]) else 'FAIL'}")
    stop = time.perf_counter()
    print(f"Time: {stop - start:.3f}s\n")
    print("Fortuna")
    start = time.perf_counter()
    values = proc_pool(Fortuna.random_range)
    print(f"{values} - {'PASS' if len(set(values)) >= len(values[1:-1]) else 'FAIL'}")
    stop = time.perf_counter()
    print(f"Time: {stop - start:.3f}s\n")
