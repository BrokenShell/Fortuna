"""Deterministic Python standard-library reference cases."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from benchmarks.model import BenchmarkCase

VALUES = tuple(range(100))


def _random_method_case(
    name: str,
    method_name: str,
    arguments: tuple[Any, ...] = (),
    *,
    input_metadata: Any = None,
) -> BenchmarkCase:
    def setup():
        generator = random.Random(0)
        method = getattr(generator, method_name)
        if arguments:
            return lambda: method(*arguments)
        return method

    return BenchmarkCase(
        "reference",
        name,
        setup=setup,
        workload={
            "args": arguments,
            "kwargs": {},
            "seed": 0,
            "input": input_metadata,
            "setup_variant": f"random.Random.{method_name}",
        },
    )


def _random_operation_case(
    name: str,
    factory: Callable[[random.Random], Callable[[], Any]],
    *,
    arguments: tuple[Any, ...] = (),
) -> BenchmarkCase:
    def setup():
        return factory(random.Random(0))

    return BenchmarkCase(
        "reference",
        name,
        setup=setup,
        workload={
            "args": arguments,
            "kwargs": {},
            "seed": 0,
            "input": None,
            "setup_variant": "random.Random custom operation",
        },
    )


def _shuffle_setup(size: int):
    def setup():
        generator = random.Random(0)
        values = list(range(size))
        return lambda: generator.shuffle(values)

    return setup


def reference_cases() -> list[BenchmarkCase]:
    cases = [
        _random_method_case("random", "random"),
        _random_method_case("randrange-1000", "randrange", (1000,)),
        _random_method_case("randint", "randint", (-1000, 1000)),
        _random_method_case("getrandbits-64", "getrandbits", (64,)),
        _random_method_case("uniform", "uniform", (-1.0, 1.0)),
        _random_method_case("triangular", "triangular", (0.0, 1.0, 0.5)),
        _random_method_case(
            "choice-100",
            "choice",
            (VALUES,),
            input_metadata={"type": "tuple", "contents": "range(100)"},
        ),
        _random_operation_case(
            "bernoulli-0.5",
            lambda generator: lambda: generator.random() < 0.5,
            arguments=(0.5,),
        ),
        _random_method_case("betavariate", "betavariate", (2.0, 3.0)),
        _random_method_case("paretovariate", "paretovariate", (2.0,)),
        _random_method_case("vonmisesvariate", "vonmisesvariate", (0.0, 1.0)),
        _random_method_case("expovariate", "expovariate", (1.0,)),
        _random_method_case("gammavariate", "gammavariate", (2.0, 3.0)),
        _random_method_case("weibullvariate", "weibullvariate", (3.0, 2.0)),
        _random_method_case("normalvariate", "normalvariate", (0.0, 1.0)),
        _random_method_case("lognormvariate", "lognormvariate", (0.0, 1.0)),
        _random_method_case(
            "sample-100-10",
            "sample",
            (VALUES, 10),
            input_metadata={"type": "tuple", "contents": "range(100)"},
        ),
        BenchmarkCase(
            "reference",
            "shuffle-100",
            setup=_shuffle_setup(100),
            description="Setup supplies a fresh mutable list for every sample.",
            workload={
                "args": [100],
                "kwargs": {},
                "seed": 0,
                "input": {"type": "list", "contents": "range(100)"},
                "setup_variant": "random.Random.shuffle mutable-list",
            },
        ),
    ]
    if hasattr(random.Random, "binomialvariate"):
        cases.append(_random_method_case("binomialvariate", "binomialvariate", (100, 0.5)))
    return cases
