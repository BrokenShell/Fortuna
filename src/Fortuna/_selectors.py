"""Collection selectors built on Fortuna's random generator primitives."""

from __future__ import annotations

import math
import operator
from collections import deque
from collections.abc import Callable, Iterable, Mapping, MutableSequence
from enum import StrEnum
from itertools import cycle as iter_cycle
from numbers import Real
from typing import Any

from . import _core

_DEFAULT_RESOLVE_DEPTH = 100
_MISSING = object()


def _integer(value: Any, *, name: str, minimum: int | None = None) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    if type(value) is int:
        result = value
    else:
        try:
            result = operator.index(value)
        except TypeError as error:
            raise TypeError(f"{name} must be an integer") from error
    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    return result


def _draw(generator: Any | None, method: str, *args: Any, **kwargs: Any) -> Any:
    """Draw through an explicit generator or the thread-local core function."""
    if generator is not None:
        return getattr(generator, method)(*args, **kwargs)
    return getattr(_core, method)(*args, **kwargs)


def resolve(
    value: Any,
    *args: Any,
    resolve_callables: bool = True,
    max_depth: int = _DEFAULT_RESOLVE_DEPTH,
    **kwargs: Any,
) -> Any:
    """Resolve a chain of callables, passing arguments to the first call only.

    Exceptions raised by selected callables are part of their behavior and are
    never interpreted as a signal to stop resolving.
    """
    if not isinstance(resolve_callables, bool):
        raise TypeError("resolve_callables must be a bool")
    if not resolve_callables or not callable(value):
        return value

    depth_limit = _integer(max_depth, name="max_depth", minimum=1)
    seen: list[Any] = []
    current = value
    first_call = True
    depth = 0

    while callable(current):
        if any(current is previous for previous in seen):
            raise RuntimeError("callable resolution cycle detected")
        if depth >= depth_limit:
            raise RuntimeError(f"callable resolution exceeded max_depth={depth_limit}")
        # Retaining the objects is necessary: retaining only their ids permits
        # CPython to reuse an id after an intermediate callable is destroyed.
        seen.append(current)
        if first_call:
            current = current(*args, **kwargs)
            first_call = False
        else:
            current = current()
        depth += 1
    return current


def random_value(data: Iterable[Any], *, generator: Any | None = None) -> Any:
    """Return one uniformly selected value from a nonempty iterable."""
    if generator is not None and type(generator) is _core.Generator:
        return generator.random_value(data)

    data_type = type(data)
    values = data if data_type is tuple else tuple(data)
    size = len(values)
    if not size:
        raise ValueError("data must not be empty")
    if generator is None:
        index = _core.random_index(size)
    else:
        index = IndexSelector._validated_index(generator.random_index(size), size)
    return values[index]


def shuffle(array: MutableSequence[Any], *, generator: Any | None = None) -> None:
    """Shuffle a mutable sequence in place using Fortuna's native Knuth-B loop."""
    if not isinstance(array, MutableSequence):
        raise TypeError("array must be a mutable sequence")
    if generator is None:
        _core.shuffle(array)
        return
    native_shuffle = getattr(generator, "shuffle", None)
    if callable(native_shuffle):
        native_shuffle(array)
        return
    # Preserve dependency injection for custom generator-like objects. The
    # optimized Fortuna Generator path above owns the release-critical case.
    uniform = IndexSelector(IndexProfile.UNIFORM, generator=generator)
    for position in range(len(array) - 1, 0, -1):
        other = uniform(position + 1)
        array[position], array[other] = array[other], array[position]


def sample(
    population: Iterable[Any],
    k: int,
    *,
    generator: Any | None = None,
) -> list[Any]:
    """Return ``k`` uniformly selected values without replacement."""
    checked_k = _integer(k, name="k", minimum=0)
    data = list(population)
    size = len(data)
    if checked_k > size:
        raise ValueError("sample size k must not exceed the population size")
    uniform = IndexSelector(IndexProfile.UNIFORM, generator=generator)
    for position in range(checked_k):
        other = position + uniform(size - position)
        data[position], data[other] = data[other], data[position]
    return data[:checked_k]


class IndexProfile(StrEnum):
    """Canonical positional index profiles supported by Fortuna 6."""

    UNIFORM = "uniform"
    FRONT_TRIANGULAR = "front_triangular"
    CENTER_TRIANGULAR = "center_triangular"
    BACK_TRIANGULAR = "back_triangular"
    MIXED_TRIANGULAR = "mixed_triangular"
    FRONT_EXPONENTIAL = "front_exponential"
    CENTER_NORMAL = "center_normal"
    BACK_EXPONENTIAL = "back_exponential"
    MIXED_EXPONENTIAL_NORMAL = "mixed_exponential_normal"
    FRONT_POISSON = "front_poisson"
    EDGE_POISSON = "edge_poisson"
    BACK_POISSON = "back_poisson"
    QUANTUM_MONTY = "quantum_monty"


_PROFILE_METHODS = {
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


def _coerce_profile(profile: IndexProfile | str) -> IndexProfile:
    if isinstance(profile, IndexProfile):
        return profile
    if not isinstance(profile, str):
        raise TypeError("profile must be an IndexProfile or canonical profile string")
    try:
        return IndexProfile(profile)
    except ValueError as error:
        raise ValueError(f"unknown index profile: {profile!r}") from error


class IndexSelector:
    """Callable adapter from an :class:`IndexProfile` to an index draw."""

    __slots__ = ("_draw_method", "_generator", "_method_name", "_profile")

    def __init__(
        self,
        profile: IndexProfile | str = IndexProfile.UNIFORM,
        *,
        generator: Any | None = None,
    ) -> None:
        self._draw_method: Callable[..., Any] | None = None
        self._generator = generator
        self.profile = profile

    @property
    def profile(self) -> IndexProfile:
        return self._profile

    @profile.setter
    def profile(self, value: IndexProfile | str) -> None:
        profile = _coerce_profile(value)
        self._profile = profile
        self._method_name = _PROFILE_METHODS[profile]
        self._draw_method = None

    @property
    def generator(self) -> Any | None:
        return self._generator

    @generator.setter
    def generator(self, value: Any | None) -> None:
        self._generator = value
        self._draw_method = None

    def __call__(self, size: int, *, count: int | None = None) -> int | list[int]:
        checked_size = _integer(size, name="size", minimum=1)
        method = self._draw_method
        if method is None:
            source = self._generator
            if source is None:
                source = _core
            method = getattr(source, self._method_name)
            self._draw_method = method
        if count is None:
            value = method(checked_size)
            if type(value) is int:
                if 0 <= value < checked_size:
                    return value
                raise ValueError(f"generated index {value} is outside [0, {checked_size})")
            return self._validated_index(value, checked_size)
        checked_count = _integer(count, name="count", minimum=0)
        values = method(checked_size, count=checked_count)
        if not isinstance(values, list):
            raise TypeError("bulk profile generation must return a list")
        if len(values) != checked_count:
            raise ValueError(
                f"bulk profile generation returned {len(values)} values; expected {checked_count}"
            )
        return [self._validated_index(value, checked_size) for value in values]

    @staticmethod
    def _validated_index(value: Any, size: int) -> int:
        index = _integer(value, name="generated index")
        if not 0 <= index < size:
            raise ValueError(f"generated index {index} is outside [0, {size})")
        return index

    def take(self, count: int, size: int) -> list[int]:
        result = self(size, count=count)
        if not isinstance(result, list):  # pragma: no cover - internal invariant
            raise RuntimeError("bulk index selection did not return a list")
        return result


class _ValueEngine:
    __slots__ = ("generator", "resolve_callables")

    def __init__(self, *, resolve_callables: bool, generator: Any | None) -> None:
        if not isinstance(resolve_callables, bool):
            raise TypeError("resolve_callables must be a bool")
        self.resolve_callables = resolve_callables
        self.generator = generator

    def _resolve(self, value: Any, *args: Any, **kwargs: Any) -> Any:
        return resolve(
            value,
            *args,
            resolve_callables=self.resolve_callables,
            **kwargs,
        )

    def take(self, count: int, *args: Any, **kwargs: Any) -> list[Any]:
        checked_count = _integer(count, name="count", minimum=0)
        return [self(*args, **kwargs) for _ in range(checked_count)]


class RandomValue(_ValueEngine):
    """Select a value using a positional profile or custom index callable."""

    __slots__ = ("data", "selector")

    def __init__(
        self,
        collection: Iterable[Any],
        selector: IndexProfile | str | IndexSelector | Callable[[int], int] = (
            IndexProfile.UNIFORM
        ),
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        self.data = tuple(collection)
        if not self.data:
            raise ValueError("collection must not be empty")
        if isinstance(selector, IndexSelector):
            self.selector = IndexSelector(
                selector.profile,
                generator=generator if generator is not None else selector.generator,
            )
        elif isinstance(selector, (IndexProfile, str)):
            self.selector = IndexSelector(selector, generator=generator)
        elif callable(selector):
            self.selector = selector
        else:
            raise TypeError("selector must be an IndexProfile, canonical string, or callable")

    def _index(self) -> int:
        value = self.selector(len(self.data))
        index = _integer(value, name="selector result")
        if not 0 <= index < len(self.data):
            raise ValueError(
                f"selector returned {index}; expected an index in [0, {len(self.data)})"
            )
        return index

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._resolve(self.data[self._index()], *args, **kwargs)


class TruffleShuffle(_ValueEngine):
    """Stateful wide-uniform selector with randomized forward rotation."""

    __slots__ = ("data", "rotate_size")

    def __init__(
        self,
        collection: Iterable[Any],
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        data = list(collection)
        if not data:
            raise ValueError("collection must not be empty")
        uniform = IndexSelector(IndexProfile.UNIFORM, generator=generator)
        for position in range(len(data) - 1, 0, -1):
            other = uniform(position + 1)
            data[position], data[other] = data[other], data[position]
        self.data = deque(data)
        self.rotate_size = max(1, math.isqrt(len(data)))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        profile = IndexSelector(IndexProfile.FRONT_POISSON, generator=self.generator)
        distance = 1 + profile(self.rotate_size)
        self.data.rotate(distance)
        return self._resolve(self.data[-1], *args, **kwargs)


class QuantumMonty(_ValueEngine):
    """Value selector backed by Fortuna's named positional profiles."""

    QUANTUM_MONTY_PROFILES = (
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

    __slots__ = ("data", "size", "_cycle", "_truffle")

    def __init__(
        self,
        collection: Iterable[Any],
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        self.data = tuple(collection)
        if not self.data:
            raise ValueError("collection must not be empty")
        self.size = len(self.data)
        self._cycle = iter_cycle(self.data)
        self._truffle = TruffleShuffle(
            self.data,
            resolve_callables=resolve_callables,
            generator=generator,
        )

    def _profile_value(
        self,
        profile: IndexProfile,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        index = IndexSelector(profile, generator=self.generator)(self.size)
        if not isinstance(index, int):  # pragma: no cover - scalar contract invariant
            raise RuntimeError("scalar index selection returned a bulk result")
        return self._resolve(self.data[index], *args, **kwargs)

    def dispatch(self, profile: IndexProfile | str) -> Callable[..., Any]:
        canonical = _coerce_profile(profile)
        return {
            IndexProfile.UNIFORM: self.flat_uniform,
            IndexProfile.FRONT_TRIANGULAR: self.front_triangular,
            IndexProfile.CENTER_TRIANGULAR: self.center_triangular,
            IndexProfile.BACK_TRIANGULAR: self.back_triangular,
            IndexProfile.MIXED_TRIANGULAR: self.mixed_triangular,
            IndexProfile.FRONT_EXPONENTIAL: self.front_exponential,
            IndexProfile.CENTER_NORMAL: self.center_normal,
            IndexProfile.BACK_EXPONENTIAL: self.back_exponential,
            IndexProfile.MIXED_EXPONENTIAL_NORMAL: self.mixed_exponential_normal,
            IndexProfile.FRONT_POISSON: self.front_poisson,
            IndexProfile.EDGE_POISSON: self.edge_poisson,
            IndexProfile.BACK_POISSON: self.back_poisson,
            IndexProfile.QUANTUM_MONTY: self.quantum_monty,
        }[canonical]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.quantum_monty(*args, **kwargs)

    def flat_uniform(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.UNIFORM, *args, **kwargs)

    def cycle(self, *args: Any, **kwargs: Any) -> Any:
        return self._resolve(next(self._cycle), *args, **kwargs)

    def truffle_shuffle(self, *args: Any, **kwargs: Any) -> Any:
        return self._truffle(*args, **kwargs)

    def front_triangular(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.FRONT_TRIANGULAR, *args, **kwargs)

    def center_triangular(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.CENTER_TRIANGULAR, *args, **kwargs)

    def back_triangular(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.BACK_TRIANGULAR, *args, **kwargs)

    def mixed_triangular(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.MIXED_TRIANGULAR, *args, **kwargs)

    def front_exponential(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.FRONT_EXPONENTIAL, *args, **kwargs)

    def center_normal(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.CENTER_NORMAL, *args, **kwargs)

    def back_exponential(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.BACK_EXPONENTIAL, *args, **kwargs)

    def mixed_exponential_normal(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.MIXED_EXPONENTIAL_NORMAL, *args, **kwargs)

    def front_poisson(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.FRONT_POISSON, *args, **kwargs)

    def edge_poisson(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.EDGE_POISSON, *args, **kwargs)

    def back_poisson(self, *args: Any, **kwargs: Any) -> Any:
        return self._profile_value(IndexProfile.BACK_POISSON, *args, **kwargs)

    def quantum_monty(self, *args: Any, **kwargs: Any) -> Any:
        checked_index = IndexSelector(IndexProfile.UNIFORM, generator=self.generator)(
            len(self.QUANTUM_MONTY_PROFILES)
        )
        profile = self.QUANTUM_MONTY_PROFILES[checked_index]
        return self._profile_value(profile, *args, **kwargs)


def _selection_engine(
    collection: Iterable[Any],
    strategy: Any,
    *,
    resolve_callables: bool,
    generator: Any | None,
) -> _ValueEngine:
    if strategy is TruffleShuffle:
        return TruffleShuffle(
            collection,
            resolve_callables=resolve_callables,
            generator=generator,
        )
    if strategy is QuantumMonty:
        return QuantumMonty(
            collection,
            resolve_callables=resolve_callables,
            generator=generator,
        )
    if strategy is RandomValue:
        return RandomValue(
            collection,
            resolve_callables=resolve_callables,
            generator=generator,
        )
    return RandomValue(
        collection,
        selector=strategy,
        resolve_callables=resolve_callables,
        generator=generator,
    )


class FlexCat(_ValueEngine):
    """Select a category and then a value using independent strategies.

    A strategy is a canonical :class:`IndexProfile`, an ``IndexSelector``, a
    custom index callable, or one of the value-engine classes ``RandomValue``,
    ``TruffleShuffle``, and ``QuantumMonty``.
    """

    __slots__ = ("matrix_data", "key_selector", "value_selectors")

    def __init__(
        self,
        matrix_data: Mapping[Any, Iterable[Any]],
        key_selector: Any = IndexProfile.FRONT_TRIANGULAR,
        value_selector: Any = TruffleShuffle,
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        if not isinstance(matrix_data, Mapping):
            raise TypeError("matrix_data must be a mapping")
        self.matrix_data = dict(matrix_data)
        if not self.matrix_data:
            raise ValueError("matrix_data must not be empty")
        keys = tuple(self.matrix_data)
        self.key_selector = _selection_engine(
            keys,
            key_selector,
            resolve_callables=False,
            generator=generator,
        )
        self.value_selectors = {
            key: _selection_engine(
                values,
                value_selector,
                resolve_callables=resolve_callables,
                generator=generator,
            )
            for key, values in self.matrix_data.items()
        }

    def __call__(self, cat_key: Any = _MISSING, *args: Any, **kwargs: Any) -> Any:
        key = self.key_selector() if cat_key is _MISSING else cat_key
        return self.value_selectors[key](*args, **kwargs)


def _weighted_pairs(weighted_table: Iterable[Any]) -> list[tuple[float, Any]]:
    result: list[tuple[float, Any]] = []
    for position, pair in enumerate(weighted_table):
        try:
            weight, value = pair
        except (TypeError, ValueError) as error:
            raise TypeError(f"weighted item {position} must be a (weight, value) pair") from error
        if isinstance(weight, bool) or not isinstance(weight, Real):
            raise TypeError(f"weight at position {position} must be a real number")
        numeric_weight = float(weight)
        if not math.isfinite(numeric_weight):
            raise ValueError(f"weight at position {position} must be finite")
        result.append((numeric_weight, value))
    if not result:
        raise ValueError("weighted_table must not be empty")
    return result


class _WeightedChoice(_ValueEngine):
    __slots__ = ("data", "total")

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        draw = _draw(self.generator, "random_float", 0.0, self.total)
        for cumulative_weight, value in self.data:
            if draw < cumulative_weight:
                return self._resolve(value, *args, **kwargs)
        # A conforming random_float is half-open, but retain a safe last-value
        # fallback for floating-point rounding at the upper boundary.
        return self._resolve(self.data[-1][1], *args, **kwargs)


class RelativeWeightedChoice(_WeightedChoice):
    """Choose values using nonnegative relative real weights."""

    def __init__(
        self,
        weighted_table: Iterable[Any],
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        cumulative = 0.0
        data: list[tuple[float, Any]] = []
        for weight, value in _weighted_pairs(weighted_table):
            if weight < 0.0:
                raise ValueError("relative weights must be nonnegative")
            cumulative += weight
            if not math.isfinite(cumulative):
                raise ValueError("relative weight total must be finite")
            data.append((cumulative, value))
        if cumulative <= 0.0:
            raise ValueError("at least one relative weight must be positive")
        self.data = tuple(data)
        self.total = cumulative


class CumulativeWeightedChoice(_WeightedChoice):
    """Choose values using finite, positive, strictly increasing thresholds."""

    def __init__(
        self,
        weighted_table: Iterable[Any],
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        pairs = _weighted_pairs(weighted_table)
        previous = 0.0
        for weight, _ in pairs:
            if weight <= previous:
                raise ValueError("cumulative weights must be positive and strictly increasing")
            previous = weight
        self.data = tuple(pairs)
        self.total = previous
