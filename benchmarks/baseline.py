"""Compare compatible benchmark results with a previous JSON artifact."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .model import BenchmarkResult, calculate_workload_signature

_COMPARABILITY_FIELDS = (
    ("python", "version"),
    ("python", "implementation"),
    ("python", "compiler"),
    ("platform", "system"),
    ("platform", "release"),
    ("platform", "machine"),
    ("cpu", "model"),
    ("cpu", "logical_count"),
    ("cpu", "affinity"),
    ("execution", "benchmark_threads"),
    ("native_build", "toolchain", "compilers"),
    ("native_build", "toolchain", "build_options"),
    ("native_build", "toolchain", "build_packages"),
)


def _nested(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = payload
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def compatibility_issues(
    current_environment: dict[str, Any], baseline: dict[str, Any]
) -> list[str]:
    """Return reasons that a baseline is not directly comparable."""

    previous_environment = baseline.get("environment")
    if not isinstance(previous_environment, dict):
        return ["baseline has no environment metadata"]
    issues = []
    current_metadata = _nested(
        current_environment, ("native_build", "toolchain", "build_metadata_available")
    )
    previous_metadata = _nested(
        previous_environment, ("native_build", "toolchain", "build_metadata_available")
    )
    if current_metadata is not True or previous_metadata is not True:
        issues.append(
            "native build compiler/options metadata is unavailable; "
            "the artifacts are exploratory only"
        )
    for path in _COMPARABILITY_FIELDS:
        current = _nested(current_environment, path)
        previous = _nested(previous_environment, path)
        if current != previous:
            label = ".".join(path)
            issues.append(f"{label} differs: current={current!r}, baseline={previous!r}")
    return issues


def load_baseline(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} is not a Fortuna benchmark artifact")
    if payload.get("schema_version") not in {1, 2} or not isinstance(payload.get("results"), list):
        raise ValueError(f"{path} is not a Fortuna benchmark artifact")
    if any(not isinstance(item, dict) for item in payload["results"]):
        raise ValueError(f"{path} contains a malformed benchmark result")
    return payload


def compare_results(
    results: Iterable[BenchmarkResult],
    baseline: dict[str, Any],
    threshold_percent: float,
    *,
    require_complete: bool = False,
) -> int:
    """Annotate results and return the number of regressions.

    Exploratory comparisons preserve support for schema-v1 artifacts. A complete
    comparison is suitable for a gate: every selected result and its baseline
    must be successful and must carry matching, explicitly declared workload
    metadata.
    """

    if not math.isfinite(threshold_percent) or threshold_percent < 0:
        raise ValueError("regression threshold must be finite and nonnegative")
    result_list = list(results)
    current_ids = [result.identifier for result in result_list]
    if len(current_ids) != len(set(current_ids)):
        raise ValueError("current selection contains duplicate benchmark identifiers")

    previous: dict[str, dict[str, Any]] = {}
    for item in baseline["results"]:
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("baseline contains a result without a valid identifier")
        if identifier in previous:
            raise ValueError(f"baseline contains duplicate result {identifier}")
        previous[identifier] = item

    regressions = 0
    for result in result_list:
        old = previous.get(result.identifier)
        if result.status != "ok" or result.stats is None:
            if require_complete:
                raise ValueError(
                    f"selected result is not comparable for {result.identifier}: "
                    f"status={result.status}"
                )
            continue
        if old is None:
            if require_complete:
                raise ValueError(f"baseline is missing selected result {result.identifier}")
            continue
        if old.get("status") != "ok":
            if require_complete:
                raise ValueError(
                    f"baseline result is not comparable for {result.identifier}: "
                    f"status={old.get('status')!r}"
                )
            continue
        if old.get("metric") != result.metric_name:
            raise ValueError(f"baseline metric differs for {result.identifier}")
        if old.get("values_per_call") != result.values_per_call:
            raise ValueError(f"baseline workload differs for {result.identifier}")

        current_workload = result.workload
        current_signature = result.workload_signature
        old_workload = old.get("workload")
        old_signature = old.get("workload_signature")
        if current_workload is not None or current_signature is not None:
            if not isinstance(current_workload, dict) or not isinstance(current_signature, str):
                raise ValueError(f"current workload identity is malformed for {result.identifier}")
            if calculate_workload_signature(current_workload) != current_signature:
                raise ValueError(f"current workload signature is invalid for {result.identifier}")
        if old_workload is not None or old_signature is not None:
            if not isinstance(old_workload, dict) or not isinstance(old_signature, str):
                raise ValueError(f"baseline workload identity is malformed for {result.identifier}")
            if calculate_workload_signature(old_workload) != old_signature:
                raise ValueError(f"baseline workload signature is invalid for {result.identifier}")

        if current_signature is not None and old_signature is not None:
            if current_signature != old_signature:
                raise ValueError(f"baseline workload differs for {result.identifier}")
        elif require_complete:
            raise ValueError(f"workload identity is missing for {result.identifier}")
        if require_complete and (
            current_workload.get("declared") is not True or old_workload.get("declared") is not True
        ):
            raise ValueError(f"workload is not explicitly declared for {result.identifier}")

        old_median = old.get("stats", {}).get("median")
        if (
            not isinstance(old_median, (int, float))
            or not math.isfinite(old_median)
            or old_median <= 0
        ):
            raise ValueError(f"baseline median is invalid for {result.identifier}")
        delta = (result.stats.median - old_median) / old_median * 100
        if delta > threshold_percent:
            classification = "regression"
            regressions += 1
        elif delta < -threshold_percent:
            classification = "improvement"
        else:
            classification = "stable"
        result.comparison = {
            "baseline_median": old_median,
            "delta_percent": delta,
            "threshold_percent": threshold_percent,
            "classification": classification,
        }
    return regressions
