from collections import deque

import pytest

import Fortuna
from Fortuna import RandomValue, TruffleShuffle, WeightedChoice, random_value, sample, shuffle


class FixedGenerator:
    def __init__(self, *, indices=(0,), floats=(0.0,), poisson=(0,)):
        self.indices = deque(indices)
        self.floats = deque(floats)
        self.poisson = deque(poisson)

    def random_index(self, size):
        return self.indices.popleft()

    def front_triangular(self, size):
        return self.random_index(size)

    def center_triangular(self, size):
        return self.random_index(size)

    def back_triangular(self, size):
        return self.random_index(size)

    def random_float(self, low=0.0, high=1.0):
        return self.floats.popleft()

    def poisson_variate(self, mean):
        return self.poisson.popleft()


def test_random_value_function_materializes_iterables_and_validates_custom_draws():
    generator = FixedGenerator(indices=(1,))
    assert random_value((value for value in ("zero", "one")), generator=generator) == "one"

    with pytest.raises(ValueError, match="data must not be empty"):
        random_value(())
    with pytest.raises(ValueError, match="outside"):
        random_value((1, 2), generator=FixedGenerator(indices=(2,)))
    with pytest.raises(TypeError, match="not bool"):
        random_value((1, 2), generator=FixedGenerator(indices=(False,)))


def test_custom_shuffle_and_sample_validate_injected_indexes():
    values = [0, 1, 2]
    shuffle(values, generator=FixedGenerator(indices=(0, 0)))
    assert sorted(values) == [0, 1, 2]
    assert sample(range(4), 2, generator=FixedGenerator(indices=(3, 1))) == [3, 2]

    with pytest.raises(ValueError, match="outside"):
        shuffle([0, 1], generator=FixedGenerator(indices=(2,)))
    with pytest.raises(ValueError, match="sample size"):
        sample(range(2), 3)


def test_random_value_is_uniform_by_default_and_exposes_slim_strategies():
    selector = RandomValue(
        ("front", "center", "back"), generator=FixedGenerator(indices=(1, 2, 0, 1))
    )

    assert selector() == "center"
    assert selector.uniform() == "back"
    assert selector.front_triangular() == "front"
    assert selector.center_triangular() == "center"


def test_random_value_cycle_take_and_callable_resolution():
    selector = RandomValue(
        (lambda value: value + 1, lambda: 7), generator=FixedGenerator(indices=(0,))
    )

    assert selector(4) == 5
    assert selector.cycle(9) == 10
    assert selector.cycle() == 7
    assert RandomValue((1, 2), generator=FixedGenerator(indices=(0, 1))).take(2) == [1, 2]

    def value():
        return 3

    assert RandomValue((value,), resolve_callables=False)() is value
    with pytest.raises(TypeError, match="resolve_callables"):
        RandomValue((1,), resolve_callables=1)


def test_callable_resolution_rejects_cycles_and_runaway_chains():
    class Loop:
        def __call__(self):
            return self

    with pytest.raises(RuntimeError, match="cycle"):
        RandomValue((Loop(),))()

    class Link:
        def __init__(self, remaining):
            self.remaining = remaining

        def __call__(self):
            return Link(self.remaining - 1) if self.remaining else "done"

    with pytest.raises(RuntimeError, match="max_depth=100"):
        RandomValue((Link(101),))()


def test_random_value_truffle_shuffle_is_lazy_and_reused():
    selector = RandomValue(range(16), generator=Fortuna.Generator(42))
    assert selector._truffle is None

    first = selector.truffle_shuffle()
    truffle = selector._truffle
    second = selector.truffle_shuffle()

    assert truffle is not None
    assert selector._truffle is truffle
    assert first in range(16)
    assert second in range(16)


def test_truffle_shuffle_is_stateful_and_validates_custom_poisson_draws():
    selector = TruffleShuffle(range(4), generator=FixedGenerator(indices=(0, 0, 0), poisson=(0, 0)))
    assert selector() in range(4)
    assert selector() in range(4)

    broken = TruffleShuffle(range(4), generator=FixedGenerator(indices=(0, 0, 0), poisson=(-1,)))
    with pytest.raises(ValueError, match="nonnegative"):
        broken()


def test_weighted_choice_uses_relative_weights_and_boundary_draws():
    table = ((1, "first"), (2, "second"), (1, "third"))
    assert WeightedChoice(table, generator=FixedGenerator(floats=(0.0,)))() == "first"
    assert WeightedChoice(table, generator=FixedGenerator(floats=(1.0,)))() == "second"
    assert WeightedChoice(table, generator=FixedGenerator(floats=(3.5,)))() == "third"


@pytest.mark.parametrize(
    "table",
    [(), ((-1, "bad"),), ((0, "zero"),), ((float("inf"), "bad"),)],
)
def test_weighted_choice_rejects_invalid_tables(table):
    with pytest.raises((TypeError, ValueError)):
        WeightedChoice(table)


@pytest.mark.parametrize("draw", [False, -0.1, 1.0, float("nan"), float("inf")])
def test_weighted_choice_validates_custom_draws(draw):
    choice = WeightedChoice(((1, "value"),), generator=FixedGenerator(floats=(draw,)))
    with pytest.raises((TypeError, ValueError)):
        choice()


def test_weighted_choice_resolves_selected_callables_and_supports_take():
    choice = WeightedChoice(
        ((1, lambda value=3: value),), generator=FixedGenerator(floats=(0.0, 0.0))
    )
    assert choice() == 3
    assert choice.take(1, 8) == [8]
