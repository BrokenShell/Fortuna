import pytest

import Fortuna

SCALAR_FAST_PATHS = (
    ("random_uint", (7, 10_007)),
    ("ability_dice", (6,)),
    ("plus_or_minus", (31,)),
    ("plus_or_minus_triangular", (31,)),
    ("plus_or_minus_normal", (31,)),
    ("front_triangular", (101,)),
    ("center_triangular", (101,)),
    ("back_triangular", (101,)),
    ("mixed_triangular", (101,)),
    ("front_exponential", (101,)),
    ("center_normal", (101,)),
    ("back_exponential", (101,)),
    ("mixed_exponential_normal", (101,)),
    ("front_poisson", (101,)),
    ("edge_poisson", (101,)),
    ("back_poisson", (101,)),
    ("quantum_monty", (101,)),
)

INVALID_SCALAR_FAST_PATHS = (
    ("random_uint", (2, 1)),
    ("ability_dice", (2,)),
    ("plus_or_minus_normal", (-1,)),
    ("front_triangular", (0,)),
    ("quantum_monty", (0,)),
)

COUNT_PRECEDENCE_CASES = (
    ("random_uint", (2, 1)),
    ("ability_dice", (2,)),
    ("plus_or_minus", (-1,)),
    ("front_poisson", (0,)),
)


@pytest.mark.parametrize(("method", "args"), SCALAR_FAST_PATHS)
def test_generator_scalar_fast_paths_match_bulk_sequence(method, args):
    bulk = Fortuna.Generator(0xF07A_6001)
    scalar = Fortuna.Generator(0xF07A_6001)

    assert getattr(bulk, method)(*args, count=64) == [
        getattr(scalar, method)(*args) for _ in range(64)
    ]


@pytest.mark.parametrize(("method", "args"), SCALAR_FAST_PATHS)
def test_module_scalar_fast_paths_match_bulk_sequence(method, args):
    function = getattr(Fortuna, method)
    Fortuna.seed(0xF07A_6001)
    expected = function(*args, count=64)
    Fortuna.seed(0xF07A_6001)

    assert [function(*args) for _ in range(64)] == expected


@pytest.mark.parametrize(("method", "args"), INVALID_SCALAR_FAST_PATHS)
def test_invalid_generator_scalar_fast_paths_do_not_advance(method, args):
    tested = Fortuna.Generator(0xF07A_6002)
    control = Fortuna.Generator(0xF07A_6002)

    with pytest.raises(ValueError):
        getattr(tested, method)(*args)

    assert tested.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(("method", "args"), INVALID_SCALAR_FAST_PATHS)
def test_invalid_module_scalar_fast_paths_do_not_advance(method, args):
    Fortuna.seed(0xF07A_6002)
    control = Fortuna.Generator(0xF07A_6002)

    with pytest.raises(ValueError):
        getattr(Fortuna, method)(*args)

    assert Fortuna.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(("method", "args"), COUNT_PRECEDENCE_CASES)
@pytest.mark.parametrize("owner_kind", ["module", "generator"])
def test_scalar_fast_path_count_error_precedes_parameter_error(owner_kind, method, args):
    owner = Fortuna if owner_kind == "module" else Fortuna.Generator(0xF07A_6003)

    with pytest.raises(ValueError, match="count must be nonnegative"):
        getattr(owner, method)(*args, count=-1)
