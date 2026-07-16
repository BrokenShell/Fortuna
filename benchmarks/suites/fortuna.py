"""Thin, replaceable adapters for Fortuna's evolving API.

Keeping every API assumption in this module makes benchmark cases cheap to
rename while Fortuna 6 settles its public contract.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

from benchmarks.model import BenchmarkCase


def _load_fortuna() -> tuple[Any | None, str | None]:
    try:
        return importlib.import_module("Fortuna"), None
    except Exception as error:
        return None, f"Fortuna unavailable: {type(error).__name__}: {error}"


def _resolve(module: Any | None, name: str, import_error: str | None):
    if module is None:
        return None, import_error
    value = getattr(module, name, None)
    if not callable(value):
        return None, f"Fortuna.{name} is unavailable"
    return value, None


def _scalar(
    module: Any | None,
    import_error: str | None,
    name: str,
    arguments: tuple[Any, ...] = (),
) -> BenchmarkCase:
    function, reason = _resolve(module, name, import_error)
    if function is None:
        operation = None
    elif arguments:

        def operation():
            return function(*arguments)
    else:
        operation = function
    return BenchmarkCase(
        "fortuna-scalar",
        name,
        operation=operation,
        skip_reason=reason,
    )


def _shuffle(module: Any | None, import_error: str | None) -> BenchmarkCase:
    function, reason = _resolve(module, "shuffle", import_error)
    if function is None:
        return BenchmarkCase("fortuna-scalar", "shuffle-100", skip_reason=reason)

    def setup():
        values = list(range(100))
        return lambda: function(values)

    return BenchmarkCase("fortuna-scalar", "shuffle-100", setup=setup)


def fortuna_scalar_cases() -> list[BenchmarkCase]:
    fortuna, error = _load_fortuna()
    specs = (
        ("canonical", ()),
        ("random_below", (1000,)),
        ("random_range", (0, 1000)),
        ("random_int", (-1000, 1000)),
        ("random_float", (-1.0, 1.0)),
        ("triangular", (0.0, 1.0, 0.5)),
        ("random_value", (tuple(range(100)),)),
        ("dice", (3, 6)),
        ("percent_true", (50.0,)),
        ("quantum_monty", (100,)),
        ("normal_variate", (0.0, 1.0)),
        ("exponential_variate", (1.0,)),
    )
    cases = [_scalar(fortuna, error, name, arguments) for name, arguments in specs]
    cases.append(_shuffle(fortuna, error))
    return cases


def shuffle_algorithm_cases() -> list[BenchmarkCase]:
    """Compare native shuffle loops without changing Fortuna's public API."""

    fortuna, error = _load_fortuna()
    benchmark_functions: dict[str, Callable[..., Any]] = {}
    if fortuna is not None:
        core = importlib.import_module("Fortuna._core")
        for algorithm in ("knuth_b", "fisher_yates"):
            function = getattr(core, f"_benchmark_shuffle_{algorithm}", None)
            if callable(function):
                benchmark_functions[algorithm] = function
            else:
                error = f"Fortuna._core._benchmark_shuffle_{algorithm} is unavailable"

    cases: list[BenchmarkCase] = []
    for size in (10, 100, 1_000, 10_000, 100_000, 1_000_000):
        for label, algorithm in (("knuth-b", "knuth_b"), ("fisher-yates", "fisher_yates")):
            function = benchmark_functions.get(algorithm)
            if function is None:
                cases.append(
                    BenchmarkCase(
                        "shuffle-algorithms",
                        f"{label}-{size}",
                        skip_reason=error,
                    )
                )
                continue

            def setup(
                size: int = size,
                function: Callable[..., Any] = function,
            ):
                # Resetting outside the timed interval gives both algorithms the
                # same initial engine state for every independent sample.
                assert fortuna is not None
                fortuna.seed(0x5EED)
                values = list(range(size))
                return lambda: function(values)

            cases.append(
                BenchmarkCase(
                    "shuffle-algorithms",
                    f"{label}-{size}",
                    setup=setup,
                )
            )
    return cases


def _module_bulk_case(
    module: Any | None,
    import_error: str | None,
    name: str,
    count: int,
    arguments: tuple[Any, ...],
) -> BenchmarkCase:
    function, reason = _resolve(module, name, import_error)
    operation = None if function is None else lambda: function(*arguments, count=count)
    return BenchmarkCase(
        "fortuna-bulk",
        f"module-{name}-{count}",
        operation=operation,
        unit="value",
        values_per_call=count,
        skip_reason=reason,
    )


def _generator_factory(module: Any) -> tuple[Callable[[], Any] | None, str | None]:
    generator_type = getattr(module, "Generator", None)
    if generator_type is None:
        return None, "Fortuna.Generator is unavailable"
    from_entropy = getattr(generator_type, "from_entropy", None)
    if callable(from_entropy):
        return from_entropy, None
    if callable(generator_type):
        return generator_type, None
    return None, "Fortuna.Generator cannot be constructed"


def _generator_bulk_case(
    module: Any | None,
    import_error: str | None,
    name: str,
    count: int,
    arguments: tuple[Any, ...],
) -> BenchmarkCase:
    reason = import_error
    factory = None
    if module is not None:
        factory, reason = _generator_factory(module)
        method = getattr(getattr(module, "Generator", None), name, None)
        if factory is not None and not callable(method):
            reason = f"Fortuna.Generator.{name} is unavailable"

    if reason:
        return BenchmarkCase(
            "fortuna-bulk",
            f"generator-{name}-{count}",
            unit="value",
            values_per_call=count,
            skip_reason=reason,
        )

    assert factory is not None

    def setup():
        generator = factory()
        method = getattr(generator, name)
        return lambda: method(*arguments, count=count)

    return BenchmarkCase(
        "fortuna-bulk",
        f"generator-{name}-{count}",
        setup=setup,
        unit="value",
        values_per_call=count,
    )


def fortuna_bulk_cases() -> list[BenchmarkCase]:
    """Tentative Fortuna 6 cases; missing APIs appear as explicit skips.

    Bulk generation uses the same public name and arguments as scalar generation,
    plus the keyword-only ``count`` contract.
    """

    fortuna, error = _load_fortuna()
    count = 10_000
    specs = (
        ("canonical", ()),
        ("random_int", (-1000, 1000)),
        ("random_float", (-1.0, 1.0)),
        ("random_range", (0, 1000, 1)),
    )
    cases: list[BenchmarkCase] = []
    for name, arguments in specs:
        cases.append(_module_bulk_case(fortuna, error, name, count, arguments))
        cases.append(_generator_bulk_case(fortuna, error, name, count, arguments))
    return cases
