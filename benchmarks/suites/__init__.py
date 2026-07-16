"""Benchmark suite registry."""

from __future__ import annotations

from benchmarks.model import BenchmarkCase

from .fortuna import fortuna_bulk_cases, fortuna_scalar_cases, shuffle_algorithm_cases
from .reference import reference_cases


def all_cases() -> list[BenchmarkCase]:
    return [
        *reference_cases(),
        *fortuna_scalar_cases(),
        *fortuna_bulk_cases(),
        *shuffle_algorithm_cases(),
    ]


def suite_names() -> tuple[str, ...]:
    return ("reference", "fortuna-scalar", "fortuna-bulk", "shuffle-algorithms")
