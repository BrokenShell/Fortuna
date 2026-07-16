import pytest

import Fortuna

PROFILE_NAMES = (
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


@pytest.mark.parametrize("name", PROFILE_NAMES)
def test_profiles_are_bounded_and_support_bulk(name):
    values = getattr(Fortuna.Generator(123), name)(31, count=2_000)
    assert len(values) == 2_000
    assert all(0 <= value < 31 for value in values)


@pytest.mark.parametrize("name", PROFILE_NAMES)
def test_profiles_reject_empty_size_even_for_empty_bulk(name):
    with pytest.raises(ValueError):
        getattr(Fortuna.Generator(123), name)(0, count=0)


def test_directional_profile_shapes_are_honest():
    size = 101
    count = 20_000
    front_triangular = Fortuna.Generator(1).front_triangular(size, count=count)
    center_triangular = Fortuna.Generator(1).center_triangular(size, count=count)
    back_triangular = Fortuna.Generator(1).back_triangular(size, count=count)
    front_exponential = Fortuna.Generator(2).front_exponential(size, count=count)
    center_normal = Fortuna.Generator(2).center_normal(size, count=count)
    back_exponential = Fortuna.Generator(2).back_exponential(size, count=count)

    assert sum(front_triangular) / count < 40
    assert 45 < sum(center_triangular) / count < 55
    assert sum(back_triangular) / count > 60
    assert sum(front_exponential) / count < 20
    assert 45 < sum(center_normal) / count < 55
    assert sum(back_exponential) / count > 80


def test_plus_or_minus_profiles_are_bounded_and_centered():
    for name in ("plus_or_minus", "plus_or_minus_triangular", "plus_or_minus_normal"):
        values = getattr(Fortuna.Generator(77), name)(20, count=10_000)
        assert all(-20 <= value <= 20 for value in values)
        assert abs(sum(values) / len(values)) < 1.0
