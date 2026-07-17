import math

import pytest

import Fortuna
from Fortuna import RandomValue, WeightedChoice, _core
from Fortuna._selectors import _center_normal_weights, _front_normal_weights

SEED = 0xF07A_6110
SIZE = 100
COUNT = 64


def test_normal_profile_weights_fill_three_sigma_and_are_exact_mirrors():
    front = _front_normal_weights(5)
    center = _center_normal_weights(5)

    assert front[0] == 1.0
    assert front[-1] == pytest.approx(math.exp(-4.5))
    assert center == center[::-1]
    assert center[2] == 1.0
    assert tuple(reversed(front)) == front[::-1]
    assert _front_normal_weights(1) == (1.0,)
    assert _center_normal_weights(1) == (1.0,)


def test_even_center_normal_profile_has_two_equal_middle_peaks():
    weights = _center_normal_weights(6)

    assert weights == weights[::-1]
    assert weights[2] == weights[3] == max(weights)


@pytest.mark.parametrize(
    ("method", "weights"),
    [
        ("front_normal", _front_normal_weights(SIZE)),
        ("center_normal", _center_normal_weights(SIZE)),
        ("back_normal", tuple(reversed(_front_normal_weights(SIZE)))),
    ],
)
def test_normal_profiles_match_prepared_weighted_choice_schedule(method, weights):
    profile_generator = Fortuna.Generator(SEED)
    control_generator = Fortuna.Generator(SEED)
    profile = RandomValue(range(SIZE), resolve_callables=False, generator=profile_generator)
    control = WeightedChoice(
        relative=zip(weights, range(SIZE), strict=True),
        resolve_callables=False,
        generator=control_generator,
    )

    assert [getattr(profile, method)() for _ in range(COUNT)] == control.take(COUNT)
    assert profile_generator.random_below(2**64) == control_generator.random_below(2**64)


@pytest.mark.parametrize("draw", [False, float("nan"), float("inf"), -1.0, 2.0])
def test_normal_profiles_validate_custom_generator_draws(draw):
    class Generator:
        def random_float(self, low=0.0, high=1.0):
            return draw

    selector = RandomValue(("front", "back"), generator=Generator())

    with pytest.raises((TypeError, ValueError)):
        selector.front_normal()


def test_normal_profile_observes_module_monkeypatch_after_preparation(monkeypatch):
    selector = RandomValue(("front", "back"), resolve_callables=False)
    selector.front_normal()
    monkeypatch.setattr(_core, "random_float", lambda low, high: high)

    with pytest.raises(ValueError, match="must be in"):
        selector.front_normal()
