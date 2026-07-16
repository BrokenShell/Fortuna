import inspect
import math
import subprocess
import sys
import threading
from collections.abc import MutableSequence
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest

import Fortuna


def test_version_and_seed_zero_are_deterministic():
    assert Fortuna.storm_version() == "5.0.1"
    first = Fortuna.Generator(0)
    second = Fortuna.Generator(0)
    assert first.random_uint(0, 2**64 - 1, count=32) == second.random_uint(0, 2**64 - 1, count=32)


def test_generator_constructor_exposes_its_runtime_signature():
    assert Fortuna.Generator.__text_signature__ == "(seed=0)"
    assert str(inspect.signature(Fortuna.Generator)) == "(seed=0)"
    assert (
        Fortuna.Generator.__doc__
        == "Owned random engine with deterministic and entropy construction modes."
    )


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("percent_true", (37.5,)),
        ("bernoulli_variate", (0.375,)),
        ("random_below", (101,)),
        ("random_index", (101,)),
        ("random_int", (-10, 10)),
        ("random_uint", (0, 100)),
        ("random_range", (-20, 30, 3)),
        ("d", (20,)),
        ("dice", (3, 6)),
        ("canonical", ()),
        ("random_float", (-2.5, 7.25)),
        ("triangular", (-2.5, 7.25, 1.0)),
        ("exponential_variate", (2.5,)),
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


@pytest.mark.parametrize(
    ("function", "args"),
    [
        (Fortuna.percent_true, (37.5,)),
        (Fortuna.bernoulli_variate, (0.375,)),
        (Fortuna.random_below, (101,)),
        (Fortuna.random_index, (101,)),
        (Fortuna.random_int, (-10, 10)),
        (Fortuna.random_range, (-20, 30, 3)),
        (Fortuna.d, (20,)),
        (Fortuna.dice, (3, 6)),
        (Fortuna.random_float, (-2.5, 7.25)),
        (Fortuna.triangular, (-2.5, 7.25, 1.0)),
        (Fortuna.exponential_variate, (2.5,)),
        (Fortuna.normal_variate, (3.0, 2.0)),
    ],
)
def test_specialized_module_scalar_is_bulk_equivalent(function, args):
    Fortuna.seed(8128)
    expected = function(*args, count=64)
    Fortuna.seed(8128)
    assert [function(*args) for _ in range(64)] == expected


@pytest.mark.parametrize(
    ("method", "args", "expected"),
    [
        ("random_below", (1000,), [555, 385, 940, 353, 102, 1, 227, 650]),
        ("random_index", (1000,), [555, 385, 940, 353, 102, 1, 227, 650]),
        ("random_int", (-1000, 1000), [-153, 623, 983, 138, -242, 705, 778, -313]),
        (
            "random_range",
            (-1000, 1000, 3),
            [-460, -133, 947, 413, -727, 113, 332, -940],
        ),
    ],
)
def test_specialized_bounded_sequences_are_stable(method, args, expected):
    assert getattr(Fortuna.Generator(8128), method)(*args, count=8) == expected
    Fortuna.seed(8128)
    assert getattr(Fortuna, method)(*args, count=8) == expected


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("percent_true", (-1.0,)),
        ("bernoulli_variate", (1.5,)),
        ("random_below", (0,)),
        ("random_index", (0,)),
        ("random_int", (10, 1)),
        ("random_range", (0, 10, 0)),
        ("d", (0,)),
        ("dice", (2**63, 3)),
        ("random_float", (2.0, 1.0)),
        ("triangular", (0.0, 1.0, 2.0)),
        ("exponential_variate", (0.0,)),
        ("normal_variate", (0.0, -1.0)),
    ],
)
def test_invalid_specialized_generator_scalar_does_not_advance(method, args):
    tested = Fortuna.Generator(99)
    control = Fortuna.Generator(99)
    with pytest.raises((ValueError, OverflowError)):
        getattr(tested, method)(*args)
    assert tested.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(
    ("function", "args"),
    [
        (Fortuna.random_index, (0,)),
        (Fortuna.random_int, (10, 1)),
        (Fortuna.random_float, (2.0, 1.0)),
        (Fortuna.triangular, (0.0, 1.0, 2.0)),
    ],
)
def test_invalid_specialized_module_scalar_does_not_advance(function, args):
    Fortuna.seed(99)
    control = Fortuna.Generator(99)
    with pytest.raises(ValueError):
        function(*args)
    assert Fortuna.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize("owner", [Fortuna, Fortuna.Generator(99)])
@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("random_index", (0,)),
        ("random_int", (10, 1)),
        ("random_float", (2.0, 1.0)),
        ("triangular", (0.0, 1.0, 2.0)),
    ],
)
def test_bulk_count_error_precedes_specialized_parameter_error(owner, method, args):
    with pytest.raises(ValueError, match="count must be nonnegative"):
        getattr(owner, method)(*args, count=-1)


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


@pytest.mark.parametrize("owner_kind", ["module", "generator"])
@pytest.mark.parametrize(
    ("method", "args", "message"),
    [
        ("random_int", (-(2**63) - 1, 0), "low must be in the signed 64-bit range"),
        ("random_int", (0, 2**63), "high must be in the signed 64-bit range"),
        ("random_range", (0, 2**63), "stop must be in the signed 64-bit range"),
        ("random_uint", (0, 2**64), "high must be in the unsigned 64-bit range"),
        ("random_index", (2**64,), "size must be in the unsigned 64-bit range"),
    ],
)
def test_integer_overflow_names_the_parameter_without_advancing(owner_kind, method, args, message):
    seed = 0xF07A_6004
    control = Fortuna.Generator(seed)
    if owner_kind == "module":
        Fortuna.seed(seed)
        owner = Fortuna
    else:
        owner = Fortuna.Generator(seed)

    with pytest.raises(OverflowError, match=message):
        getattr(owner, method)(*args)

    assert owner.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize("owner_kind", ["module", "generator"])
def test_count_overflow_is_parameter_specific_and_does_not_advance(owner_kind):
    seed = 0xF07A_6005
    control = Fortuna.Generator(seed)
    if owner_kind == "module":
        Fortuna.seed(seed)
        owner = Fortuna
    else:
        owner = Fortuna.Generator(seed)

    with pytest.raises(OverflowError, match="count exceeds the platform size limit"):
        owner.random_int(0, 1, count=2**64)

    assert owner.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


def test_integer_overflow_precedence_remains_coercion_then_count_then_domain():
    generator = Fortuna.Generator(0xF07A_6006)

    with pytest.raises(OverflowError, match="low must be in the signed 64-bit range"):
        generator.random_int(-(2**63) - 1, -2, count=-1)
    with pytest.raises(OverflowError, match="count exceeds the platform size limit"):
        generator.random_int(2, 1, count=2**64)


def test_seed_overflow_names_seed_and_preserves_existing_state():
    seed = 0xF07A_6007
    generator = Fortuna.Generator(seed)
    control = Fortuna.Generator(seed)

    with pytest.raises(OverflowError, match="seed must be in the unsigned 64-bit range"):
        generator.seed(2**64)
    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)

    Fortuna.seed(seed)
    control = Fortuna.Generator(seed)
    with pytest.raises(OverflowError, match="seed must be in the unsigned 64-bit range"):
        Fortuna.seed(2**64)
    assert Fortuna.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


def test_index_protocol_overflow_uses_the_same_parameter_specific_errors():
    class HugeSigned:
        def __index__(self):
            return 2**63

    class HugeUnsigned:
        def __index__(self):
            return 2**64

    class HugeCount:
        def __index__(self):
            return 2**64

    generator = Fortuna.Generator(1)
    with pytest.raises(OverflowError, match="high must be in the signed 64-bit range"):
        generator.random_int(0, HugeSigned())
    with pytest.raises(OverflowError, match="size must be in the unsigned 64-bit range"):
        generator.random_index(HugeUnsigned())
    with pytest.raises(OverflowError, match="count exceeds the platform size limit"):
        generator.canonical(count=HugeCount())


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
    expected_next = 295_456_441_680_805_878
    generator_values = list(range(10))
    generator = Fortuna.Generator(101)
    generator.shuffle(generator_values)
    assert generator_values == expected
    assert generator.random_uint(0, 2**64 - 1) == expected_next

    module_values = list(range(10))
    Fortuna.seed(101)
    Fortuna.shuffle(module_values)
    assert module_values == expected
    assert Fortuna.random_uint(0, 2**64 - 1) == expected_next


@pytest.mark.parametrize("size", [2, 10, 100, 256, 257])
def test_exact_list_shuffle_fast_path_preserves_knuth_b_schedule_and_state(size):
    seed = 0xF07A_6000 + size
    expected = list(range(size))
    control = Fortuna.Generator(seed)
    last = size - 1
    for position in range(last - 1, -1, -1):
        other = control.random_uint(position, last)
        expected[position], expected[other] = expected[other], expected[position]
    expected_next = control.random_uint(0, 2**64 - 1)

    generator_values = list(range(size))
    generator = Fortuna.Generator(seed)
    generator.shuffle(generator_values)
    assert generator_values == expected
    assert generator.random_uint(0, 2**64 - 1) == expected_next

    module_values = list(range(size))
    Fortuna.seed(seed)
    Fortuna.shuffle(module_values)
    assert module_values == expected
    assert Fortuna.random_uint(0, 2**64 - 1) == expected_next


@pytest.mark.parametrize("values", [[], [0]])
def test_degenerate_shuffle_consumes_no_entropy(values):
    generator = Fortuna.Generator(101)
    control = Fortuna.Generator(101)
    generator.shuffle(values)
    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)

    Fortuna.seed(101)
    Fortuna.shuffle(values)
    actual = Fortuna.random_uint(0, 2**64 - 1)
    Fortuna.seed(101)
    assert actual == Fortuna.random_uint(0, 2**64 - 1)


def test_generator_shuffle_releases_lock_before_sequence_callbacks():
    entered = threading.Event()
    release = threading.Event()

    class BlockingList(list):
        def __getitem__(self, index):
            if not entered.is_set():
                entered.set()
                assert release.wait(timeout=5)
            return super().__getitem__(index)

    generator = Fortuna.Generator(8128)
    control = Fortuna.Generator(8128)
    values = BlockingList(range(10))
    for position in range(8, -1, -1):
        control.random_uint(position, 9)
    expected = control.random_uint(0, 2**64 - 1)

    with ThreadPoolExecutor(max_workers=2) as executor:
        shuffle_future = executor.submit(generator.shuffle, values)
        assert entered.wait(timeout=2)
        draw_future = executor.submit(generator.random_uint, 0, 2**64 - 1)
        try:
            actual = draw_future.result(timeout=1)
        except TimeoutError:
            release.set()
            shuffle_future.result(timeout=2)
            draw_future.result(timeout=2)
            pytest.fail("Generator.shuffle held its native lock during a sequence callback")
        finally:
            release.set()
        shuffle_future.result(timeout=2)

    assert actual == expected
    assert sorted(values) == list(range(10))


def test_generator_shuffle_sequence_callback_can_reenter_generator_without_deadlock():
    script = """
from Fortuna import Generator

class ReentrantList(list):
    def __init__(self, values, generator):
        super().__init__(values)
        self.generator = generator
        self.calls = 0

    def __getitem__(self, index):
        self.calls += 1
        self.generator.random_uint(0, 2**64 - 1)
        return super().__getitem__(index)

generator = Generator(8128)
values = ReentrantList(range(10), generator)
generator.shuffle(values)
assert values.calls > 0
assert sorted(values) == list(range(10))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        check=False,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr


def test_shuffle_callback_error_consumes_complete_index_schedule_and_releases_lock():
    class ExplodingList(list):
        def __getitem__(self, index):
            raise RuntimeError("sequence callback failed")

    generator = Fortuna.Generator(8128)
    control = Fortuna.Generator(8128)
    for position in range(8, -1, -1):
        control.random_uint(position, 9)

    with pytest.raises(RuntimeError, match="sequence callback failed"):
        generator.shuffle(ExplodingList(range(10)))

    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


def test_shuffle_reports_oversized_index_schedule_as_memory_error():
    class VirtualSequence(MutableSequence):
        def __len__(self):
            return sys.maxsize

        def __getitem__(self, index):
            raise AssertionError("oversized shuffle must fail before sequence access")

        def __setitem__(self, index, value):
            raise AssertionError("oversized shuffle must fail before sequence access")

        def __delitem__(self, index):
            raise NotImplementedError

        def insert(self, index, value):
            raise NotImplementedError

    with pytest.raises(MemoryError, match="shuffle index schedule is too large"):
        Fortuna.Generator(8128).shuffle(VirtualSequence())


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
