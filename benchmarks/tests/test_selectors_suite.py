from __future__ import annotations

from benchmarks.suites import all_cases, suite_names
from benchmarks.suites.selectors import INDEX_PROFILES, selector_cases


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
    assert len(cases) == 108
    for prefix in (
        "index-",
        "random-value-",
        "truffle-",
        "quantum-",
        "flex-",
        "weighted-relative-",
        "weighted-cumulative-",
        "sample-",
        "shuffle-",
        "resolve-",
    ):
        assert any(name.startswith(prefix) for name in names)


def test_selector_suite_operations_prepare_and_run_once():
    for case in selector_cases():
        assert case.skip_reason is None
        case.prepare()()


def test_selector_bulk_cases_report_per_value():
    bulk_cases = [case for case in selector_cases() if "bulk" in case.name]

    assert bulk_cases
    assert len(bulk_cases) == 27
    assert all(case.unit == "value" for case in bulk_cases)
    assert all(case.values_per_call == 1_000 for case in bulk_cases)


def test_index_selector_workloads_match_timed_calls_and_rng_ownership():
    cases = _cases_by_name()
    scalar = cases["index-uniform-scalar-module"].workload_payload
    bulk = cases["index-front-triangular-bulk-module-1000"].workload_payload
    custom = cases["index-uniform-scalar-custom"].workload_payload

    assert scalar["args"] == [100]
    assert scalar["kwargs"] == {}
    assert bulk["args"] == [100]
    assert bulk["kwargs"] == {"count": 1_000}
    assert custom["seed"] is None
    assert custom["input"]["selector"]["generator"]["type"] == "_ConstantIndexGenerator"


def test_index_selector_covers_every_profile_with_module_and_generator_sources():
    cases = _cases_by_name()

    for profile in INDEX_PROFILES:
        benchmark_profile = profile.replace("_", "-")
        for source, source_type in (
            ("module", "Fortuna module-global engine"),
            ("generator", "Fortuna.Generator"),
        ):
            workload = cases[f"index-{benchmark_profile}-scalar-{source}"].workload_payload

            assert workload["args"] == [100]
            assert workload["kwargs"] == {}
            assert workload["seed"] == 0x5EED
            assert workload["input"] == {
                "callable": "IndexSelector.__call__",
                "selector": {
                    "generator": {"seed": 0x5EED, "type": source_type},
                    "profile": profile,
                },
            }

            bulk = cases[f"index-{benchmark_profile}-bulk-{source}-1000"].workload_payload
            assert bulk["args"] == [100]
            assert bulk["kwargs"] == {"count": 1_000}
            assert bulk["seed"] == 0x5EED
            assert bulk["input"] == workload["input"]

    custom_bulk = cases["index-uniform-bulk-custom-1000"].workload_payload
    assert custom_bulk["args"] == [100]
    assert custom_bulk["kwargs"] == {"count": 1_000}
    assert custom_bulk["seed"] is None
    assert custom_bulk["input"]["selector"]["generator"] == {
        "recipe": "random_index returns 0 or count zeros",
        "type": "_ConstantIndexGenerator",
    }


def test_reused_and_construction_workloads_distinguish_calls_from_fixtures():
    cases = _cases_by_name()

    for name in (
        "random-value-noncallable",
        "truffle-call-100",
        "quantum-named-100",
        "weighted-relative-call-100",
    ):
        workload = cases[name].workload_payload
        assert workload["args"] == []
        assert workload["kwargs"] == {}
        assert workload["input"] is not None

    for name in (
        "random-value-construction-100",
        "truffle-construction-100",
        "quantum-construction-100",
        "weighted-cumulative-construction-100",
    ):
        workload = cases[name].workload_payload
        assert workload["args"][0]["fixture"]
        assert workload["input"]["fixtures"][0]["recipe"]

    function = cases["random-value-function-100"].workload_payload
    assert function["args"] == [{"fixture": "values-100"}]
    assert function["input"]["callable"] == "random_value"


def test_quantum_and_flex_workloads_record_real_dispatch_arguments():
    cases = _cases_by_name()

    assert cases["quantum-dispatch-string-100"].workload_payload["args"] == ["center_normal"]
    assert cases["quantum-dispatch-enum-100"].workload_payload["args"] == [
        {"enum": "IndexProfile.CENTER_NORMAL"}
    ]
    assert cases["flex-default-explicit-key-10x10"].workload_payload["args"] == [3]
    assert cases["flex-default-random-key-10x10"].workload_payload["args"] == []
    assert cases["flex-uniform-construction-10x10"].workload_payload["kwargs"] == {
        "key_selector": "uniform",
        "value_selector": "uniform",
    }


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


def test_resolve_workloads_record_values_kwargs_and_chain_depth():
    cases = _cases_by_name()
    disabled = cases["resolve-disabled"].workload_payload
    deep = cases["resolve-depth-100"].workload_payload

    assert disabled["args"] == [{"fixture": "resolved-value-callable"}]
    assert disabled["kwargs"] == {"resolve_callables": False}
    assert deep["args"] == [{"fixture": "resolution-chain-100"}]
    assert deep["kwargs"] == {}
    assert deep["seed"] is None
    assert deep["input"]["value"]["callable_hops"] == 100
