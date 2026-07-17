from collections import deque

import pytest

import Fortuna
from Fortuna import RandomValue, TruffleShuffle, WeightedChoice, _core

SEED = 0xF07A_6005
SIZE = 100
COUNT = 64


def test_random_value_uniform_path_preserves_native_schedule():
    generator = Fortuna.Generator(SEED)
    control = Fortuna.Generator(SEED)
    selector = RandomValue(range(SIZE), resolve_callables=False, generator=generator)

    assert selector.take(COUNT) == [control.random_value(range(SIZE)) for _ in range(COUNT)]
    assert generator.random_below(2**64) == control.random_below(2**64)


@pytest.mark.parametrize(
    "method",
    ["front_triangular", "center_triangular", "back_triangular"],
)
def test_random_value_triangular_paths_preserve_native_schedule(method):
    generator = Fortuna.Generator(SEED)
    control = Fortuna.Generator(SEED)
    selector = RandomValue(range(SIZE), resolve_callables=False, generator=generator)

    actual = [getattr(selector, method)() for _ in range(COUNT)]
    expected = [getattr(control, method)(SIZE) for _ in range(COUNT)]

    assert actual == expected
    assert generator.random_below(2**64) == control.random_below(2**64)


@pytest.mark.parametrize(
    ("method", "result"),
    [
        ("random_index", SIZE),
        ("front_triangular", -1),
        ("center_triangular", False),
        ("back_triangular", SIZE),
    ],
)
def test_random_value_validates_monkeypatched_module_indexes(monkeypatch, method, result):
    selector = RandomValue(range(SIZE), resolve_callables=False)
    monkeypatch.setattr(_core, method, lambda size: result)

    with pytest.raises((TypeError, ValueError)):
        getattr(selector, "uniform" if method == "random_index" else method)()


@pytest.mark.parametrize(
    "method",
    ["front_triangular", "center_triangular", "back_triangular"],
)
def test_random_value_triangular_paths_preserve_callable_resolution(method):
    selector = RandomValue(
        (lambda value: value + 1,),
        generator=Fortuna.Generator(SEED),
    )

    assert getattr(selector, method)(4) == 5


@pytest.mark.parametrize(
    "method",
    ["front_normal", "center_normal", "back_normal"],
)
def test_random_value_normal_paths_preserve_callable_resolution(method):
    selector = RandomValue(
        (lambda value: value + 1,),
        generator=Fortuna.Generator(SEED),
    )

    assert getattr(selector, method)(4) == 5


def test_truffle_shuffle_matches_native_shuffle_and_rotation_schedule():
    generator = Fortuna.Generator(SEED)
    control = Fortuna.Generator(SEED)
    selector = TruffleShuffle(range(SIZE), resolve_callables=False, generator=generator)

    expected = list(range(SIZE))
    control.shuffle(expected)
    expected = deque(expected)
    rotate_size = selector.rotate_size
    observed = []
    for _ in range(COUNT):
        expected.rotate(1 + control._front_poisson(rotate_size))
        observed.append(expected[-1])

    assert selector.take(COUNT) == observed
    assert generator.random_below(2**64) == control.random_below(2**64)


def test_module_truffle_shuffle_preserves_seeded_schedule_and_state():
    Fortuna.seed(SEED)
    control = Fortuna.Generator(SEED)
    selector = TruffleShuffle(range(SIZE), resolve_callables=False)

    expected = list(range(SIZE))
    control.shuffle(expected)
    expected = deque(expected)
    observed = []
    for _ in range(COUNT):
        expected.rotate(1 + control._front_poisson(selector.rotate_size))
        observed.append(expected[-1])

    assert selector.take(COUNT) == observed
    assert Fortuna.random_below(2**64) == control.random_below(2**64)


@pytest.mark.parametrize("size", [4, 100, 1000])
def test_weighted_choice_preserves_native_schedule_and_state(size):
    weights = tuple(0.0 if index % 7 == 0 else float(index % 5 + 1) for index in range(size))
    table = tuple(zip(weights, range(size), strict=True))
    total = sum(weights)
    cumulative = []
    running = 0.0
    for weight in weights:
        running += weight
        cumulative.append(running)

    relative_generator = Fortuna.Generator(SEED)
    cumulative_generator = Fortuna.Generator(SEED)
    control = Fortuna.Generator(SEED)
    relative_selector = WeightedChoice(
        relative=table,
        resolve_callables=False,
        generator=relative_generator,
    )
    cumulative_selector = WeightedChoice(
        cumulative=tuple(zip(cumulative, range(size), strict=True)),
        resolve_callables=False,
        generator=cumulative_generator,
    )
    expected = []
    for _ in range(COUNT):
        draw = control.random_float(0.0, total)
        expected.append(next(index for index, boundary in enumerate(cumulative) if draw < boundary))

    assert relative_selector.take(COUNT) == expected
    assert cumulative_selector.take(COUNT) == expected
    expected_state = control.random_below(2**64)
    assert relative_generator.random_below(2**64) == expected_state
    assert cumulative_generator.random_below(2**64) == expected_state


def test_module_weighted_choice_preserves_seeded_schedule_and_state():
    table = ((0.0, "zero"), (1.0, "common"), (3.0, "rare"))
    Fortuna.seed(SEED)
    control = Fortuna.Generator(SEED)
    selector = WeightedChoice(table, resolve_callables=False)

    expected = []
    for _ in range(COUNT):
        draw = control.random_float(0.0, 4.0)
        expected.append("common" if draw < 1.0 else "rare")

    assert selector.take(COUNT) == expected
    assert Fortuna.random_below(2**64) == control.random_below(2**64)


def test_module_cumulative_weighted_choice_preserves_seeded_schedule_and_state():
    table = ((0.0, "zero"), (1.0, "common"), (4.0, "rare"))
    Fortuna.seed(SEED)
    control = Fortuna.Generator(SEED)
    selector = WeightedChoice(cumulative=table, resolve_callables=False)

    expected = []
    for _ in range(COUNT):
        draw = control.random_float(0.0, 4.0)
        expected.append("common" if draw < 1.0 else "rare")

    assert selector.take(COUNT) == expected
    assert Fortuna.random_below(2**64) == control.random_below(2**64)


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: WeightedChoice(((1.0, "value"),), resolve_callables=False),
        lambda: WeightedChoice(cumulative=((1.0, "value"),), resolve_callables=False),
    ],
)
def test_weighted_choice_observes_module_monkeypatch_after_construction(monkeypatch, constructor):
    selector = constructor()
    monkeypatch.setattr(_core, "random_float", lambda low, high: high)

    with pytest.raises(ValueError, match="must be in"):
        selector()


def test_weighted_choice_feeds_normalized_boundaries_to_the_native_selector(monkeypatch):
    observed = []

    class Selector:
        def __call__(self):
            return 0

    def prepare(boundaries, generator):
        observed.append((tuple(boundaries), generator))
        return Selector()

    monkeypatch.setattr(_core, "_prepared_cumulative_weighted_index", prepare)
    WeightedChoice(relative=((1.0, "a"), (2.0, "b"), (1.0, "c")))
    WeightedChoice(cumulative=((1.0, "a"), (3.0, "b"), (4.0, "c")))

    assert observed == [((1.0, 3.0, 4.0), None), ((1.0, 3.0, 4.0), None)]


def test_module_random_value_fast_path_observes_monkeypatches(monkeypatch):
    monkeypatch.setattr(_core, "random_index", lambda size: size - 1)
    assert Fortuna.random_value(("first", "last")) == "last"


def test_native_sample_and_shuffle_preserve_generator_state():
    first = Fortuna.Generator(SEED)
    second = Fortuna.Generator(SEED)

    values = list(range(SIZE))
    first.shuffle(values)
    expected = list(range(SIZE))
    second.shuffle(expected)
    assert values == expected

    assert first.sample(range(SIZE), 20) == second.sample(range(SIZE), 20)
    assert first.random_below(2**64) == second.random_below(2**64)


def test_custom_generator_sample_consumes_one_validated_offset_per_value():
    class Generator:
        def __init__(self):
            self.values = deque((3, 1, 0))

        def random_index(self, size):
            return self.values.popleft()

    assert Fortuna.sample(range(5), 3, generator=Generator()) == [3, 2, 1]
