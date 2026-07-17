"""Small, auditable benchmark engine based on ``perf_counter_ns``."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from statistics import median
from time import perf_counter_ns

from .model import BenchmarkCase, BenchmarkResult, BenchmarkStats, SkipBenchmark


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    warmups: int = 3
    samples: int = 11
    target_sample_ns: int = 50_000_000
    min_loops: int = 1
    max_loops: int = 100_000_000

    def __post_init__(self) -> None:
        if self.warmups < 0:
            raise ValueError("warmups cannot be negative")
        if self.samples < 1:
            raise ValueError("samples must be positive")
        if self.target_sample_ns < 1:
            raise ValueError("target_sample_ns must be positive")
        if not 1 <= self.min_loops <= self.max_loops:
            raise ValueError("loop limits are invalid")


def _time_batch(case: BenchmarkCase, loops: int) -> int:
    operation = case.prepare()
    start = perf_counter_ns()
    for _ in range(loops):
        operation()
    return perf_counter_ns() - start


def calibrate(case: BenchmarkCase, config: BenchmarkConfig) -> int:
    """Find a loop count that approaches the configured sample duration."""

    loops = config.min_loops
    while True:
        elapsed = max(_time_batch(case, loops), 1)
        if elapsed >= config.target_sample_ns or loops >= config.max_loops:
            return loops

        estimate = math.ceil(loops * config.target_sample_ns / elapsed)
        # Guard against noisy first measurements and avoid excessive retries.
        loops = min(config.max_loops, max(loops * 2, estimate))


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot calculate a quantile of no values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * fraction


def calculate_stats(samples: Sequence[float]) -> BenchmarkStats:
    ordered = sorted(samples)
    center = median(ordered)
    q1 = _quantile(ordered, 0.25)
    q3 = _quantile(ordered, 0.75)
    deviations = [abs(value - center) for value in ordered]
    return BenchmarkStats(
        samples=len(ordered),
        minimum=ordered[0],
        median=center,
        q1=q1,
        q3=q3,
        iqr=q3 - q1,
        mad=median(deviations),
    )


def run_case(case: BenchmarkCase, config: BenchmarkConfig) -> BenchmarkResult:
    result = BenchmarkResult(
        suite=case.suite,
        name=case.name,
        status="ok",
        unit=case.unit,
        values_per_call=case.values_per_call,
        workload=case.workload_payload,
        workload_signature=case.workload_signature,
    )
    try:
        loops = calibrate(case, config)
        result.loops = loops
        for _ in range(config.warmups):
            _time_batch(case, loops)

        divisor = loops * case.values_per_call
        result.samples_ns = [_time_batch(case, loops) / divisor for _ in range(config.samples)]
        result.stats = calculate_stats(result.samples_ns)
        if case.unit == "value" and result.stats.median > 0:
            result.values_per_second = 1_000_000_000 / result.stats.median
    except SkipBenchmark as error:
        result.status = "skipped"
        result.reason = str(error)
    except Exception as error:  # A failed case must not hide the rest of a suite.
        result.status = "error"
        result.reason = f"{type(error).__name__}: {error}"
    return result


def run_cases(cases: Iterable[BenchmarkCase], config: BenchmarkConfig) -> list[BenchmarkResult]:
    return [run_case(case, config) for case in cases]
