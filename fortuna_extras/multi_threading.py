from Fortuna import *
from random import randrange
import concurrent.futures
import time


if __name__ == '__main__':
    rand_limit = 100  # Distribution range 0-99
    n_jobs = 4  # Total number of threads

    print("\nBase Case: Random.randrange")
    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        args = [rand_limit] * n_jobs
        results = executor.map(randrange, args)
        for result in results:
            print(result)
    finish = time.perf_counter()
    print(f'Random.randrange: {round(finish-start, 2)} second(s)')

    print("\nTest Case: Fortuna.random_below")
    start = time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        args = [rand_limit] * n_jobs
        results = executor.map(random_range, args)
        for result in results:
            print(result)
    finish = time.perf_counter()
    print(f'Fortuna.random_below: {round(finish-start, 2)} second(s)')
