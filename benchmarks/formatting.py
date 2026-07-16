"""Human-readable benchmark output."""

from __future__ import annotations

from collections.abc import Iterable

from .model import BenchmarkResult


def _number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.3f}m"
    if value >= 1_000:
        return f"{value / 1_000:.3f}k"
    return f"{value:.2f}"


def render_results(results: Iterable[BenchmarkResult]) -> str:
    items = list(results)
    headings = ("benchmark", "median", "min", "IQR", "MAD", "throughput", "change")
    rows: list[tuple[str, ...]] = []
    for result in items:
        if result.status != "ok" or result.stats is None:
            rows.append((result.identifier, result.status, "-", "-", "-", "-", result.reason or ""))
            continue
        stats = result.stats
        comparison = result.comparison or {}
        change = (
            f"{comparison['delta_percent']:+.2f}% {comparison['classification']}"
            if comparison
            else "-"
        )
        throughput = (
            f"{_number(result.values_per_second)} values/s"
            if result.values_per_second is not None
            else "-"
        )
        rows.append(
            (
                result.identifier,
                f"{_number(stats.median)} {result.metric_name}",
                _number(stats.minimum),
                _number(stats.iqr),
                _number(stats.mad),
                throughput,
                change,
            )
        )

    widths = [len(value) for value in headings]
    for row in rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row, strict=True)]

    def line(row: tuple[str, ...]) -> str:
        return "  ".join(
            value.ljust(width) for value, width in zip(row, widths, strict=True)
        ).rstrip()

    separator = tuple("-" * width for width in widths)
    return "\n".join((line(headings), line(separator), *(line(row) for row in rows)))
