import time as _time
import math as _math
import random as _random

from RNG import *
from MonkeyScope import distribution_timer


def quick_test():
    def floor_mod_10(x):
        return _math.floor(x) % 10

    print("\nMonkeyScope: RNG Tests")
    start = _time.time()
    print("\nBoolean Variate Distributions\n")
    distribution_timer(bernoulli_variate, 1/3)
    distribution_timer(bernoulli_variate, 2/3)

    print("\nInteger Variate Distributions\n")
    print("Base Case")
    distribution_timer(_random.randint, 1, 6)
    distribution_timer(uniform_int_variate, 1, 6)
    distribution_timer(binomial_variate, 4, 0.5)
    distribution_timer(negative_binomial_variate, 5, 0.75)
    distribution_timer(geometric_variate, 0.75)
    distribution_timer(poisson_variate, 4.5)

    print("\nFloating Point Variate Distributions\n")
    print("Base Case")
    distribution_timer(_random.random, post_processor=round)
    distribution_timer(generate_canonical, post_processor=round)
    print("Base Case")
    distribution_timer(_random.uniform, 0.0, 10.0, post_processor=_math.floor)
    distribution_timer(uniform_real_variate, 0.0, 10.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.expovariate, 1.0, post_processor=_math.floor)
    distribution_timer(exponential_variate, 1.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.gammavariate, 1.0, 1.0, post_processor=_math.floor)
    distribution_timer(gamma_variate, 1.0, 1.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.weibullvariate, 1.0, 1.0, post_processor=_math.floor)
    distribution_timer(weibull_variate, 1.0, 1.0, post_processor=_math.floor)
    distribution_timer(extreme_value_variate, 0.0, 1.0, post_processor=round)
    print("Base Case")
    distribution_timer(_random.gauss, 5.0, 2.0, post_processor=round)
    distribution_timer(normal_variate, 5.0, 2.0, post_processor=round)
    print("Base Case")
    distribution_timer(_random.lognormvariate, 1.6, 0.25, post_processor=round)
    distribution_timer(lognormal_variate, 1.6, 0.25, post_processor=round)
    distribution_timer(chi_squared_variate, 1.0, post_processor=_math.floor)
    distribution_timer(cauchy_variate, 0.0, 1.0, post_processor=floor_mod_10)
    distribution_timer(fisher_f_variate, 8.0, 8.0, post_processor=_math.floor)
    distribution_timer(student_t_variate, 8.0, post_processor=round)

    end = _time.time()
    duration = round(end - start, 4)
    print(f"\nTotal Test Time: {duration} seconds")


if __name__ == "__main__":
    quick_test()
