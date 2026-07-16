"""Data structures shared by the benchmark runner and suites."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BenchmarkUnit = Literal["call", "value"]
Operation = Callable[[], Any]
Setup = Callable[[], Operation]
_WORKLOAD_FIELDS = frozenset({"args", "kwargs", "seed", "input", "setup_variant"})


def _normalize_workload_value(value: Any, path: str = "workload") -> Any:
    """Return a deterministic, JSON-safe representation of workload metadata."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path} contains a non-finite float")
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError(f"{path} mapping keys must be strings")
        return {
            key: _normalize_workload_value(value[key], f"{path}.{key}") for key in sorted(value)
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [
            _normalize_workload_value(item, f"{path}[{index}]") for index, item in enumerate(value)
        ]
    raise ValueError(f"{path} contains unsupported value {type(value).__name__}")


def calculate_workload_signature(payload: Mapping[str, Any]) -> str:
    """Hash canonical workload metadata for artifact comparison."""

    normalized = _normalize_workload_value(payload)
    encoded = json.dumps(
        normalized,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


class SkipBenchmark(RuntimeError):
    """Signal that a benchmark is not applicable in the current checkout."""


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    """One independently measurable operation.

    ``setup`` runs outside the timed interval for every calibration, warmup, and
    measured sample. It returns the zero-argument operation to time. Use it for
    mutable inputs (for example, a newly-created list for a shuffle case).
    """

    suite: str
    name: str
    operation: Operation | None = None
    setup: Setup | None = None
    unit: BenchmarkUnit = "call"
    values_per_call: int = 1
    description: str = ""
    skip_reason: str | None = None
    workload: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.operation is not None and self.setup is not None:
            raise ValueError("provide operation or setup, not both")
        if not self.skip_reason and self.operation is None and self.setup is None:
            raise ValueError("a runnable case needs operation or setup")
        if self.values_per_call < 1:
            raise ValueError("values_per_call must be positive")
        if self.unit == "call" and self.values_per_call != 1:
            raise ValueError("scalar cases must measure one call")
        if self.workload is not None:
            fields = set(self.workload)
            if fields != _WORKLOAD_FIELDS:
                missing = sorted(_WORKLOAD_FIELDS - fields)
                extra = sorted(fields - _WORKLOAD_FIELDS)
                details = []
                if missing:
                    details.append(f"missing {', '.join(missing)}")
                if extra:
                    details.append(f"unknown {', '.join(extra)}")
                raise ValueError(f"workload metadata is incomplete ({'; '.join(details)})")
            if not isinstance(self.workload["args"], Sequence) or isinstance(
                self.workload["args"], (str, bytes, bytearray)
            ):
                raise ValueError("workload.args must be a sequence")
            if not isinstance(self.workload["kwargs"], Mapping):
                raise ValueError("workload.kwargs must be a mapping")
            if (
                not isinstance(self.workload["setup_variant"], str)
                or not self.workload["setup_variant"]
            ):
                raise ValueError("workload.setup_variant must be a non-empty string")
            object.__setattr__(self, "workload", _normalize_workload_value(self.workload))

    @property
    def identifier(self) -> str:
        return f"{self.suite}/{self.name}"

    @property
    def workload_payload(self) -> dict[str, Any]:
        """Describe the timed workload without inspecting opaque callables."""

        if self.workload is not None:
            payload = dict(self.workload)
            declared = True
        else:
            payload = {
                "args": [],
                "kwargs": {},
                "seed": None,
                "input": None,
                "setup_variant": "per-sample-setup" if self.setup else "direct-operation",
            }
            declared = False
        return {"schema_version": 1, "declared": declared, **payload}

    @property
    def workload_signature(self) -> str:
        return calculate_workload_signature(self.workload_payload)

    def prepare(self) -> Operation:
        if self.skip_reason:
            raise SkipBenchmark(self.skip_reason)
        if self.setup is not None:
            operation = self.setup()
            if not callable(operation):
                raise TypeError(f"setup for {self.identifier} did not return a callable")
            return operation
        assert self.operation is not None
        return self.operation


@dataclass(frozen=True, slots=True)
class BenchmarkStats:
    samples: int
    minimum: float
    median: float
    q1: float
    q3: float
    iqr: float
    mad: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(slots=True)
class BenchmarkResult:
    suite: str
    name: str
    status: Literal["ok", "skipped", "error"]
    unit: BenchmarkUnit
    values_per_call: int
    loops: int = 0
    samples_ns: list[float] = field(default_factory=list)
    stats: BenchmarkStats | None = None
    values_per_second: float | None = None
    reason: str | None = None
    comparison: dict[str, Any] | None = None
    workload: dict[str, Any] | None = None
    workload_signature: str | None = None

    @property
    def identifier(self) -> str:
        return f"{self.suite}/{self.name}"

    @property
    def metric_name(self) -> str:
        return "ns/value" if self.unit == "value" else "ns/call"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "suite": self.suite,
            "name": self.name,
            "id": self.identifier,
            "status": self.status,
            "unit": self.unit,
            "metric": self.metric_name,
            "values_per_call": self.values_per_call,
            "loops": self.loops,
            "samples_ns": self.samples_ns,
        }
        if self.stats is not None:
            payload["stats"] = self.stats.to_dict()
        if self.values_per_second is not None:
            payload["values_per_second"] = self.values_per_second
        if self.reason:
            payload["reason"] = self.reason
        if self.comparison is not None:
            payload["comparison"] = self.comparison
        if self.workload is not None:
            payload["workload"] = self.workload
        if self.workload_signature is not None:
            payload["workload_signature"] = self.workload_signature
        return payload
