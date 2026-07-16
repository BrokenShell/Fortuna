"""Release contract matrix for every count-aware numeric API."""

import inspect

import pytest

import Fortuna

API_CASES = (
    ("canonical", ()),
    ("percent_true", (50.0,)),
    ("bernoulli_variate", (0.5,)),
    ("random_below", (1_000,)),
    ("random_index", (1_000,)),
    ("random_int", (-1_000, 1_000)),
    ("random_uint", (0, 1_000)),
    ("random_range", (-1_000, 1_000, 3)),
    ("d", (20,)),
    ("dice", (3, 6)),
    ("ability_dice", (4,)),
    ("plus_or_minus", (100,)),
    ("plus_or_minus_triangular", (100,)),
    ("plus_or_minus_normal", (100,)),
    ("random_float", (-1.0, 1.0)),
    ("triangular", (0.0, 1.0, 0.5)),
    ("beta_variate", (2.0, 5.0)),
    ("pareto_variate", (2.0,)),
    ("vonmises_variate", (0.0, 1.0)),
    ("binomial_variate", (100, 0.5)),
    ("negative_binomial_variate", (10, 0.5)),
    ("geometric_variate", (0.5,)),
    ("poisson_variate", (4.0,)),
    ("exponential_variate", (1.0,)),
    ("gamma_variate", (2.0, 3.0)),
    ("weibull_variate", (2.0, 3.0)),
    ("normal_variate", (0.0, 1.0)),
    ("log_normal_variate", (0.0, 1.0)),
    ("extreme_value_variate", (0.0, 1.0)),
    ("chi_squared_variate", (4.0,)),
    ("cauchy_variate", (0.0, 1.0)),
    ("fisher_f_variate", (4.0, 5.0)),
    ("student_t_variate", (4.0,)),
    ("front_triangular", (100,)),
    ("center_triangular", (100,)),
    ("back_triangular", (100,)),
    ("mixed_triangular", (100,)),
    ("front_exponential", (100,)),
    ("center_normal", (100,)),
    ("back_exponential", (100,)),
    ("mixed_exponential_normal", (100,)),
    ("front_poisson", (100,)),
    ("edge_poisson", (100,)),
    ("back_poisson", (100,)),
    ("quantum_monty", (100,)),
)


def test_contract_matrix_covers_every_public_count_api():
    expected = {method for method, _ in API_CASES}
    module_methods = {
        name
        for name in Fortuna.__all__
        if name != "Generator"
        and callable(method := getattr(Fortuna, name, None))
        and "count" in inspect.signature(method).parameters
    }
    generator_methods = {
        name
        for name in dir(Fortuna.Generator)
        if not name.startswith("_")
        and callable(method := getattr(Fortuna.Generator, name))
        and "count" in inspect.signature(method).parameters
    }

    assert module_methods == expected
    assert generator_methods == expected


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
def test_generator_bulk_matches_repeated_scalar_for_every_count_api(method, arguments):
    bulk_generator = Fortuna.Generator(8128)
    scalar_generator = Fortuna.Generator(8128)

    bulk = getattr(bulk_generator, method)(*arguments, count=8)
    scalar = [getattr(scalar_generator, method)(*arguments) for _ in range(8)]

    assert bulk == scalar


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
def test_module_bulk_matches_repeated_scalar_for_every_count_api(method, arguments):
    function = getattr(Fortuna, method)
    Fortuna.seed(8128)
    bulk = function(*arguments, count=8)
    Fortuna.seed(8128)
    scalar = [function(*arguments) for _ in range(8)]

    assert bulk == scalar


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
def test_zero_count_is_side_effect_free_for_every_count_api(method, arguments):
    tested = Fortuna.Generator(99)
    control = Fortuna.Generator(99)

    assert getattr(tested, method)(*arguments, count=0) == []
    assert tested.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
def test_module_zero_count_is_side_effect_free_for_every_count_api(method, arguments):
    Fortuna.seed(99)
    control = Fortuna.Generator(99)

    assert getattr(Fortuna, method)(*arguments, count=0) == []
    assert Fortuna.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
@pytest.mark.parametrize(
    ("count", "error", "message"),
    [
        (True, TypeError, "count must be an integer, not bool"),
        (-1, ValueError, "count must be nonnegative"),
    ],
)
def test_invalid_count_is_consistent_and_side_effect_free(method, arguments, count, error, message):
    tested = Fortuna.Generator(99)
    control = Fortuna.Generator(99)

    with pytest.raises(error, match=message):
        getattr(tested, method)(*arguments, count=count)
    assert tested.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(("method", "arguments"), API_CASES, ids=[case[0] for case in API_CASES])
@pytest.mark.parametrize(
    ("count", "error", "message"),
    [
        (True, TypeError, "count must be an integer, not bool"),
        (-1, ValueError, "count must be nonnegative"),
    ],
)
def test_module_invalid_count_is_consistent_and_side_effect_free(
    method, arguments, count, error, message
):
    Fortuna.seed(99)
    control = Fortuna.Generator(99)

    with pytest.raises(error, match=message):
        getattr(Fortuna, method)(*arguments, count=count)
    assert Fortuna.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)
