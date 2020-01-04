import time as _time
import math as _math
import random as _random
import itertools as _itertools

from Pyewacket import *
from MonkeyScope import distribution_timer, timer


def software_seed_test(seed_test_size):
    arr1 = [i for i in range(seed_test_size)]
    seed(2**32)
    shuffle(arr1)
    arr2 = [i for i in range(seed_test_size)]
    seed(2**32)
    shuffle(arr2)
    if arr1 == arr2:
        print("Software Seed Test Passed")
    else:
        print("Software Seed Test Failed")


def hardware_seed_test(seed_test_size):
    arr3 = [i for i in range(seed_test_size)]
    seed(0)
    shuffle(arr3)
    arr4 = [i for i in range(seed_test_size)]
    seed(0)
    shuffle(arr4)
    if arr3 != arr4:
        print("Hardware Seed Test Passed")
    else:
        print("Hardware Seed Test Failed")


def quick_test():
    R = _random.Random()
    print("\nMonkeyScope: Pyewacket\n")
    start_test = _time.time()
    print("Base Case")
    distribution_timer(R._randbelow, 10)
    distribution_timer(randbelow, 10)
    print("Base Case")
    distribution_timer(_random.randint, 1, 10)
    distribution_timer(randint, 1, 10)
    print("Base Case")
    distribution_timer(_random.randrange, 0, 10, 2)
    distribution_timer(randrange, 0, 10, 2)
    print("Base Case")
    distribution_timer(_random.random, post_processor=round)
    distribution_timer(random, post_processor=round)
    print("Base Case")
    distribution_timer(_random.uniform, 0.0, 10.0, post_processor=_math.floor)
    distribution_timer(uniform, 0.0, 10.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.expovariate, 1.0, post_processor=_math.floor)
    distribution_timer(expovariate, 1.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.gammavariate, 2.0, 1.0, post_processor=round)
    distribution_timer(gammavariate, 2.0, 1.0, post_processor=round)
    print("Base Case")
    distribution_timer(_random.weibullvariate, 1.0, 1.0, post_processor=_math.floor)
    distribution_timer(weibullvariate, 1.0, 1.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.betavariate, 3.0, 3.0, post_processor=round)
    distribution_timer(betavariate, 3.0, 3.0, post_processor=round)
    print("Base Case")
    distribution_timer(_random.paretovariate, 4.0, post_processor=_math.floor)
    distribution_timer(paretovariate, 4.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.gauss, 1.0, 1.0, post_processor=round)
    distribution_timer(gauss, 1.0, 1.0, post_processor=round)
    print("Base Case")
    distribution_timer(_random.normalvariate, 0.0, 2.8, post_processor=round)
    distribution_timer(normalvariate, 0.0, 2.8, post_processor=round)
    print("Base Case")
    distribution_timer(_random.lognormvariate, 0.0, 0.5, post_processor=round)
    distribution_timer(lognormvariate, 0.0, 0.5, post_processor=round)
    print("Base Case")
    distribution_timer(_random.vonmisesvariate, 0, 0, post_processor=_math.floor)
    distribution_timer(vonmisesvariate, 0, 0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.triangular, 0.0, 10.0, 0.0, post_processor=_math.floor)
    distribution_timer(triangular, 0.0, 10.0, 0.0, post_processor=_math.floor)
    some_list = [i for i in range(10)]
    print("Base Case")
    distribution_timer(_random.choice, some_list)
    distribution_timer(choice, some_list)
    weights = [i for i in reversed(range(1, 11))]
    sample_size = 1
    print("Base Case")
    distribution_timer(_random.choices, some_list, weights, k=sample_size)
    distribution_timer(choices, some_list, weights, k=sample_size)
    cum_weights = list(_itertools.accumulate(weights))
    print("Base Case")
    distribution_timer(_random.choices, some_list, cum_weights=cum_weights, k=sample_size)
    distribution_timer(choices, some_list, cum_weights=cum_weights, k=sample_size)
    some_shuffle_list = [i for i in range(100)]
    print("Base Case")
    print(f"Timer only: random.shuffle(some_list) of size {len(some_shuffle_list)}:")
    timer(_random.shuffle, some_shuffle_list, cycles=8)
    print()
    print(f"Timer only: shuffle(some_list) of size {len(some_shuffle_list)}:")
    timer(shuffle, some_shuffle_list, cycles=8)
    print()
    print("Base Case")
    distribution_timer(_random.sample, some_list, k=3)
    distribution_timer(sample, some_list, k=3)
    stop_test = _time.time()
    print(f"\nTotal Test Time: {round(stop_test - start_test, 3)} sec")


if __name__ == "__main__":
    quick_test()
