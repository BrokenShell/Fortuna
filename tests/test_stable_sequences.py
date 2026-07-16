"""Golden vectors for Fortuna/Storm-owned Fortuna 6 sequence contracts.

This deliberately excludes C++ standard-library distribution transforms and
every positional profile that uses one. Those sequences are toolchain-local,
not part of Fortuna's cross-platform stability promise.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

import Fortuna

SEED = 0xF07A_6008
UINT64_MAX = 2**64 - 1
POPULATION = tuple(range(20))


@pytest.mark.parametrize(
    ("method", "arguments", "expected", "expected_next"),
    [
        (
            "random_uint",
            (7, UINT64_MAX - 16),
            [
                3_186_676_285_918_477_169,
                11_767_622_565_797_284_515,
                3_827_615_796_449_682_224,
                8_565_062_673_365_611_013,
                5_934_172_038_177_969_603,
                3_023_732_989_049_988_271,
                14_116_850_841_048_732_355,
                5_914_639_430_290_737_019,
            ],
            5_762_370_405_561_471_798,
        ),
        (
            "d",
            (20,),
            [3, 9, 18, 7, 17, 5, 9, 13],
            5_762_370_405_561_471_798,
        ),
        (
            "dice",
            (3, 6),
            [10, 9, 3, 12, 14, 11, 10, 12],
            5_752_389_478_553_983_903,
        ),
        (
            "ability_dice",
            (6,),
            [13, 12, 16, 15, 9, 14, 14, 15],
            17_107_445_535_596_616_815,
        ),
        (
            "plus_or_minus",
            (31,),
            [3, 4, 12, -18, 7, 11, 2, 17],
            5_762_370_405_561_471_798,
        ),
        (
            "plus_or_minus_triangular",
            (31,),
            [-18, -21, 20, 8, -6, 11, 5, 9],
            14_522_694_573_454_084_749,
        ),
        (
            "front_triangular",
            (101,),
            [7, 17, 15, 56, 53, 12, 59, 21],
            14_522_694_573_454_084_749,
        ),
        (
            "center_triangular",
            (101,),
            [41, 17, 16, 60, 76, 46, 61, 37],
            14_522_694_573_454_084_749,
        ),
        (
            "back_triangular",
            (101,),
            [76, 18, 17, 64, 99, 80, 63, 53],
            14_522_694_573_454_084_749,
        ),
        (
            "mixed_triangular",
            (101,),
            [12, 16, 64, 80, 21, 71, 11, 74],
            5_752_389_478_553_983_903,
        ),
    ],
)
def test_owned_numeric_golden_vectors(
    method: str,
    arguments: tuple[Any, ...],
    expected: list[int],
    expected_next: int,
) -> None:
    generator = Fortuna.Generator(SEED)
    assert getattr(generator, method)(*arguments, count=len(expected)) == expected
    assert generator.random_uint(0, UINT64_MAX) == expected_next

    Fortuna.seed(SEED)
    assert getattr(Fortuna, method)(*arguments, count=len(expected)) == expected
    assert Fortuna.random_uint(0, UINT64_MAX) == expected_next


def _assert_collection_schedule(
    operation: Callable[[Any], Any],
    expected: Any,
    expected_next: int,
) -> None:
    generator = Fortuna.Generator(SEED)
    assert operation(generator) == expected
    assert generator.random_uint(0, UINT64_MAX) == expected_next


def test_random_value_owned_schedule_golden_vector() -> None:
    expected = [2, 8, 17, 6, 16, 4, 8, 12]
    expected_next = 5_762_370_405_561_471_798

    _assert_collection_schedule(
        lambda generator: [generator.random_value(POPULATION) for _ in expected],
        expected,
        expected_next,
    )
    _assert_collection_schedule(
        lambda generator: [Fortuna.random_value(POPULATION, generator=generator) for _ in expected],
        expected,
        expected_next,
    )

    Fortuna.seed(SEED)
    assert [Fortuna.random_value(POPULATION) for _ in expected] == expected
    assert Fortuna.random_uint(0, UINT64_MAX) == expected_next


def test_partial_fisher_yates_sample_owned_schedule_golden_vector() -> None:
    expected = [2, 10, 9, 6, 16, 14, 18]
    expected_next = 5_914_639_430_290_737_012

    _assert_collection_schedule(
        lambda generator: generator.sample(POPULATION, len(expected)),
        expected,
        expected_next,
    )
    _assert_collection_schedule(
        lambda generator: Fortuna.sample(
            POPULATION,
            len(expected),
            generator=generator,
        ),
        expected,
        expected_next,
    )

    Fortuna.seed(SEED)
    assert Fortuna.sample(POPULATION, len(expected)) == expected
    assert Fortuna.random_uint(0, UINT64_MAX) == expected_next
