from __future__ import annotations

from benchmarks.suites import all_cases, suite_names
from benchmarks.suites.selectors import RANDOM_VALUE_METHODS, SHUFFLE_SIZES, selector_cases


def _cases_by_name():
    return {case.name: case for case in selector_cases()}


def test_registered_cases_are_unique_and_strictly_comparable():
    cases = all_cases()
    identifiers = [case.identifier for case in cases]

    assert len(identifiers) == len(set(identifiers))
    assert all(case.workload_payload["declared"] for case in cases)


def test_selector_suite_is_registered():
    assert "selectors" in suite_names()
    assert any(case.suite == "selectors" for case in all_cases())


def test_selector_suite_names_are_unique_and_cover_each_api_family():
    cases = selector_cases()
    names = [case.name for case in cases]

    assert len(names) == len(set(names))
    assert all(case.suite == "selectors" for case in cases)
    assert all(case.workload_payload["declared"] for case in cases)
    assert all(case.workload_payload["input"] is not None for case in cases)
    assert len(cases) == 68
    for prefix in (
        "random-value-",
        "truffle-",
        "weighted-choice-",
        "sample-",
        "shuffle-",
    ):
        assert any(name.startswith(prefix) for name in names)


def test_selector_suite_operations_prepare_and_run_once():
    for case in selector_cases():
        assert case.skip_reason is None
        case.prepare()()


def test_random_value_covers_each_strategy_and_rng_owner():
    cases = _cases_by_name()

    for method in RANDOM_VALUE_METHODS:
        benchmark_method = method.replace("_", "-")
        for source, source_type in (
            ("module", "Fortuna module-global engine"),
            ("generator", "Fortuna.Generator"),
        ):
            workload = cases[f"random-value-{benchmark_method}-{source}-100"].workload_payload

            assert workload["args"] == []
            assert workload["kwargs"] == {}
            assert workload["seed"] == 0x5EED
            assert workload["input"]["callable"] == f"RandomValue.{method}"
            assert workload["input"]["constructor"]["generator"] == {
                "seed": 0x5EED,
                "type": source_type,
            }
            assert workload["input"]["fixtures"] == [
                {
                    "id": "values-100",
                    "recipe": "tuple(range(100))",
                    "size": 100,
                    "type": "tuple",
                }
            ]


def test_random_value_call_and_resolution_cases_are_explicit():
    cases = _cases_by_name()
    plain = cases["random-value-call-uniform-module-100"].workload_payload
    resolved = cases["random-value-callable-resolution-module-100"].workload_payload
    disabled = cases["random-value-callable-resolution-disabled-module-100"].workload_payload

    assert plain["input"]["callable"] == "RandomValue.__call__"
    assert plain["input"]["constructor"]["resolve_callables"] is True
    assert resolved["input"]["constructor"]["values"]["type"] == "tuple[callable, ...]"
    assert resolved["input"]["constructor"]["resolve_callables"] is True
    assert disabled["input"]["constructor"]["resolve_callables"] is False


def test_random_value_take_cases_report_per_value():
    cases = _cases_by_name()

    for count in (10, 1_000):
        case = cases[f"random-value-take-{count}"]

        assert case.unit == "value"
        assert case.values_per_call == count
        assert case.workload_payload["args"] == [count]
        assert case.workload_payload["input"]["callable"] == "RandomValue.take"


def test_reused_and_construction_workloads_distinguish_calls_from_fixtures():
    cases = _cases_by_name()

    for name in (
        "random-value-uniform-module-100",
        "truffle-call-100",
        "weighted-choice-call-100",
    ):
        workload = cases[name].workload_payload
        assert workload["args"] == []
        assert workload["kwargs"] == {}
        assert workload["input"] is not None

    for name in (
        "random-value-construction-100",
        "truffle-construction-100",
        "weighted-choice-construction-100",
    ):
        workload = cases[name].workload_payload
        assert workload["args"][0]["fixture"]
        assert workload["input"]["fixtures"][0]["recipe"]

    function = cases["random-value-function-100"].workload_payload
    assert function["args"] == [{"fixture": "values-100"}]
    assert function["input"]["callable"] == "random_value"


def test_weighted_choice_workloads_preserve_relative_weight_scaling():
    cases = _cases_by_name()

    for size in (4, 100, 1_000):
        workload = cases[f"weighted-choice-call-{size}"].workload_payload
        fixture = workload["input"]["fixtures"][0]

        assert workload["input"]["callable"] == "WeightedChoice.__call__"
        assert fixture["id"] == f"weighted-relative-{size}"
        assert fixture["size"] == size
        assert fixture["weight_model"] == "relative"


def test_weighted_choice_cumulative_workloads_are_explicit():
    cases = _cases_by_name()

    for size in (4, 100, 1_000):
        call = cases[f"weighted-choice-cumulative-call-{size}"].workload_payload
        construction = cases[f"weighted-choice-cumulative-construction-{size}"].workload_payload
        fixture = call["input"]["fixtures"][0]

        assert call["input"]["constructor"] == {
            "cumulative": {"fixture": f"weighted-cumulative-{size}"}
        }
        assert fixture["weight_model"] == "cumulative"
        assert construction["args"] == []
        assert construction["kwargs"] == {"cumulative": {"fixture": f"weighted-cumulative-{size}"}}


def test_collection_workloads_define_population_mutation_and_source_recipes():
    cases = _cases_by_name()
    sample = cases["sample-explicit-generator-100-10"].workload_payload
    shuffle = cases["shuffle-public-10"].workload_payload

    assert sample["args"] == [{"fixture": "population-100"}, 10]
    assert sample["kwargs"] == {"generator": {"fixture": "fortuna-generator"}}
    assert sample["input"]["source"] == {
        "id": "fortuna-generator",
        "seed": 0x5EED,
        "type": "Fortuna.Generator",
    }
    assert shuffle["args"] == [{"fixture": "mutable-values-10"}]
    assert shuffle["input"]["fixtures"][0]["recipe"] == "list(range(10))"
    assert shuffle["input"]["mutation"] == "in place across timed loop iterations"


def test_shuffle_covers_public_rng_owners_across_the_size_matrix():
    cases = _cases_by_name()

    for size in SHUFFLE_SIZES:
        fixture = {
            "id": f"mutable-values-{size}",
            "recipe": f"list(range({size}))",
            "size": size,
            "type": "list",
        }
        for name, callable_name in (
            (f"shuffle-public-{size}", "Fortuna.shuffle"),
            (f"shuffle-generator-method-{size}", "Generator.shuffle"),
        ):
            workload = cases[name].workload_payload

            assert workload["args"] == [{"fixture": fixture["id"]}]
            assert workload["input"]["callable"] == callable_name
            assert workload["input"]["fixtures"] == [fixture]
            assert workload["input"]["mutation"] == "in place across timed loop iterations"


def test_sample_custom_generator_fallback_has_exact_workload_metadata():
    workload = _cases_by_name()["sample-custom-generator-100-10"].workload_payload

    assert workload["args"] == [{"fixture": "population-100"}, 10]
    assert workload["kwargs"] == {"generator": {"fixture": "constant-index-generator"}}
    assert workload["seed"] is None
    assert workload["setup_variant"] == "custom generator fallback"
    assert workload["input"] == {
        "callable": "Fortuna.sample",
        "fixtures": [
            {
                "id": "population-100",
                "recipe": "tuple(range(100))",
                "size": 100,
                "type": "tuple",
            }
        ],
        "source": {
            "id": "constant-index-generator",
            "recipe": "random_index(size) returns 0",
            "seed": None,
            "type": "_ConstantIndexGenerator",
        },
    }
