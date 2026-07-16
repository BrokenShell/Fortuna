from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from copy import deepcopy
from pathlib import Path

from benchmarks.__main__ import main
from benchmarks.baseline import compare_results, compatibility_issues, load_baseline
from benchmarks.environment import collect_environment
from benchmarks.model import BenchmarkCase, BenchmarkResult
from benchmarks.runner import BenchmarkConfig, calculate_stats, run_case

FAST = BenchmarkConfig(warmups=0, samples=3, target_sample_ns=10_000, max_loops=10_000)
DECLARED_WORKLOAD = {
    "args": [1, 10],
    "kwargs": {"count": 1},
    "seed": 8675309,
    "input": {"kind": "integer-range", "size": 10},
    "setup_variant": "reset-generator-per-sample",
}


class StatisticsTests(unittest.TestCase):
    def test_robust_statistics(self) -> None:
        stats = calculate_stats([1.0, 2.0, 3.0, 4.0, 100.0])
        self.assertEqual(stats.minimum, 1.0)
        self.assertEqual(stats.median, 3.0)
        self.assertEqual(stats.q1, 2.0)
        self.assertEqual(stats.q3, 4.0)
        self.assertEqual(stats.iqr, 2.0)
        self.assertEqual(stats.mad, 1.0)


class RunnerTests(unittest.TestCase):
    def test_scalar_case(self) -> None:
        result = run_case(BenchmarkCase("test", "scalar", operation=lambda: 1), FAST)
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.metric_name, "ns/call")
        self.assertEqual(len(result.samples_ns), 3)
        self.assertIsNotNone(result.stats)
        self.assertIsNotNone(result.workload)
        self.assertIsNotNone(result.workload_signature)

    def test_bulk_case_reports_throughput(self) -> None:
        result = run_case(
            BenchmarkCase(
                "test",
                "bulk",
                operation=lambda: list(range(10)),
                unit="value",
                values_per_call=10,
            ),
            FAST,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.metric_name, "ns/value")
        self.assertGreater(result.values_per_second or 0, 0)

    def test_setup_runs_outside_each_timed_batch(self) -> None:
        created: list[list[int]] = []

        def setup():
            values: list[int] = []
            created.append(values)
            return lambda: values.append(1)

        result = run_case(BenchmarkCase("test", "mutable", setup=setup), FAST)
        self.assertEqual(result.status, "ok")
        self.assertGreaterEqual(len(created), FAST.samples + 1)  # calibration plus samples
        self.assertEqual(len({id(values) for values in created}), len(created))

    def test_skip_and_error_are_results(self) -> None:
        skipped = run_case(BenchmarkCase("test", "skip", skip_reason="not ready"), FAST)
        self.assertEqual(skipped.status, "skipped")
        self.assertEqual(skipped.reason, "not ready")

        def broken():
            raise RuntimeError("boom")

        failed = run_case(BenchmarkCase("test", "error", operation=broken), FAST)
        self.assertEqual(failed.status, "error")
        self.assertIn("boom", failed.reason or "")


class WorkloadIdentityTests(unittest.TestCase):
    def test_declared_workload_is_canonical_and_serialized(self) -> None:
        case = BenchmarkCase("test", "identity", operation=lambda: 1, workload=DECLARED_WORKLOAD)
        reordered = BenchmarkCase(
            "test",
            "identity",
            operation=lambda: 1,
            workload={
                "setup_variant": "reset-generator-per-sample",
                "input": {"size": 10, "kind": "integer-range"},
                "seed": 8675309,
                "kwargs": {"count": 1},
                "args": (1, 10),
            },
        )
        self.assertTrue(case.workload_payload["declared"])
        self.assertEqual(case.workload_payload, reordered.workload_payload)
        self.assertEqual(case.workload_signature, reordered.workload_signature)

        result = BenchmarkResult("test", "identity", "ok", "call", 1)
        result.workload = case.workload_payload
        result.workload_signature = case.workload_signature
        serialized = result.to_dict()
        self.assertEqual(serialized["workload"], case.workload_payload)
        self.assertEqual(serialized["workload_signature"], case.workload_signature)

    def test_undeclared_workload_has_an_explicit_fallback_identity(self) -> None:
        direct = BenchmarkCase("test", "direct", operation=lambda: 1)
        setup = BenchmarkCase("test", "setup", setup=lambda: lambda: 1)
        self.assertFalse(direct.workload_payload["declared"])
        self.assertEqual(direct.workload_payload["setup_variant"], "direct-operation")
        self.assertEqual(setup.workload_payload["setup_variant"], "per-sample-setup")
        self.assertNotEqual(direct.workload_signature, setup.workload_signature)

    def test_workload_must_be_complete_and_json_safe(self) -> None:
        incomplete = {key: value for key, value in DECLARED_WORKLOAD.items() if key != "seed"}
        with self.assertRaisesRegex(ValueError, "missing seed"):
            BenchmarkCase("test", "incomplete", operation=lambda: 1, workload=incomplete)
        invalid = {**DECLARED_WORKLOAD, "seed": float("nan")}
        with self.assertRaisesRegex(ValueError, "non-finite"):
            BenchmarkCase("test", "invalid", operation=lambda: 1, workload=invalid)


class ComparisonTests(unittest.TestCase):
    @staticmethod
    def _identified_result(workload=None) -> BenchmarkResult:
        if workload is None:
            workload = DECLARED_WORKLOAD
        case = BenchmarkCase("test", "case", operation=lambda: 1, workload=workload)
        result = BenchmarkResult("test", "case", "ok", "call", 1)
        result.stats = calculate_stats([100.0, 100.0, 100.0])
        result.workload = case.workload_payload
        result.workload_signature = case.workload_signature
        return result

    @staticmethod
    def _baseline_for(result: BenchmarkResult) -> dict:
        return {"schema_version": 2, "results": [deepcopy(result.to_dict())]}

    def test_baseline_root_must_be_an_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "baseline.json")
            path.write_text(json.dumps([]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not a Fortuna benchmark artifact"):
                load_baseline(path)

    def test_comparison_classifies_regression(self) -> None:
        result = BenchmarkResult("test", "case", "ok", "call", 1)
        result.stats = calculate_stats([120.0, 120.0, 120.0])
        baseline = {
            "schema_version": 1,
            "results": [
                {
                    "id": "test/case",
                    "status": "ok",
                    "metric": "ns/call",
                    "values_per_call": 1,
                    "stats": {"median": 100.0},
                }
            ],
        }
        regressions = compare_results([result], baseline, threshold_percent=10.0)
        self.assertEqual(regressions, 1)
        self.assertEqual(result.comparison["classification"], "regression")

    def test_comparison_rejects_changed_workload_and_nonfinite_values(self) -> None:
        result = BenchmarkResult("test", "case", "ok", "value", 10)
        result.stats = calculate_stats([10.0, 10.0, 10.0])
        baseline = {
            "schema_version": 1,
            "results": [
                {
                    "id": "test/case",
                    "status": "ok",
                    "metric": "ns/value",
                    "values_per_call": 20,
                    "stats": {"median": 10.0},
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "workload differs"):
            compare_results([result], baseline, threshold_percent=10.0)
        baseline["results"][0]["values_per_call"] = 10
        baseline["results"][0]["stats"]["median"] = float("nan")
        with self.assertRaisesRegex(ValueError, "median is invalid"):
            compare_results([result], baseline, threshold_percent=10.0)
        with self.assertRaisesRegex(ValueError, "threshold"):
            compare_results([result], baseline, threshold_percent=float("nan"))

    def test_complete_comparison_rejects_missing_and_legacy_workloads(self) -> None:
        result = self._identified_result()
        with self.assertRaisesRegex(ValueError, "missing selected result"):
            compare_results(
                [result], {"schema_version": 2, "results": []}, 10.0, require_complete=True
            )

        legacy = self._baseline_for(result)
        legacy["schema_version"] = 1
        legacy["results"][0].pop("workload")
        legacy["results"][0].pop("workload_signature")
        self.assertEqual(compare_results([result], legacy, 10.0), 0)
        with self.assertRaisesRegex(ValueError, "identity is missing"):
            compare_results([result], legacy, 10.0, require_complete=True)

    def test_complete_comparison_rejects_undeclared_workloads(self) -> None:
        case = BenchmarkCase("test", "case", operation=lambda: 1)
        result = BenchmarkResult("test", "case", "ok", "call", 1)
        result.stats = calculate_stats([100.0, 100.0, 100.0])
        result.workload = case.workload_payload
        result.workload_signature = case.workload_signature
        with self.assertRaisesRegex(ValueError, "not explicitly declared"):
            compare_results([result], self._baseline_for(result), 10.0, require_complete=True)

    def test_comparison_rejects_each_changed_workload_dimension(self) -> None:
        baseline_result = self._identified_result()
        baseline = self._baseline_for(baseline_result)
        changes = {
            "args": [2, 10],
            "kwargs": {"count": 2},
            "seed": 42,
            "input": {"kind": "integer-range", "size": 20},
            "setup_variant": "shared-generator",
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                changed = self._identified_result({**DECLARED_WORKLOAD, field: value})
                with self.assertRaisesRegex(ValueError, "workload differs"):
                    compare_results([changed], deepcopy(baseline), 10.0)

    def test_comparison_rejects_tampered_workload_signature(self) -> None:
        result = self._identified_result()
        baseline = self._baseline_for(result)
        baseline["results"][0]["workload"]["seed"] = 42
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            compare_results([result], baseline, 10.0)

    def test_environment_compatibility_is_explicit(self) -> None:
        environment = {
            "python": {"version": "3.14", "implementation": "CPython", "compiler": "clang"},
            "platform": {"system": "Darwin", "release": "25", "machine": "arm64"},
            "cpu": {"model": "Example", "logical_count": 8, "affinity": None},
            "execution": {"benchmark_threads": 1},
            "native_build": {
                "extension": {"sha256": "candidate"},
                "toolchain": {
                    "build_metadata_available": True,
                    "compilers": {"cpp": {"id": "clang", "version": "21"}},
                    "build_options": {"buildtype": "release", "optimization": "3"},
                    "build_packages": {
                        "Cython": "3.1.2",
                        "meson": "1.8.2",
                        "meson-python": "0.18.0",
                        "ninja": "1.13.0",
                    },
                },
            },
        }
        baseline = {"environment": deepcopy(environment)}
        baseline["environment"]["native_build"]["extension"]["sha256"] = "baseline"
        assert compatibility_issues(environment, baseline) == []
        changed = {**environment, "python": {**environment["python"], "version": "3.13"}}
        issues = compatibility_issues(changed, baseline)
        self.assertTrue(any("python.version differs" in issue for issue in issues))
        changed_options = deepcopy(environment)
        changed_options["native_build"]["toolchain"]["build_options"]["optimization"] = "2"
        issues = compatibility_issues(changed_options, baseline)
        self.assertTrue(any("native_build.toolchain.build_options" in issue for issue in issues))

    def test_environment_compatibility_rejects_native_build_package_drift(self) -> None:
        environment = {
            "native_build": {
                "toolchain": {
                    "build_metadata_available": True,
                    "compilers": {"cpp": {"id": "clang", "version": "21"}},
                    "build_options": {"buildtype": "release", "optimization": "3"},
                    "build_packages": {
                        "Cython": "3.1.2",
                        "meson": "1.8.2",
                        "meson-python": "0.18.0",
                        "ninja": "1.13.0",
                    },
                }
            }
        }
        baseline = {"environment": deepcopy(environment)}
        environment["native_build"]["toolchain"]["build_packages"]["Cython"] = "3.1.3"

        issues = compatibility_issues(environment, baseline)

        self.assertTrue(any("native_build.toolchain.build_packages" in issue for issue in issues))

    def test_environment_compatibility_rejects_missing_native_build_metadata(self) -> None:
        environment = {
            "native_build": {
                "toolchain": {
                    "build_metadata_available": True,
                    "compilers": {"cpp": {"id": "clang", "version": "21"}},
                    "build_options": {"buildtype": "release", "optimization": "3"},
                    "build_packages": {},
                }
            }
        }
        baseline = {"environment": deepcopy(environment)}
        del environment["native_build"]["toolchain"]["build_metadata_available"]

        issues = compatibility_issues(environment, baseline)

        self.assertTrue(any("metadata is unavailable" in issue for issue in issues))

    def test_strict_comparison_rejects_allow_incomparable_override(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(
                [
                    "--baseline",
                    "unused.json",
                    "--require-complete-baseline",
                    "--allow-incomparable-baseline",
                ]
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("cannot be used with a strict comparison", stderr.getvalue())

    def test_environment_captures_native_build_identity(self) -> None:
        native = collect_environment()["native_build"]
        self.assertIn("available", native)
        if native["available"]:
            self.assertEqual(len(native["extension"]["sha256"]), 64)
            self.assertIn("compilers", native["toolchain"])


if __name__ == "__main__":
    unittest.main()
