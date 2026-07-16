import math

import pytest

import Fortuna


def test_version_and_seed_zero_are_deterministic():
    assert Fortuna.storm_version() == "5.0.1"
    first = Fortuna.Generator(0)
    second = Fortuna.Generator(0)
    assert first.random_uint(0, 2**64 - 1, count=32) == second.random_uint(0, 2**64 - 1, count=32)


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("random_int", (-10, 10)),
        ("random_uint", (0, 100)),
        ("random_range", (-20, 30, 3)),
        ("canonical", ()),
        ("normal_variate", (3.0, 2.0)),
        ("front_triangular", (17,)),
        ("quantum_monty", (17,)),
    ],
)
def test_bulk_is_scalar_equivalent(method, args):
    bulk = Fortuna.Generator(8128)
    scalar = Fortuna.Generator(8128)
    assert getattr(bulk, method)(*args, count=64) == [
        getattr(scalar, method)(*args) for _ in range(64)
    ]


def test_canonical_sequence_is_stable():
    expected = [
        0.755155532954539,
        0.6390313938546974,
        0.7521452007480266,
        0.13627268363243705,
        0.9032689664283783,
    ]
    generator = Fortuna.Generator(42)
    assert generator.canonical(count=0) == []
    assert generator.canonical(count=5) == expected
    Fortuna.seed(42)
    assert Fortuna.canonical(count=0) == []
    assert Fortuna.canonical(count=5) == expected


def test_integer_boundaries_do_not_round_through_float():
    generator = Fortuna.Generator(7)
    minimum = -(2**63)
    maximum = 2**63 - 1
    assert generator.random_int(minimum, minimum) == minimum
    assert generator.random_int(maximum, maximum) == maximum
    assert generator.random_uint(2**64 - 1, 2**64 - 1) == 2**64 - 1
    assert all(
        value in {2**53 - 1, 2**53, 2**53 + 1}
        for value in generator.random_int(2**53 - 1, 2**53 + 1, count=128)
    )


def test_python_style_directed_random_range():
    generator = Fortuna.Generator(4)
    assert all(0 <= value < 10 for value in generator.random_range(10, count=50))
    assert all(value in range(10, -1, -2) for value in generator.random_range(10, -1, -2, count=50))
    with pytest.raises(ValueError):
        generator.random_range(10, 0, 1)
    with pytest.raises(ValueError):
        generator.random_range(0, 10, 0)


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("random_int", (10, 1)),
        ("random_range", (0, 10, 0)),
        ("normal_variate", (0.0, -1.0)),
        ("front_poisson", (0,)),
    ],
)
def test_count_zero_still_validates_without_advancing(method, args):
    tested = Fortuna.Generator(99)
    control = Fortuna.Generator(99)
    with pytest.raises((ValueError, OverflowError)):
        getattr(tested, method)(*args, count=0)
    assert tested.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


def test_zero_count_and_count_validation():
    assert Fortuna.Generator(1).random_int(0, 1, count=0) == []
    with pytest.raises(ValueError):
        Fortuna.random_int(0, 1, count=-1)
    with pytest.raises(TypeError):
        Fortuna.random_int(0, 1, count=True)


def test_stream_derivation_is_stable_and_type_domain_separated():
    values = []
    for stream_id in (7, "7", b"7", -7, "worker-3"):
        first = Fortuna.for_stream(42, stream_id)
        second = Fortuna.Generator.for_stream(42, stream_id)
        assert first.random_uint(0, 2**64 - 1) == second.random_uint(0, 2**64 - 1)
        values.append(Fortuna.for_stream(42, stream_id).random_uint(0, 2**64 - 1))
    assert len(set(values)) == len(values)
    assert values == [
        1_196_009_599_846_878_293,
        8_555_391_131_741_082_812,
        9_487_148_860_459_484_187,
        17_027_638_332_073_367_379,
        29_152_502_809_120_148,
    ]
    with pytest.raises(TypeError):
        Fortuna.for_stream(42, True)


def test_degenerate_distributions_have_deliberate_behavior():
    generator = Fortuna.Generator(3)
    maximum = float.fromhex("0x1.fffffffffffffp+1023")
    assert generator.poisson_variate(0.0, count=4) == [0, 0, 0, 0]
    assert generator.normal_variate(8.5, 0.0) == 8.5
    assert generator.normal_variate(maximum, 0.0) == maximum
    assert generator.normal_variate(maximum, 0.0, count=2) == [maximum, maximum]
    assert generator.log_normal_variate(math.log(3.0), 0.0) == pytest.approx(3.0)
    with pytest.raises(OverflowError):
        generator.log_normal_variate(1000.0, 0.0)


def test_extreme_triangular_span_rejected_and_huge_vonmises_terminates():
    generator = Fortuna.Generator(5)
    with pytest.raises(OverflowError):
        generator.triangular(
            -float.fromhex("0x1.fffffffffffffp+1023"), float.fromhex("0x1.fffffffffffffp+1023"), 0.0
        )
    value = generator.vonmises_variate(0.0, float.fromhex("0x1.fffffffffffffp+1023"))
    assert math.isfinite(value)
    assert 0.0 <= value < math.tau


def test_generator_collection_operations():
    generator = Fortuna.Generator(101)
    assert generator.random_value(("only",)) == "only"
    data = list(range(20))
    generator.shuffle(data)
    assert sorted(data) == list(range(20))
    result = generator.sample(range(20), 7)
    assert len(result) == 7
    assert len(set(result)) == 7
    with pytest.raises(ValueError):
        generator.sample(range(2), 3)


def test_knuth_b_shuffle_is_deterministic_for_module_and_generator():
    expected = [5, 8, 1, 7, 3, 4, 6, 9, 0, 2]
    generator_values = list(range(10))
    Fortuna.Generator(101).shuffle(generator_values)
    assert generator_values == expected

    module_values = list(range(10))
    Fortuna.seed(101)
    Fortuna.shuffle(module_values)
    assert module_values == expected


@pytest.mark.parametrize(
    "function",
    [
        Fortuna._core._benchmark_shuffle_knuth_b,
        Fortuna._core._benchmark_shuffle_fisher_yates,
    ],
)
def test_internal_shuffle_benchmark_variants_preserve_contents(function):
    values = list(range(100))
    Fortuna.seed(0x5EED)
    function(values)
    assert sorted(values) == list(range(100))


def test_generator_random_value_materializes_iterables():
    generator = Fortuna.Generator(1)
    assert generator.random_value(value for value in ("only",)) == "only"
    with pytest.raises(ValueError):
        generator.random_value(iter(()))


def test_invalid_shuffle_does_not_advance_generator():
    generator = Fortuna.Generator(55)
    control = Fortuna.Generator(55)
    with pytest.raises(TypeError, match="mutable sequence"):
        generator.shuffle((1, 2, 3))
    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


def test_random_below_supports_the_full_uint64_domain():
    generator = Fortuna.Generator(0)
    values = generator.random_below(2**64, count=32)
    assert all(0 <= value < 2**64 for value in values)
    assert any(value > 2**63 - 1 for value in values)

    Fortuna.seed(0)
    assert Fortuna.random_below(2**64, count=32) == values
    with pytest.raises(OverflowError):
        generator.random_below(2**64 + 1)
    with pytest.raises(OverflowError):
        generator.random_index(2**64)


def test_ability_dice_has_no_historical_upper_clamp():
    values = Fortuna.Generator(22).ability_dice(100, count=20)
    assert all(3 <= value <= 18 for value in values)
