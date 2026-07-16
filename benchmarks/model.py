"""Data structures shared by the benchmark runner and suites."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BenchmarkUnit = Literal["call", "value"]
Operation = Callable[[], Any]
Setup = Callable[[], Operation]


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

    def __post_init__(self) -> None:
        if self.operation is not None and self.setup is not None:
            raise ValueError("provide operation or setup, not both")
        if not self.skip_reason and self.operation is None and self.setup is None:
            raise ValueError("a runnable case needs operation or setup")
        if self.values_per_call < 1:
            raise ValueError("values_per_call must be positive")
        if self.unit == "call" and self.values_per_call != 1:
            raise ValueError("scalar cases must measure one call")

    @property
    def identifier(self) -> str:
        return f"{self.suite}/{self.name}"

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
        return payload
