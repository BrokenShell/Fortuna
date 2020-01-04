import time as _time
import math as _math
import random as _random

from Fortuna import *
from MonkeyScope import distribution_timer, timer

__all__ = (
    "quick_test",
)


def quick_test():
    print("\nMonkeyScope: Fortuna Quick Test")
    print("\nRandom Sequence Values:\n")
    start_test = _time.time()
    some_list = [i for i in range(10)]
    print(f"some_list = {some_list}\n")
    print("Base Case")
    distribution_timer(
        _random.choice, some_list, label="Random.choice(some_list)"
    )
    distribution_timer(
        random_value, some_list, label="random_value(some_list)"
    )

    print("\nWide Distribution\n")
    truffle = TruffleShuffle(some_list)
    print("truffle = TruffleShuffle(some_list)")
    distribution_timer(truffle, label="truffle()")

    print("\nSingle objects with many distribution possibilities\n")
    some_tuple = tuple(i for i in range(10))
    print("some_tuple = tuple(i for i in range(10))\n")
    monty = QuantumMonty(some_tuple)
    print("monty = QuantumMonty(some_tuple)")
    distribution_timer(monty, label="monty()")

    rand_value = RandomValue(some_tuple)
    print(f"rand_value = {rand_value}")
    distribution_timer(rand_value, label="rand_value()")

    print("\nWeighted Tables:\n")
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

    print("\nRandom Matrix Values:\n")
    some_matrix = {
        "A": (1, 2, 3, 4), "B": (10, 20, 30, 40), "C": (100, 200, 300, 400)
    }
    print(f"some_matrix = {some_matrix}\n")
    print('flex_cat = FlexCat(some_matrix)')
    flex_cat = FlexCat(some_matrix)
    distribution_timer(flex_cat, label='flex_cat()')
    distribution_timer(flex_cat, "C", label='flex_cat("C")')

    print("\nRandom Integers:\n")
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

    print("\nRandom Floats:\n")
    print("Base Case")
    distribution_timer(_random.random, post_processor=round)
    distribution_timer(canonical, post_processor=round)
    distribution_timer(random_float, 0.0, 10.0, post_processor=_math.floor)
    print("Base Case")
    distribution_timer(_random.triangular, 0.0, 10.0, 5.0, post_processor=round)
    distribution_timer(triangular, 0.0, 10.0, 5.0, post_processor=round)

    print("\nRandom Booleans:\n")
    distribution_timer(percent_true, 33.33)

    print("\nShuffle Performance:\n")
    shuffle_cycles = 7
    small, medium, large = 10, 100, 1000
    some_small_list = list(range(small))
    print(f"some_small_list = [i for i in range({small})]")
    some_med_list = list(range(medium))
    print(f"some_med_list = [i for i in range({medium})]")
    some_large_list = list(range(large))
    print(f"some_large_list = [i for i in range({large})]")

    print("\nBase Case:")
    print("Random.shuffle()")
    timer(_random.shuffle, some_small_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_med_list, cycles=shuffle_cycles)
    timer(_random.shuffle, some_large_list, cycles=shuffle_cycles)
    some_small_list.sort()
    some_med_list.sort()
    some_large_list.sort()
    print("\nFortuna.shuffle()")
    timer(shuffle, some_small_list, cycles=shuffle_cycles)
    timer(shuffle, some_med_list, cycles=shuffle_cycles)
    timer(shuffle, some_large_list, cycles=shuffle_cycles)
    print("\nFortuna.knuth_a()")
    timer(knuth_a, some_small_list, cycles=shuffle_cycles)
    timer(knuth_a, some_med_list, cycles=shuffle_cycles)
    timer(knuth_a, some_large_list, cycles=shuffle_cycles)
    print("\nFortuna.fisher_yates()")
    timer(fisher_yates, some_small_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_med_list, cycles=shuffle_cycles)
    timer(fisher_yates, some_large_list, cycles=shuffle_cycles)
    print("\n")

    print("-" * 73)
    stop_test = _time.time()
    print(f"Total Test Time: {round(stop_test - start_test, 3)} seconds")


if __name__ == "__main__":
    quick_test()
