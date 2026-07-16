from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.baseline import compare_results, compatibility_issues, load_baseline
from benchmarks.model import BenchmarkCase, BenchmarkResult
from benchmarks.runner import BenchmarkConfig, calculate_stats, run_case

FAST = BenchmarkConfig(warmups=0, samples=3, target_sample_ns=10_000, max_loops=10_000)


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


class ComparisonTests(unittest.TestCase):
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

    def test_environment_compatibility_is_explicit(self) -> None:
        environment = {
            "python": {"version": "3.14", "implementation": "CPython", "compiler": "clang"},
            "platform": {"system": "Darwin", "release": "25", "machine": "arm64"},
            "cpu": {"model": "Example", "logical_count": 8, "affinity": None},
            "execution": {"benchmark_threads": 1},
        }
        baseline = {"environment": environment.copy()}
        assert compatibility_issues(environment, baseline) == []
        changed = {**environment, "python": {**environment["python"], "version": "3.13"}}
        issues = compatibility_issues(changed, baseline)
        self.assertTrue(any("python.version differs" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
