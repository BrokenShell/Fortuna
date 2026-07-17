"""Static consumer contract checked by Pyright; this module is not run by pytest."""

from collections.abc import Callable, MutableSequence
from typing import Literal, assert_type, overload

import Fortuna
from Fortuna import _core


class CustomGenerator(Fortuna.Generator):
    pass


class IndexGenerator:
    @overload
    def random_index(self, size: int, *, count: None = None) -> int: ...

    @overload
    def random_index(self, size: int, *, count: int) -> list[int]: ...

    @overload
    def random_index(self, size: int, *, count: int | None) -> int | list[int]: ...

    def random_index(self, size: int, *, count: int | None = None) -> int | list[int]:
        return 0 if count is None else [0] * count


class ShuffleGenerator:
    def shuffle(self, data: MutableSequence[object]) -> None:
        data.reverse()


class SimpleIndexGenerator:
    """A normal duck-typed generator should not need overload boilerplate."""

    def random_index(self, size: int, *, count: int | None = None) -> int | list[int]:
        return 0 if count is None else [0] * count


generator = Fortuna.Generator(0)
assert_type(CustomGenerator.from_entropy(), CustomGenerator)
assert_type(CustomGenerator.for_stream(0, "worker-1"), CustomGenerator)

assert_type(Fortuna.percent_true(), bool)
assert_type(Fortuna.percent_true(count=None), bool)
assert_type(Fortuna.percent_true(count=4), list[bool])
assert_type(generator.bernoulli_variate(), bool)
assert_type(generator.bernoulli_variate(count=4), list[bool])

assert_type(Fortuna.random_int(-4, 4), int)
assert_type(Fortuna.random_int(-4, 4, count=None), int)
assert_type(Fortuna.random_int(-4, 4, count=4), list[int])
assert_type(generator.front_triangular(10), int)
assert_type(generator.front_triangular(10, count=4), list[int])

assert_type(Fortuna.canonical(), float)
assert_type(Fortuna.canonical(count=4), list[float])
assert_type(generator.normal_variate(0.0, 1.0), float)
assert_type(generator.normal_variate(0.0, 1.0, count=4), list[float])

Direction = Literal["north", "south"]
words: tuple[Direction, Direction] = ("north", "south")
assert_type(Fortuna.random_value(words), Direction)
assert_type(Fortuna.random_value(words, generator=IndexGenerator()), Direction)
assert_type(Fortuna.random_value(words, generator=SimpleIndexGenerator()), Direction)
assert_type(generator.random_value(words), Direction)
assert_type(Fortuna.sample(words, 1), list[Direction])
assert_type(Fortuna.sample(words, 1, generator=IndexGenerator()), list[Direction])
assert_type(Fortuna.sample(words, 1, generator=SimpleIndexGenerator()), list[Direction])
assert_type(generator.sample(words, 1), list[Direction])

mutable_words = list(words)
assert_type(Fortuna.shuffle(mutable_words), None)
assert_type(Fortuna.shuffle(mutable_words, generator=ShuffleGenerator()), None)
assert_type(Fortuna.shuffle(mutable_words, generator=SimpleIndexGenerator()), None)
assert_type(generator.shuffle(mutable_words), None)

value_generator = Fortuna.RandomValue(words)
assert_type(value_generator(), Direction)
assert_type(value_generator.uniform(), Direction)
assert_type(value_generator.cycle(), Direction)
assert_type(value_generator.truffle_shuffle(), Direction)
assert_type(value_generator.front_triangular(), Direction)
assert_type(value_generator.center_triangular(), Direction)
assert_type(value_generator.back_triangular(), Direction)
assert_type(value_generator.take(2), list[Direction])
assert_type(Fortuna.TruffleShuffle(words)(), Direction)
relative_weights: tuple[tuple[int, Direction], ...] = ((1, "north"), (1, "south"))
assert_type(Fortuna.WeightedChoice(relative_weights)(), Direction)
assert_type(Fortuna.WeightedChoice(relative=relative_weights)(), Direction)
cumulative_weights: tuple[tuple[int, Direction], ...] = ((1, "north"), (2, "south"))
assert_type(Fortuna.WeightedChoice(cumulative=cumulative_weights)(), Direction)


def selected_direction() -> Direction:
    return "north"


def selected_direction_factory() -> Callable[[], Direction]:
    return selected_direction


direction_callables: tuple[Callable[[], Direction], ...] = (selected_direction,)
nested_direction_callables: tuple[Callable[[], Callable[[], Direction]], ...] = (
    selected_direction_factory,
)
assert_type(Fortuna.RandomValue(direction_callables)(), Direction)
assert_type(Fortuna.RandomValue(nested_direction_callables)(), Direction)
assert_type(
    Fortuna.RandomValue(direction_callables, resolve_callables=False)(),
    Callable[[], Direction],
)

# These calls deliberately exercise rejected static contracts. The project
# reports unused ignores, so removing the corresponding type error fails CI.
Fortuna.random_int(0, 1, count=1.5)  # pyright: ignore[reportCallIssue, reportArgumentType]
Fortuna.shuffle(words)  # pyright: ignore[reportArgumentType]
phantom_count_api = _core._CountAPI  # pyright: ignore[reportAttributeAccessIssue]


def check_dynamic_count(dynamic_count: int | None) -> None:
    assert_type(Fortuna.percent_true(count=dynamic_count), bool | list[bool])
    assert_type(generator.bernoulli_variate(count=dynamic_count), bool | list[bool])
    assert_type(Fortuna.random_int(-4, 4, count=dynamic_count), int | list[int])
    assert_type(generator.front_triangular(10, count=dynamic_count), int | list[int])
    assert_type(Fortuna.canonical(count=dynamic_count), float | list[float])
    assert_type(generator.normal_variate(0.0, 1.0, count=dynamic_count), float | list[float])
