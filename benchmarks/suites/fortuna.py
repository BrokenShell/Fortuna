"""Thin, replaceable adapters for Fortuna's evolving API.

Keeping every API assumption in this module makes benchmark cases cheap to
rename while Fortuna 6 settles its public contract.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from benchmarks.model import BenchmarkCase


@dataclass(frozen=True, slots=True)
class _NumericWorkload:
    """Stable identity and scaling for one public numeric/profile operation."""

    name: str
    method: str
    arguments: tuple[Any, ...]
    bulk_count: int


# One representative workload for every public numeric/profile API shared by
# the module and Generator. Counts keep one bulk call comfortably below the
# runner's default 50 ms sample target while amortizing Python call overhead.
_CORE_WORKLOADS = (
    _NumericWorkload("canonical", "canonical", (), 10_000),
    _NumericWorkload("percent_true", "percent_true", (50.0,), 10_000),
    _NumericWorkload("bernoulli_variate", "bernoulli_variate", (0.5,), 10_000),
    _NumericWorkload("random_below", "random_below", (1_000,), 10_000),
    _NumericWorkload("random_index", "random_index", (1_000,), 10_000),
    _NumericWorkload("random_int", "random_int", (-1_000, 1_000), 10_000),
    _NumericWorkload("random_range", "random_range", (-1_000, 1_000, 3), 10_000),
    _NumericWorkload("d", "d", (20,), 10_000),
    _NumericWorkload("dice", "dice", (3, 6), 5_000),
    _NumericWorkload("ability_dice", "ability_dice", (4,), 5_000),
    _NumericWorkload("plus_or_minus", "plus_or_minus", (100,), 10_000),
    _NumericWorkload("plus_or_minus_triangular", "plus_or_minus_triangular", (100,), 10_000),
    _NumericWorkload("plus_or_minus_normal", "plus_or_minus_normal", (100,), 5_000),
    _NumericWorkload("random_float", "random_float", (-1.0, 1.0), 10_000),
    _NumericWorkload("triangular", "triangular", (0.0, 1.0, 0.5), 10_000),
    _NumericWorkload("beta_variate", "beta_variate", (2.0, 5.0), 1_000),
    _NumericWorkload("pareto_variate", "pareto_variate", (2.0,), 5_000),
    _NumericWorkload("vonmises_variate", "vonmises_variate", (0.0, 1.0), 2_000),
    _NumericWorkload("binomial_variate", "binomial_variate", (100, 0.5), 2_000),
    _NumericWorkload("negative_binomial_variate", "negative_binomial_variate", (10, 0.5), 2_000),
    _NumericWorkload("geometric_variate", "geometric_variate", (0.5,), 5_000),
    _NumericWorkload("poisson_variate", "poisson_variate", (4.0,), 2_000),
    _NumericWorkload("exponential_variate", "exponential_variate", (1.0,), 5_000),
    _NumericWorkload("gamma_variate", "gamma_variate", (2.0, 3.0), 2_000),
    _NumericWorkload("weibull_variate", "weibull_variate", (2.0, 3.0), 5_000),
    _NumericWorkload("normal_variate", "normal_variate", (0.0, 1.0), 5_000),
    _NumericWorkload("log_normal_variate", "log_normal_variate", (0.0, 1.0), 2_000),
    _NumericWorkload("extreme_value_variate", "extreme_value_variate", (0.0, 1.0), 5_000),
    _NumericWorkload("chi_squared_variate", "chi_squared_variate", (4.0,), 2_000),
    _NumericWorkload("cauchy_variate", "cauchy_variate", (0.0, 1.0), 5_000),
    _NumericWorkload("fisher_f_variate", "fisher_f_variate", (4.0, 5.0), 1_000),
    _NumericWorkload("student_t_variate", "student_t_variate", (4.0,), 2_000),
    _NumericWorkload("front_triangular", "front_triangular", (100,), 10_000),
    _NumericWorkload("center_triangular", "center_triangular", (100,), 10_000),
    _NumericWorkload("back_triangular", "back_triangular", (100,), 10_000),
)


# Branch-sensitive scalar regimes. Bulk retains one workload per public API to
# keep the default suite bounded; these cases expose important fast/rejection
# paths without duplicating the entire bulk matrix.
_SCALAR_REGIMES = (
    _NumericWorkload("random_below-full-domain", "random_below", (2**64,), 10_000),
    _NumericWorkload("random_range-descending", "random_range", (1_000, -1_000, -3), 10_000),
    _NumericWorkload("triangular-edge-mode", "triangular", (0.0, 1.0, 0.0), 10_000),
    _NumericWorkload("vonmises-uniform", "vonmises_variate", (0.0, 0.0), 5_000),
    _NumericWorkload("binomial-large", "binomial_variate", (100_000, 0.5), 1_000),
    _NumericWorkload("negative-binomial-rare", "negative_binomial_variate", (10, 0.1), 1_000),
    _NumericWorkload("geometric-rare", "geometric_variate", (0.1,), 2_000),
    _NumericWorkload("poisson-large", "poisson_variate", (1_000.0,), 1_000),
    _NumericWorkload("gamma-subunit-shape", "gamma_variate", (0.5, 3.0), 1_000),
    _NumericWorkload("normal-degenerate", "normal_variate", (3.0, 0.0), 10_000),
    _NumericWorkload("log-normal-degenerate", "log_normal_variate", (1.0, 0.0), 10_000),
)


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


def _workload_description(
    owner: str,
    workload: _NumericWorkload,
    *,
    count: int | None = None,
) -> str:
    identity = f"owner={owner}; method={workload.method}; arguments={workload.arguments!r}; seed=0"
    if count is not None:
        identity += f"; count={count}"
    return identity


def _workload_metadata(
    owner: str,
    workload: _NumericWorkload,
    *,
    count: int | None = None,
    input_data: Any = None,
) -> dict[str, Any]:
    return {
        "args": workload.arguments,
        "kwargs": {} if count is None else {"count": count},
        "seed": 0,
        "input": input_data,
        "setup_variant": f"{owner}.{workload.method}-seed-0-per-sample",
    }


def _module_scalar(
    module: Any | None,
    import_error: str | None,
    workload: _NumericWorkload,
) -> BenchmarkCase:
    function, reason = _resolve(module, workload.method, import_error)
    seed, seed_reason = _resolve(module, "seed", import_error)
    reason = reason or seed_reason
    description = _workload_description("module", workload)
    metadata = _workload_metadata("module", workload)
    if function is None or seed is None:
        return BenchmarkCase(
            "fortuna-scalar",
            workload.name,
            description=description,
            skip_reason=reason,
            workload=metadata,
        )

    def setup():
        seed(0)
        if workload.arguments:
            return lambda: function(*workload.arguments)
        return function

    return BenchmarkCase(
        "fortuna-scalar",
        workload.name,
        setup=setup,
        description=description,
        workload=metadata,
    )


def _shuffle(module: Any | None, import_error: str | None) -> BenchmarkCase:
    function, reason = _resolve(module, "shuffle", import_error)
    seed, seed_reason = _resolve(module, "seed", import_error)
    reason = reason or seed_reason
    description = "owner=module; method=shuffle; arguments=(list(range(100)),); seed=0"
    metadata = {
        "args": [],
        "kwargs": {},
        "seed": 0,
        "input": {"container": "list", "contents": "range(100)", "size": 100},
        "setup_variant": "module-seed-0-fresh-list-per-sample",
    }
    if function is None or seed is None:
        return BenchmarkCase(
            "fortuna-scalar",
            "shuffle-100",
            description=description,
            skip_reason=reason,
            workload=metadata,
        )

    def setup():
        seed(0)
        values = list(range(100))
        return lambda: function(values)

    return BenchmarkCase(
        "fortuna-scalar",
        "shuffle-100",
        setup=setup,
        description=description,
        workload=metadata,
    )


def _generator_scalar(
    module: Any | None,
    import_error: str | None,
    workload: _NumericWorkload,
) -> BenchmarkCase:
    generator_type = getattr(module, "Generator", None) if module is not None else None
    description = _workload_description("Generator", workload)
    metadata = _workload_metadata("generator", workload)
    if not callable(generator_type):
        return BenchmarkCase(
            "fortuna-scalar",
            f"generator-{workload.name}",
            description=description,
            skip_reason=import_error or "Fortuna.Generator is unavailable",
            workload=metadata,
        )
    method = getattr(generator_type, workload.method, None)
    if not callable(method):
        return BenchmarkCase(
            "fortuna-scalar",
            f"generator-{workload.name}",
            description=description,
            skip_reason=f"Fortuna.Generator.{workload.method} is unavailable",
            workload=metadata,
        )

    def setup():
        generator = generator_type(0)
        bound = getattr(generator, workload.method)
        if workload.arguments:
            return lambda: bound(*workload.arguments)
        return bound

    return BenchmarkCase(
        "fortuna-scalar",
        f"generator-{workload.name}",
        setup=setup,
        description=description,
        workload=metadata,
    )


def fortuna_scalar_cases() -> list[BenchmarkCase]:
    fortuna, error = _load_fortuna()
    workloads = (*_CORE_WORKLOADS, *_SCALAR_REGIMES)
    cases = [_module_scalar(fortuna, error, workload) for workload in workloads]
    cases.extend(_generator_scalar(fortuna, error, workload) for workload in workloads)

    random_value = _NumericWorkload("random_value", "random_value", (tuple(range(100)),), 1)
    cases.append(_module_scalar(fortuna, error, random_value))
    cases.append(_generator_scalar(fortuna, error, random_value))
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
            metadata = {
                "args": [],
                "kwargs": {},
                "seed": 0,
                "input": {"container": "list", "contents": f"range({size})", "size": size},
                "setup_variant": f"module-seed-0-{algorithm}-fresh-list-per-sample",
            }
            if function is None:
                cases.append(
                    BenchmarkCase(
                        "shuffle-algorithms",
                        f"{label}-{size}",
                        skip_reason=error,
                        workload=metadata,
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
                fortuna.seed(0)
                values = list(range(size))
                return lambda: function(values)

            cases.append(
                BenchmarkCase(
                    "shuffle-algorithms",
                    f"{label}-{size}",
                    setup=setup,
                    workload=metadata,
                )
            )
    return cases


def _module_bulk_case(
    module: Any | None,
    import_error: str | None,
    workload: _NumericWorkload,
) -> BenchmarkCase:
    function, reason = _resolve(module, workload.method, import_error)
    seed, seed_reason = _resolve(module, "seed", import_error)
    reason = reason or seed_reason
    description = _workload_description("module", workload, count=workload.bulk_count)
    metadata = _workload_metadata("module", workload, count=workload.bulk_count)
    case_name = f"module-{workload.name}-{workload.bulk_count}"
    if function is None or seed is None:
        return BenchmarkCase(
            "fortuna-bulk",
            case_name,
            unit="value",
            values_per_call=workload.bulk_count,
            description=description,
            skip_reason=reason,
            workload=metadata,
        )

    def setup():
        seed(0)
        return lambda: function(*workload.arguments, count=workload.bulk_count)

    return BenchmarkCase(
        "fortuna-bulk",
        case_name,
        setup=setup,
        unit="value",
        values_per_call=workload.bulk_count,
        description=description,
        workload=metadata,
    )


def _generator_bulk_case(
    module: Any | None,
    import_error: str | None,
    workload: _NumericWorkload,
) -> BenchmarkCase:
    generator_type = getattr(module, "Generator", None) if module is not None else None
    description = _workload_description("Generator", workload, count=workload.bulk_count)
    metadata = _workload_metadata("generator", workload, count=workload.bulk_count)
    case_name = f"generator-{workload.name}-{workload.bulk_count}"
    if not callable(generator_type):
        return BenchmarkCase(
            "fortuna-bulk",
            case_name,
            unit="value",
            values_per_call=workload.bulk_count,
            description=description,
            skip_reason=import_error or "Fortuna.Generator is unavailable",
            workload=metadata,
        )
    method = getattr(generator_type, workload.method, None)
    if not callable(method):
        return BenchmarkCase(
            "fortuna-bulk",
            case_name,
            unit="value",
            values_per_call=workload.bulk_count,
            description=description,
            skip_reason=f"Fortuna.Generator.{workload.method} is unavailable",
            workload=metadata,
        )

    def setup():
        generator = generator_type(0)
        bound = getattr(generator, workload.method)
        return lambda: bound(*workload.arguments, count=workload.bulk_count)

    return BenchmarkCase(
        "fortuna-bulk",
        case_name,
        setup=setup,
        unit="value",
        values_per_call=workload.bulk_count,
        description=description,
        workload=metadata,
    )


def fortuna_bulk_cases() -> list[BenchmarkCase]:
    """Tentative Fortuna 6 cases; missing APIs appear as explicit skips.

    Bulk generation uses the same public name and arguments as scalar generation,
    plus the keyword-only ``count`` contract.
    """

    fortuna, error = _load_fortuna()
    cases: list[BenchmarkCase] = []
    for workload in _CORE_WORKLOADS:
        cases.append(_module_bulk_case(fortuna, error, workload))
        cases.append(_generator_bulk_case(fortuna, error, workload))
    return cases
