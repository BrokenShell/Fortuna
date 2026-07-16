from __future__ import annotations

import math
from collections import deque

import pytest

from Fortuna._selectors import (
    CumulativeWeightedChoice,
    FlexCat,
    IndexProfile,
    IndexSelector,
    QuantumMonty,
    RandomValue,
    RelativeWeightedChoice,
    TruffleShuffle,
    random_value,
    resolve,
    sample,
    shuffle,
)

PROFILE_METHODS = {
    IndexProfile.UNIFORM: "random_index",
    IndexProfile.FRONT_TRIANGULAR: "front_triangular",
    IndexProfile.CENTER_TRIANGULAR: "center_triangular",
    IndexProfile.BACK_TRIANGULAR: "back_triangular",
    IndexProfile.MIXED_TRIANGULAR: "mixed_triangular",
    IndexProfile.FRONT_EXPONENTIAL: "front_exponential",
    IndexProfile.CENTER_NORMAL: "center_normal",
    IndexProfile.BACK_EXPONENTIAL: "back_exponential",
    IndexProfile.MIXED_EXPONENTIAL_NORMAL: "mixed_exponential_normal",
    IndexProfile.FRONT_POISSON: "front_poisson",
    IndexProfile.EDGE_POISSON: "edge_poisson",
    IndexProfile.BACK_POISSON: "back_poisson",
    IndexProfile.QUANTUM_MONTY: "quantum_monty",
}


class FakeGenerator:
    def __init__(self, *, indices=(), floats=()) -> None:
        self.indices = deque(indices)
        self.floats = deque(floats)
        self.calls = []

    def random_index(self, size, *, count=None):
        self.calls.append(("random_index", size))
        if count is None:
            return self.indices.popleft() if self.indices else 0
        return [self.indices.popleft() if self.indices else 0 for _ in range(count)]

    def random_float(self, low, high):
        self.calls.append(("random_float", low, high))
        return self.floats.popleft() if self.floats else low

    def __getattr__(self, name):
        if name not in set(PROFILE_METHODS.values()) - {"random_index"}:
            raise AttributeError(name)

        def profile(size, *, count=None):
            self.calls.append((name, size))
            return 0 if count is None else [0] * count

        return profile


def test_index_profile_contains_only_canonical_names():
    assert {profile.value for profile in IndexProfile} == {
        "uniform",
        "front_triangular",
        "center_triangular",
        "back_triangular",
        "mixed_triangular",
        "front_exponential",
        "center_normal",
        "back_exponential",
        "mixed_exponential_normal",
        "front_poisson",
        "edge_poisson",
        "back_poisson",
        "quantum_monty",
    }
    for historical in (
        "front_linear",
        "middle_linear",
        "front_gauss",
        "middle_gauss",
        "quantum_gauss",
        "middle_poisson",
        "quantum_poisson",
    ):
        with pytest.raises(ValueError, match="unknown index profile"):
            IndexSelector(historical)


@pytest.mark.parametrize(("profile", "method"), PROFILE_METHODS.items())
def test_index_selector_routes_every_profile(profile, method):
    generator = FakeGenerator()
    selector = IndexSelector(profile.value, generator=generator)
    assert selector(7) == 0
    assert generator.calls == [(method, 7)]


def test_index_selector_bulk_and_validation():
    generator = FakeGenerator(indices=(2, 1, 0))
    selector = IndexSelector(generator=generator)
    assert selector.take(3, 4) == [2, 1, 0]
    assert selector(4, count=0) == []
    with pytest.raises(ValueError, match="size must be >= 1"):
        selector(0)
    with pytest.raises(ValueError, match="count must be >= 0"):
        selector(1, count=-1)
    with pytest.raises(TypeError, match="not bool"):
        selector(True)


def test_index_selector_bulk_uses_one_generator_call_and_validates_result():
    generator = FakeGenerator(indices=(2, 1, 0))
    selector = IndexSelector(generator=generator)
    assert selector(4, count=3) == [2, 1, 0]
    assert generator.calls == [("random_index", 4)]

    class BrokenBulkGenerator(FakeGenerator):
        def __init__(self, result):
            super().__init__()
            self.result = result

        def random_index(self, size, *, count=None):
            return self.result

    with pytest.raises(TypeError, match="must return a list"):
        IndexSelector(generator=BrokenBulkGenerator((0,)))(2, count=1)
    with pytest.raises(ValueError, match="expected 2"):
        IndexSelector(generator=BrokenBulkGenerator([0]))(2, count=2)
    with pytest.raises(ValueError, match=r"outside \[0, 2\)"):
        IndexSelector(generator=BrokenBulkGenerator([2]))(2, count=1)


def test_resolve_nested_callable_passes_arguments_only_to_first_call():
    def outer(number, *, increment):
        return lambda: number + increment

    assert resolve(outer, 4, increment=3) == 7

    def value():
        return 5

    assert resolve(value, resolve_callables=False) is value


def test_resolve_propagates_selected_callable_errors():
    def broken():
        raise TypeError("callable implementation failed")

    with pytest.raises(TypeError, match="implementation failed"):
        resolve(broken)


def test_resolve_detects_callable_cycles_and_depth_overflow():
    class Loop:
        def __call__(self):
            return self

    with pytest.raises(RuntimeError, match="cycle"):
        resolve(Loop())

    def first():
        return lambda: 1

    with pytest.raises(RuntimeError, match="max_depth=1"):
        resolve(first, max_depth=1)
    with pytest.raises(ValueError, match="max_depth must be >= 1"):
        resolve(first, max_depth=0)


def test_resolve_retains_intermediate_callables_so_ids_cannot_be_reused():
    class Link:
        def __init__(self, remaining):
            self.remaining = remaining

        def __call__(self):
            if self.remaining == 0:
                return "done"
            return Link(self.remaining - 1)

    assert resolve(Link(50)) == "done"


def test_random_value_uses_uniform_index_and_rejects_empty_data():
    generator = FakeGenerator(indices=(2,))
    assert random_value(iter(("a", "b", "c")), generator=generator) == "c"
    assert generator.calls == [("random_index", 3)]
    with pytest.raises(ValueError, match="data must not be empty"):
        random_value((), generator=generator)


def test_shuffle_custom_generator_fallback_is_fisher_yates_and_returns_none():
    generator = FakeGenerator(indices=(0, 1, 0))
    values = [0, 1, 2, 3]
    assert shuffle(values, generator=generator) is None
    assert values == [2, 3, 1, 0]
    assert generator.calls == [
        ("random_index", 4),
        ("random_index", 3),
        ("random_index", 2),
    ]
    with pytest.raises(TypeError, match="mutable sequence"):
        shuffle((1, 2), generator=generator)


def test_sample_without_replacement_and_validation():
    generator = FakeGenerator(indices=(3, 2, 0))
    result = sample(range(5), 3, generator=generator)
    assert result == [3, 0, 2]
    assert len(set(result)) == 3
    assert generator.calls == [
        ("random_index", 5),
        ("random_index", 4),
        ("random_index", 3),
    ]
    assert sample((1, 2), 0, generator=generator) == []
    with pytest.raises(ValueError, match="k must be >= 0"):
        sample((1,), -1, generator=generator)
    with pytest.raises(ValueError, match="must not exceed"):
        sample((1,), 2, generator=generator)
    with pytest.raises(TypeError, match="not bool"):
        sample((1,), True, generator=generator)


def test_random_value_selects_resolves_and_takes_values():
    generator = FakeGenerator(indices=(1, 0, 1))
    selector = RandomValue(
        (lambda value: value + 1, lambda value: value + 2),
        generator=generator,
    )
    assert selector(10) == 12
    assert selector.take(2, 10) == [11, 12]


def test_random_value_rejects_empty_and_invalid_custom_selector_results():
    with pytest.raises(ValueError, match="must not be empty"):
        RandomValue(())
    with pytest.raises(ValueError, match="expected an index"):
        RandomValue((1, 2), selector=lambda size: size)()
    with pytest.raises(TypeError, match="selector result"):
        RandomValue((1,), selector=lambda size: False)()


def test_random_value_can_return_callables_without_resolving():
    def value():
        return 1

    assert RandomValue((value,), resolve_callables=False, generator=FakeGenerator())() is value
    with pytest.raises(TypeError, match="resolve_callables must be a bool"):
        RandomValue((1,), resolve_callables=1)


def test_truffle_shuffle_handles_single_value_and_preserves_contents():
    singleton = TruffleShuffle(("only",), generator=FakeGenerator())
    assert singleton.take(3) == ["only", "only", "only"]

    values = (1, 2, 3, 4)
    engine = TruffleShuffle(values, generator=FakeGenerator(indices=(0, 0, 0)))
    assert set(engine.data) == set(values)
    assert len(engine.data) == len(values)
    with pytest.raises(ValueError, match="must not be empty"):
        TruffleShuffle(())


@pytest.mark.parametrize(
    ("strategy_index", "expected_method"),
    [
        (0, "front_triangular"),
        (1, "center_triangular"),
        (2, "back_triangular"),
        (3, "front_exponential"),
        (4, "center_normal"),
        (5, "back_exponential"),
        (6, "front_poisson"),
        (7, "edge_poisson"),
        (8, "back_poisson"),
    ],
)
def test_quantum_monty_is_exactly_the_nine_approved_base_profiles(
    strategy_index,
    expected_method,
):
    generator = FakeGenerator(indices=(strategy_index,))
    monty = QuantumMonty(("value",), generator=generator)
    assert monty() == "value"
    assert generator.calls == [
        ("random_index", 9),
        (expected_method, 1),
    ]


def test_quantum_monty_profile_inventory_and_dispatch():
    assert QuantumMonty.QUANTUM_MONTY_PROFILES == (
        IndexProfile.FRONT_TRIANGULAR,
        IndexProfile.CENTER_TRIANGULAR,
        IndexProfile.BACK_TRIANGULAR,
        IndexProfile.FRONT_EXPONENTIAL,
        IndexProfile.CENTER_NORMAL,
        IndexProfile.BACK_EXPONENTIAL,
        IndexProfile.FRONT_POISSON,
        IndexProfile.EDGE_POISSON,
        IndexProfile.BACK_POISSON,
    )
    monty = QuantumMonty(("value",), generator=FakeGenerator())
    assert monty.dispatch("center_normal").__self__ is monty
    assert monty.dispatch("center_normal").__name__ == "center_normal"
    with pytest.raises(ValueError, match="unknown index profile"):
        monty.dispatch("middle_gauss")


def test_quantum_monty_cycle_and_callable_resolution():
    monty = QuantumMonty(
        (lambda suffix: f"A{suffix}", lambda suffix: f"B{suffix}"),
        generator=FakeGenerator(indices=(0,)),
    )
    assert monty.cycle("!") == "A!"
    assert monty.cycle("?") == "B?"


def test_flex_cat_selects_categories_and_honors_falsey_explicit_key():
    generator = FakeGenerator()
    flex = FlexCat(
        {0: ("zero",), 1: ("one",)},
        value_selector=IndexProfile.UNIFORM,
        generator=generator,
    )
    assert flex(0) == "zero"
    assert flex() == "zero"
    assert flex.take(2, 1) == ["one", "one"]


def test_flex_cat_rejects_bad_matrix_data_and_empty_categories():
    with pytest.raises(TypeError, match="must be a mapping"):
        FlexCat([])
    with pytest.raises(ValueError, match="must not be empty"):
        FlexCat({})
    with pytest.raises(ValueError, match="must not be empty"):
        FlexCat({"empty": ()})


def test_relative_weighted_choice_accepts_real_weights_and_boundaries():
    generator = FakeGenerator(floats=(0.0, 0.5, 1.0, 3.999))
    choice = RelativeWeightedChoice(
        ((0.5, "a"), (0.5, "b"), (3, "c")),
        generator=generator,
    )
    assert choice.take(4) == ["a", "b", "c", "c"]


@pytest.mark.parametrize(
    "table",
    [
        (),
        ((-1, "a"),),
        ((0, "a"),),
        ((math.inf, "a"),),
        ((math.nan, "a"),),
        ((True, "a"),),
        (("1", "a"),),
    ],
)
def test_relative_weighted_choice_rejects_invalid_tables(table):
    with pytest.raises((TypeError, ValueError)):
        RelativeWeightedChoice(table, generator=FakeGenerator())


def test_cumulative_weighted_choice_requires_increasing_positive_thresholds():
    generator = FakeGenerator(floats=(0.2, 1.0, 2.9))
    choice = CumulativeWeightedChoice(
        ((0.5, "a"), (1.5, "b"), (3.0, "c")),
        generator=generator,
    )
    assert choice.take(3) == ["a", "b", "c"]
    for table in (
        ((0, "a"),),
        ((1, "a"), (1, "b")),
        ((2, "a"), (1, "b")),
    ):
        with pytest.raises(ValueError, match="strictly increasing"):
            CumulativeWeightedChoice(table, generator=FakeGenerator())


def test_weighted_choice_resolves_values_and_propagates_errors():
    choice = RelativeWeightedChoice(
        ((1, lambda number: number + 1),),
        generator=FakeGenerator(),
    )
    assert choice(2) == 3

    def broken():
        raise RuntimeError("selected callable failed")

    choice = CumulativeWeightedChoice(((1, broken),), generator=FakeGenerator())
    with pytest.raises(RuntimeError, match="selected callable failed"):
        choice()


def test_take_contract_for_value_engines():
    choice = RelativeWeightedChoice(((1, "value"),), generator=FakeGenerator())
    assert choice.take(0) == []
    with pytest.raises(ValueError, match="count must be >= 0"):
        choice.take(-1)
    with pytest.raises(TypeError, match="not bool"):
        choice.take(True)


def test_flexcat_can_address_none_as_an_explicit_category():
    flex = FlexCat(
        {None: ("none",), "other": ("other",)},
        generator=FakeGenerator(),
    )
    assert flex(None) == "none"


def test_relative_weight_total_must_remain_finite():
    with pytest.raises(ValueError, match="total must be finite"):
        RelativeWeightedChoice(
            ((1e308, "first"), (1e308, "second")),
            generator=FakeGenerator(),
        )
