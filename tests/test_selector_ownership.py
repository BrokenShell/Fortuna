from __future__ import annotations

import pytest

from Fortuna import Generator
from Fortuna._selectors import (
    CumulativeWeightedChoice,
    FlexCat,
    IndexProfile,
    IndexSelector,
    QuantumMonty,
    RandomValue,
    RelativeWeightedChoice,
    TruffleShuffle,
)


class _FixedGenerator:
    def __init__(self, index: int) -> None:
        self.index = index
        self.calls = 0

    def random_index(self, size: int, *, count: int | None = None):
        self.calls += 1
        if count is None:
            return self.index
        return [self.index] * count

    def back_triangular(self, size: int, *, count: int | None = None):
        return self.random_index(size, count=count)


def test_random_value_retains_supplied_index_selector_identity_and_configuration() -> None:
    first = _FixedGenerator(0)
    second = _FixedGenerator(1)
    index_selector = IndexSelector(generator=first)
    selector = RandomValue(("first", "second"), selector=index_selector)

    assert selector.selector is index_selector
    assert selector.generator is first
    assert selector() == "first"

    index_selector.generator = second
    index_selector.profile = IndexProfile.BACK_TRIANGULAR

    assert selector.generator is second
    assert selector() == "second"


def test_random_value_retains_index_selector_subclass() -> None:
    class LastIndex(IndexSelector):
        def __call__(self, size: int, *, count: int | None = None):
            if count is None:
                return size - 1
            return [size - 1] * count

    index_selector = LastIndex()
    selector = RandomValue(("first", "last"), selector=index_selector)

    assert selector.selector is index_selector
    assert selector() == "last"


def test_random_value_rejects_ambiguous_index_selector_generator_override() -> None:
    with pytest.raises(
        TypeError,
        match="generator must be omitted when selector is an IndexSelector",
    ):
        RandomValue(
            ("first", "second"),
            selector=IndexSelector(generator=_FixedGenerator(0)),
            generator=_FixedGenerator(1),
        )


def test_random_value_rejects_inert_generator_with_custom_selector() -> None:
    with pytest.raises(
        TypeError,
        match="generator must be omitted when selector is a custom callable",
    ):
        RandomValue(
            ("first", "second"),
            selector=lambda size: size - 1,
            generator=Generator(8128),
        )


@pytest.mark.parametrize("argument", ["key_selector", "value_selector"])
def test_flex_cat_rejects_ambiguous_index_selector_generator_before_draws(argument) -> None:
    generator = Generator(8128)
    control = Generator(8128)

    with pytest.raises(
        TypeError,
        match="generator must be omitted when selector is an IndexSelector",
    ):
        FlexCat(
            {"first": (1, 2), "second": (3, 4)},
            generator=generator,
            **{argument: IndexSelector()},
        )

    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize("argument", ["key_selector", "value_selector"])
def test_flex_cat_rejects_inert_generator_with_custom_selector_before_draws(argument) -> None:
    generator = Generator(8128)
    control = Generator(8128)

    with pytest.raises(
        TypeError,
        match="generator must be omitted when selector is a custom callable",
    ):
        FlexCat(
            {"first": (1, 2), "second": (3, 4)},
            generator=generator,
            **{argument: lambda size: size - 1},
        )

    assert generator.random_uint(0, 2**64 - 1) == control.random_uint(0, 2**64 - 1)


@pytest.mark.parametrize(
    "factory",
    [
        lambda generator: RandomValue((1, 2), generator=generator),
        lambda generator: TruffleShuffle((1, 2), generator=generator),
        lambda generator: QuantumMonty((1, 2), generator=generator),
        lambda generator: FlexCat({"key": (1, 2)}, generator=generator),
        lambda generator: RelativeWeightedChoice(((1, 1),), generator=generator),
        lambda generator: CumulativeWeightedChoice(((1, 1),), generator=generator),
    ],
)
def test_value_engine_generator_binding_is_read_only(factory) -> None:
    generator = Generator(1)
    selector = factory(generator)

    assert selector.generator is generator
    with pytest.raises(AttributeError):
        selector.generator = Generator(2)


def test_index_selector_zero_count_validates_size_without_generator_access() -> None:
    class InaccessibleGenerator:
        @property
        def random_index(self):
            raise AssertionError("count=0 must not access the generator")

    selector = IndexSelector(generator=InaccessibleGenerator())

    assert selector(3, count=0) == []
    with pytest.raises(ValueError, match="size must be >= 1"):
        selector(0, count=0)


@pytest.mark.parametrize("count", [-1, False])
def test_index_selector_bulk_validates_count_before_size(count) -> None:
    selector = IndexSelector()

    expected = ValueError if count == -1 else TypeError
    with pytest.raises(expected, match="count"):
        selector(0, count=count)
