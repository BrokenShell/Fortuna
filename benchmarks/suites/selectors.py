"""Benchmarks for Fortuna's public selector and collection APIs."""

from __future__ import annotations

import importlib
import random
from collections.abc import Callable
from typing import Any

from benchmarks.model import BenchmarkCase, BenchmarkUnit

SUITE = "selectors"
SEED = 0x5EED
VALUES_100 = tuple(range(100))
SAMPLE_REGIMES = ((100, 10), (1_000, 10), (1_000, 500))
WEIGHT_SIZES = (4, 100, 1_000)
SHUFFLE_SIZES = (0, 1, 10, 100, 1_000, 10_000, 100_000, 1_000_000)
RANDOM_VALUE_METHODS = (
    "uniform",
    "cycle",
    "truffle_shuffle",
    "front_triangular",
    "center_triangular",
    "back_triangular",
    "front_normal",
    "center_normal",
    "back_normal",
)

VALUES_100_FIXTURE = {
    "id": "values-100",
    "type": "tuple",
    "recipe": "tuple(range(100))",
    "size": 100,
}


def _fixture_reference(identifier: str) -> dict[str, str]:
    return {"fixture": identifier}


def _range_fixture(identifier: str, *, size: int, container: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "type": container,
        "recipe": f"{container}(range({size}))",
        "size": size,
    }


def _weighted_fixture(size: int, *, weight_model: str = "relative") -> dict[str, Any]:
    if weight_model == "relative":
        recipe = "tuple((1.0, index) for index in range(size))"
    elif weight_model == "cumulative":
        recipe = "tuple((float(index + 1), index) for index in range(size))"
    else:
        raise ValueError(f"unknown weight model: {weight_model}")
    return {
        "id": f"weighted-{weight_model}-{size}",
        "type": "tuple[tuple[float, int], ...]",
        "recipe": recipe,
        "size": size,
        "weight_model": weight_model,
    }


class _ConstantIndexGenerator:
    """Minimal deterministic dependency-injection target."""

    def random_index(self, size: int) -> int:
        return 0


def _resolved_value() -> int:
    return 1


def _load_fortuna() -> tuple[Any | None, str | None]:
    try:
        return importlib.import_module("Fortuna"), None
    except Exception as error:
        return None, f"Fortuna unavailable: {type(error).__name__}: {error}"


def _case(
    name: str,
    fortuna: Any | None,
    import_error: str | None,
    setup_factory: Callable[[Any], Callable[[], Any]],
    *,
    unit: BenchmarkUnit = "call",
    values_per_call: int = 1,
    description: str = "",
    workload_args: tuple[Any, ...] = (),
    workload_kwargs: dict[str, Any] | None = None,
    workload_input: Any,
    setup_variant: str,
    seed: int | None = SEED,
) -> BenchmarkCase:
    workload = {
        "args": workload_args,
        "kwargs": workload_kwargs or {},
        "seed": seed,
        "input": workload_input,
        "setup_variant": setup_variant,
    }
    if fortuna is None:
        return BenchmarkCase(
            SUITE,
            name,
            unit=unit,
            values_per_call=values_per_call,
            description=description,
            skip_reason=import_error or "Fortuna unavailable",
            workload=workload,
        )
    return BenchmarkCase(
        SUITE,
        name,
        setup=lambda: setup_factory(fortuna),
        unit=unit,
        values_per_call=values_per_call,
        description=description,
        workload=workload,
    )


def _random_value_method_setup(
    fortuna: Any,
    *,
    method_name: str,
    source: str,
    callable_values: bool = False,
    resolve_callables: bool = True,
) -> Callable[[], Any]:
    values = (_resolved_value,) * 100 if callable_values else VALUES_100
    generator = None
    if source == "module":
        fortuna.seed(SEED)
    elif source == "generator":
        generator = fortuna.Generator(SEED)
    else:
        raise ValueError(f"unknown RandomValue source: {source}")
    selector = fortuna.RandomValue(
        values,
        generator=generator,
        resolve_callables=resolve_callables,
    )
    return getattr(selector, method_name)


def _random_value_take_setup(fortuna: Any, count: int) -> Callable[[], Any]:
    fortuna.seed(SEED)
    selector = fortuna.RandomValue(VALUES_100)
    return lambda: selector.take(count)


def _random_value_construction_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.RandomValue(VALUES_100)


def _random_value_function_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.random_value(VALUES_100)


def _truffle_call_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return fortuna.TruffleShuffle(VALUES_100)


def _truffle_construction_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.TruffleShuffle(VALUES_100)


def _weighted_data(size: int) -> tuple[tuple[float, int], ...]:
    return tuple((1.0, index) for index in range(size))


def _cumulative_weighted_data(size: int) -> tuple[tuple[float, int], ...]:
    return tuple((float(index + 1), index) for index in range(size))


def _weighted_call_setup(fortuna: Any, *, size: int) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return fortuna.WeightedChoice(_weighted_data(size))


def _weighted_construction_setup(fortuna: Any, *, size: int) -> Callable[[], Any]:
    fortuna.seed(SEED)
    data = _weighted_data(size)
    return lambda: fortuna.WeightedChoice(data)


def _cumulative_weighted_call_setup(fortuna: Any, *, size: int) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return fortuna.WeightedChoice(cumulative=_cumulative_weighted_data(size))


def _cumulative_weighted_construction_setup(fortuna: Any, *, size: int) -> Callable[[], Any]:
    fortuna.seed(SEED)
    data = _cumulative_weighted_data(size)
    return lambda: fortuna.WeightedChoice(cumulative=data)


def _sample_setup(
    fortuna: Any,
    *,
    size: int,
    count: int,
    source: str,
) -> Callable[[], Any]:
    population = tuple(range(size))
    if source == "module":
        fortuna.seed(SEED)
        return lambda: fortuna.sample(population, count)
    if source == "explicit-generator":
        generator = fortuna.Generator(SEED)
        return lambda: fortuna.sample(population, count, generator=generator)
    if source == "generator-method":
        generator = fortuna.Generator(SEED)
        return lambda: generator.sample(population, count)
    if source == "custom-generator":
        generator = _ConstantIndexGenerator()
        return lambda: fortuna.sample(population, count, generator=generator)
    generator = random.Random(SEED)
    return lambda: generator.sample(population, count)


def _shuffle_setup(fortuna: Any, *, size: int, generator_method: bool) -> Callable[[], Any]:
    values = list(range(size))
    if generator_method:
        generator = fortuna.Generator(SEED)
        return lambda: generator.shuffle(values)
    fortuna.seed(SEED)
    return lambda: fortuna.shuffle(values)


def selector_cases() -> list[BenchmarkCase]:
    fortuna, error = _load_fortuna()
    cases: list[BenchmarkCase] = []

    for source in ("module", "generator"):
        source_input = {
            "module": {"type": "Fortuna module-global engine", "seed": SEED},
            "generator": {"type": "Fortuna.Generator", "seed": SEED},
        }[source]
        for method_name in RANDOM_VALUE_METHODS:
            cases.append(
                _case(
                    f"random-value-{method_name.replace('_', '-')}-{source}-100",
                    fortuna,
                    error,
                    lambda module, method_name=method_name, source=source: (
                        _random_value_method_setup(
                            module,
                            method_name=method_name,
                            source=source,
                        )
                    ),
                    workload_input={
                        "callable": f"RandomValue.{method_name}",
                        "constructor": {
                            "values": _fixture_reference("values-100"),
                            "generator": source_input,
                        },
                        "fixtures": [VALUES_100_FIXTURE],
                    },
                    setup_variant="reused RandomValue",
                )
            )

    for label, callable_values, resolve_callables in (
        ("call-uniform", False, True),
        ("callable-resolution", True, True),
        ("callable-resolution-disabled", True, False),
    ):

        def random_value_call_factory(
            module: Any,
            callable_values: bool = callable_values,
            resolve_callables: bool = resolve_callables,
        ) -> Callable[[], Any]:
            return _random_value_method_setup(
                module,
                method_name="__call__",
                source="module",
                callable_values=callable_values,
                resolve_callables=resolve_callables,
            )

        cases.append(
            _case(
                f"random-value-{label}-module-100",
                fortuna,
                error,
                random_value_call_factory,
                workload_input={
                    "callable": "RandomValue.__call__",
                    "constructor": {
                        "resolve_callables": resolve_callables,
                        "values": (
                            {
                                "id": "resolved-callables-100",
                                "type": "tuple[callable, ...]",
                                "recipe": "(_resolved_value,) * 100",
                                "size": 100,
                            }
                            if callable_values
                            else _fixture_reference("values-100")
                        ),
                    },
                    "fixtures": [VALUES_100_FIXTURE] if not callable_values else [],
                },
                setup_variant="reused RandomValue",
            )
        )

    for count in (10, 1_000):
        cases.append(
            _case(
                f"random-value-take-{count}",
                fortuna,
                error,
                lambda module, count=count: _random_value_take_setup(module, count),
                unit="value",
                values_per_call=count,
                workload_args=(count,),
                workload_input={
                    "callable": "RandomValue.take",
                    "constructor": {"values": _fixture_reference("values-100")},
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="reused RandomValue",
            )
        )

    cases.extend(
        (
            _case(
                "random-value-function-100",
                fortuna,
                error,
                _random_value_function_setup,
                workload_args=(_fixture_reference("values-100"),),
                workload_input={
                    "callable": "random_value",
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="module-level function",
            ),
            _case(
                "random-value-construction-100",
                fortuna,
                error,
                _random_value_construction_setup,
                workload_args=(_fixture_reference("values-100"),),
                workload_input={
                    "callable": "RandomValue",
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="RandomValue construction",
            ),
            _case(
                "truffle-call-100",
                fortuna,
                error,
                _truffle_call_setup,
                workload_input={
                    "callable": "TruffleShuffle.__call__",
                    "constructor": {"values": _fixture_reference("values-100")},
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="reused TruffleShuffle",
            ),
            _case(
                "truffle-construction-100",
                fortuna,
                error,
                _truffle_construction_setup,
                workload_args=(_fixture_reference("values-100"),),
                workload_input={
                    "callable": "TruffleShuffle",
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="TruffleShuffle construction",
            ),
        )
    )

    for size in WEIGHT_SIZES:
        fixture = _weighted_fixture(size)
        cumulative_fixture = _weighted_fixture(size, weight_model="cumulative")
        cases.extend(
            (
                _case(
                    f"weighted-choice-call-{size}",
                    fortuna,
                    error,
                    lambda module, size=size: _weighted_call_setup(module, size=size),
                    workload_input={
                        "callable": "WeightedChoice.__call__",
                        "constructor": {"weighted_table": _fixture_reference(fixture["id"])},
                        "fixtures": [fixture],
                    },
                    setup_variant="reused WeightedChoice",
                ),
                _case(
                    f"weighted-choice-construction-{size}",
                    fortuna,
                    error,
                    lambda module, size=size: _weighted_construction_setup(
                        module,
                        size=size,
                    ),
                    workload_args=(_fixture_reference(fixture["id"]),),
                    workload_input={
                        "callable": "WeightedChoice",
                        "fixtures": [fixture],
                    },
                    setup_variant="WeightedChoice construction",
                ),
                _case(
                    f"weighted-choice-cumulative-call-{size}",
                    fortuna,
                    error,
                    lambda module, size=size: _cumulative_weighted_call_setup(
                        module,
                        size=size,
                    ),
                    workload_input={
                        "callable": "WeightedChoice.__call__",
                        "constructor": {"cumulative": _fixture_reference(cumulative_fixture["id"])},
                        "fixtures": [cumulative_fixture],
                    },
                    setup_variant="reused cumulative WeightedChoice",
                ),
                _case(
                    f"weighted-choice-cumulative-construction-{size}",
                    fortuna,
                    error,
                    lambda module, size=size: _cumulative_weighted_construction_setup(
                        module,
                        size=size,
                    ),
                    workload_kwargs={"cumulative": _fixture_reference(cumulative_fixture["id"])},
                    workload_input={
                        "callable": "WeightedChoice",
                        "fixtures": [cumulative_fixture],
                    },
                    setup_variant="cumulative WeightedChoice construction",
                ),
            )
        )

    for size, count in SAMPLE_REGIMES:
        for source in ("module", "explicit-generator", "generator-method", "stdlib"):
            population_id = f"population-{size}"
            population = _range_fixture(population_id, size=size, container="tuple")
            source_input: dict[str, Any] = {
                "type": "Fortuna module-global engine",
                "seed": SEED,
            }
            workload_kwargs: dict[str, Any] = {}
            if source == "explicit-generator":
                workload_kwargs = {"generator": {"fixture": "fortuna-generator"}}
                source_input = {
                    "type": "Fortuna.Generator",
                    "id": "fortuna-generator",
                    "seed": SEED,
                }
            elif source == "generator-method":
                source_input = {"type": "Fortuna.Generator", "seed": SEED}
            elif source == "stdlib":
                source_input = {"type": "random.Random", "seed": SEED}
            cases.append(
                _case(
                    f"sample-{source}-{size}-{count}",
                    fortuna,
                    error,
                    lambda module, size=size, count=count, source=source: _sample_setup(
                        module,
                        size=size,
                        count=count,
                        source=source,
                    ),
                    workload_args=(_fixture_reference(population_id), count),
                    workload_kwargs=workload_kwargs,
                    workload_input={
                        "callable": {
                            "module": "Fortuna.sample",
                            "explicit-generator": "Fortuna.sample",
                            "generator-method": "Generator.sample",
                            "stdlib": "random.Random.sample",
                        }[source],
                        "source": source_input,
                        "fixtures": [population],
                    },
                    setup_variant="reused seeded source",
                )
            )

    custom_population = _range_fixture("population-100", size=100, container="tuple")
    cases.append(
        _case(
            "sample-custom-generator-100-10",
            fortuna,
            error,
            lambda module: _sample_setup(
                module,
                size=100,
                count=10,
                source="custom-generator",
            ),
            workload_args=(_fixture_reference("population-100"), 10),
            workload_kwargs={"generator": {"fixture": "constant-index-generator"}},
            workload_input={
                "callable": "Fortuna.sample",
                "source": {
                    "id": "constant-index-generator",
                    "type": "_ConstantIndexGenerator",
                    "recipe": "random_index(size) returns 0",
                    "seed": None,
                },
                "fixtures": [custom_population],
            },
            setup_variant="custom generator fallback",
            seed=None,
        )
    )

    for size in SHUFFLE_SIZES:
        values_id = f"mutable-values-{size}"
        values = _range_fixture(values_id, size=size, container="list")
        cases.append(
            _case(
                f"shuffle-public-{size}",
                fortuna,
                error,
                lambda module, size=size: _shuffle_setup(
                    module,
                    size=size,
                    generator_method=False,
                ),
                workload_args=(_fixture_reference(values_id),),
                workload_input={
                    "callable": "Fortuna.shuffle",
                    "mutation": "in place across timed loop iterations",
                    "fixtures": [values],
                },
                setup_variant="public module shuffle",
            )
        )

    for size in SHUFFLE_SIZES:
        values_id = f"mutable-values-{size}"
        cases.append(
            _case(
                f"shuffle-generator-method-{size}",
                fortuna,
                error,
                lambda module, size=size: _shuffle_setup(
                    module,
                    size=size,
                    generator_method=True,
                ),
                workload_args=(_fixture_reference(values_id),),
                workload_input={
                    "callable": "Generator.shuffle",
                    "source": {"type": "Fortuna.Generator", "seed": SEED},
                    "mutation": "in place across timed loop iterations",
                    "fixtures": [_range_fixture(values_id, size=size, container="list")],
                },
                setup_variant="Generator.shuffle",
            )
        )
    return cases
