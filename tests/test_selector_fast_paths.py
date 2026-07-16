from __future__ import annotations

import math
from collections import deque
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest

from Fortuna import _core
from Fortuna._selectors import (
    IndexProfile,
    IndexSelector,
    QuantumMonty,
    RandomValue,
    TruffleShuffle,
    sample,
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

SEED = 0xA11CE
SIZE = 37
COUNT = 19
UINT64_MAX = 2**64 - 1


def _next_module_draw() -> int:
    return _core.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize(("profile", "method_name"), PROFILE_METHODS.items())
@pytest.mark.parametrize("bulk", [False, True], ids=["scalar", "bulk"])
@pytest.mark.parametrize("source", ["module", "generator"])
def test_index_selector_native_paths_preserve_profile_sequence_and_next_draw(
    profile: IndexProfile,
    method_name: str,
    bulk: bool,
    source: str,
):
    control = _core.Generator(SEED)
    if source == "module":
        _core.seed(SEED)
        selector = IndexSelector(profile)
        next_draw: Callable[[], int] = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = IndexSelector(profile, generator=generator)

        def next_draw():
            return generator.random_uint(0, UINT64_MAX)

    control_method = getattr(control, method_name)
    if bulk:
        actual = selector(SIZE, count=COUNT)
        expected = control_method(SIZE, count=COUNT)
    else:
        actual = [selector(SIZE) for _ in range(COUNT)]
        expected = [control_method(SIZE) for _ in range(COUNT)]

    assert actual == expected
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("source", ["module", "generator"])
def test_quantum_monty_value_engine_fused_path_preserves_sequence_and_next_draw(source):
    control = _core.Generator(SEED)
    if source == "module":
        _core.seed(SEED)
        selector = QuantumMonty(range(SIZE), resolve_callables=False)
        next_draw: Callable[[], int] = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = QuantumMonty(
            range(SIZE),
            resolve_callables=False,
            generator=generator,
        )

        def next_draw():
            return generator.random_uint(0, UINT64_MAX)

    assert selector.take(COUNT) == [control.quantum_monty(SIZE) for _ in range(COUNT)]
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("source", ["module", "generator"])
def test_random_value_engine_native_path_preserves_sequence_and_next_draw(source):
    control = _core.Generator(SEED)
    values = tuple(range(SIZE))
    if source == "module":
        _core.seed(SEED)
        selector = RandomValue(values, resolve_callables=False)
        next_draw: Callable[[], int] = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = RandomValue(
            values,
            resolve_callables=False,
            generator=generator,
        )

        def next_draw():
            return generator.random_uint(0, UINT64_MAX)

    assert selector.take(COUNT) == [control.random_value(values) for _ in range(COUNT)]
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        (False, TypeError, "generated index must be an integer, not bool"),
        (SIZE, ValueError, rf"outside \[0, {SIZE}\)"),
    ],
)
def test_random_value_engine_validates_monkeypatched_module_endpoint(
    monkeypatch, result, error, message
):
    monkeypatch.setattr(_core, "random_index", lambda size: result)
    selector = RandomValue(range(SIZE), resolve_callables=False)

    with pytest.raises(error, match=message):
        selector()


def test_random_value_engine_retains_cached_module_draw_binding(monkeypatch):
    native = _core.random_index
    calls = []

    def random_index(size):
        calls.append(size)
        return 1

    monkeypatch.setattr(_core, "random_index", random_index)
    selector = RandomValue(("first", "second"), resolve_callables=False)
    assert selector.selector(2) == 1
    monkeypatch.setattr(_core, "random_index", native)

    assert selector() == "second"
    assert calls == [2, 2]


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        (False, TypeError, "generated index must be an integer, not bool"),
        (SIZE, ValueError, rf"outside \[0, {SIZE}\)"),
    ],
)
def test_quantum_monty_value_engine_validates_monkeypatched_module_endpoint(
    monkeypatch, result, error, message
):
    selector = QuantumMonty(range(SIZE), resolve_callables=False)
    calls = []

    def quantum_monty(size):
        calls.append(size)
        return result

    monkeypatch.setattr(_core, "quantum_monty", quantum_monty)
    with pytest.raises(error, match=message):
        selector()
    assert calls == [SIZE]


@pytest.mark.parametrize("source", ["module", "generator"])
def test_truffle_shuffle_cached_draw_preserves_sequence_and_next_draw(source):
    control = _core.Generator(SEED)
    values = list(range(SIZE))
    expected_data = values.copy()
    for position in range(SIZE - 1, 0, -1):
        other = control.random_index(position + 1)
        expected_data[position], expected_data[other] = (
            expected_data[other],
            expected_data[position],
        )
    expected_data = deque(expected_data)
    rotate_size = max(1, math.isqrt(SIZE))
    expected = []
    for _ in range(COUNT):
        expected_data.rotate(1 + control.front_poisson(rotate_size))
        expected.append(expected_data[-1])

    if source == "module":
        _core.seed(SEED)
        selector = TruffleShuffle(values, resolve_callables=False)
        next_draw: Callable[[], int] = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = TruffleShuffle(
            values,
            resolve_callables=False,
            generator=generator,
        )

        def next_draw():
            return generator.random_uint(0, UINT64_MAX)

    assert selector.take(COUNT) == expected
    assert next_draw() == control.random_uint(0, UINT64_MAX)


def test_truffle_shuffle_cached_custom_draw_remains_validated():
    class InvalidGenerator:
        @staticmethod
        def random_index(size):
            return 0

        @staticmethod
        def front_poisson(size):
            return size

    selector = TruffleShuffle(range(SIZE), generator=InvalidGenerator())
    with pytest.raises(ValueError, match="outside"):
        selector()


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        (False, TypeError, "generated index must be an integer, not bool"),
        (5, ValueError, r"outside \[0, 5\)"),
    ],
)
def test_index_selector_monkeypatched_module_scalar_result_remains_validated(
    monkeypatch,
    result,
    error,
    message,
):
    monkeypatch.setattr(_core, "random_index", lambda size: result)

    with pytest.raises(error, match=message):
        IndexSelector()(5)


@pytest.mark.parametrize(
    ("result", "error", "message"),
    [
        ((0, 1), TypeError, "must return a list"),
        ([0], ValueError, "expected 2"),
        ([0, 5], ValueError, r"outside \[0, 5\)"),
        ([0, False], TypeError, "generated index must be an integer, not bool"),
    ],
)
def test_index_selector_monkeypatched_module_bulk_result_remains_validated(
    monkeypatch,
    result,
    error,
    message,
):
    monkeypatch.setattr(
        _core,
        "random_index",
        lambda size, *, count=None: result,
    )

    with pytest.raises(error, match=message):
        IndexSelector()(5, count=2)


def test_index_selector_generator_subclass_override_is_called_and_validated():
    class GeneratorSubclass(_core.Generator):
        def __init__(self, seed):
            self.calls = []
            self.result: Any = 1

        def random_index(self, size, *, count=None):
            self.calls.append((size, count))
            return self.result

    generator = GeneratorSubclass(SEED)
    selector = IndexSelector(generator=generator)

    assert selector(5) == 1
    generator.result = [2, 3]
    assert selector(5, count=2) == [2, 3]
    generator.result = 5
    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        selector(5)
    generator.result = [0, False]
    with pytest.raises(TypeError, match="generated index must be an integer, not bool"):
        selector(5, count=2)

    assert generator.calls == [(5, None), (5, 2), (5, None), (5, 2)]


def test_index_selector_generator_mutation_invalidates_native_trust():
    class InvalidGenerator:
        @staticmethod
        def random_index(size, *, count=None):
            return size if count is None else [size] * count

    selector = IndexSelector(generator=_core.Generator(SEED))
    selector(5)
    selector.generator = InvalidGenerator()

    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        selector(5)
    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        selector(5, count=2)


def test_index_selector_profile_mutation_invalidates_module_trust(monkeypatch):
    selector = IndexSelector(IndexProfile.UNIFORM)
    _core.seed(SEED)
    selector(5)

    def invalid_profile(size, *, count=None):
        return size if count is None else [size] * count

    monkeypatch.setattr(_core, "back_triangular", invalid_profile)
    selector.profile = IndexProfile.BACK_TRIANGULAR

    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        selector(5)
    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        selector(5, count=2)


@pytest.mark.parametrize("source", ["module", "generator"])
def test_index_selector_size_conversion_can_reenter_native_source(source):
    control = _core.Generator(SEED)
    if source == "module":
        _core.seed(SEED)
        selector = IndexSelector(IndexProfile.CENTER_NORMAL)

        def reentrant_draw():
            return _core.random_uint(0, UINT64_MAX)

        next_draw = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = IndexSelector(IndexProfile.CENTER_NORMAL, generator=generator)

        def reentrant_draw():
            return generator.random_uint(0, UINT64_MAX)

        next_draw = reentrant_draw

    class ReentrantSize:
        def __index__(self):
            assert reentrant_draw() == control.random_uint(0, UINT64_MAX)
            return SIZE

    assert selector(ReentrantSize()) == control.center_normal(SIZE)
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("source", ["module", "generator"])
def test_index_selector_count_conversion_can_reenter_native_source(source):
    control = _core.Generator(SEED)
    if source == "module":
        _core.seed(SEED)
        selector = IndexSelector(IndexProfile.EDGE_POISSON)

        def reentrant_draw():
            return _core.random_uint(0, UINT64_MAX)

        next_draw = _next_module_draw
    else:
        generator = _core.Generator(SEED)
        selector = IndexSelector(IndexProfile.EDGE_POISSON, generator=generator)

        def reentrant_draw():
            return generator.random_uint(0, UINT64_MAX)

        next_draw = reentrant_draw

    class ReentrantCount:
        def __index__(self):
            assert reentrant_draw() == control.random_uint(0, UINT64_MAX)
            return COUNT

    assert selector(SIZE, count=ReentrantCount()) == control.edge_poisson(SIZE, count=COUNT)
    assert next_draw() == control.random_uint(0, UINT64_MAX)


def _forward_partial_fisher_yates(
    generator: _core.Generator,
    population: Iterable[Any],
    k: int,
) -> list[Any]:
    working = list(population)
    for position in range(k):
        other = position + generator.random_index(len(working) - position)
        working[position], working[other] = working[other], working[position]
    return working[:k]


def _sample_surface(name: str, seed: int = SEED):
    if name == "module":
        _core.seed(seed)
        return (
            lambda population, k: sample(population, k),
            _next_module_draw,
        )

    generator = _core.Generator(seed)
    if name == "generator":
        draw = generator.sample
    else:

        def draw(population, k):
            return sample(population, k, generator=generator)

    def next_draw():
        return generator.random_uint(0, UINT64_MAX)

    return draw, next_draw


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_native_paths_preserve_forward_partial_fisher_yates_and_next_draw(
    surface,
):
    population = tuple(range(23))
    control = _core.Generator(SEED)
    expected = _forward_partial_fisher_yates(control, population, 11)
    draw, next_draw = _sample_surface(surface)

    assert draw(population, 11) == expected
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_k_zero_does_not_advance_engine(surface):
    draw, next_draw = _sample_surface(surface)
    control = _core.Generator(SEED)

    assert draw(range(5), 0) == []
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_singleton_consumes_one_draw(surface):
    draw, next_draw = _sample_surface(surface)
    control = _core.Generator(SEED)

    assert draw(["only"], 1) == ["only"]
    control.random_index(1)
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_does_not_modify_input(surface):
    population = list(range(17))
    original = population.copy()
    draw, _ = _sample_surface(surface)

    result = draw(population, 9)

    assert population == original
    assert len(result) == 9
    assert len(set(result)) == 9


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_k_conversion_failure_precedes_materialization_and_drawing(surface):
    materialized = False

    def population():
        nonlocal materialized
        materialized = True
        yield 1

    class BrokenCount:
        def __index__(self):
            raise RuntimeError("broken count")

    draw, next_draw = _sample_surface(surface)
    control = _core.Generator(SEED)

    with pytest.raises(RuntimeError, match="broken count"):
        draw(population(), BrokenCount())

    assert not materialized
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_materialization_failure_does_not_advance_engine(surface):
    def population():
        yield 1
        raise RuntimeError("broken population")

    draw, next_draw = _sample_surface(surface)
    control = _core.Generator(SEED)

    with pytest.raises(RuntimeError, match="broken population"):
        draw(population(), 1)

    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_oversized_k_does_not_advance_engine(surface):
    draw, next_draw = _sample_surface(surface)
    control = _core.Generator(SEED)

    with pytest.raises(ValueError, match="sample"):
        draw(range(3), 4)

    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("count", [-1, 4])
@pytest.mark.parametrize("surface", ["module", "generator"])
def test_private_sample_entry_rejects_invalid_count_without_advancing(surface, count):
    population = [0, 1, 2]
    control = _core.Generator(SEED)
    if surface == "module":
        _core.seed(SEED)

        def draw():
            return _core._sample_materialized(population.copy(), count)

        next_draw = _next_module_draw
    else:
        generator = _core.Generator(SEED)

        def draw():
            return generator._sample_materialized(population.copy(), count)

        def next_draw():
            return generator.random_uint(0, UINT64_MAX)

    with pytest.raises(ValueError, match="sample size"):
        draw()

    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["module", "generator", "explicit"])
def test_sample_k_conversion_can_reenter_native_source(surface):
    control = _core.Generator(SEED)
    if surface == "module":
        _core.seed(SEED)

        def reentrant_draw():
            return _core.random_uint(0, UINT64_MAX)

        next_draw = _next_module_draw
    else:
        generator = _core.Generator(SEED)

        def reentrant_draw():
            return generator.random_uint(0, UINT64_MAX)

        next_draw = reentrant_draw

    class ReentrantCount:
        def __index__(self):
            assert reentrant_draw() == control.random_uint(0, UINT64_MAX)
            return 4

    if surface == "module":
        actual = sample(range(10), ReentrantCount())
    elif surface == "generator":
        actual = generator.sample(range(10), ReentrantCount())
    else:
        actual = sample(range(10), ReentrantCount(), generator=generator)

    assert actual == _forward_partial_fisher_yates(control, range(10), 4)
    assert next_draw() == control.random_uint(0, UINT64_MAX)


@pytest.mark.parametrize("surface", ["generator", "explicit"])
def test_sample_generator_subclass_override_is_called_and_validated(surface):
    class GeneratorSubclass(_core.Generator):
        def __init__(self, seed):
            self.indices = deque((3, 2, 0))
            self.calls = []

        def random_index(self, size, *, count=None):
            self.calls.append((size, count))
            return self.indices.popleft()

    generator = GeneratorSubclass(SEED)
    if surface == "generator":
        actual = generator.sample(range(5), 3)
    else:
        actual = sample(range(5), 3, generator=generator)

    assert actual == [3, 0, 2]
    assert generator.calls == [(5, None), (4, None), (3, None)]


def test_top_level_sample_generator_subclass_invalid_override_remains_validated():
    class GeneratorSubclass(_core.Generator):
        @staticmethod
        def random_index(size, *, count=None):
            return size

    generator = GeneratorSubclass(SEED)
    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        sample(range(5), 1, generator=generator)


def test_sample_custom_generator_fallback_calls_and_validates_override():
    class CustomGenerator:
        def __init__(self):
            self.indices = deque((3, 2, 0))
            self.calls = []

        def random_index(self, size, *, count=None):
            self.calls.append((size, count))
            return self.indices.popleft()

    generator = CustomGenerator()
    assert sample(range(5), 3, generator=generator) == [3, 0, 2]
    assert generator.calls == [(5, None), (4, None), (3, None)]

    generator.indices = deque((5,))
    with pytest.raises(ValueError, match=r"outside \[0, 5\)"):
        sample(range(5), 1, generator=generator)


def test_shared_generator_serializes_entire_native_sample_operations():
    population = range(2_000)
    sample_size = 1_000
    workers = 4
    shared = _core.Generator(SEED)
    control = _core.Generator(SEED)
    expected = [tuple(control.sample(population, sample_size)) for _ in range(workers)]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        actual = list(
            executor.map(
                lambda _: tuple(shared.sample(population, sample_size)),
                range(workers),
            )
        )

    assert sorted(actual) == sorted(expected)
    assert shared.random_uint(0, UINT64_MAX) == control.random_uint(0, UINT64_MAX)
