"""Compare compatible benchmark results with a previous JSON artifact."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .model import BenchmarkResult

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
    if payload.get("schema_version") != 1 or not isinstance(payload.get("results"), list):
        raise ValueError(f"{path} is not a Fortuna benchmark artifact")
    if any(not isinstance(item, dict) for item in payload["results"]):
        raise ValueError(f"{path} contains a malformed benchmark result")
    return payload


def compare_results(
    results: Iterable[BenchmarkResult],
    baseline: dict[str, Any],
    threshold_percent: float,
) -> int:
    if not math.isfinite(threshold_percent) or threshold_percent < 0:
        raise ValueError("regression threshold must be finite and nonnegative")
    previous = {item.get("id"): item for item in baseline["results"] if item.get("status") == "ok"}
    regressions = 0
    for result in results:
        old = previous.get(result.identifier)
        if result.status != "ok" or result.stats is None or not old:
            continue
        if old.get("metric") != result.metric_name:
            continue
        if old.get("values_per_call") != result.values_per_call:
            raise ValueError(f"baseline workload differs for {result.identifier}")
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
