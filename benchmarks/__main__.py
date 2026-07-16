"""Command-line entry point for Fortuna's repository-local benchmarks."""

from __future__ import annotations

import argparse
import fnmatch
import math
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from .baseline import compare_results, compatibility_issues, load_baseline
from .environment import collect_environment, dump_json
from .formatting import render_results
from .model import BenchmarkCase
from .runner import BenchmarkConfig, run_cases
from .suites import all_cases, suite_names


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Fortuna's internal benchmarks.")
    parser.add_argument(
        "--suite",
        action="append",
        choices=suite_names(),
        help="run only this suite; repeat to select multiple suites",
    )
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        metavar="GLOB",
        help="case or suite/case glob; repeat to select multiple cases",
    )
    parser.add_argument("--list", action="store_true", help="list cases without running them")
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--samples", type=int, default=11)
    parser.add_argument(
        "--target-ms",
        type=float,
        default=50.0,
        help="target duration of each independent sample",
    )
    parser.add_argument("--output", type=Path, help="write the complete JSON artifact here")
    parser.add_argument("--json", action="store_true", help="also print JSON to stdout")
    parser.add_argument("--baseline", type=Path, help="compare against an earlier artifact")
    parser.add_argument(
        "--threshold", type=float, default=10.0, help="regression threshold percent"
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="return a failure status when comparison finds a regression",
    )
    parser.add_argument(
        "--allow-incomparable-baseline",
        action="store_true",
        help="compare despite runtime or machine metadata differences",
    )
    parser.add_argument(
        "--allow-skips",
        action="store_true",
        help="return success even when selected benchmark cases are unavailable",
    )
    return parser


def _matches(case: BenchmarkCase, patterns: Sequence[str]) -> bool:
    return not patterns or any(
        fnmatch.fnmatchcase(case.identifier, pattern) or fnmatch.fnmatchcase(case.name, pattern)
        for pattern in patterns
    )


def select_cases(
    cases: Sequence[BenchmarkCase], suites: Sequence[str], patterns: Sequence[str]
) -> list[BenchmarkCase]:
    return [
        case for case in cases if (not suites or case.suite in suites) and _matches(case, patterns)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not math.isfinite(args.threshold) or args.threshold < 0:
        print("Regression threshold must be finite and nonnegative.", file=sys.stderr)
        return 2
    cases = select_cases(all_cases(), args.suite or (), args.case)
    if not cases:
        print("No benchmark cases matched.", file=sys.stderr)
        return 2
    if args.list:
        for case in cases:
            state = f" [skip: {case.skip_reason}]" if case.skip_reason else ""
            print(f"{case.identifier}{state}")
        return 0

    try:
        config = BenchmarkConfig(
            warmups=args.warmups,
            samples=args.samples,
            target_sample_ns=int(args.target_ms * 1_000_000),
        )
    except ValueError as error:
        print(f"Invalid benchmark configuration: {error}", file=sys.stderr)
        return 2

    environment = collect_environment()
    results = run_cases(cases, config)
    regressions = 0
    if args.baseline:
        try:
            baseline = load_baseline(args.baseline)
            issues = compatibility_issues(environment, baseline)
            if issues and not args.allow_incomparable_baseline:
                print("Baseline is not comparable:", file=sys.stderr)
                for issue in issues:
                    print(f"- {issue}", file=sys.stderr)
                return 2
            regressions = compare_results(results, baseline, args.threshold)
        except (OSError, ValueError) as error:
            print(f"Cannot use baseline: {error}", file=sys.stderr)
            return 2

    payload = {
        "schema_version": 1,
        "environment": environment,
        "config": asdict(config),
        "selection": {"suites": args.suite or [], "cases": args.case},
        "summary": {
            "ok": sum(result.status == "ok" for result in results),
            "skipped": sum(result.status == "skipped" for result in results),
            "errors": sum(result.status == "error" for result in results),
            "regressions": regressions,
        },
        "results": [result.to_dict() for result in results],
    }
    rendered_json = dump_json(payload, args.output)
    print(render_results(results))
    print(
        f"\n{payload['summary']['ok']} passed, {payload['summary']['skipped']} skipped, "
        f"{payload['summary']['errors']} errors, {regressions} regressions"
    )
    if args.output:
        print(f"JSON: {args.output}")
    if args.json:
        print("\n" + rendered_json, end="")

    if payload["summary"]["errors"]:
        return 1
    if payload["summary"]["skipped"] and not args.allow_skips:
        return 1
    if args.fail_on_regression and regressions:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
