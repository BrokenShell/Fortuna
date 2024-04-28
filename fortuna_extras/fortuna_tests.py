import time as _time

import math as _math
import random as _random

from Fortuna import *
from MonkeyScope import distribution_timer, timer


def quick_test():
    print("\nMonkeyScope: Fortuna Quick Test")
    print(f"Fortuna Version: {version}")
    print(f"Storm Version: {storm_version()}")
    start_test = _time.time()
    i_clamps = [
        smart_clamp(1, 2, 3),
        smart_clamp(1, 3, 2),
        smart_clamp(2, 1, 3),
        smart_clamp(2, 3, 1),
        smart_clamp(3, 1, 2),
        smart_clamp(3, 2, 1),
    ]
    print(f"\nSmart Clamp: {'Pass' if all(val == 2 for val in i_clamps) else 'Fail'}")
    f_clamps = [
        float_clamp(0.1, 0.2, 0.3),
        float_clamp(0.1, 0.3, 0.2),
        float_clamp(0.2, 0.1, 0.3),
        float_clamp(0.2, 0.3, 0.1),
        float_clamp(0.3, 0.1, 0.2),
        float_clamp(0.3, 0.2, 0.1),
    ]
    print(f"Float Clamp: {'Pass' if all(val == 0.2 for val in f_clamps) else 'Fail'}")
    some_list = [i for i in range(10)]
    print("\nData:")
    print(f"{some_list = }\n")
    print("Base Case")
    distribution_timer(
        _random.choice, some_list, label="Random.choice(some_list)"
    )
    distribution_timer(
        random_value, some_list, label="random_value(some_list)"
    )

    print("\nWide Distribution")
    truffle = TruffleShuffle(some_list)
    print("Truffle = TruffleShuffle(some_list)")
    distribution_timer(truffle, label="Truffle()")
    truffle = truffle_shuffle(some_list)
    print("truffle = truffle_shuffle(some_list)")
    distribution_timer(truffle, label="truffle()")

    print("\nQuantumMonty")
    some_tuple = tuple(i for i in range(10))
    print("some_tuple = tuple(i for i in range(10))\n")
    monty = QuantumMonty(some_tuple)
    print("monty = QuantumMonty(some_tuple)")
    distribution_timer(monty, label="monty()")

    rand_value = RandomValue(some_tuple)
    print(f"rand_value = {rand_value}")
    distribution_timer(rand_value, label="rand_value()")

    print("\nWeighted Tables:")
    population = ("A", "B", "C", "D")
    cum_weights = (1, 3, 6, 10)
    rel_weights = (1, 2, 3, 4)
    cum_weighted_table = zip(cum_weights, population)
    rel_weighted_table = zip(rel_weights, population)
    print(f"population = {population}")
    print(f"cum_weights = {cum_weights}")
    print(f"rel_weights = {rel_weights}")
    print(f"cum_weighted_table = zip(cum_weights, population)")
    print(f"rel_weighted_table = zip(rel_weights, population)\n")
    print("Cumulative Base Case")
    distribution_timer(
        _random.choices, population, cum_weights=cum_weights,
        label="Random.choices(population, cum_weights=cum_weights)"
    )
    cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)
    print("cum_weighted_choice = CumulativeWeightedChoice(cum_weighted_table)")
    distribution_timer(cum_weighted_choice, label="cum_weighted_choice()")
    distribution_timer(
        cumulative_weighted_choice, tuple(zip(cum_weights, population)),
        label="cumulative_weighted_choice(tuple(zip(cum_weights, population)))"
    )
    print("Relative Base Case")
    distribution_timer(
        _random.choices, population, weights=rel_weights,
        label="Random.choices(population, weights=rel_weights)"
    )
    rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)
    print("rel_weighted_choice = RelativeWeightedChoice(rel_weighted_table)")
    distribution_timer(rel_weighted_choice, label="rel_weighted_choice()")

    print("\nRandom Matrix Values:")
    some_matrix = {
        "A": (1, 2, 3, 4), "B": (10, 20, 30, 40), "C": (100, 200, 300, 400)
    }
    print(f"some_matrix = {some_matrix}\n")
    print('flex_cat = FlexCat(some_matrix)')
    flex_cat = FlexCat(some_matrix)
    distribution_timer(flex_cat, label='flex_cat()')
    distribution_timer(flex_cat, "C", label='flex_cat("C")')

    print("\nRandom Integers:")
    print("Base Case")
    distribution_timer(_random.randrange, 10)
    distribution_timer(random_below, 10)
    distribution_timer(random_index, 10)
    distribution_timer(random_range, 10)
    distribution_timer(random_below, -10)
    distribution_timer(random_index, -10)
    distribution_timer(random_range, -10)
    print("Base Case")
    distribution_timer(_random.randrange, 1, 10)
    distribution_timer(random_range, 1, 10)
    distribution_timer(random_range, 10, 1)
    print("Base Case")
    distribution_timer(_random.randint, -5, 5)
    distribution_timer(random_int, -5, 5)
    distribution_timer(random_uint, max_uint() - 10, max_uint())
    print("Base Case")
    distribution_timer(_random.randrange, 1, 20, 2)
    distribution_timer(random_range, 1, 20, 2)
    distribution_timer(random_range, 1, 20, -2)
    distribution_timer(random_range, 20, 1, -2)
    distribution_timer(d, 10)
    distribution_timer(dice, 3, 6)
    distribution_timer(ability_dice, 4)
    distribution_timer(plus_or_minus, 5)
    distribution_timer(plus_or_minus_linear, 5)
    distribution_timer(plus_or_minus_gauss, 5)

    print("\nRandom Floats:")
    print("Base Case")
    timer(_random.random)
    timer(canonical)

    print("Base Case")
    distribution_timer(_random.uniform, 0.0, 10.0, post_processor=_math.floor)
    distribution_timer(random_float, 0.0, 10.0, post_processor=_math.floor)

    print("Base Case")
    distribution_timer(_random.triangular, 0.0, 10.0, 5.0, post_processor=round)
    distribution_timer(triangular, 0.0, 10.0, 5.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.vonmisesvariate, 0.0, 1.0, post_processor=round)
    distribution_timer(vonmises_variate, 0.0, 1.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.expovariate, 2.0, post_processor=round)
    distribution_timer(exponential_variate, 2.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.gammavariate, 1.0, 1.0, post_processor=round)
    distribution_timer(gamma_variate, 1.0, 1.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.weibullvariate, 1.0, 1.0, post_processor=round)
    distribution_timer(weibull_variate, 1.0, 1.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.normalvariate, 0.0, 1.0, post_processor=round)
    distribution_timer(normal_variate, 0.0, 1.0, post_processor=round)

    print("Base Case")
    distribution_timer(_random.lognormvariate, 0.0, 1.0, post_processor=round)
    distribution_timer(log_normal_variate, 0.0, 1.0, post_processor=round)

    print("timer(beta_variate, 1.0, 1.0)")
    timer(beta_variate, 1.0, 1.0)
    print("\ntimer(pareto_variate, 1.0)")
    timer(pareto_variate, 1.0)
    print("\ntimer(bernoulli_variate, 0.5)")
    timer(bernoulli_variate, 0.5)
    print("\ntimer(binomial_variate, 3, 0.5)")
    timer(binomial_variate, 3, 0.5)
    print("\ntimer(negative_binomial_variate, 3, 0.5)")
    timer(negative_binomial_variate, 3, 0.5)
    print("\ntimer(geometric_variate, 0.5)")
    timer(geometric_variate, 0.5)
    print("\ntimer(poisson_variate, 0.5)")
    timer(poisson_variate, 0.5)
    print("\ntimer(extreme_value_variate, 0.0, 2.0)")
    timer(extreme_value_variate, 0.0, 2.0)
    print("\ntimer(chi_squared_variate, 5.0)")
    timer(chi_squared_variate, 5.0)
    print("\ntimer(cauchy_variate, 0.0, 2.0)")
    timer(cauchy_variate, 0.0, 2.0)
    print("\ntimer(fisher_f_variate, 2.0, 3.0)")
    timer(fisher_f_variate, 2.0, 3.0)
    print("\ntimer(student_t_variate, 5.0)")
    timer(student_t_variate, 5.0)

    print("\nRandom Booleans:")
    distribution_timer(percent_true, 33.33)

    print("\nShuffle Performance:")
    shuffle_cycles = 7
    small, medium, large = 10, 100, 1000
    some_small_list = list(range(small))
    print(f"\tsome_small_list = [i for i in range({small})]")
    some_med_list = list(range(medium))
    print(f"\tsome_med_list = [i for i in range({medium})]")
    some_large_list = list(range(large))
    print(f"\tsome_large_list = [i for i in range({large})]")
    print("\nBase Case:")
    print("Random.shuffle()  # fisher_yates in python")
    timer(_random.shuffle, some_small_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_med_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_large_list, cycles=shuffle_cycles)
    some_small_list.sort()
    some_med_list.sort()
    some_large_list.sort()
    print("\nFortuna.shuffle()  # knuth_b in cython")
    timer(shuffle, some_small_list, cycles=shuffle_cycles)
    timer(shuffle, some_med_list, cycles=shuffle_cycles)
    timer(shuffle, some_large_list, cycles=shuffle_cycles)
    some_small_list.sort()
    some_med_list.sort()
    some_large_list.sort()
    print("\nFortuna.knuth_a()  # knuth_a in cython")
    timer(knuth_a, some_small_list, cycles=shuffle_cycles)
    timer(knuth_a, some_med_list, cycles=shuffle_cycles)
    timer(knuth_a, some_large_list, cycles=shuffle_cycles)
    some_small_list.sort()
    some_med_list.sort()
    some_large_list.sort()
    print("\nFortuna.fisher_yates()  # fisher_yates in cython")
    timer(fisher_yates, some_small_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_med_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_large_list, cycles=shuffle_cycles)

    print("\n\nClamp Performance:")
    print("smart_clamp(3, 2, 1) # should be 2: ", smart_clamp(3, 2, 1))
    timer(smart_clamp, 3, 2, 1, cycles=shuffle_cycles)
    print("float_clamp(3.0, 2.0, 1.0) # should be 2.0: ", float_clamp(3.0, 2.0, 1.0))
    timer(float_clamp, 3.0, 2.0, 1.0, cycles=shuffle_cycles)

    stop_test = _time.time()
    print("\n")
    print("-" * 73)
    print(f"Total Test Time: {round(stop_test - start_test, 3)} seconds")


if __name__ == "__main__":
    quick_test()
