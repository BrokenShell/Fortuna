from Fortuna import *


def range_accuracy(func, *args, expected_range, verbose=True, **kwargs):
    results = {func(*args, **kwargs) for _ in range(200000)}
    for itm in results:
        assert itm in expected_range, f"Range Error, range exceeded ({itm})."
    for itm in expected_range:
        assert itm in results, f"Range Warning, range not satisfied ({itm})."
    if verbose:
        print(f"{func.__name__}{args + tuple(kwargs)}: Success")


def range_tests():
    print("\n\nOutput Range Tests: ")
    range_accuracy(random_below, 0, expected_range=(0,))
    range_accuracy(random_index, 0, expected_range=(-1,))
    range_accuracy(random_range, 0, expected_range=(0,))

    range_accuracy(random_below, 6, expected_range=range(6))
    range_accuracy(random_index, 6, expected_range=range(6))
    range_accuracy(random_range, 6, expected_range=range(6))

    range_accuracy(random_below, -6, expected_range=range(-5, 1))
    range_accuracy(random_index, -6, expected_range=range(-6, 0))
    range_accuracy(random_range, -6, expected_range=range(-6, 0))

    range_accuracy(random_int, -3, 3, expected_range=range(-3, 4))
    range_accuracy(random_int, 3, -3, expected_range=range(-3, 4))
    range_accuracy(random_range, -3, 3, expected_range=range(-3, 3))
    range_accuracy(random_range, 3, -3, expected_range=range(-3, 3))

    range_accuracy(random_range, 0, 12, 2, expected_range=range(0, 12, 2))
    range_accuracy(random_range, 12, 0, 2, expected_range=range(0, 12, 2))

    range_accuracy(random_range, -6, 6, 2, expected_range=range(-6, 6, 2))
    range_accuracy(random_range, 6, -6, 2, expected_range=range(-6, 6, 2))

    range_accuracy(random_range, -6, 6, -2, expected_range=(-4, -2, 0, 2, 4, 6))
    range_accuracy(random_range, 6, -6, -2, expected_range=(-4, -2, 0, 2, 4, 6))

    range_accuracy(random_range, 1, 20, -2, expected_range=range(2, 21, 2))
    range_accuracy(random_range, 1, 20, 2, expected_range=range(1, 20, 2))

    range_accuracy(d, 6, expected_range=range(1, 7))
    range_accuracy(d, -6, expected_range=range(-6, 0))
    range_accuracy(dice, 2, 6, expected_range=range(2, 13))
    range_accuracy(dice, -2, -6, expected_range=range(2, 13))

    range_accuracy(plus_or_minus, 3, expected_range=range(-3, 4))
    range_accuracy(plus_or_minus_linear, 3, expected_range=range(-3, 4))
    range_accuracy(plus_or_minus_gauss, 3, expected_range=range(-3, 4))
    range_accuracy(plus_or_minus_gauss, 100, expected_range=range(-100, 101))

    range_accuracy(front_gauss, 6, expected_range=range(6))
    range_accuracy(middle_gauss, 6, expected_range=range(6))
    range_accuracy(back_gauss, 6, expected_range=range(6))
    range_accuracy(quantum_gauss, 6, expected_range=range(6))
    range_accuracy(front_poisson, 6, expected_range=range(6))
    range_accuracy(middle_poisson, 6, expected_range=range(6))
    range_accuracy(back_poisson, 6, expected_range=range(6))
    range_accuracy(quantum_poisson, 6, expected_range=range(6))
    range_accuracy(front_linear, 6, expected_range=range(6))
    range_accuracy(middle_linear, 6, expected_range=range(6))
    range_accuracy(back_linear, 6, expected_range=range(6))
    range_accuracy(quantum_linear, 6, expected_range=range(6))
    range_accuracy(quantum_monty, 6, expected_range=range(6))

    range_accuracy(front_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(middle_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(back_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_gauss, -6, expected_range=range(-6, 0))
    range_accuracy(front_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(middle_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(back_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_poisson, -6, expected_range=range(-6, 0))
    range_accuracy(front_linear, -6, expected_range=range(-6, 0))
    range_accuracy(middle_linear, -6, expected_range=range(-6, 0))
    range_accuracy(back_linear, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_linear, -6, expected_range=range(-6, 0))
    range_accuracy(quantum_monty, -6, expected_range=range(-6, 0))

    range_accuracy(percent_true, 50, expected_range=(True, False))
    range_accuracy(percent_true, 0.1, expected_range=(True, False))

    print("Over All: Success!")


if __name__ == "__main__":
    range_tests()
