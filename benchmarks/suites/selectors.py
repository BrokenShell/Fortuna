"""Benchmarks for Fortuna's Python selector and composite APIs."""

from __future__ import annotations

import importlib
import random
from collections.abc import Callable
from typing import Any

from benchmarks.model import BenchmarkCase, BenchmarkUnit

SUITE = "selectors"
SEED = 0x5EED
VALUES_100 = tuple(range(100))
MATRIX_10X10 = {key: tuple(range(key * 10, (key + 1) * 10)) for key in range(10)}
SAMPLE_REGIMES = ((100, 10), (1_000, 10), (1_000, 500))
WEIGHT_SIZES = (4, 100, 1_000)
INDEX_PROFILES = (
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
)

VALUES_100_FIXTURE = {
    "id": "values-100",
    "type": "tuple",
    "recipe": "tuple(range(100))",
    "size": 100,
}
MATRIX_10X10_FIXTURE = {
    "id": "matrix-10x10",
    "type": "dict[int, tuple[int, ...]]",
    "recipe": "key -> tuple(range(key * 10, (key + 1) * 10))",
    "keys": 10,
    "values_per_key": 10,
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


def _weighted_fixture(size: int, *, cumulative: bool) -> dict[str, Any]:
    label = "cumulative" if cumulative else "relative"
    return {
        "id": f"weighted-{label}-{size}",
        "type": "tuple[tuple[float, int], ...]",
        "recipe": (
            "tuple((float(index + 1), index) for index in range(size))"
            if cumulative
            else "tuple((1.0, index) for index in range(size))"
        ),
        "size": size,
        "weight_model": label,
    }


class _ConstantIndexGenerator:
    """Minimal deterministic dependency-injection target."""

    def random_index(self, size: int, *, count: int | None = None) -> int | list[int]:
        if count is None:
            return 0
        return [0] * count


class _ResolutionChain:
    __slots__ = ("remaining",)

    def __init__(self, remaining: int) -> None:
        self.remaining = remaining

    def __call__(self) -> int | _ResolutionChain:
        if self.remaining == 0:
            return 1
        return _ResolutionChain(self.remaining - 1)


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
    workload_input: Any = None,
    setup_variant: str,
    seed: int | None = SEED,
) -> BenchmarkCase:
    if fortuna is None:
        return BenchmarkCase(SUITE, name, skip_reason=import_error or "Fortuna unavailable")
    return BenchmarkCase(
        SUITE,
        name,
        setup=lambda: setup_factory(fortuna),
        unit=unit,
        values_per_call=values_per_call,
        description=description,
        workload={
            "args": workload_args,
            "kwargs": workload_kwargs or {},
            "seed": seed,
            "input": workload_input,
            "setup_variant": setup_variant,
        },
    )


def _index_selector_setup(
    fortuna: Any,
    *,
    source: str,
    profile: str,
    count: int | None,
) -> Callable[[], Any]:
    if source == "module":
        fortuna.seed(SEED)
        generator = None
    elif source == "generator":
        generator = fortuna.Generator(SEED)
    else:
        generator = _ConstantIndexGenerator()
    selector = fortuna.IndexSelector(profile, generator=generator)
    if count is None:
        return lambda: selector(100)
    return lambda: selector(100, count=count)


def _random_value_setup(
    fortuna: Any,
    *,
    resolve_callables: bool,
    callable_values: bool,
) -> Callable[[], Any]:
    fortuna.seed(SEED)
    values = (_resolved_value,) * 100 if callable_values else VALUES_100
    selector = fortuna.RandomValue(values, resolve_callables=resolve_callables)
    return selector


def _random_value_construction_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.RandomValue(VALUES_100)


def _random_value_function_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.random_value(VALUES_100)


def _truffle_call_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    selector = fortuna.TruffleShuffle(VALUES_100)
    return selector


def _truffle_construction_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.TruffleShuffle(VALUES_100)


def _quantum_setup(fortuna: Any, operation: str) -> Callable[[], Any]:
    fortuna.seed(SEED)
    selector = fortuna.QuantumMonty(VALUES_100)
    if operation == "named":
        return selector.front_triangular
    if operation == "mixed":
        return selector
    if operation == "cycle":
        return selector.cycle
    if operation == "dispatch-enum":
        profile = fortuna.IndexProfile.CENTER_NORMAL
        return lambda: selector.dispatch(profile)
    if operation == "dispatch-string":
        return lambda: selector.dispatch("center_normal")
    raise ValueError(f"unknown QuantumMonty benchmark operation: {operation}")


def _quantum_construction_setup(fortuna: Any) -> Callable[[], Any]:
    fortuna.seed(SEED)
    return lambda: fortuna.QuantumMonty(VALUES_100)


def _flex_setup(fortuna: Any, *, uniform: bool, explicit_key: bool) -> Callable[[], Any]:
    fortuna.seed(SEED)
    kwargs = {"key_selector": "uniform", "value_selector": "uniform"} if uniform else {}
    selector = fortuna.FlexCat(MATRIX_10X10, **kwargs)
    if explicit_key:
        return lambda: selector(3)
    return selector


def _flex_construction_setup(fortuna: Any, *, uniform: bool) -> Callable[[], Any]:
    fortuna.seed(SEED)
    kwargs = {"key_selector": "uniform", "value_selector": "uniform"} if uniform else {}
    return lambda: fortuna.FlexCat(MATRIX_10X10, **kwargs)


def _weighted_data(size: int, *, cumulative: bool) -> tuple[tuple[float, int], ...]:
    if cumulative:
        return tuple((float(index + 1), index) for index in range(size))
    return tuple((1.0, index) for index in range(size))


def _weighted_call_setup(
    fortuna: Any,
    *,
    size: int,
    cumulative: bool,
) -> Callable[[], Any]:
    fortuna.seed(SEED)
    selector_type = (
        fortuna.CumulativeWeightedChoice if cumulative else fortuna.RelativeWeightedChoice
    )
    return selector_type(_weighted_data(size, cumulative=cumulative))


def _weighted_construction_setup(
    fortuna: Any,
    *,
    size: int,
    cumulative: bool,
) -> Callable[[], Any]:
    fortuna.seed(SEED)
    selector_type = (
        fortuna.CumulativeWeightedChoice if cumulative else fortuna.RelativeWeightedChoice
    )
    data = _weighted_data(size, cumulative=cumulative)
    return lambda: selector_type(data)


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


def _resolve_setup(fortuna: Any, operation: str) -> Callable[[], Any]:
    if operation == "noncallable":
        return lambda: fortuna.resolve(1)
    if operation == "disabled":
        return lambda: fortuna.resolve(_resolved_value, resolve_callables=False)
    if operation == "one":
        return lambda: fortuna.resolve(_resolved_value)
    if operation == "depth-10":
        chain = _ResolutionChain(9)
        return lambda: fortuna.resolve(chain)
    if operation == "depth-100":
        chain = _ResolutionChain(99)
        return lambda: fortuna.resolve(chain)
    raise ValueError(f"unknown resolve benchmark operation: {operation}")


def selector_cases() -> list[BenchmarkCase]:
    fortuna, error = _load_fortuna()
    cases: list[BenchmarkCase] = []

    index_workloads = [
        (f"index-{profile.replace('_', '-')}-scalar-{source}", source, profile, None)
        for profile in INDEX_PROFILES
        for source in ("module", "generator")
    ]
    index_workloads.extend(
        (
            f"index-{profile.replace('_', '-')}-bulk-{source}-1000",
            source,
            profile,
            1_000,
        )
        for profile in INDEX_PROFILES
        for source in ("module", "generator")
    )
    index_workloads.extend(
        (
            ("index-uniform-scalar-custom", "custom", "uniform", None),
            ("index-uniform-bulk-custom-1000", "custom", "uniform", 1_000),
        )
    )

    for name, source, profile, count in index_workloads:
        workload_seed = None if source == "custom" else SEED
        generator_input = {
            "module": {"type": "Fortuna module-global engine", "seed": SEED},
            "generator": {"type": "Fortuna.Generator", "seed": SEED},
            "custom": {
                "type": "_ConstantIndexGenerator",
                "recipe": "random_index returns 0 or count zeros",
            },
        }[source]
        cases.append(
            _case(
                name,
                fortuna,
                error,
                lambda module, source=source, profile=profile, count=count: _index_selector_setup(
                    module,
                    source=source,
                    profile=profile,
                    count=count,
                ),
                unit="value" if count is not None else "call",
                values_per_call=count or 1,
                workload_args=(100,),
                workload_kwargs={} if count is None else {"count": count},
                workload_input={
                    "callable": "IndexSelector.__call__",
                    "selector": {"profile": profile, "generator": generator_input},
                },
                setup_variant="reused IndexSelector",
                seed=workload_seed,
            )
        )

    for name, resolve_callables, callable_values in (
        ("random-value-noncallable", True, False),
        ("random-value-resolution-disabled", False, True),
        ("random-value-callable", True, True),
    ):

        def random_value_factory(
            module: Any,
            resolve_callables: bool = resolve_callables,
            callable_values: bool = callable_values,
        ) -> Callable[[], Any]:
            return _random_value_setup(
                module,
                resolve_callables=resolve_callables,
                callable_values=callable_values,
            )

        cases.append(
            _case(
                name,
                fortuna,
                error,
                random_value_factory,
                workload_input={
                    "callable": "RandomValue.__call__",
                    "constructor": {"resolve_callables": resolve_callables},
                    "values": (
                        {
                            "id": "resolved-callables-100",
                            "type": "tuple[callable, ...]",
                            "recipe": "(_resolved_value,) * 100",
                            "size": 100,
                        }
                        if callable_values
                        else VALUES_100_FIXTURE
                    ),
                },
                setup_variant="reused RandomValue",
            )
        )
    cases.append(
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
        )
    )
    cases.append(
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
        )
    )

    cases.extend(
        (
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

    for operation in ("named", "mixed", "cycle", "dispatch-enum", "dispatch-string"):
        if operation == "dispatch-enum":
            workload_args = ({"enum": "IndexProfile.CENTER_NORMAL"},)
        elif operation == "dispatch-string":
            workload_args = ("center_normal",)
        else:
            workload_args = ()
        cases.append(
            _case(
                f"quantum-{operation}-100",
                fortuna,
                error,
                lambda module, operation=operation: _quantum_setup(module, operation),
                workload_args=workload_args,
                workload_input={
                    "callable": {
                        "named": "QuantumMonty.front_triangular",
                        "mixed": "QuantumMonty.__call__",
                        "cycle": "QuantumMonty.cycle",
                        "dispatch-enum": "QuantumMonty.dispatch",
                        "dispatch-string": "QuantumMonty.dispatch",
                    }[operation],
                    "constructor": {"values": _fixture_reference("values-100")},
                    "fixtures": [VALUES_100_FIXTURE],
                },
                setup_variant="reused QuantumMonty",
            )
        )
    cases.append(
        _case(
            "quantum-construction-100",
            fortuna,
            error,
            _quantum_construction_setup,
            workload_args=(_fixture_reference("values-100"),),
            workload_input={
                "callable": "QuantumMonty",
                "fixtures": [VALUES_100_FIXTURE],
            },
            setup_variant="QuantumMonty construction",
        )
    )

    for configuration, uniform in (("default", False), ("uniform", True)):
        constructor_kwargs = (
            {"key_selector": "uniform", "value_selector": "uniform"} if uniform else {}
        )
        for selection, explicit_key in (("explicit-key", True), ("random-key", False)):
            cases.append(
                _case(
                    f"flex-{configuration}-{selection}-10x10",
                    fortuna,
                    error,
                    lambda module, uniform=uniform, explicit_key=explicit_key: _flex_setup(
                        module,
                        uniform=uniform,
                        explicit_key=explicit_key,
                    ),
                    workload_args=(3,) if explicit_key else (),
                    workload_input={
                        "callable": "FlexCat.__call__",
                        "constructor": {
                            "mapping": _fixture_reference("matrix-10x10"),
                            "kwargs": constructor_kwargs,
                        },
                        "fixtures": [MATRIX_10X10_FIXTURE],
                    },
                    setup_variant="reused FlexCat",
                )
            )
        cases.append(
            _case(
                f"flex-{configuration}-construction-10x10",
                fortuna,
                error,
                lambda module, uniform=uniform: _flex_construction_setup(
                    module,
                    uniform=uniform,
                ),
                workload_args=(_fixture_reference("matrix-10x10"),),
                workload_kwargs=constructor_kwargs,
                workload_input={
                    "callable": "FlexCat",
                    "fixtures": [MATRIX_10X10_FIXTURE],
                },
                setup_variant="FlexCat construction",
            )
        )

    for size in WEIGHT_SIZES:
        for label, cumulative in (("relative", False), ("cumulative", True)):
            fixture = _weighted_fixture(size, cumulative=cumulative)
            selector_type = "CumulativeWeightedChoice" if cumulative else "RelativeWeightedChoice"
            cases.append(
                _case(
                    f"weighted-{label}-call-{size}",
                    fortuna,
                    error,
                    lambda module, size=size, cumulative=cumulative: _weighted_call_setup(
                        module,
                        size=size,
                        cumulative=cumulative,
                    ),
                    workload_input={
                        "callable": f"{selector_type}.__call__",
                        "constructor": {"weighted_values": _fixture_reference(fixture["id"])},
                        "fixtures": [fixture],
                    },
                    setup_variant="reused weighted selector",
                )
            )
            cases.append(
                _case(
                    f"weighted-{label}-construction-{size}",
                    fortuna,
                    error,
                    lambda module, size=size, cumulative=cumulative: _weighted_construction_setup(
                        module,
                        size=size,
                        cumulative=cumulative,
                    ),
                    workload_args=(_fixture_reference(fixture["id"]),),
                    workload_input={
                        "callable": selector_type,
                        "fixtures": [fixture],
                    },
                    setup_variant="weighted selector construction",
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
    custom_sample_population = _range_fixture(
        "population-100",
        size=100,
        container="tuple",
    )
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
                "fixtures": [custom_sample_population],
            },
            setup_variant="custom generator fallback",
            seed=None,
        )
    )
    for size in (0, 1, 10, 100):
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
    cases.append(
        _case(
            "shuffle-generator-method-100",
            fortuna,
            error,
            lambda module: _shuffle_setup(module, size=100, generator_method=True),
            workload_args=(_fixture_reference("mutable-values-100"),),
            workload_input={
                "callable": "Generator.shuffle",
                "source": {"type": "Fortuna.Generator", "seed": SEED},
                "mutation": "in place across timed loop iterations",
                "fixtures": [_range_fixture("mutable-values-100", size=100, container="list")],
            },
            setup_variant="Generator.shuffle",
        )
    )

    for operation in ("noncallable", "disabled", "one", "depth-10", "depth-100"):
        if operation == "noncallable":
            workload_args = (1,)
            workload_kwargs = {}
            value_input: Any = {"type": "int", "value": 1}
        elif operation == "disabled":
            workload_args = ({"fixture": "resolved-value-callable"},)
            workload_kwargs = {"resolve_callables": False}
            value_input = {
                "id": "resolved-value-callable",
                "type": "function",
                "recipe": "_resolved_value returns 1",
            }
        elif operation == "one":
            workload_args = ({"fixture": "resolved-value-callable"},)
            workload_kwargs = {}
            value_input = {
                "id": "resolved-value-callable",
                "type": "function",
                "recipe": "_resolved_value returns 1",
            }
        else:
            depth = 10 if operation == "depth-10" else 100
            chain_id = f"resolution-chain-{depth}"
            workload_args = ({"fixture": chain_id},)
            workload_kwargs = {}
            value_input = {
                "id": chain_id,
                "type": "_ResolutionChain",
                "recipe": f"_ResolutionChain({depth - 1}) yields {depth} callable hops then 1",
                "callable_hops": depth,
            }
        cases.append(
            _case(
                f"resolve-{operation}",
                fortuna,
                error,
                lambda module, operation=operation: _resolve_setup(module, operation),
                workload_args=workload_args,
                workload_kwargs=workload_kwargs,
                workload_input={"callable": "Fortuna.resolve", "value": value_input},
                setup_variant="resolve callable chain",
                seed=None,
            )
        )

    return cases
