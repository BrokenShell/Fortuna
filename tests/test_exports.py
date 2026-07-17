from pathlib import Path

import Fortuna

EXPECTED_ALL = (
    "__version__",
    "storm_version",
    "Generator",
    "seed",
    "from_entropy",
    "for_stream",
    "percent_true",
    "bernoulli_variate",
    "random_below",
    "random_index",
    "random_int",
    "random_range",
    "d",
    "dice",
    "ability_dice",
    "plus_or_minus",
    "plus_or_minus_triangular",
    "plus_or_minus_normal",
    "canonical",
    "random_float",
    "triangular",
    "beta_variate",
    "pareto_variate",
    "vonmises_variate",
    "binomial_variate",
    "negative_binomial_variate",
    "geometric_variate",
    "poisson_variate",
    "exponential_variate",
    "gamma_variate",
    "weibull_variate",
    "normal_variate",
    "log_normal_variate",
    "extreme_value_variate",
    "chi_squared_variate",
    "cauchy_variate",
    "fisher_f_variate",
    "student_t_variate",
    "front_triangular",
    "center_triangular",
    "back_triangular",
    "random_value",
    "shuffle",
    "sample",
    "RandomValue",
    "TruffleShuffle",
    "WeightedChoice",
)


def test_public_export_contract_is_explicit_and_complete():
    assert Fortuna.__all__ == EXPECTED_ALL
    assert all(hasattr(Fortuna, name) for name in EXPECTED_ALL)


def test_api_reference_covers_every_public_export():
    api_reference = (Path(__file__).parents[1] / "docs" / "api.md").read_text()
    missing = [name for name in EXPECTED_ALL if f"`{name}" not in api_reference]
    assert missing == []


def test_removed_and_historical_names_are_not_exported():
    removed = {
        "version",
        "max_uint",
        "max_int",
        "min_int",
        "min_float",
        "max_float",
        "min_below",
        "min_above",
        "smart_clamp",
        "float_clamp",
        "distribution_range",
        "DistributionRange",
        "FloatDistributionRange",
        "ZeroCool",
        "knuth_a",
        "fisher_yates",
        "truffle_shuffle",
        "TruffleShuffle2",
        "random_uint",
        "resolve",
        "IndexProfile",
        "IndexSelector",
        "QuantumMonty",
        "FlexCat",
        "RelativeWeightedChoice",
        "CumulativeWeightedChoice",
        "mixed_triangular",
        "front_exponential",
        "center_normal",
        "back_exponential",
        "mixed_exponential_normal",
        "front_poisson",
        "edge_poisson",
        "back_poisson",
        "quantum_monty",
        "cumulative_weighted_choice",
        "MultiChoice",
        "front_linear",
        "middle_linear",
        "back_linear",
        "quantum_linear",
        "front_gauss",
        "middle_gauss",
        "back_gauss",
        "quantum_gauss",
        "middle_poisson",
        "quantum_poisson",
    }
    assert removed.isdisjoint(Fortuna.__all__)
    assert all(not hasattr(Fortuna, name) for name in removed)


def test_removed_numeric_and_profile_methods_are_not_on_generator():
    removed = {
        "random_uint",
        "mixed_triangular",
        "front_exponential",
        "center_normal",
        "back_exponential",
        "mixed_exponential_normal",
        "front_poisson",
        "edge_poisson",
        "back_poisson",
        "quantum_monty",
    }
    assert all(not hasattr(Fortuna.Generator, name) for name in removed)


def test_normal_value_profiles_use_new_names_without_gauss_aliases():
    assert all(
        hasattr(Fortuna.RandomValue, name)
        for name in ("front_normal", "center_normal", "back_normal")
    )
    assert all(
        not hasattr(Fortuna.RandomValue, name)
        for name in ("front_gauss", "middle_gauss", "back_gauss")
    )
