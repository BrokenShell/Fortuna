import pytest

import Fortuna

PROFILE_NAMES = ("front_triangular", "center_triangular", "back_triangular")


@pytest.mark.parametrize("name", PROFILE_NAMES)
@pytest.mark.parametrize("size", [1, 2, 17, 100])
def test_triangular_profiles_remain_in_bounds(name, size):
    values = getattr(Fortuna.Generator(2), name)(size, count=2_000)
    assert all(0 <= value < size for value in values)


def test_triangular_profiles_have_honest_positional_bias():
    size = 100
    count = 20_000
    front = Fortuna.Generator(2).front_triangular(size, count=count)
    center = Fortuna.Generator(2).center_triangular(size, count=count)
    back = Fortuna.Generator(2).back_triangular(size, count=count)

    assert sum(front) / count < 40
    assert 45 < sum(center) / count < 55
    assert sum(back) / count > 60


@pytest.mark.parametrize("name", PROFILE_NAMES)
def test_triangular_profiles_reject_empty_sizes(name):
    with pytest.raises(ValueError):
        getattr(Fortuna, name)(0)
