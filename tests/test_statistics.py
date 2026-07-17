"""Fast, seeded statistical checks for Fortuna's declared distributions.

These tests deliberately validate distribution properties, not particular PRNG
output sequences.  Every test uses an explicit ``Generator`` so a failure is
reproducible without coupling the suite to module-level entropy or test order.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from collections.abc import Iterable, Sequence

import pytest

import Fortuna

pytestmark = pytest.mark.statistical


def _assert_probability(
    observed_true: int,
    sample_size: int,
    expected_probability: float,
    *,
    standard_errors: float = 7.0,
) -> None:
    """Check a Bernoulli proportion with a conservative normal-score bound."""

    expected = sample_size * expected_probability
    standard_deviation = math.sqrt(
        sample_size * expected_probability * (1.0 - expected_probability)
    )
    assert abs(observed_true - expected) <= standard_errors * standard_deviation


def _assert_discrete_uniform(samples: Sequence[int], support: Iterable[int]) -> None:
    """Bound every cell of a discrete uniform sample at seven binomial sigmas.

    Seven sigmas per cell makes the family-wise false-alarm probability tiny,
    even after checking every category, while still detecting meaningful bias.
    """

    categories = tuple(support)
    counts = Counter(samples)
    assert set(counts) <= set(categories)

    probability = 1.0 / len(categories)
    expected = len(samples) * probability
    cell_standard_deviation = math.sqrt(len(samples) * probability * (1.0 - probability))
    tolerance = 7.0 * cell_standard_deviation
    for category in categories:
        assert abs(counts[category] - expected) <= tolerance


def _assert_mean_and_variance(
    samples: Sequence[float | int],
    *,
    expected_mean: float,
    expected_variance: float,
    fourth_central_moment: float,
    standard_errors: float = 7.0,
) -> None:
    """Check first two moments using their theoretical sampling errors.

    The sample-variance expression is the exact variance of the unbiased sample
    variance for IID observations with a finite fourth central moment.
    """

    sample_size = len(samples)
    mean_error = math.sqrt(expected_variance / sample_size)
    observed_mean = statistics.fmean(samples)
    assert observed_mean == pytest.approx(
        expected_mean,
        abs=standard_errors * mean_error,
    )

    variance_error = math.sqrt(
        (fourth_central_moment - ((sample_size - 3) / (sample_size - 1)) * expected_variance**2)
        / sample_size
    )
    observed_variance = statistics.variance(samples)
    assert observed_variance == pytest.approx(
        expected_variance,
        abs=standard_errors * variance_error,
    )


def _assert_bounded_mean(
    samples: Sequence[int],
    expected_mean: float,
    *,
    low: int,
    high: int,
    alpha: float = 1e-10,
) -> None:
    """Use Hoeffding's inequality for a distribution-free bounded-mean check."""

    tolerance = (high - low) * math.sqrt(math.log(2.0 / alpha) / (2 * len(samples)))
    assert statistics.fmean(samples) == pytest.approx(expected_mean, abs=tolerance)


def _assert_same_discrete_distribution(
    left: Sequence[int],
    right: Sequence[int],
    support: Iterable[int],
    *,
    alpha: float = 1e-10,
) -> None:
    """Apply the two-sample DKW bound to discrete empirical CDFs."""

    left_counts = Counter(left)
    right_counts = Counter(right)
    left_cumulative = 0
    right_cumulative = 0
    maximum_distance = 0.0
    for value in support:
        left_cumulative += left_counts[value]
        right_cumulative += right_counts[value]
        maximum_distance = max(
            maximum_distance,
            abs(left_cumulative / len(left) - right_cumulative / len(right)),
        )

    effective_size = len(left) * len(right) / (len(left) + len(right))
    tolerance = math.sqrt(math.log(2 / alpha) / (2 * effective_size))
    assert maximum_distance <= tolerance


@pytest.mark.parametrize(
    ("method_name", "arguments", "support"),
    [
        ("random_index", (17,), range(17)),
        ("random_int", (-8, 8), range(-8, 9)),
    ],
)
def test_uniform_integer_generators_have_flat_category_frequencies(
    method_name: str,
    arguments: tuple[int, ...],
    support: range,
) -> None:
    generator = Fortuna.Generator(0xF07A_1001)
    samples = getattr(generator, method_name)(*arguments, count=34_000)
    _assert_discrete_uniform(samples, support)


def test_percent_true_and_bernoulli_match_declared_probabilities() -> None:
    sample_size = 30_000

    percent_generator = Fortuna.Generator(0xF07A_2001)
    percent_samples = percent_generator.percent_true(27.5, count=sample_size)
    _assert_probability(sum(percent_samples), sample_size, 0.275)

    bernoulli_generator = Fortuna.Generator(0xF07A_2002)
    bernoulli_samples = bernoulli_generator.bernoulli_variate(0.73, count=sample_size)
    _assert_probability(sum(bernoulli_samples), sample_size, 0.73)


def test_die_is_uniform_and_dice_have_theoretical_first_two_moments() -> None:
    die_samples = Fortuna.Generator(0xF07A_3001).d(12, count=36_000)
    _assert_discrete_uniform(die_samples, range(1, 13))

    rolls = 4
    sides = 8
    samples = Fortuna.Generator(0xF07A_3002).dice(rolls, sides, count=30_000)
    single_variance = (sides**2 - 1) / 12
    single_fourth_moment = (sides**2 - 1) * (3 * sides**2 - 7) / 240
    variance = rolls * single_variance
    fourth_moment = rolls * single_fourth_moment + 3 * rolls * (rolls - 1) * single_variance**2
    _assert_mean_and_variance(
        samples,
        expected_mean=rolls * (sides + 1) / 2,
        expected_variance=variance,
        fourth_central_moment=fourth_moment,
    )


@pytest.mark.parametrize(
    ("method_name", "arguments", "expected_mean", "expected_variance", "fourth_moment"),
    [
        ("normal_variate", (4.0, 2.5), 4.0, 2.5**2, 3 * 2.5**4),
        (
            "exponential_variate",
            (0.4,),
            1 / 0.4,
            1 / 0.4**2,
            9 / 0.4**4,
        ),
        (
            "gamma_variate",
            (3.5, 1.2),
            3.5 * 1.2,
            3.5 * 1.2**2,
            3 * 3.5 * (3.5 + 2) * 1.2**4,
        ),
        (
            "poisson_variate",
            (7.5,),
            7.5,
            7.5,
            7.5 + 3 * 7.5**2,
        ),
        (
            "binomial_variate",
            (20, 0.3),
            20 * 0.3,
            20 * 0.3 * 0.7,
            3 * (20 * 0.3 * 0.7) ** 2 + 20 * 0.3 * 0.7 * (1 - 6 * 0.3 * 0.7),
        ),
    ],
)
def test_standard_distributions_match_theoretical_first_two_moments(
    method_name: str,
    arguments: tuple[float | int, ...],
    expected_mean: float,
    expected_variance: float,
    fourth_moment: float,
) -> None:
    generator = Fortuna.Generator(0xF07A_4001)
    samples = getattr(generator, method_name)(*arguments, count=30_000)
    _assert_mean_and_variance(
        samples,
        expected_mean=expected_mean,
        expected_variance=expected_variance,
        fourth_central_moment=fourth_moment,
    )


def test_cauchy_distribution_matches_declared_quartiles() -> None:
    """Validate a heavy-tailed distribution without pretending its moments exist."""

    location = 3.0
    scale = 1.5
    samples = sorted(Fortuna.Generator(0xF07A_4002).cauchy_variate(location, scale, count=30_000))

    # Dvoretzky-Kiefer-Wolfowitz: with probability at least 1-alpha, every
    # empirical quantile p lies between the true p-epsilon and p+epsilon
    # quantiles. This remains valid for Cauchy's heavy tails.
    alpha = 1e-10
    epsilon = math.sqrt(math.log(2 / alpha) / (2 * len(samples)))

    def cauchy_quantile(probability: float) -> float:
        return location + scale * math.tan(math.pi * (probability - 0.5))

    for probability in (0.25, 0.5, 0.75):
        observed = samples[math.ceil(probability * len(samples)) - 1]
        assert cauchy_quantile(probability - epsilon) <= observed
        assert observed <= cauchy_quantile(probability + epsilon)


def test_front_and_back_triangular_profiles_are_mirrors() -> None:
    size = 101
    sample_size = 30_000
    front = Fortuna.Generator(0xF07A_5001).front_triangular(size, count=sample_size)
    back = Fortuna.Generator(0xF07A_5002).back_triangular(size, count=sample_size)
    mirrored_back = [size - 1 - value for value in back]
    _assert_same_discrete_distribution(front, mirrored_back, range(size))


def test_triangular_profiles_have_honest_positional_ordering() -> None:
    size = 101
    midpoint = (size - 1) / 2
    sample_size = 30_000
    generator = Fortuna.Generator(0xF07A_5004)

    triangular = {
        name: getattr(generator, name)(size, count=sample_size)
        for name in ("front_triangular", "center_triangular", "back_triangular")
    }
    assert statistics.fmean(triangular["front_triangular"]) < midpoint
    _assert_bounded_mean(triangular["center_triangular"], midpoint, low=0, high=size - 1)
    assert statistics.fmean(triangular["back_triangular"]) > midpoint
