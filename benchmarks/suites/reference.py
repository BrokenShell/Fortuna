"""Python standard-library reference cases."""

from __future__ import annotations

import random

from benchmarks.model import BenchmarkCase

VALUES = tuple(range(100))


def _shuffle_setup(size: int):
    def setup():
        values = list(range(size))
        return lambda: random.shuffle(values)

    return setup


def reference_cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("reference", "random", operation=random.random),
        BenchmarkCase("reference", "randrange-1000", operation=lambda: random.randrange(1000)),
        BenchmarkCase("reference", "randint", operation=lambda: random.randint(-1000, 1000)),
        BenchmarkCase("reference", "uniform", operation=lambda: random.uniform(-1.0, 1.0)),
        BenchmarkCase(
            "reference", "triangular", operation=lambda: random.triangular(0.0, 1.0, 0.5)
        ),
        BenchmarkCase("reference", "choice-100", operation=lambda: random.choice(VALUES)),
        BenchmarkCase(
            "reference",
            "shuffle-100",
            setup=_shuffle_setup(100),
            description="Setup supplies a fresh mutable list for every sample.",
        ),
    ]
