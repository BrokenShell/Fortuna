"""Collection selectors built on Fortuna's random generator primitives."""

from __future__ import annotations

import math
import operator
from collections import deque
from collections.abc import Callable, Iterable, MutableSequence
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

_T = TypeVar("_T")
_Weight = int | float
_Resolvable: TypeAlias = _T | Callable[..., "_Resolvable[_T]"]


class _IndexGenerator(Protocol):
    def random_index(self, size: int) -> Any: ...


class _ShuffleGenerator(Protocol):
    def shuffle(self, data: MutableSequence[Any]) -> None: ...


class _FloatGenerator(Protocol):
    def random_float(self, low: float = 0.0, high: float = 1.0) -> Any: ...


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


def _validated_index(value: Any, size: int) -> int:
    index = _integer(value, name="generated index")
    if not 0 <= index < size:
        raise ValueError(f"generated index {index} is outside [0, {size})")
    return index


def _resolve_callable(
    value: Any,
    *args: Any,
    max_depth: int = _DEFAULT_RESOLVE_DEPTH,
    **kwargs: Any,
) -> Any:
    """Resolve callable values while detecting cycles and runaway chains."""
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
        seen.append(current)
        if first_call:
            current = current(*args, **kwargs)
            first_call = False
        else:
            current = current()
        depth += 1
    return current


_NATIVE_RANDOM_INDEX = _core.random_index
_NATIVE_RANDOM_FLOAT = _core.random_float
_NATIVE_SHUFFLE = _core.shuffle
_NATIVE_FRONT_TRIANGULAR = _core.front_triangular
_NATIVE_CENTER_TRIANGULAR = _core.center_triangular
_NATIVE_BACK_TRIANGULAR = _core.back_triangular
_NATIVE_FRONT_POISSON = _core._front_poisson


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
        index = _validated_index(method(size), size)
    else:
        index = _validated_index(generator.random_index(size), size)
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
    index_generator = cast(_IndexGenerator, generator)
    for position in range(len(array) - 1, 0, -1):
        other = _validated_index(index_generator.random_index(position + 1), position + 1)
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
    for position in range(checked_k):
        offset = _validated_index(generator.random_index(size - position), size - position)
        other = position + offset
        data[position], data[other] = data[other], data[position]
    return data[:checked_k]


class _ValueEngine(Generic[_T]):
    __slots__ = ("_generator", "resolve_callables")

    def __init__(self, *, resolve_callables: bool, generator: Any | None) -> None:
        if not isinstance(resolve_callables, bool):
            raise TypeError("resolve_callables must be a bool")
        self.resolve_callables = resolve_callables
        self._generator = generator

    @property
    def generator(self) -> Any | None:
        """Return this engine's read-only draw source."""
        return self._generator

    if TYPE_CHECKING:

        def __call__(self, *args: Any, **kwargs: Any) -> _T: ...

    def take(self, count: int, *args: Any, **kwargs: Any) -> list[_T]:
        checked_count = _integer(count, name="count", minimum=0)
        return [self(*args, **kwargs) for _ in range(checked_count)]


class TruffleShuffle(_ValueEngine[_T]):
    """Stateful wide-uniform selector with randomized forward rotation."""

    __slots__ = (
        "_distance_method",
        "_selector",
        "_trusted_distance",
        "data",
        "rotate_size",
    )

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
        self.rotate_size = max(1, math.isqrt(len(data)))
        self._distance_method: Callable[[int], Any] | None = None
        self._trusted_distance = False
        native_source = type(generator) is _core.Generator or (
            generator is None
            and _core.shuffle is _NATIVE_SHUFFLE
            and _core._front_poisson is _NATIVE_FRONT_POISSON
        )
        if native_source:
            self.data = tuple(data)
            self._selector = _core._wide_index_selector(len(data), generator)
        else:
            shuffle(data, generator=generator)
            self.data = deque(data)
            self._selector = None

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        selector = self._selector
        if selector is not None:
            selected = self.data[selector()]
            if self.resolve_callables and callable(selected):
                return cast(_T, _resolve_callable(selected, *args, **kwargs))
            return cast(_T, selected)
        method = self._distance_method
        if method is None:
            generator = self._generator
            if generator is None:
                method = _core._front_poisson
                self._trusted_distance = method is _NATIVE_FRONT_POISSON
            elif type(generator) is _core.Generator:
                method = generator._front_poisson
                self._trusted_distance = type(generator) is _core.Generator
            else:
                poisson = generator.poisson_variate

                def rejection_distance(size: int) -> int:
                    while True:
                        value = _integer(poisson(size / 4.0), name="generated distance")
                        if value < 0:
                            raise ValueError("generated distance must be nonnegative")
                        if value < size:
                            return value

                method = rejection_distance
                self._trusted_distance = True
            self._distance_method = method
        value = method(self.rotate_size)
        if self._trusted_distance:
            distance = 1 + value
        else:
            distance = 1 + _validated_index(value, self.rotate_size)
        cast(deque[Any], self.data).rotate(distance)
        selected = self.data[-1]
        if self.resolve_callables and callable(selected):
            return cast(_T, _resolve_callable(selected, *args, **kwargs))
        return selected


class RandomValue(_ValueEngine[_T]):
    """Prepared value generator with uniform, cyclic, and positional strategies."""

    __slots__ = ("_cycle", "_truffle", "data", "size")

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

    def uniform(self, *args: Any, **kwargs: Any) -> _T:
        generator = self._generator
        if generator is None:
            method = _core.random_index
            if method is _NATIVE_RANDOM_INDEX:
                value = _core._random_value_materialized(self.data)
            else:
                value = self.data[_validated_index(method(self.size), self.size)]
        elif type(generator) is _core.Generator:
            value = generator.random_value(self.data)
        else:
            value = self.data[_validated_index(generator.random_index(self.size), self.size)]
        if self.resolve_callables and callable(value):
            return cast(_T, _resolve_callable(value, *args, **kwargs))
        return value

    __call__ = uniform

    def cycle(self, *args: Any, **kwargs: Any) -> _T:
        value = next(self._cycle)
        if self.resolve_callables and callable(value):
            return cast(_T, _resolve_callable(value, *args, **kwargs))
        return value

    def truffle_shuffle(self, *args: Any, **kwargs: Any) -> _T:
        selector = self._truffle
        if selector is None:
            selector = TruffleShuffle(
                self.data,
                resolve_callables=self.resolve_callables,
                generator=self._generator,
            )
            self._truffle = selector
        return selector(*args, **kwargs)

    # Keep the three profile paths explicit. A shared string-dispatch helper
    # adds another Python call and getattr to every prepared selection.
    def front_triangular(self, *args: Any, **kwargs: Any) -> _T:
        generator = self._generator
        if generator is None:
            method = _core.front_triangular
            index = method(self.size)
            if method is not _NATIVE_FRONT_TRIANGULAR:
                index = _validated_index(index, self.size)
        elif type(generator) is _core.Generator:
            index = generator.front_triangular(self.size)
        else:
            index = _validated_index(generator.front_triangular(self.size), self.size)
        value = self.data[index]
        if self.resolve_callables and callable(value):
            return cast(_T, _resolve_callable(value, *args, **kwargs))
        return value

    def center_triangular(self, *args: Any, **kwargs: Any) -> _T:
        generator = self._generator
        if generator is None:
            method = _core.center_triangular
            index = method(self.size)
            if method is not _NATIVE_CENTER_TRIANGULAR:
                index = _validated_index(index, self.size)
        elif type(generator) is _core.Generator:
            index = generator.center_triangular(self.size)
        else:
            index = _validated_index(generator.center_triangular(self.size), self.size)
        value = self.data[index]
        if self.resolve_callables and callable(value):
            return cast(_T, _resolve_callable(value, *args, **kwargs))
        return value

    def back_triangular(self, *args: Any, **kwargs: Any) -> _T:
        generator = self._generator
        if generator is None:
            method = _core.back_triangular
            index = method(self.size)
            if method is not _NATIVE_BACK_TRIANGULAR:
                index = _validated_index(index, self.size)
        elif type(generator) is _core.Generator:
            index = generator.back_triangular(self.size)
        else:
            index = _validated_index(generator.back_triangular(self.size), self.size)
        value = self.data[index]
        if self.resolve_callables and callable(value):
            return cast(_T, _resolve_callable(value, *args, **kwargs))
        return value


def _weighted_pairs(
    weighted_table: Iterable[tuple[_Weight, _T]],
    *,
    table_name: str,
    number_name: str,
) -> list[tuple[float, _T]]:
    result: list[tuple[float, _T]] = []
    try:
        iterator = iter(weighted_table)
    except TypeError as error:
        message = f"{table_name} must be an iterable of ({number_name}, value) pairs"
        raise TypeError(message) from error
    for position, pair in enumerate(iterator):
        try:
            number, value = pair
        except (TypeError, ValueError) as error:
            raise TypeError(
                f"{table_name} item {position} must be a ({number_name}, value) pair"
            ) from error
        if isinstance(number, bool) or not isinstance(number, Real):
            raise TypeError(f"{number_name} at position {position} must be a real number")
        try:
            numeric = float(number)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                f"{number_name} at position {position} must be representable as a float"
            ) from error
        if not math.isfinite(numeric):
            raise ValueError(f"{number_name} at position {position} must be finite")
        result.append((numeric, value))
    if not result:
        raise ValueError(f"{table_name} must not be empty")
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


class WeightedChoice(_ValueEngine[_T]):
    """Prepare selection from one relative-weight or cumulative-boundary table.

    A positional table is equivalent to the explicit ``relative=`` form.
    """

    __slots__ = ("_selector", "data", "total")

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

    @overload
    def __init__(
        self,
        *,
        relative: Iterable[tuple[_Weight, _T]],
        resolve_callables: Literal[False],
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        relative: Iterable[tuple[_Weight, _Resolvable[_T]]],
        resolve_callables: Literal[True] = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        cumulative: Iterable[tuple[_Weight, _T]],
        resolve_callables: Literal[False],
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        cumulative: Iterable[tuple[_Weight, _Resolvable[_T]]],
        resolve_callables: Literal[True] = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None: ...

    def __init__(
        self,
        weighted_table: Iterable[tuple[_Weight, Any]] | None = None,
        *,
        relative: Iterable[tuple[_Weight, Any]] | None = None,
        cumulative: Iterable[tuple[_Weight, Any]] | None = None,
        resolve_callables: bool = True,
        generator: _core.Generator | _FloatGenerator | None = None,
    ) -> None:
        super().__init__(resolve_callables=resolve_callables, generator=generator)
        supplied = sum(source is not None for source in (weighted_table, relative, cumulative))
        if supplied != 1:
            raise TypeError(
                "WeightedChoice requires exactly one of weighted_table, relative, or cumulative"
            )

        cumulative_input = cumulative is not None
        if cumulative_input:
            table = cast(Iterable[tuple[_Weight, Any]], cumulative)
            table_name = "cumulative"
            number_name = "cumulative boundary"
        else:
            table = cast(
                Iterable[tuple[_Weight, Any]],
                relative if relative is not None else weighted_table,
            )
            table_name = "relative" if relative is not None else "weighted_table"
            number_name = "weight"

        data: list[tuple[float, _T]] = []
        boundaries: list[float] = []
        total = 0.0
        for number, value in _weighted_pairs(table, table_name=table_name, number_name=number_name):
            if number < 0.0:
                if cumulative_input:
                    raise ValueError("cumulative boundaries must be nonnegative")
                raise ValueError("weights must be nonnegative")
            if cumulative_input:
                if boundaries and number < total:
                    raise ValueError("cumulative boundaries must be nondecreasing")
                total = number
            else:
                total += number
                if not math.isfinite(total):
                    raise ValueError("weight total must be finite")
            boundaries.append(total)
            data.append((total, value))
        if total <= 0.0:
            if cumulative_input:
                raise ValueError("final cumulative boundary must be positive")
            raise ValueError("at least one weight must be positive")
        self.data = tuple(data)
        self.total = total
        native_source = type(generator) is _core.Generator or (
            generator is None and _core.random_float is _NATIVE_RANDOM_FLOAT
        )
        native_generator = cast(_core.Generator | None, generator)
        self._selector = (
            _core._prepared_cumulative_weighted_index(boundaries, native_generator)
            if native_source
            else None
        )

    def __call__(self, *args: Any, **kwargs: Any) -> _T:
        source = self._generator
        selector = self._selector
        if selector is not None and (
            source is not None or _core.random_float is _NATIVE_RANDOM_FLOAT
        ):
            selected = self.data[selector()][1]
        else:
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
                    selected = value
                    break
            else:
                selected = self.data[-1][1]
        if self.resolve_callables and callable(selected):
            return cast(_T, _resolve_callable(selected, *args, **kwargs))
        return selected
