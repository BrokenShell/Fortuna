"""Collection selectors built on Fortuna's random generator primitives."""

from __future__ import annotations

import math
import operator
from collections import deque
from collections.abc import Callable, Iterable, Mapping, MutableSequence
from enum import StrEnum
from itertools import cycle as iter_cycle
from numbers import Real
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Protocol,
    TypeAlias,
    TypeVar,
    cast,
    overload,
)

from . import _core

_DEFAULT_RESOLVE_DEPTH = 100
_MISSING = object()

_T = TypeVar("_T")
_K = TypeVar("_K")
_Weight = int | float
_Resolvable: TypeAlias = _T | Callable[..., "_Resolvable[_T]"]


class _IndexGenerator(Protocol):
    def random_index(self, size: int) -> Any: ...


class _ShuffleGenerator(Protocol):
    def shuffle(self, data: MutableSequence[Any]) -> None: ...


class _FloatGenerator(Protocol):
    def random_float(self, low: float = 0.0, high: float = 1.0) -> Any: ...


class _IndexCallable(Protocol):
    def __call__(self, size: int) -> Any: ...


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


def random_value(
    data: Iterable[_T], *, generator: _core.Generator | _IndexGenerator | None = None
) -> _T:
    """Return one uniformly selected value from a nonempty iterable."""
    if generator is not None and type(generator) is _core.Generator:
        return generator.random_value(data)

    data_type = type(data)
    if generator is None and (data_type is tuple or data_type is list):
        method = _core.random_index
        if method is _NATIVE_RANDOM_INDEX:
            exact_data: tuple[_T, ...] | list[_T] = data  # type: ignore[assignment]
            return _core._random_value_materialized(exact_data)
    values: tuple[_T, ...] = data if data_type is tuple else tuple(data)  # type: ignore[assignment]
    size = len(values)
    if not size:
        raise ValueError("data must not be empty")
    if generator is None:
        method = _core.random_index
        if method is _NATIVE_RANDOM_INDEX:
            return _core._random_value_materialized(values)
        index = method(size)
    else:
        index = IndexSelector._validated_index(generator.random_index(size), size)
    return values[index]


def shuffle(
    array: MutableSequence[_T],
    *,
    generator: _core.Generator | _IndexGenerator | _ShuffleGenerator | None = None,
) -> None:
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
    population: Iterable[_T],
    k: int,
    *,
    generator: _core.Generator | _IndexGenerator | None = None,
) -> list[_T]:
    """Return ``k`` uniformly selected values without replacement."""
    checked_k = _integer(k, name="k", minimum=0)
    data = list(population)
    size = len(data)
    if checked_k > size:
        raise ValueError("sample size k must not exceed the population size")
    if generator is None:
        return _core._sample_materialized(data, checked_k)
    if type(generator) is _core.Generator:
        return generator._sample_materialized(data, checked_k)
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

_NATIVE_PROFILE_METHODS = {
    profile: getattr(_core, method_name) for profile, method_name in _PROFILE_METHODS.items()
}
_NATIVE_RANDOM_FLOAT = _core.random_float
_NATIVE_RANDOM_INDEX = _NATIVE_PROFILE_METHODS[IndexProfile.UNIFORM]
_NATIVE_FRONT_POISSON = _NATIVE_PROFILE_METHODS[IndexProfile.FRONT_POISSON]
_NATIVE_QUANTUM_MONTY = _NATIVE_PROFILE_METHODS[IndexProfile.QUANTUM_MONTY]
_QUANTUM_MONTY_DISPATCH = {
    IndexProfile.UNIFORM: "flat_uniform",
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

    __slots__ = (
        "_draw_method",
        "_generator",
        "_method_name",
        "_profile",
        "_trusted_native",
    )

    def __init__(
        self,
        profile: IndexProfile | str = IndexProfile.UNIFORM,
        *,
        generator: Any | None = None,
    ) -> None:
        self._draw_method: Callable[..., Any] | None = None
        self._generator = generator
        self._trusted_native = False
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
        self._trusted_native = False

    @property
    def generator(self) -> Any | None:
        return self._generator

    @generator.setter
    def generator(self, value: Any | None) -> None:
        self._generator = value
        self._draw_method = None
        self._trusted_native = False

    @overload
    def __call__(self, size: int, *, count: None = None) -> int: ...

    @overload
    def __call__(self, size: int, *, count: int) -> list[int]: ...

    @overload
    def __call__(self, size: int, *, count: int | None) -> int | list[int]: ...

    def __call__(self, size: int, *, count: int | None = None) -> int | list[int]:
        checked_count: int | None = None
        if count is not None:
            if type(count) is int:
                checked_count = count
                if checked_count < 0:
                    raise ValueError("count must be nonnegative")
            else:
                checked_count = _integer(count, name="count")
                if checked_count < 0:
                    raise ValueError("count must be nonnegative")
        if type(size) is int:
            checked_size = size
            if checked_size < 1:
                raise ValueError("size must be >= 1")
        else:
            checked_size = _integer(size, name="size", minimum=1)
        if checked_count == 0:
            return []
        method = self._draw_method
        if method is None:
            source = self._generator
            if source is None:
                method = getattr(_core, self._method_name)
                self._trusted_native = method is _NATIVE_PROFILE_METHODS[self._profile]
            else:
                method = getattr(source, self._method_name)
                self._trusted_native = type(source) is _core.Generator
            self._draw_method = method
        if checked_count is None:
            value = method(checked_size)
            if self._trusted_native:
                return value
            if type(value) is int:
                if 0 <= value < checked_size:
                    return value
                raise ValueError(f"generated index {value} is outside [0, {checked_size})")
            return self._validated_index(value, checked_size)
        values = method(checked_size, count=checked_count)
        if self._trusted_native:
            return values
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


def _profile_index(profile: IndexProfile, size: int, generator: Any | None) -> int:
    """Draw one already-sized profile index without constructing an adapter.

    Value engines validate and retain their collection size at construction, so
    routing every pull through a fresh ``IndexSelector`` only repeats adapter
    setup.  Keep the same native trust boundary here: exact Fortuna entry points
    are trusted, while custom generators, subclasses, and monkeypatched module
    functions are validated before their result can index a collection.
    """
    method_name = _PROFILE_METHODS[profile]
    if generator is None:
        method = getattr(_core, method_name)
        value = method(size)
        if method is _NATIVE_PROFILE_METHODS[profile]:
            return value
    else:
        method = getattr(generator, method_name)
        value = method(size)
        if type(generator) is _core.Generator:
            return value
    return IndexSelector._validated_index(value, size)


class _ValueEngine(Generic[_T]):
    __slots__ = ("_generator", "resolve_callables")

    def __init__(self, *, resolve_callables: bool, generator: Any | None) -> None:
        if not isinstance(resolve_callables, bool):
            raise TypeError("resolve_callables must be a bool")
        self.resolve_callables = resolve_callables
        self._generator = generator

    @property
    def generator(self) -> Any | None:
        """Return this engine's draw source; the binding is read-only."""
        return self._generator

    if TYPE_CHECKING:

        def __call__(self, *args: Any, **kwargs: Any) -> _T: ...

    def _resolve(self, value: _T, *args: Any, **kwargs: Any) -> _T:
        resolve_callables = self.resolve_callables
        if resolve_callables is False:
            return value
        if resolve_callables is not True:
            raise TypeError("resolve_callables must be a bool")
        if not callable(value):
            return value
        return cast(
            _T,
            resolve(
                value,
                *args,
                resolve_callables=self.resolve_callables,
                **kwargs,
            ),
        )

    def take(self, count: int, *args: Any, **kwargs: Any) -> list[_T]:
        checked_count = _integer(count, name="count", minimum=0)
        return [self(*args, **kwargs) for _ in range(checked_count)]


class RandomValue(_ValueEngine[_T]):
    """Select using an owned profile or a retained index callable.

    A supplied ``IndexSelector`` or custom callable owns its draw source, so it
    cannot be combined with this constructor's ``generator`` argument.
    """

    __slots__ = ("data", "selector")

    @overload
    def __init__(
        self,
        collection: Iterable[_T],
        selector: IndexProfile | str | IndexSelector | _IndexCallable = IndexProfile.UNIFORM,
        *,
        resolve_callables: Literal[False],
        generator: Any | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        collection: Iterable[_Resolvable[_T]],
        selector: IndexProfile | str | IndexSelector | _IndexCallable = IndexProfile.UNIFORM,
        *,
        resolve_callables: Literal[True] = True,
        generator: Any | None = None,
    ) -> None: ...

    def __init__(
        self,
        collection: Iterable[Any],
        selector: IndexProfile | str | IndexSelector | _IndexCallable = IndexProfile.UNIFORM,
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        self.data = tuple(collection)
        if not self.data:
            raise ValueError("collection must not be empty")
        if isinstance(selector, IndexSelector):
            if generator is not None:
                raise TypeError("generator must be omitted when selector is an IndexSelector")
            self.selector = selector
        elif isinstance(selector, (IndexProfile, str)):
            self.selector = IndexSelector(selector, generator=generator)
        elif callable(selector):
            if generator is not None:
                raise TypeError("generator must be omitted when selector is a custom callable")
            self.selector = selector
        else:
            raise TypeError("selector must be an IndexProfile, canonical string, or callable")

    @property
    def generator(self) -> Any | None:
        if isinstance(self.selector, IndexSelector):
            return self.selector.generator
        return self._generator

    def _index(self) -> int:
        selector = self.selector
        value = selector(len(self.data))
        if type(selector) is IndexSelector:
            # The exact adapter has already enforced the complete scalar index
            # contract.  Subclasses and arbitrary callables remain untrusted.
            return cast(int, value)
        index = _integer(value, name="selector result")
        if not 0 <= index < len(self.data):
            raise ValueError(
                f"selector returned {index}; expected an index in [0, {len(self.data)})"
            )
        return index

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        selector = self.selector
        if type(selector) is IndexSelector and selector.profile is IndexProfile.UNIFORM:
            generator = selector.generator
            if generator is None:
                method = _core.random_index
                bound_method = selector._draw_method
                if method is _NATIVE_RANDOM_INDEX and (
                    bound_method is None or bound_method is method
                ):
                    return self._resolve(
                        _core._random_value_materialized(self.data),
                        *args,
                        **kwargs,
                    )
            elif type(generator) is _core.Generator:
                return self._resolve(generator.random_value(self.data), *args, **kwargs)
        return self._resolve(self.data[self._index()], *args, **kwargs)


class TruffleShuffle(_ValueEngine[_T]):
    """Stateful wide-uniform selector with randomized forward rotation."""

    __slots__ = ("_distance_method", "_trusted_distance", "data", "rotate_size")

    @overload
    def __init__(
        self,
        collection: Iterable[_T],
        *,
        resolve_callables: Literal[False],
        generator: Any | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        collection: Iterable[_Resolvable[_T]],
        *,
        resolve_callables: Literal[True] = True,
        generator: Any | None = None,
    ) -> None: ...

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
        self._distance_method: Callable[[int], Any] | None = None
        self._trusted_distance = False

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        method = self._distance_method
        if method is None:
            generator = self._generator
            if generator is None:
                method = _core.front_poisson
                self._trusted_distance = method is _NATIVE_FRONT_POISSON
            else:
                method = generator.front_poisson
                self._trusted_distance = type(generator) is _core.Generator
            self._distance_method = method
        value = method(self.rotate_size)
        if self._trusted_distance:
            distance = 1 + value
        else:
            distance = 1 + IndexSelector._validated_index(value, self.rotate_size)
        self.data.rotate(distance)
        return self._resolve(self.data[-1], *args, **kwargs)


class QuantumMonty(_ValueEngine[_T]):
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

    @overload
    def __init__(
        self,
        collection: Iterable[_T],
        *,
        resolve_callables: Literal[False],
        generator: Any | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        collection: Iterable[_Resolvable[_T]],
        *,
        resolve_callables: Literal[True] = True,
        generator: Any | None = None,
    ) -> None: ...

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
        self._truffle: TruffleShuffle[_T] | None = None

    def _truffle_selector(self) -> TruffleShuffle[_T]:
        selector = self._truffle
        if selector is None:
            # Construct into a local first so a failed initialization never
            # leaves a partially initialized selector in the cache.
            selector = TruffleShuffle(
                self.data,
                resolve_callables=self.resolve_callables,
                generator=self.generator,
            )
            self._truffle = selector
        return selector

    def _profile_value(
        self,
        profile: IndexProfile,
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        index = _profile_index(profile, self.size, self.generator)
        return self._resolve(self.data[index], *args, **kwargs)

    def dispatch(self, profile: IndexProfile | str) -> Callable[..., _T]:
        canonical = _coerce_profile(profile)
        return getattr(self, _QUANTUM_MONTY_DISPATCH[canonical])

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        return self.quantum_monty(*args, **kwargs)

    def flat_uniform(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.UNIFORM, *args, **kwargs)

    def cycle(self, *args: Any, **kwargs: Any) -> _T:
        return self._resolve(next(self._cycle), *args, **kwargs)

    def truffle_shuffle(self, *args: Any, **kwargs: Any) -> _T:
        return self._truffle_selector()(*args, **kwargs)

    def front_triangular(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.FRONT_TRIANGULAR, *args, **kwargs)

    def center_triangular(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.CENTER_TRIANGULAR, *args, **kwargs)

    def back_triangular(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.BACK_TRIANGULAR, *args, **kwargs)

    def mixed_triangular(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.MIXED_TRIANGULAR, *args, **kwargs)

    def front_exponential(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.FRONT_EXPONENTIAL, *args, **kwargs)

    def center_normal(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.CENTER_NORMAL, *args, **kwargs)

    def back_exponential(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.BACK_EXPONENTIAL, *args, **kwargs)

    def mixed_exponential_normal(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.MIXED_EXPONENTIAL_NORMAL, *args, **kwargs)

    def front_poisson(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.FRONT_POISSON, *args, **kwargs)

    def edge_poisson(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.EDGE_POISSON, *args, **kwargs)

    def back_poisson(self, *args: Any, **kwargs: Any) -> _T:
        return self._profile_value(IndexProfile.BACK_POISSON, *args, **kwargs)

    def quantum_monty(self, *args: Any, **kwargs: Any) -> _T:
        generator = self._generator
        if generator is None:
            method = _core.quantum_monty
            checked_index = method(self.size)
            if method is not _NATIVE_QUANTUM_MONTY:
                checked_index = IndexSelector._validated_index(checked_index, self.size)
            return self._resolve(self.data[checked_index], *args, **kwargs)
        if type(generator) is _core.Generator:
            checked_index = generator.quantum_monty(self.size)
            return self._resolve(self.data[checked_index], *args, **kwargs)
        checked_index = _profile_index(
            IndexProfile.UNIFORM,
            len(self.QUANTUM_MONTY_PROFILES),
            generator,
        )
        profile = self.QUANTUM_MONTY_PROFILES[checked_index]
        return self._profile_value(profile, *args, **kwargs)


def _selection_engine(
    collection: Iterable[_T],
    strategy: Any,
    *,
    resolve_callables: bool,
    generator: Any | None,
) -> _ValueEngine[_T]:
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


def _validated_selection_strategy(strategy: Any) -> Any:
    """Validate a selector configuration without constructing a value engine."""
    if strategy is TruffleShuffle or strategy is QuantumMonty or strategy is RandomValue:
        return strategy
    if isinstance(strategy, IndexSelector):
        return strategy
    if isinstance(strategy, (IndexProfile, str)):
        return _coerce_profile(strategy)
    if callable(strategy):
        return strategy
    raise TypeError("selector must be an IndexProfile, canonical string, or callable")


def _validate_generator_ownership(strategy: Any, generator: Any | None) -> None:
    if generator is None:
        return
    if isinstance(strategy, IndexSelector):
        raise TypeError("generator must be omitted when selector is an IndexSelector")
    if (
        callable(strategy)
        and strategy is not RandomValue
        and strategy is not TruffleShuffle
        and strategy is not QuantumMonty
    ):
        raise TypeError("generator must be omitted when selector is a custom callable")


class FlexCat(_ValueEngine[_T], Generic[_K, _T]):
    """Select a category and then a value using independent strategies.

    A strategy is a canonical :class:`IndexProfile`, an ``IndexSelector``, a
    custom index callable, or one of the value-engine classes ``RandomValue``,
    ``TruffleShuffle``, and ``QuantumMonty``.
    """

    __slots__ = ("matrix_data", "key_selector", "value_selectors")

    @overload
    def __init__(
        self,
        matrix_data: Mapping[_K, Iterable[_T]],
        key_selector: Any = IndexProfile.FRONT_TRIANGULAR,
        value_selector: Any = TruffleShuffle,
        *,
        resolve_callables: Literal[False],
        generator: Any | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        matrix_data: Mapping[_K, Iterable[_Resolvable[_T]]],
        key_selector: Any = IndexProfile.FRONT_TRIANGULAR,
        value_selector: Any = TruffleShuffle,
        *,
        resolve_callables: Literal[True] = True,
        generator: Any | None = None,
    ) -> None: ...

    def __init__(
        self,
        matrix_data: Mapping[_K, Iterable[Any]],
        key_selector: Any = IndexProfile.FRONT_TRIANGULAR,
        value_selector: Any = TruffleShuffle,
        *,
        resolve_callables: bool = True,
        generator: Any | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        if not isinstance(matrix_data, Mapping):
            raise TypeError("matrix_data must be a mapping")
        copied_matrix = dict(matrix_data)
        if not copied_matrix:
            raise ValueError("matrix_data must not be empty")

        checked_key_selector = _validated_selection_strategy(key_selector)
        checked_value_selector = _validated_selection_strategy(value_selector)
        _validate_generator_ownership(checked_key_selector, generator)
        _validate_generator_ownership(checked_value_selector, generator)
        materialized_matrix: dict[_K, tuple[Any, ...]] = {}
        for key, values in copied_matrix.items():
            materialized_values = tuple(values)
            if not materialized_values:
                raise ValueError("collection must not be empty")
            materialized_matrix[key] = materialized_values

        keys = tuple(materialized_matrix)
        constructed_key_selector = _selection_engine(
            keys,
            checked_key_selector,
            resolve_callables=False,
            generator=generator,
        )
        constructed_value_selectors = {
            key: _selection_engine(
                values,
                checked_value_selector,
                resolve_callables=resolve_callables,
                generator=generator,
            )
            for key, values in materialized_matrix.items()
        }
        self.matrix_data = materialized_matrix
        self.key_selector = constructed_key_selector
        self.value_selectors = constructed_value_selectors

    @overload
    def __call__(self, cat_key: _K, *args: Any, **kwargs: Any) -> _T: ...

    @overload
    def __call__(self, **kwargs: Any) -> _T: ...

    def __call__(self, cat_key: object = _MISSING, *args: Any, **kwargs: Any) -> _T:
        key = self.key_selector() if cat_key is _MISSING else cast(_K, cat_key)
        return self.value_selectors[key](*args, **kwargs)


def _weighted_pairs(weighted_table: Iterable[tuple[_Weight, _T]]) -> list[tuple[float, _T]]:
    result: list[tuple[float, _T]] = []
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


def _validated_weighted_draw(value: Any, total: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError("generated weighted draw must be a real number")
    try:
        draw = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(
            "generated weighted draw must be representable as a finite float"
        ) from error
    if not math.isfinite(draw):
        raise ValueError("generated weighted draw must be finite")
    if not 0.0 <= draw < total:
        raise ValueError(f"generated weighted draw must be in [0, {total})")
    return draw


class _WeightedChoice(_ValueEngine[_T]):
    __slots__ = ("data", "total")

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        source = self.generator
        if source is None:
            draw_method = _core.random_float
            trusted_native = draw_method is _NATIVE_RANDOM_FLOAT
        else:
            draw_method = source.random_float
            trusted_native = type(source) is _core.Generator
        draw = draw_method(0.0, self.total)
        if not trusted_native:
            draw = _validated_weighted_draw(draw, self.total)
        for cumulative_weight, value in self.data:
            if draw < cumulative_weight:
                return self._resolve(value, *args, **kwargs)
        # A conforming random_float is half-open, but retain a safe last-value
        # fallback for floating-point rounding at the upper boundary.
        return self._resolve(self.data[-1][1], *args, **kwargs)


class RelativeWeightedChoice(_WeightedChoice[_T]):
    """Choose values using nonnegative relative real weights."""

    @overload
    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, _T]],
        *,
        resolve_callables: Literal[False],
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, _Resolvable[_T]]],
        *,
        resolve_callables: Literal[True] = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, Any]],
        *,
        resolve_callables: bool = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        cumulative = 0.0
        data: list[tuple[float, _T]] = []
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


class CumulativeWeightedChoice(_WeightedChoice[_T]):
    """Choose values using finite, positive, strictly increasing thresholds."""

    @overload
    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, _T]],
        *,
        resolve_callables: Literal[False],
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, _Resolvable[_T]]],
        *,
        resolve_callables: Literal[True] = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, Any]],
        *,
        resolve_callables: bool = True,
        generator: _core.Generator | _FloatGenerator | None = None,
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
