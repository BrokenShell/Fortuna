from __future__ import annotations

from collections.abc import Iterator

import pytest

from Fortuna import Generator
from Fortuna._selectors import FlexCat, IndexProfile, QuantumMonty, TruffleShuffle

SEED = 0xF07A_6000
VALUES = tuple(range(12))


def _next_draw(generator: Generator) -> int:
    return generator.random_uint(0, 2**32)


class _RecordingGenerator:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def random_index(self, size: int, *, count: int | None = None):
        self.calls.append(("random_index", size))
        return 0 if count is None else [0] * count

    def __getattr__(self, name: str):
        def draw(size: int, *, count: int | None = None):
            self.calls.append((name, size))
            return 0 if count is None else [0] * count

        return draw


def test_quantum_monty_construction_does_not_advance_owned_generator() -> None:
    generator = Generator(SEED)
    control = Generator(SEED)

    QuantumMonty(VALUES, generator=generator)

    assert _next_draw(generator) == _next_draw(control)


def test_quantum_monty_defers_custom_generator_access_until_selected_path() -> None:
    generator = _RecordingGenerator()
    selector = QuantumMonty(VALUES, generator=generator)

    assert generator.calls == []
    assert selector.cycle() == VALUES[0]
    assert generator.calls == []
    assert selector.front_triangular() == VALUES[0]
    assert generator.calls == [("front_triangular", len(VALUES))]


def test_quantum_monty_profiles_and_cycle_do_not_initialize_truffle() -> None:
    generator = Generator(SEED)
    control = Generator(SEED)
    selector = QuantumMonty(VALUES, generator=generator)

    assert selector._truffle is None
    assert selector.cycle() == VALUES[0]
    assert selector.front_triangular() == VALUES[control.front_triangular(len(VALUES))]
    assert selector._truffle is None
    assert _next_draw(generator) == _next_draw(control)


def test_quantum_monty_lazily_constructs_and_reuses_truffle() -> None:
    generator = Generator(SEED)
    control = Generator(SEED)
    selector = QuantumMonty(VALUES, generator=generator)
    reference = TruffleShuffle(VALUES, generator=control)

    assert selector.truffle_shuffle() == reference()
    cached = selector._truffle
    assert cached is not None
    assert selector.truffle_shuffle() == reference()
    assert selector._truffle is cached
    assert _next_draw(generator) == _next_draw(control)


def test_quantum_monty_call_sequence_starts_at_constructor_seed() -> None:
    generator = Generator(SEED)
    control = Generator(SEED)
    selector = QuantumMonty(VALUES, generator=generator)

    expected = []
    for _ in range(32):
        profile = selector.QUANTUM_MONTY_PROFILES[
            control.random_index(len(selector.QUANTUM_MONTY_PROFILES))
        ]
        expected.append(VALUES[getattr(control, profile.value)(len(VALUES))])

    assert selector.take(32) == expected
    assert _next_draw(generator) == _next_draw(control)


class _BrokenValues:
    def __iter__(self) -> Iterator[int]:
        yield 1
        raise RuntimeError("category materialization failed")


class _NeverIterated:
    def __init__(self) -> None:
        self.iterations = 0

    def __iter__(self) -> Iterator[int]:
        self.iterations += 1
        raise AssertionError("invalid selector configuration must fail first")


@pytest.mark.parametrize(
    ("matrix", "match"),
    [
        ({"valid": VALUES, "empty": ()}, "collection must not be empty"),
        ({"valid": VALUES, "broken": _BrokenValues()}, "category materialization failed"),
    ],
)
def test_flex_cat_category_failure_does_not_advance_generator(matrix, match) -> None:
    generator = Generator(SEED)
    control = Generator(SEED)

    with pytest.raises((RuntimeError, ValueError), match=match):
        FlexCat(matrix, key_selector=TruffleShuffle, generator=generator)

    assert _next_draw(generator) == _next_draw(control)


@pytest.mark.parametrize("argument", ["key_selector", "value_selector"])
def test_flex_cat_selector_configuration_failure_does_not_advance_generator(argument) -> None:
    generator = Generator(SEED)
    control = Generator(SEED)
    kwargs = {argument: "not_a_profile"}

    with pytest.raises(ValueError, match="unknown index profile"):
        FlexCat({"first": VALUES, "second": VALUES}, generator=generator, **kwargs)

    assert _next_draw(generator) == _next_draw(control)


def test_flex_cat_validation_failure_does_not_access_custom_generator() -> None:
    generator = _RecordingGenerator()

    with pytest.raises(ValueError, match="unknown index profile"):
        FlexCat(
            {"first": VALUES, "second": VALUES},
            key_selector=TruffleShuffle,
            value_selector="not_a_profile",
            generator=generator,
        )

    assert generator.calls == []


def test_flex_cat_selector_validation_precedes_category_materialization() -> None:
    values = _NeverIterated()

    with pytest.raises(ValueError, match="unknown index profile"):
        FlexCat({"category": values}, value_selector="not_a_profile")

    assert values.iterations == 0


def test_flex_cat_valid_construction_preserves_seeded_sequence_and_mapping_order() -> None:
    matrix = {
        "a": tuple(range(5)),
        "b": tuple(range(10, 15)),
        "c": tuple(range(20, 25)),
    }
    generator = Generator(8128)
    selector = FlexCat(matrix, generator=generator)

    assert tuple(selector.matrix_data) == tuple(matrix)
    assert selector.matrix_data == matrix
    assert [selector() for _ in range(12)] == [
        1,
        4,
        3,
        0,
        11,
        20,
        10,
        1,
        12,
        11,
        10,
        4,
    ]


def test_flex_cat_materializes_one_shot_categories_before_selector_construction() -> None:
    selector = FlexCat(
        {"first": iter((1, 2, 3)), "second": iter((4, 5, 6))},
        key_selector=IndexProfile.UNIFORM,
        value_selector=IndexProfile.UNIFORM,
        generator=Generator(SEED),
    )

    assert selector.matrix_data == {"first": (1, 2, 3), "second": (4, 5, 6)}
    assert selector("first") in {1, 2, 3}
    assert selector("second") in {4, 5, 6}
